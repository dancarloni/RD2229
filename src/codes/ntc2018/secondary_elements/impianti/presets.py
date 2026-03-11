from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import CategoriaImpianto, ImpiantoSpec, TipoSupporto


def carica_presets_da_json(filepath: Path | None = None) -> dict[str, dict[str, Any]]:
    if filepath is None:
        filepath = (
            Path(__file__).parent.parent.parent.parent.parent / "data" / "impianti_presets.json"
        )

    if not filepath.exists():
        return {}

    with open(filepath) as f:
        return json.load(f)


def crea_spec_da_preset(data: dict[str, Any]) -> ImpiantoSpec:
    return ImpiantoSpec(
        categoria=CategoriaImpianto(data.get("categoria", "tubazione_sospesa")),
        massa_kg=float(data.get("massa_kg", 50.0)),
        quota_cm=float(data.get("quota_cm", 300.0)),
        tipo_supporto=TipoSupporto(data.get("tipo_supporto", "sospensione")),
        numero_ancoraggi=int(data.get("numero_ancoraggi", 2)),
        presenza_giunto_flessibile=bool(data.get("presenza_giunto_flessibile", True)),
        classe_funzione=data.get("classe_funzione"),
        resistenza_supporto_kn=data.get("resistenza_supporto_kn"),
        lunghezza_percorso_m=float(data.get("lunghezza_percorso_m", 1.0)),
    )


def get_preset(nome: str) -> ImpiantoSpec | None:
    presets = carica_presets_da_json()
    if nome in presets:
        return crea_spec_da_preset(presets[nome])
    return None


def lista_preset_disponibili() -> list[str]:
    presets = carica_presets_da_json()
    return list(presets.keys())
