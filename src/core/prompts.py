import src.core.env as env

from pathlib import Path
from functools import lru_cache
from supabase import Client, create_client

@lru_cache
def load_instruction(name: str):
    """Baca file instruksi berdasarkan nama file, contoh: load_instruction('agent-lead')"""

    path = env.INSTRUCTIONS_DIR/f"{name}.md"

    if not path.exists():
        raise FileNotFoundError(
            f"File instruksi tidak ditermukan: {path}. \n"
            f"Cek nama file di {env.INSTRUCTIONS_DIR}"
        )

    return path.read_text(encoding="utf-8")