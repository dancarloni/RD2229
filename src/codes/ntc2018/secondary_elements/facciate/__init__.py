from __future__ import annotations

from .checks_sle import verifica_sle_facciata
from .checks_slu import verifica_slu_facciata
from .models import (
    ContestoSLEFacciata,
    ContestoSLUFacciata,
    FacciataSpec,
    RisultatoFacciata,
    SistemaFacciata,
    StatoDannoSLE,
)


def spec_from_dict(inputs: dict) -> FacciataSpec:
    sistema = SistemaFacciata(inputs.get("sistema", SistemaFacciata.CURTAIN_WALL.value))
    return FacciataSpec(
        sistema=sistema,
        modulo_luce_cm=float(inputs.get("modulo_luce_cm", 100.0)),
        massa_superficiale_kg_m2=float(inputs.get("massa_superficiale_kg_m2", 50.0)),
        tipo_sottostruttura=inputs.get("tipo_sottostruttura", "alluminio"),
        tipo_ancoraggio=inputs.get("tipo_ancoraggio", "fisso"),
        area_m2=float(inputs.get("area_m2", 50.0)),
        drift_capacita_perc=inputs.get("drift_capacita_perc"),
    )


def check_slu(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLUFacciata(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        pressione_vento_kpa=float(inputs.get("P_vento", 0.0)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_facciata(spec, context, passaggi)

    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "facciate",
        "norm_references": ["NTC2018 §7.2.6", "Fase S6"],
        "decision_log": passaggi,
        "domanda_combinata_kg": risultato.domanda_combinata_kg,
        "resistenza_ancoraggi_kg": risultato.resistenza_ancoraggi_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
    }


def check_sle(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLEFacciata(
        drift_calcolato_perc=float(inputs.get("drift_calcolato_perc", 0.5))
    )
    passaggi: list[str] = []
    risultato = verifica_sle_facciata(spec, context, passaggi)

    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA

    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "facciate",
        "norm_references": ["NTC2018 §7.2.6", "Fase S6"],
        "decision_log": passaggi,
        "stato_danno": risultato.stato_danno.value,
        "rischio_martellamento": risultato.rischio_martellamento,
    }


def verifica_facciata_completa(inputs: dict) -> RisultatoFacciata:
    spec = spec_from_dict(inputs)
    passaggi: list[str] = []

    context_slu = ContestoSLUFacciata(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        pressione_vento_kpa=float(inputs.get("P_vento", 0.0)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    risultato_slu = verifica_slu_facciata(spec, context_slu, passaggi)

    context_sle = ContestoSLEFacciata(
        drift_calcolato_perc=float(inputs.get("drift_calcolato_perc", 0.5))
    )
    risultato_sle = verifica_sle_facciata(spec, context_sle, passaggi)

    return RisultatoFacciata(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_facciata_completa",
    "FacciataSpec",
    "RisultatoFacciata",
    "SistemaFacciata",
]
