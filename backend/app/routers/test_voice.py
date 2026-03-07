"""
Aggressively Optimised & Thread-Safe Voice Test Endpoint.
"""
import base64
import io
import json
import logging
import os
import re
import shutil
import subprocess
import time
import wave
import asyncio
from typing import AsyncGenerator

import numpy as np
import soundfile as sf
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse

from app.config import settings

router = APIRouter(prefix="/api/v1/test", tags=["Voice Test"])
logger = logging.getLogger(__name__)

# ── Model Singletons ──────────────────────────────────────────────────
_whisper = None
_llm = None


def _get_whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        # This will be the absolute path we set in .env
        model_path = getattr(settings, "WHISPER_MODEL_SIZE", "tiny.en")
        print(f"[VOICE-MODELS] Loading Whisper from: {model_path}")
        t0 = time.perf_counter()
        
        # Check if it is a directory (local model)
        is_local = os.path.isdir(model_path)
        
        _whisper = WhisperModel(
            model_path, 
            device="cpu", 
            compute_type="int8",
            cpu_threads=4, 
            download_root=settings.WHISPER_MODEL_PATH,
            local_files_only=is_local
        )
        # Warmup
        _whisper.transcribe(np.zeros(16000, dtype=np.float32))
        print(f"[VOICE-MODELS] Whisper warmup done in {time.perf_counter()-t0:.2f}s")
    return _whisper


def _get_llm():
    global _llm
    if _llm is None:
        try:
            from llama_cpp import Llama
            model_name = os.path.basename(settings.LLAMA_MODEL_PATH)
            print(f"[VOICE-MODELS] Loading Llama {model_name} (CPU Optimized)...")
            t0 = time.perf_counter()
            _llm = Llama(
                model_path=settings.LLAMA_MODEL_PATH,
                n_ctx=512,
                n_threads=4, # Reduced threads to avoid CPU saturation
                n_batch=512,
                verbose=False,
            )
            # Warmup
            print("[VOICE-MODELS] Warming up Llama...")
            _llm("Hi", max_tokens=1)
            print(f"[VOICE-MODELS] Llama warmup done in {time.perf_counter()-t0:.2f}s")
        except Exception as e:
            print(f"[VOICE-MODELS] [ERROR] LLM Load failed: {e}")
    return _llm


def _find_piper() -> str:
    candidates = [
        "/app/piper/piper",  # Docker/Linux path (Priority)
        r"d:\Beraxis\backend\venv\Scripts\piper.exe",
        r"d:\Beraxis\venv\Scripts\piper.exe",
        shutil.which("piper")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "piper"


# ── Logic ─────────────────────────────────────────────────────────────

def _piper_synth(text: str) -> bytes:
    voice_model = os.path.join(settings.PIPER_MODELS_DIR, f"{settings.PIPER_DEFAULT_VOICE}.onnx")
    piper_exe = _find_piper()
    try:
        t0 = time.perf_counter()
        result = subprocess.run(
            [piper_exe, "--model", voice_model, "--output_raw"],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=10
        )
        print(f"[VOICE-TTS] Piper synth for {len(text)} chars took {(time.perf_counter()-t0)*1000:.0f}ms")
        pcm = result.stdout
        # Wrap in WAV
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(settings.PIPER_SAMPLE_RATE)
            wf.writeframes(pcm)
        return buf.getvalue()
    except Exception as e:
        print(f"[VOICE-TTS] [ERROR] Piper synthesis failed: {e}")
        return b""


@router.get("/voice", response_class=HTMLResponse, include_in_schema=False)
async def voice_ui():
    html_path = os.path.join(os.path.dirname(__file__), "..", "..", "test_voice.html")
    if os.path.exists(html_path):
        return HTMLResponse(open(html_path, encoding="utf-8").read())
    return HTMLResponse("<h1>test_voice.html not found</h1>", 404)


@router.post("/voice")
async def voice_endpoint(audio: UploadFile = File(...)):
    """Single-request streaming pipeline."""
    raw = await audio.read()
    
    async def stream_results():
        t_total_start = time.perf_counter()
        
        # 1. STT Phase
        print(f"\n[VOICE-FLOW] Received {len(raw)} bytes audio. Decoding...")
        try:
            audio_np, sr = sf.read(io.BytesIO(raw), dtype="float32")
            if audio_np.ndim > 1: audio_np = audio_np.mean(axis=1)
        except Exception as e:
            print(f"[VOICE-FLOW] [ERROR] Audio decode failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'text': f'Audio decode error: {e}'})}\n\n"
            return

        print("[VOICE-FLOW] Transcribing with Whisper...")
        t_stt_start = time.perf_counter()
        whisper = _get_whisper()
        segments, _ = await asyncio.to_thread(
            whisper.transcribe, audio_np, beam_size=1, language="en"
        )
        transcript = " ".join(s.text for s in segments).strip() or "Hello"
        t_stt_done = time.perf_counter()
        print(f"[VOICE-FLOW] STT done in {(t_stt_done-t_stt_start)*1000:.0f}ms -> User: {transcript}")
        
        # Yield transcript to UI immediately
        yield f"data: {json.dumps({'type': 'stt', 'text': transcript, 'ms': int((t_stt_done-t_stt_start)*1000)})}\n\n"

        # 2. LLM + TTS Phase
        llm = _get_llm()
        if not llm:
            print("[VOICE-FLOW] [ERROR] LLM not loaded")
            yield f"data: {json.dumps({'type': 'audio', 'text': 'LLM Offline', 'wav': ''})}\n\n"
            return

        print("[VOICE-FLOW] Generating LLM response...")
        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            "You are Beraxis. Be EXTREMELY BRIEF (under 10 words). Be helpful.<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n{transcript}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        loop = asyncio.get_event_loop()
        q = asyncio.Queue()

        def _run_llm():
            try:
                # Threaded iterator
                it = llm(prompt, stream=True, max_tokens=64, stop=["<|eot_id|>"])
                for chunk in it:
                    token = chunk["choices"][0]["text"]
                    # Thread-safe queue interaction
                    loop.call_soon_threadsafe(q.put_nowait, token)
            except Exception as e:
                print(f"[VOICE-FLOW] [ERROR] LLM Thread error: {e}")
            finally:
                loop.call_soon_threadsafe(q.put_nowait, None)

        asyncio.create_task(asyncio.to_thread(_run_llm))

        buffer = ""
        full_ai_response = ""
        t_first_token = None
        
        while True:
            token = await q.get()
            if token is None:
                print("[VOICE-FLOW] LLM stream closed")
                break
            
            if t_first_token is None:
                t_first_token = time.perf_counter()
                print(f"[VOICE-FLOW] First token in {(t_first_token-t_stt_done)*1000:.0f}ms")

            buffer += token
            full_ai_response += token
            
            # Sentence splitting
            if any(p in buffer for p in [". ", "? ", "! ", ".\n", "!\n", "?\n"]):
                sentences = re.split(r'(?<=[.!?])\s+', buffer.strip())
                if len(sentences) > 1:
                    to_speak = sentences[0]
                    buffer = " ".join(sentences[1:])
                    print(f"[VOICE-FLOW] Synthesising: {to_speak}")
                    wav_bytes = await asyncio.to_thread(_piper_synth, to_speak)
                    if wav_bytes:
                        b64 = base64.b64encode(wav_bytes).decode('ascii')
                        yield f"data: {json.dumps({'type': 'audio', 'text': to_speak, 'wav': b64})}\n\n"

        # Final sentence
        final_text = buffer.strip()
        if final_text:
            print(f"[VOICE-FLOW] Synthesising final: {final_text}")
            wav_bytes = await asyncio.to_thread(_piper_synth, final_text)
            if wav_bytes:
                b64 = base64.b64encode(wav_bytes).decode('ascii')
                yield f"data: {json.dumps({'type': 'audio', 'text': final_text, 'wav': b64})}\n\n"

        total_ms = int((time.perf_counter() - t_total_start) * 1000)
        yield f"data: {json.dumps({'type': 'done', 'full_text': full_ai_response, 'total_ms': total_ms})}\n\n"
        print(f"[VOICE-FLOW] Done in {total_ms}ms\n")

    return StreamingResponse(
        stream_results(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )
