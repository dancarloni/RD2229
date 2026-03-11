from __future__ import annotations

from .checks_sle import verifica_sle_parapetto
from .checks_slu import verifica_slu_parapetto
from .models import (
    ContestoSLEParapetto,
    ContestoSLUParapetto,
    ParapettoSpec,
    RisultatoParapetto,
    StatoDannoSLE,
    TipoAncoraggio,
    TipoParapetto,
)
from .presets import (
    carica_presets_da_json,
    crea_spec_da_preset,
    get_preset,
    lista_preset_disponibili,
)
from .report_adapter import adatta_per_report, export_markdown


def spec_from_dict(inputs: dict) -> ParapettoSpec:
    """Convert generic dict to ParapettoSpec."""
    tipo = TipoParapetto(inputs.get("tipo", TipoParapetto.CONTINUO_MURATURA.value))
    ancoraggio = TipoAncoraggio(inputs.get("tipo_ancoraggio", TipoAncoraggio.BASE_CONTINUA.value))

    return ParapettoSpec(
        tipo=tipo,
        altezza_cm=float(inputs.get("altezza_cm", 120.0)),
        lunghezza_cm=float(inputs.get("lunghezza_cm", 500.0)),
        massa_lineare_kg_m=float(inputs.get("massa_lineare_kg_m", 200.0)),
        tipo_ancoraggio=ancoraggio,
        resistenza_ancoraggio_kn=inputs.get("resistenza_ancoraggio_kn"),
        interasse_montanti_cm=inputs.get("interasse_montanti_cm"),
        spessore_parete_cm=inputs.get("spessore_parete_cm"),
        numero_montanti=inputs.get("numero_montanti"),
        area_aperture_cm2=float(inputs.get("area_aperture_cm2", 0.0)),
        comportamento_fragile=bool(inputs.get("comportamento_fragile", False)),
        vincoli_laterali=bool(inputs.get("vincoli_laterali", True)),
    )


def check_slu(inputs: dict) -> dict:
    """SLU check for parapetto (dispatcher contract)."""
    spec = spec_from_dict(inputs)
    context = ContestoSLUParapetto(
        accelerazione_spettrale_g=float(
            inputs.get("S_a", inputs.get("accelerazione_spettrale_g", 1.5))
        ),
        carico_orizzontale_servizio_kg=float(inputs.get("P_servizio", 100.0)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_parapetto(spec, context, passaggi)

    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "parapetti",
        "norm_references": ["NTC2018 §7.2.2", "Fase S3"],
        "decision_log": passaggi,
        "domanda_sismica_kg": risultato.domanda_sismica_kg,
        "domanda_servizio_kg": risultato.domanda_servizio_kg,
        "domanda_combinata_kg": risultato.domanda_combinata_kg,
        "resistenza_ancoraggio_kg": risultato.resistenza_ancoraggio_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
        "meccanismo_critico": risultato.meccanismo_critico,
    }


def check_sle(inputs: dict) -> dict:
    """SLE check for parapetto (dispatcher contract)."""
    spec = spec_from_dict(inputs)
    spostamento = inputs.get("spostamento", {})
    context = ContestoSLEParapetto(
        spostamento_bordo_cm=float(
            spostamento.get("value", inputs.get("spostamento_bordo_cm", 0.5))
        )
    )
    passaggi: list[str] = []
    risultato = verifica_sle_parapetto(spec, context, passaggi)

    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA
    confidence = "LOW" if spostamento.get("source") == "ESTIMATED" else "HIGH"
    if confidence == "LOW":
        passaggi.append("spostamento source=ESTIMATED, confidence=LOW")

    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "parapetti",
        "norm_references": ["NTC2018 §7.2.2", "Fase S3"],
        "decision_log": passaggi,
        "stato_danno": risultato.stato_danno.value,
        "spostamento_bordo_cm": risultato.spostamento_bordo_cm,
        "spostamento_ammissibile_cm": risultato.spostamento_ammissibile_cm,
        "rapporto_spostamento": round(risultato.rapporto_spostamento, 4),
        "danno_ai_giunti": risultato.danno_ai_giunti,
        "integrita_pannelli": risultato.integrita_pannelli,
        "intervento_necessario": risultato.intervento_necessario,
        "confidence": confidence,
    }


def verifica_parapetto_completa(inputs: dict) -> RisultatoParapetto:
    """Complete parapetto verification pipeline."""
    spec = spec_from_dict(inputs)
    passaggi: list[str] = []

    # SLU
    context_slu = ContestoSLUParapetto(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        carico_orizzontale_servizio_kg=float(inputs.get("P_servizio", 100.0)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    risultato_slu = verifica_slu_parapetto(spec, context_slu, passaggi)

    # SLE
    context_sle = ContestoSLEParapetto(
        spostamento_bordo_cm=float(inputs.get("spostamento_bordo_cm", 0.5))
    )
    risultato_sle = verifica_sle_parapetto(spec, context_sle, passaggi)

    return RisultatoParapetto(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_parapetto_completa",
    "ParapettoSpec",
    "RisultatoParapetto",
    "TipoParapetto",
    "TipoAncoraggio",
    "get_preset",
    "lista_preset_disponibili",
    "carica_presets_da_json",
    "crea_spec_da_preset",
    "adatta_per_report",
    "export_markdown",
]
