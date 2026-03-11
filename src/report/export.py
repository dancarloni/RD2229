"""Export multi-formato report professionale (Q.6)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .export_docx import DocxExporter
from .export_pdf import PDFExporter


def export_html(tree: Any, path: str | Path) -> Path:
    """Esporta contenuto HTML su file."""
    content = _resolve_content(tree, attr="html")
    output_path = Path(path)
    _atomic_write(output_path, content)
    return output_path


def export_md(tree: Any, path: str | Path) -> Path:
    """Esporta contenuto Markdown su file."""
    content = _resolve_content(tree, attr="markdown")
    output_path = Path(path)
    _atomic_write(output_path, content)
    return output_path


def export_ascii(tree: Any, path: str | Path) -> Path:
    """Esporta contenuto ASCII/TXT su file."""
    content = _resolve_content(tree, attr="ascii")
    output_path = Path(path)
    _atomic_write(output_path, content)
    return output_path


def export_pdf(tree: Any, path: str | Path) -> Path:
    """Esporta PDF da HTML con dipendenza opzionale."""
    html = _resolve_content(tree, attr="html")
    return PDFExporter().export(html, path)


def export_docx(tree: Any, path: str | Path) -> Path:
    """Esporta DOCX da Markdown con dipendenza opzionale."""
    markdown = _resolve_content(tree, attr="markdown")
    return DocxExporter().export(markdown, path)


def _resolve_content(tree: Any, attr: str) -> str:
    if isinstance(tree, str):
        return tree

    attr_names = [attr]
    if attr == "ascii":
        attr_names.append("ascii_text")
    for name in attr_names:
        value = getattr(tree, name, None)
        if isinstance(value, str) and value:
            return value
    raise ValueError(f"Contenuto '{attr}' non disponibile per export.")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
