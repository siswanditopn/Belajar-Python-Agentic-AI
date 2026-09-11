from dotenv import load_dotenv

load_dotenv()

import os

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent # mengarahkan langsung ke ../src
INSTRUCTIONS_DIR = SRC_DIR/"agents"/"instructions"
DOCS_DIR = SRC_DIR/"docs"
OUTPUT_DIR = SRC_DIR/"output"
TEMP = SRC_DIR/"temp"

def _required_env(name: str) -> str:
    """Ambil env wajib. Apabila gagal, tampilkan pesan error."""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"env variabel '{name}' belum diset"
        )

    return value

GEMINI_API_KEY = _required_env("GEMINI_API_KEY")
GEMINI_MODEL = _required_env("GEMINI_MODEL")
GEMINI_MODEL_TTS = _required_env("GEMINI_MODEL_TTS")

SUPABASE_URL = _required_env("SUPABASE_URL")
SUPABASE_KEY = _required_env("SUPABASE_KEY")

TELEGRAM_BOT_TOKEN = _required_env("TELEGRAM_BOT_TOKEN")