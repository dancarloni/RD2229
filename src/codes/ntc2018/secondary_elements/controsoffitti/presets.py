from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ControsoffittoSpec, TipoControsoffitto


def carica_presets_da_json(filepath: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load controsoffitto presets from JSON file."""
    if filepath is None:
        filepath = (
            Path(__file__).parent.parent.parent.parent.parent
            / "data"
            / "controsoffitti_presets.json"
        )

    if not filepath.exists():
        return {}

    with open(filepath) as f:
        return json.load(f)


def crea_spec_da_preset(data: dict[str, Any]) -> ControsoffittoSpec:
    """Convert preset dict to ControsoffittoSpec."""
    return ControsoffittoSpec(
        tipo=TipoControsoffitto(data.get("tipo", "modulare_gesso")),
        area_m2=float(data.get("area_m2", 50.0)),
        massa_superficiale_kg_m2=float(data.get("massa_superficiale_kg_m2", 15.0)),
        passo_pendini_cm=float(data.get("passo_pendini_cm", 100.0)),
        presenza_controventi=bool(data.get("presenza_controventi", True)),
        gioco_perimetrale_mm=float(data.get("gioco_perimetrale_mm", 30.0)),
        numero_pendini=data.get("numero_pendini"),
        lunghezza_controventi_m=data.get("lunghezza_controventi_m"),
    )


def get_preset(nome: str) -> ControsoffittoSpec | None:
    """Get preset by name."""
    presets = carica_presets_da_json()
    if nome in presets:
        return crea_spec_da_preset(presets[nome])
    return None


def lista_preset_disponibili() -> list[str]:
    """List available preset names."""
    presets = carica_presets_da_json()
    return list(presets.keys())
