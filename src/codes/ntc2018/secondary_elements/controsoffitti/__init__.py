from __future__ import annotations

from .checks_sle import verifica_sle_controsoffitto
from .checks_slu import verifica_slu_controsoffitto
from .models import (
    ContestoSLEControsoffitto,
    ContestoSLUControsoffitto,
    ControsoffittoSpec,
    RisultatoControsoffitto,
    StatoDannoSLE,
    TipoControsoffitto,
)
from .presets import (
    carica_presets_da_json,
    crea_spec_da_preset,
    get_preset,
    lista_preset_disponibili,
)
from .report_adapter import adatta_per_report, export_markdown


def spec_from_dict(inputs: dict) -> ControsoffittoSpec:
    """Convert generic dict to ControsoffittoSpec."""
    tipo = TipoControsoffitto(inputs.get("tipo", TipoControsoffitto.MODULARE_GESSO.value))
    return ControsoffittoSpec(
        tipo=tipo,
        area_m2=float(inputs.get("area_m2", 50.0)),
        massa_superficiale_kg_m2=float(inputs.get("massa_superficiale_kg_m2", 15.0)),
        passo_pendini_cm=float(inputs.get("passo_pendini_cm", 100.0)),
        presenza_controventi=bool(inputs.get("presenza_controventi", True)),
        gioco_perimetrale_mm=float(inputs.get("gioco_perimetrale_mm", 30.0)),
        numero_pendini=inputs.get("numero_pendini"),
        lunghezza_controventi_m=inputs.get("lunghezza_controventi_m"),
    )


def check_slu(inputs: dict) -> dict:
    """SLU check for controsoffitto."""
    spec = spec_from_dict(inputs)
    context = ContestoSLUControsoffitto(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_controsoffitto(spec, context, passaggi)

    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "controsoffitti",
        "norm_references": ["NTC2018 §7.2.4", "Fase S4"],
        "decision_log": passaggi,
        "domanda_totale_kg": risultato.domanda_totale_kg,
        "resistenza_pendini_kg": risultato.resistenza_pendini_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
    }


def check_sle(inputs: dict) -> dict:
    """SLE check for controsoffitto."""
    spec = spec_from_dict(inputs)
    context = ContestoSLEControsoffitto(
        drift_calcolato_perc=float(inputs.get("drift_calcolato_perc", 0.8))
    )
    passaggi: list[str] = []
    risultato = verifica_sle_controsoffitto(spec, context, passaggi)

    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA

    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "controsoffitti",
        "norm_references": ["NTC2018 §7.2.4", "Fase S4"],
        "decision_log": passaggi,
        "stato_danno": risultato.stato_danno.value,
        "perdita_appoggio_rischio": risultato.perdita_appoggio_rischio,
    }


def verifica_controsoffitto_completa(inputs: dict) -> RisultatoControsoffitto:
    """Complete controsoffitto verification pipeline."""
    spec = spec_from_dict(inputs)
    passaggi: list[str] = []

    context_slu = ContestoSLUControsoffitto(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    risultato_slu = verifica_slu_controsoffitto(spec, context_slu, passaggi)

    context_sle = ContestoSLEControsoffitto(
        drift_calcolato_perc=float(inputs.get("drift_calcolato_perc", 0.8))
    )
    risultato_sle = verifica_sle_controsoffitto(spec, context_sle, passaggi)

    return RisultatoControsoffitto(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_controsoffitto_completa",
    "ControsoffittoSpec",
    "RisultatoControsoffitto",
    "TipoControsoffitto",
    "get_preset",
    "lista_preset_disponibili",
    "adatta_per_report",
    "export_markdown",
]
