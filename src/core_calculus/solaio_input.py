"""Modulo Fase X1 — parsing e validazione input solai.

Design goals:
- data-driven (tipologie e metadata GUI da file dati)
- validazione strict con aggregazione errori
- separazione chiara tra valori originali e valori normalizzati SI
"""

from __future__ import annotations

import json
import pkgutil
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

from src.core.registro_log import registro
from src.core_calculus.contracts import ValidationIssue
from src.core_calculus.units import cm_to_m, kgcm2_to_mpa, kgf_m2_to_kn_m2

TIPOLOGIE_FILE = "data/solai_tipologie.json"
SOLAI_FIELDS_FILE = "data/solai_fields.json"
_MODULO_LOG = "core_calculus.solaio_input"
_NORME_VALIDE = {"NTC2018", "DM96", "DM16", "RD2229"}


class InputValidationError(ValueError):
    """Errore sollevato in caso di validazione input fallita."""

    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        message = "; ".join(f"{i.field}: {i.message_it}" for i in issues)
        super().__init__(message)


def _repo_data_path(relative_path: str) -> Path:
    return Path(__file__).resolve().parents[2] / relative_path


def _load_json_data(relative_path: str) -> Any:
    package_name = __name__.split(".")[0]
    try:
        raw = pkgutil.get_data(package_name, relative_path)
    except FileNotFoundError:
        raw = None
    if raw is not None:
        return json.loads(raw.decode("utf-8"))

    path = _repo_data_path(relative_path)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    raise RuntimeError(f"File dati non trovato: {relative_path}")


def load_tipologie() -> list[str]:
    """Carica la lista tipologie da sorgente dati esterna."""

    data = _load_json_data(TIPOLOGIE_FILE)
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise RuntimeError(f"Formato non valido per {TIPOLOGIE_FILE}: attesa lista di stringhe")
    return data


def load_fields_metadata() -> dict[str, Any]:
    """Carica i metadata GUI per i campi input solai."""

    data = _load_json_data(SOLAI_FIELDS_FILE)
    if not isinstance(data, dict):
        raise RuntimeError(f"Formato non valido per {SOLAI_FIELDS_FILE}: atteso oggetto JSON")
    return data


class Geometria(BaseModel):
    luce_cm: float = Field(..., gt=0)
    interasse_cm: float = Field(..., gt=0)
    spessore_cm: float = Field(..., gt=0)
    n_campate: int = Field(1, ge=1)


class Materiali(BaseModel):
    f_ck: float = Field(..., gt=0)
    f_yk: float = Field(..., gt=0)
    E: float = Field(..., gt=0)
    rho: float | None = Field(None, gt=0)


class Carichi(BaseModel):
    G1: float = Field(..., ge=0)
    G2: float = Field(..., ge=0)
    Q: float = Field(..., ge=0)
    categoria: str = Field(...)


class InputSolaio(BaseModel):
    tipologia: str = Field(...)
    norma: str = Field(...)
    edificio_esistente: bool = Field(...)
    unit_system: str | None = Field(default=None, description="auto | legacy_kgf_cm | si")
    geometria: Geometria
    materiali: Materiali
    carichi: Carichi
    aperture: list[dict[str, Any]] | None = Field(default_factory=list)
    cerchiature: list[dict[str, Any]] | None = Field(default_factory=list)
    lc_fc: dict[str, Any] | None = Field(default_factory=dict)

    @field_validator("tipologia")
    @classmethod
    def tipologia_valida(cls, v: str) -> str:
        valid = load_tipologie()
        if v not in valid:
            raise ValueError(f"Tipologia non valida: {v}. Valide: {valid}")
        return v

    @field_validator("norma")
    @classmethod
    def norma_valida(cls, v: str) -> str:
        if v not in _NORME_VALIDE:
            raise ValueError(f"Norma non valida: {v}. Valide: {sorted(_NORME_VALIDE)}")
        return v

    @field_validator("unit_system")
    @classmethod
    def unit_system_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in {"auto", "legacy_kgf_cm", "si"}:
            raise ValueError("unit_system deve essere 'auto', 'legacy_kgf_cm' o 'si'")
        return v

    def _detect_unit_system(self) -> str:
        if self.unit_system and self.unit_system != "auto":
            return self.unit_system

        geom = self.geometria
        car = self.carichi
        mat = self.materiali

        geom_looks_cm = any(v > 30 for v in (geom.luce_cm, geom.interasse_cm, geom.spessore_cm))
        loads_looks_kgf = max(car.G1, car.G2, car.Q) > 20
        materials_looks_kgcm2 = any(
            [
                mat.f_ck > 120,
                mat.f_yk > 1500,
                mat.E > 100000,
            ]
        )

        score_legacy = sum([geom_looks_cm, loads_looks_kgf, materials_looks_kgcm2])
        return "legacy_kgf_cm" if score_legacy >= 2 else "si"

    def _normalized_payload(self) -> dict[str, Any]:
        """Restituisce un payload normalizzato in SI (m/kN/m2/MPa)."""

        geom = self.geometria
        mat = self.materiali
        car = self.carichi
        unit_system = self._detect_unit_system()

        if unit_system == "legacy_kgf_cm":
            geometria = {
                "luce_m": cm_to_m(geom.luce_cm),
                "interasse_m": cm_to_m(geom.interasse_cm),
                "spessore_m": cm_to_m(geom.spessore_cm),
                "n_campate": geom.n_campate,
            }
            materiali = {
                "f_ck_mpa": kgcm2_to_mpa(mat.f_ck),
                "f_yk_mpa": kgcm2_to_mpa(mat.f_yk),
                "E_mpa": kgcm2_to_mpa(mat.E),
                "rho": mat.rho,
            }
            carichi = {
                "G1_kN_m2": kgf_m2_to_kn_m2(car.G1),
                "G2_kN_m2": kgf_m2_to_kn_m2(car.G2),
                "Q_kN_m2": kgf_m2_to_kn_m2(car.Q),
                "categoria": car.categoria,
            }
        else:
            geometria = {
                "luce_m": geom.luce_cm,
                "interasse_m": geom.interasse_cm,
                "spessore_m": geom.spessore_cm,
                "n_campate": geom.n_campate,
            }
            materiali = {
                "f_ck_mpa": mat.f_ck,
                "f_yk_mpa": mat.f_yk,
                "E_mpa": mat.E,
                "rho": mat.rho,
            }
            carichi = {
                "G1_kN_m2": car.G1,
                "G2_kN_m2": car.G2,
                "Q_kN_m2": car.Q,
                "categoria": car.categoria,
            }

        return {
            "unit_system_detected": unit_system,
            "geometria": geometria,
            "materiali": materiali,
            "carichi": carichi,
        }

    def as_ready_dict(self) -> dict[str, Any]:
        """Restituisce payload nested per GUI/X2/X3 con original + normalized."""

        normalized = self._normalized_payload()

        return {
            "meta": {
                "tipologia": self.tipologia,
                "norma": self.norma,
                "edificio_esistente": self.edificio_esistente,
                "unit_system": self.unit_system or "auto",
                "unit_system_detected": normalized["unit_system_detected"],
            },
            "original": {
                "geometria": self.geometria.model_dump(),
                "materiali": self.materiali.model_dump(),
                "carichi": self.carichi.model_dump(),
            },
            "normalized": {
                "geometria": normalized["geometria"],
                "materiali": normalized["materiali"],
                "carichi": normalized["carichi"],
            },
            "aperture": self.aperture,
            "cerchiature": self.cerchiature,
            "lc_fc": self.lc_fc,
        }


def parse_solaio_input(data: dict[str, Any]) -> InputSolaio:
    """Parsing + validazione rigorosa dell'input solai.

    Solleva `InputValidationError` se la validazione fallisce.
    """

    registro.debug(_MODULO_LOG, "Avvio parsing input solaio")
    try:
        solaio = InputSolaio(**data)
    except ValidationError as exc:
        issues: list[ValidationIssue] = []
        for idx, err in enumerate(exc.errors(), start=1):
            field = ".".join(str(p) for p in err.get("loc", []))
            issues.append(
                ValidationIssue(
                    severity="error",
                    field=field,
                    code=f"X1-INPUT-{idx:03d}",
                    message_it=str(err.get("msg")),
                )
            )
        registro.errore(
            _MODULO_LOG,
            "Validazione input fallita",
            dettagli=f"issues={len(issues)}",
        )
        raise InputValidationError(issues)

    # Traccia il caricamento dei metadata GUI per assicurare separazione layer data/core.
    _ = load_fields_metadata()
    ready = solaio.as_ready_dict()
    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Parsing e normalizzazione input solaio",
        input_dati={"tipologia": solaio.tipologia, "norma": solaio.norma},
        output_dati={"unit_system_detected": ready["meta"]["unit_system_detected"]},
        normativa="NTC2018 §2.5; NTC2018 §4.1.2",
        passaggi=[
            "Validazione schema completata",
            "Tipologia validata da file dati",
            "Normalizzazione unità calcolata",
            "Payload nested ready generato",
        ],
        esito="VERIFICATO",
    )
    return solaio
