import os
import requests
import sys

MODELS_DIR = "models"
LLAMA_DIR = os.path.join(MODELS_DIR, "llama")
WHISPER_DIR = os.path.join(MODELS_DIR, "whisper")
PIPER_DIR = os.path.join(MODELS_DIR, "piper")

# URLs for models
LLAMA_MODEL_URL = "https://huggingface.co/lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
LLAMA_FILENAME = "llama-3-8b-instruct.Q5_K_M.gguf" # Keeping the name from .env

PIPER_VOICE_ONNX = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx"
PIPER_VOICE_JSON = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json"

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"Skipping {dest}, already exists.")
        return
    print(f"Downloading {url} to {dest}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Done!")
    except Exception as e:
        print(f"Failed to download: {e}")

def setup():
    # 1. Create directories
    for d in [LLAMA_DIR, WHISPER_DIR, PIPER_DIR]:
        os.makedirs(d, exist_ok=True)
        print(f"Created {d}")

    # 2. Download LLM
    llama_dest = os.path.join(LLAMA_DIR, LLAMA_FILENAME)
    # Note: Llama is HUGE (5GB+), might take a while.
    # We warn the user about this.
    print("\n--- LLM SETUP ---")
    print("Warning: Downloading Llama 3 (approx 5GB). This may take several minutes depending on your internet.")
    download_file(LLAMA_MODEL_URL, llama_dest)

    # 3. Download TTS Models
    print("\n--- TTS SETUP ---")
    download_file(PIPER_VOICE_ONNX, os.path.join(PIPER_DIR, "en_US-amy-medium.onnx"))
    download_file(PIPER_VOICE_JSON, os.path.join(PIPER_DIR, "en_US-amy-medium.onnx.json"))

    print("\n--- STT SETUP ---")
    print("STT models (Faster-Whisper) will be downloaded automatically on first run by the backend.")

    print("\nAI Models Setup Complete!")

if __name__ == "__main__":
    setup()
