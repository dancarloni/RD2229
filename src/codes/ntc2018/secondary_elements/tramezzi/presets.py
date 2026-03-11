from __future__ import annotations

import json
from pathlib import Path

from .models import SistemaTramezzo, TramezzoSpec, VincoloSuperiore

PRESETS_PATH = Path(__file__).resolve().parents[5] / "data" / "tramezzi_presets.json"


def carica_presets_da_json(filepath: Path | None = None) -> dict:
    path = filepath or PRESETS_PATH
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _enum_sistema(value: str) -> SistemaTramezzo:
    return SistemaTramezzo(value)


def _enum_vincolo(value: str) -> VincoloSuperiore:
    return VincoloSuperiore(value)


def crea_spec_da_preset(data: dict) -> TramezzoSpec:
    return TramezzoSpec(
        sistema=_enum_sistema(data["sistema"]),
        altezza_cm=float(data["altezza_cm"]),
        lunghezza_cm=float(data["lunghezza_cm"]),
        spessore_cm=float(data["spessore_cm"]),
        peso_lineare_kg_m=float(data["peso_lineare_kg_m"]),
        vincolo_superiore=_enum_vincolo(data.get("vincolo_superiore", "rigido")),
        guida_superiore_scorrimento=bool(data.get("guida_superiore_scorrimento", False)),
        ancorato_lateralmente=bool(data.get("ancorato_lateralmente", True)),
        drift_capacita_perc=float(data.get("drift_capacita_perc", 1.0)),
        area_aperture_cm2=float(data.get("area_aperture_cm2", 0.0)),
        numero_aperture=int(data.get("numero_aperture", 0)),
        impianti_integrati=bool(data.get("impianti_integrati", False)),
        resistenza_fuori_piano_kg=data.get("resistenza_fuori_piano_kg"),
        resistenza_ancoraggi_kg=data.get("resistenza_ancoraggi_kg"),
    )


def get_preset(nome: str, filepath: Path | None = None) -> TramezzoSpec | None:
    presets = carica_presets_da_json(filepath)
    if nome not in presets:
        return None
    return crea_spec_da_preset(presets[nome])


def lista_preset_disponibili(filepath: Path | None = None) -> list[str]:
    return list(carica_presets_da_json(filepath).keys())
