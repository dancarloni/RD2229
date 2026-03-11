from __future__ import annotations

from .checks_sle import verifica_sle_camino
from .checks_slu import verifica_slu_camino
from .models import (
    CaminoSpec,
    ContestoSLECamino,
    ContestoSLUCamino,
    RisultatoCamino,
    StatoDannoSLE,
    TipoCamino,
)


def spec_from_dict(inputs: dict) -> CaminoSpec:
    tipo = TipoCamino(inputs.get("tipo", TipoCamino.MURATURA.value))
    return CaminoSpec(
        tipo=tipo,
        altezza_cm=float(inputs.get("altezza_cm", 300.0)),
        massa_totale_kg=float(inputs.get("massa_totale_kg", 800.0)),
        vincolo_base=inputs.get("vincolo_base", "fisso"),
        controventato=bool(inputs.get("controventato", False)),
        rigidezza_equivalente_kg_cm=inputs.get("rigidezza_equivalente_kg_cm"),
    )


def check_slu(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLUCamino(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_camino(spec, context, passaggi)

    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "camini",
        "norm_references": ["NTC2018 §7.2.7", "Fase S7"],
        "decision_log": passaggi,
        "domanda_sismica_kg": risultato.domanda_sismica_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
    }


def check_sle(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLECamino(
        spostamento_sommitale_cm=float(inputs.get("spostamento_sommitale_cm", 1.0))
    )
    passaggi: list[str] = []
    risultato = verifica_sle_camino(spec, context, passaggi)

    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA

    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "camini",
        "norm_references": ["NTC2018 §7.2.7", "Fase S7"],
        "decision_log": passaggi,
        "stato_danno": risultato.stato_danno.value,
        "danno_risonanza": risultato.danno_risonanza,
    }


def verifica_camino_completa(inputs: dict) -> RisultatoCamino:
    spec = spec_from_dict(inputs)
    passaggi: list[str] = []

    context_slu = ContestoSLUCamino(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    risultato_slu = verifica_slu_camino(spec, context_slu, passaggi)

    context_sle = ContestoSLECamino(
        spostamento_sommitale_cm=float(inputs.get("spostamento_sommitale_cm", 1.0))
    )
    risultato_sle = verifica_sle_camino(spec, context_sle, passaggi)

    return RisultatoCamino(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_camino_completa",
    "CaminoSpec",
    "RisultatoCamino",
    "TipoCamino",
]
