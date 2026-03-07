"""
AI Pipeline Component: LLM (Llama 3 via llama.cpp).
Handles conversation structure and inference.
"""
import asyncio
import os
import time
from typing import List, Dict
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global model instance
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        try:
            from llama_cpp import Llama
            model_path = settings.LLAMA_MODEL_PATH
            logger.info(f"Loading LLM {os.path.basename(model_path)} (CPU Optimized)...")
            t0 = time.perf_counter()
            _llm = Llama(
                model_path=model_path,
                n_gpu_layers=0, # Force CPU for stability unless user has CUDA setup
                n_ctx=2048,
                n_threads=8, # Optimized for this CPU
                n_batch=512,
                verbose=False
            )
            # Warmup
            _llm("Warmup prompt", max_tokens=1)
            logger.info(f"LLM loaded and warmed up in {time.perf_counter()-t0:.2f}s")
        except ImportError:
            logger.warning("llama-cpp-python not installed. LLM will use mock responses.")
            return None
        except Exception as e:
            logger.error(f"Failed to load LLM: {str(e)}")
            return None
    return _llm


def format_llama_3_prompt(system_prompt: str, history: List[Dict[str, str]], user_message: str) -> str:
    """Format messages into Llama 3 Instruct format."""
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>"
    
    for msg in history:
        role = "assistant" if msg["speaker"] == "ai" else "user"
        prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{msg['text']}<|eot_id|>"
        
    prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    return prompt


async def generate_response(
    system_prompt: str,
    conversation_history: List[Dict[str, str]], 
    user_message: str,
    temperature: float = None,
    max_tokens: int = None
) -> str:
    """Generate a single response from the LLM."""
    llm = get_llm()
    if not llm:
        # Fallback for dev environments without the model downloaded
        return f"[MOCK AI RESPONSE] I heard you say: '{user_message}'"
        
    prompt = format_llama_3_prompt(system_prompt, conversation_history, user_message)
    temp = temperature if temperature is not None else settings.LLAMA_TEMPERATURE
    mt = max_tokens if max_tokens is not None else settings.LLAMA_MAX_TOKENS
    
    # Run in threadpool since llama.cpp is blocking
    response = await asyncio.to_thread(
        llm,
        prompt,
        max_tokens=mt,
        temperature=temp,
        stop=["<|eot_id|>"],
        echo=False
    )
    
    return response["choices"][0]["text"].strip()


async def stream_response(
    system_prompt: str,
    conversation_history: List[Dict[str, str]], 
    user_message: str,
    temperature: float = None
):
    """Generate streaming response (token by token) for lower latency TTS."""
    llm = get_llm()
    if not llm:
        yield f"[MOCK AI RESPONSE] I heard you say: '{user_message}'"
        return
        
    prompt = format_llama_3_prompt(system_prompt, conversation_history, user_message)
    temp = temperature if temperature is not None else settings.LLAMA_TEMPERATURE
    
    # We use a wrapper function for the blocking generator
    def run_generator():
        return llm(
            prompt,
            max_tokens=settings.LLAMA_MAX_TOKENS,
            temperature=temp,
            stop=["<|eot_id|>"],
            stream=True
        )
        
    generator = await asyncio.to_thread(run_generator)
    
    buffer = ""
    # We yield chunks on sentence boundaries ideally
    for chunk in generator:
        text_chunk = chunk["choices"][0]["text"]
        buffer += text_chunk
        
        # Yield if we hit punctuation
        if any(p in buffer for p in [". ", "? ", "! ", ".\n"]):
            yield buffer
            buffer = ""
            
    if buffer:
        yield buffer
