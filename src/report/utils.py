"""Utility comuni modulo report."""

from __future__ import annotations

import base64
from pathlib import Path


def encode_image_base64(path: str | Path) -> str:
    """Converte un file immagine in stringa base64 senza prefisso data URI."""
    image_path = Path(path)
    data = image_path.read_bytes()
    return base64.b64encode(data).decode("ascii")


def mime_type_from_path(path: str | Path) -> str:
    """Deriva MIME type dal suffisso file."""
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".svg":
        return "image/svg+xml"
    if suffix == ".gif":
        return "image/gif"
    return "image/png"
