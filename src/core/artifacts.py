import contextvars # Keranjang
from typing import Optional, TypedDict # Mengelola struktur datanya

class Artifact(TypedDict):
    path: str
    kind: str # Apakah audio atau dokumen
    caption: Optional[str]

_artifacts: contextvars.ContextVar[Optional[list[Artifact]]] = contextvars.ContextVar("artifacts", default=None)

def start() -> None:
    """Mulai keranjang artifact baru untuk request saat ini."""
    _artifacts.set([]) # List kosong

def add(path: str, kind: str = "audio", caption: Optional[str] = None):
    """Catat satu artifact untuk dikirim oleh layer pengiriman (CLI/Telegram)"""
    bucket = _artifacts.get()
    if bucket is None:
        return

    bucket.append({
        "path": path,
        "kind": kind,
        "caption": caption
    })

def collect() -> list[Artifact]:
    """Ambil semua artifact yang terkumpul pada request ini."""
    return _artifacts.get() or []