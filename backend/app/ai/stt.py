"""
AI Pipeline Component: Speech-to-Text (Faster-Whisper).
Handles streaming audio chunks from Asterisk -> Text.
"""
import asyncio
import os
import time
import numpy as np
from typing import AsyncGenerator
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global model instance
_model = None


import os
import time

def get_model():
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel
            model_path = getattr(settings, "WHISPER_MODEL_SIZE", "tiny.en")
            logger.info(f"Loading Whisper from: {model_path}")
            
            is_local = os.path.isdir(model_path)
            
            _model = WhisperModel(
                model_path,
                device="cpu",
                compute_type="int8",
                cpu_threads=4,
                download_root=settings.WHISPER_MODEL_PATH,
                local_files_only=is_local
            )
            # Warmup
            _model.transcribe(np.zeros(16000, dtype=np.float32))
        except ImportError:
            logger.warning("faster-whisper not installed. STT will not work.")
            return None
    return _model


async def transcribe_stream(audio_chunks: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
    """
    Consumes a stream of 16kHz mono PCM chunks.
    Yields text transcripts.
    This is a simplified windowing approach. In prod, VAD (Voice Activity Detection)
    is used to chunk efficiently.
    """
    model = get_model()
    buffer = b""
    CHUNK_SIZE = 16000 * 2 * 3  # 3 seconds of 16kHz 16-bit audio
    
    async for chunk in audio_chunks:
        buffer += chunk
        
        if len(buffer) >= CHUNK_SIZE:
            # Convert PCM bytes to float32 numpy array for whisper
            audio_np = np.frombuffer(buffer, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Run inference in threadpool since faster_whisper is blocking
            segments, info = await asyncio.to_thread(
                model.transcribe, 
                audio_np, 
                beam_size=5,
                language=settings.WHISPER_LANGUAGE
            )
            
            text = " ".join([seg.text for seg in segments]).strip()
            if text:
                yield text
                
            buffer = b""  # Clear buffer after processing
            
    # Process remaining buffer
    if len(buffer) > 16000 * 2 * 0.5: # At least 0.5s audio
        audio_np = np.frombuffer(buffer, dtype=np.int16).astype(np.float32) / 32768.0
        segments, info = await asyncio.to_thread(model.transcribe, audio_np, beam_size=5, language=settings.WHISPER_LANGUAGE)
        text = " ".join([seg.text for seg in segments]).strip()
        if text:
            yield text
