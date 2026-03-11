"""Sezioni personalizzate per report (Fase Q.8)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

CustomGenerator = Callable[[Any, Any], str | None]


@dataclass(slots=True)
class CustomSection:
    name: str
    order: int
    generator: CustomGenerator


_CUSTOM_REGISTRY: dict[str, CustomSection] = {}


def register_custom_section(name: str, generator: CustomGenerator, order: int = 800) -> None:
    """Registra o sovrascrive una sezione custom."""
    _CUSTOM_REGISTRY[name] = CustomSection(name=name, order=order, generator=generator)


def unregister_custom_section(name: str) -> None:
    """Rimuove una sezione custom, se presente."""
    _CUSTOM_REGISTRY.pop(name, None)


def clear_custom_sections() -> None:
    """Reset registry custom, utile nei test."""
    _CUSTOM_REGISTRY.clear()


def get_custom_sections() -> list[CustomSection]:
    """Restituisce sezioni custom ordinate."""
    return sorted(_CUSTOM_REGISTRY.values(), key=lambda section: (section.order, section.name))


def save_section_profile(path: str | Path, sections: list[str]) -> Path:
    """Salva profilo sezioni in JSON."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"sections": sections}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def load_section_profile(path: str | Path) -> list[str]:
    """Carica profilo sezioni da JSON."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        return []
    return [str(item) for item in sections]
