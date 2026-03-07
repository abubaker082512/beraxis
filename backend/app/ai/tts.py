"""
AI Pipeline Component: Text-to-Speech (Piper).
Streams PCM audio bytes directly back to caller.
"""
import asyncio
import os
import subprocess
from typing import AsyncGenerator
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def generate_speech_stream(text_stream: AsyncGenerator[str, None], voice_id: str) -> AsyncGenerator[bytes, None]:
    """
    Consumes a stream of text chunks and yields an audio byte stream (PCM 16kHz).
    Uses Piper TTS via subprocess (optimized for low latency C++ backend).
    """
    voice = voice_id or settings.PIPER_DEFAULT_VOICE
    model_path = os.path.join(settings.PIPER_MODELS_DIR, f"{voice}.onnx")
    
    if not os.path.exists(model_path):
        logger.warning(f"Voice {voice} not found at {model_path}. Falling back to mock audio.")
        # If model doesn't exist (dev setup), yield silence
        yield b'\x00' * 32000
        return

    # Start Piper process passing text via stdin and getting raw audio via stdout
    # Using the piper executable from venv if available
    piper_exe = os.path.join(settings.BASE_DIR, "venv", "Scripts", "piper.exe")
    if not os.path.exists(piper_exe):
        piper_exe = "piper" # Fallback to system path

    process = await asyncio.create_subprocess_exec(
        piper_exe,
        "--model", model_path,
        "--output_raw",
        "--sample_rate", str(settings.PIPER_SAMPLE_RATE),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )

    async def write_text():
        # Feed text chunks as they arrive from LLM
        async for text_chunk in text_stream:
            if text_chunk.strip():
                process.stdin.write(f"{text_chunk}\n".encode("utf-8"))
                await process.stdin.drain()
        process.stdin.close()

    async def read_audio():
        # Read raw PCM audio chunk by chunk (e.g. 4096 bytes)
        while True:
            chunk = await process.stdout.read(4096)
            if not chunk:
                break
            yield chunk

    # Run writing and reading concurrently
    writer_task = asyncio.create_task(write_text())
    
    async for audio_chunk in read_audio():
        yield audio_chunk
        
    await writer_task
    await process.wait()
