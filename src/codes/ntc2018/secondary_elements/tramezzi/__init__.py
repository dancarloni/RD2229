from __future__ import annotations

from .checks_sle import verifica_sle_tramezzo
from .checks_slu import verifica_slu_tramezzo
from .models import (
    ContestoSLETramezzo,
    ContestoSLUTramezzo,
    RisultatoTramezzo,
    SistemaTramezzo,
    StatoDannoSLE,
    TramezzoSpec,
    VincoloSuperiore,
)
from .presets import (
    carica_presets_da_json,
    crea_spec_da_preset,
    get_preset,
    lista_preset_disponibili,
)
from .report_adapter import adatta_per_report, export_markdown


def spec_from_dict(inputs: dict) -> TramezzoSpec:
    sistema = SistemaTramezzo(inputs.get("sistema", SistemaTramezzo.CARTONGESSO_STANDARD.value))
    vincolo = VincoloSuperiore(inputs.get("vincolo_superiore", VincoloSuperiore.RIGIDO.value))
    return TramezzoSpec(
        sistema=sistema,
        altezza_cm=float(inputs.get("altezza_cm", inputs.get("height", 300.0))),
        lunghezza_cm=float(inputs.get("lunghezza_cm", inputs.get("width", 400.0))),
        spessore_cm=float(inputs.get("spessore_cm", inputs.get("thickness", 10.0))),
        peso_lineare_kg_m=float(inputs.get("peso_lineare_kg_m", 55.0)),
        vincolo_superiore=vincolo,
        guida_superiore_scorrimento=bool(inputs.get("guida_superiore_scorrimento", False)),
        ancorato_lateralmente=bool(inputs.get("ancorato_lateralmente", True)),
        drift_capacita_perc=float(inputs.get("drift_capacita_perc", 1.0)),
        area_aperture_cm2=float(inputs.get("area_aperture_cm2", 0.0)),
        numero_aperture=int(inputs.get("numero_aperture", 0)),
        impianti_integrati=bool(inputs.get("impianti_integrati", False)),
        resistenza_fuori_piano_kg=inputs.get("resistenza_fuori_piano_kg"),
        resistenza_ancoraggi_kg=inputs.get("resistenza_ancoraggi_kg"),
    )


def check_slu(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLUTramezzo(
        accelerazione_spettrale_g=float(
            inputs.get("S_a", inputs.get("accelerazione_spettrale_g", 1.5))
        ),
        gamma_i=float(inputs.get("gamma_a", inputs.get("gamma_i", 1.0))),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_tramezzo(spec, context, passaggi)
    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "tramezzi",
        "norm_references": ["NTC2018 §7.2.3", "Fase S2"],
        "decision_log": passaggi,
        "domanda_fuori_piano_kg": risultato.domanda_fuori_piano_kg,
        "resistenza_fuori_piano_kg": risultato.resistenza_fuori_piano_kg,
        "resistenza_ancoraggi_kg": risultato.resistenza_ancoraggi_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
        "meccanismo_critico": risultato.meccanismo_critico,
    }


def check_sle(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    drift = inputs.get("drift") or {}
    context = ContestoSLETramezzo(
        drift_calcolato_perc=float(drift.get("value", inputs.get("drift_calcolato_perc", 0.4)))
    )
    passaggi: list[str] = []
    risultato = verifica_sle_tramezzo(spec, context, passaggi)
    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA
    confidence = "LOW" if drift.get("source") == "ESTIMATED" else "HIGH"
    if confidence == "LOW":
        passaggi.append("drift source=ESTIMATED, confidence=LOW")
    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "tramezzi",
        "norm_references": ["NTC2018 §7.2.3", "Fase S2"],
        "decision_log": passaggi + [risultato.note],
        "utilisation": round(risultato.rapporto_drift, 4),
        "drift_value": risultato.drift_calcolato_perc,
        "drift_limit": risultato.drift_capacita_perc,
        "stato_danno": risultato.stato_danno.value,
        "confidence": confidence,
    }


def verifica_tramezzo_completa(
    spec: TramezzoSpec, contesto_slu: ContestoSLUTramezzo, contesto_sle: ContestoSLETramezzo
) -> RisultatoTramezzo:
    passaggi: list[str] = []
    slu = verifica_slu_tramezzo(spec, contesto_slu, passaggi)
    sle = verifica_sle_tramezzo(spec, contesto_sle, passaggi)
    return RisultatoTramezzo(
        spec=spec, risultato_slu=slu, risultato_sle=sle, passaggi_calcolo=passaggi
    )


__all__ = [
    "SistemaTramezzo",
    "VincoloSuperiore",
    "StatoDannoSLE",
    "TramezzoSpec",
    "ContestoSLUTramezzo",
    "ContestoSLETramezzo",
    "verifica_tramezzo_completa",
    "check_slu",
    "check_sle",
    "get_preset",
    "lista_preset_disponibili",
    "carica_presets_da_json",
    "crea_spec_da_preset",
    "adatta_per_report",
    "export_markdown",
]
