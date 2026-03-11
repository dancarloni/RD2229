"""Rendering immagini per report HTML/Markdown."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .utils import encode_image_base64, mime_type_from_path


def image_html_block(path: str | Path, caption: str = "") -> str:
    """Restituisce blocco HTML con immagine embedded base64."""
    src_path = Path(path)
    mime = mime_type_from_path(src_path)
    encoded = encode_image_base64(src_path)
    safe_caption = escape(caption)
    return (
        "<figure class=\"report-image\">"
        f"<img src=\"data:{mime};base64,{encoded}\" alt=\"{safe_caption}\" "
        "style=\"max-width:100%;height:auto;\">"
        f"<figcaption>{safe_caption}</figcaption>"
        "</figure>"
    )


def image_markdown_block(path: str | Path, caption: str = "") -> str:
    """Restituisce blocco Markdown con immagine a path relativo."""
    src_path = Path(path)
    safe_caption = caption or src_path.name
    return f"![{safe_caption}]({src_path.as_posix()})"
