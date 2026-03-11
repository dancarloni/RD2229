from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ParapettoSpec, TipoAncoraggio, TipoParapetto


def carica_presets_da_json(filepath: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load parapetto presets from JSON file. Defaults to data/parapetti_presets.json."""
    if filepath is None:
        filepath = (
            Path(__file__).parent.parent.parent.parent.parent / "data" / "parapetti_presets.json"
        )

    if not filepath.exists():
        return {}

    with open(filepath) as f:
        return json.load(f)


def crea_spec_da_preset(data: dict[str, Any]) -> ParapettoSpec:
    """Convert preset dict to ParapettoSpec with enum coercion."""
    return ParapettoSpec(
        tipo=TipoParapetto(data.get("tipo", "continuo_muratura")),
        altezza_cm=float(data.get("altezza_cm", 120.0)),
        lunghezza_cm=float(data.get("lunghezza_cm", 500.0)),
        massa_lineare_kg_m=float(data.get("massa_lineare_kg_m", 200.0)),
        tipo_ancoraggio=TipoAncoraggio(data.get("tipo_ancoraggio", "base_continua")),
        resistenza_ancoraggio_kn=data.get("resistenza_ancoraggio_kn"),
        interasse_montanti_cm=data.get("interasse_montanti_cm"),
        spessore_parete_cm=data.get("spessore_parete_cm"),
        numero_montanti=data.get("numero_montanti"),
        area_aperture_cm2=float(data.get("area_aperture_cm2", 0.0)),
        comportamento_fragile=bool(data.get("comportamento_fragile", False)),
        vincoli_laterali=bool(data.get("vincoli_laterali", True)),
    )


def get_preset(nome: str) -> ParapettoSpec | None:
    """Get preset by name."""
    presets = carica_presets_da_json()
    if nome in presets:
        return crea_spec_da_preset(presets[nome])
    return None


def lista_preset_disponibili() -> list[str]:
    """List available preset names."""
    presets = carica_presets_da_json()
    return list(presets.keys())
