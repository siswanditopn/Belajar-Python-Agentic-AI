import contextvars  # keranjang
from typing import Optional, TypedDict  # mengelola struktur data-nya


class Artifact(TypedDict):
    path: str
    kind: str  # "audio" | "document"
    caption: Optional[str]


_artifacts: contextvars.ContextVar[Optional[list[Artifact]]] = contextvars.ContextVar(
    "artifacts", default=None
)


def start() -> None:
    """Mulai keranjang artifact baru untuk request saat ini."""
    _artifacts.set([])  # list kosong


def add(path: str, kind: str = "audio", caption: Optional[str] = None) -> None:
    """Catat satu artifact untuk dikirim oleh layer pengiriman (CLI/Telegram)"""
    bucket = _artifacts.get()
    if bucket is None:
        return

    bucket.append({"path": path, "kind": kind, "caption": caption})


def collect() -> list[Artifact]:
    """Ambil semua artifact yang terkumpul pada request ini"""
    return _artifacts.get() or []