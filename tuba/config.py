from pathlib import Path
from typing import Final
import os

# Varsayılan LLaMA modeli (TinyLlama GGUF). İndirme yoksa otomatik yapılır.
DEFAULT_MODEL_URL: Final[str] = (
    "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/"
    "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
)

MODELS_DIR: Final[Path] = Path("models")
DEFAULT_MODEL_PATH: Final[Path] = MODELS_DIR / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

# Ortam değişkeni ile farklı model kullanılabilir
LLAMA_MODEL_ENV: Final[str] = os.getenv("TUBA_LLAMA_MODEL", str(DEFAULT_MODEL_PATH))

# OCR aramaları için azami dönüş sayısı
OCR_MAX_RESULTS: Final[int] = 5

# Vosk model ayarı (Türkçe küçük model)
DEFAULT_VOSK_URL: Final[str] = (
    "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip"
)
VOSK_DIR: Final[Path] = Path("models/vosk-model-small-tr-0.3")
VOSK_ZIP_PATH: Final[Path] = Path("models/vosk-model-small-tr-0.3.zip")
