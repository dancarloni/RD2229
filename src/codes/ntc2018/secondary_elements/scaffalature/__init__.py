from __future__ import annotations

from .checks_sle import verifica_sle_scaffalatura
from .checks_slu import verifica_slu_scaffalatura
from .models import (
    ContestoSLEScaffalatura,
    ContestoSLUScaffalatura,
    RisultatoScaffalatura,
    ScaffalaturaSpec,
    StatoDannoSLE,
    TipoScaffalatura,
)


def spec_from_dict(inputs: dict) -> ScaffalaturaSpec:
    tipo = TipoScaffalatura(inputs.get("tipo", TipoScaffalatura.LIGHT_DUTY.value))
    return ScaffalaturaSpec(
        tipo=tipo,
        altezza_cm=float(inputs.get("altezza_cm", 200.0)),
        larghezza_cm=float(inputs.get("larghezza_cm", 100.0)),
        profondita_cm=float(inputs.get("profondita_cm", 80.0)),
        massa_vuota_kg=float(inputs.get("massa_vuota_kg", 100.0)),
        massa_contenuto_kg=float(inputs.get("massa_contenuto_kg", 200.0)),
        ancorata=bool(inputs.get("ancorata", False)),
        tipo_ancoraggio=inputs.get("tipo_ancoraggio"),
    )


def check_slu(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLUScaffalatura(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_scaffalatura(spec, context, passaggi)

    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "scaffalature",
        "norm_references": ["NTC2018 §7.2.8", "Fase S8"],
        "decision_log": passaggi,
        "domanda_sismica_kg": risultato.domanda_sismica_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
        "meccanismo_critico": risultato.meccanismo_critico,
    }


def check_sle(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLEScaffalatura(
        spostamento_relativo_cm=float(inputs.get("spostamento_relativo_cm", 0.6))
    )
    passaggi: list[str] = []
    risultato = verifica_sle_scaffalatura(spec, context, passaggi)

    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA

    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "scaffalature",
        "norm_references": ["NTC2018 §7.2.8", "Fase S8"],
        "decision_log": passaggi,
        "stato_danno": risultato.stato_danno.value,
        "perdita_contenuto": risultato.perdita_contenuto,
    }


def verifica_scaffalatura_completa(inputs: dict) -> RisultatoScaffalatura:
    spec = spec_from_dict(inputs)
    passaggi: list[str] = []

    context_slu = ContestoSLUScaffalatura(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    risultato_slu = verifica_slu_scaffalatura(spec, context_slu, passaggi)

    context_sle = ContestoSLEScaffalatura(
        spostamento_relativo_cm=float(inputs.get("spostamento_relativo_cm", 0.6))
    )
    risultato_sle = verifica_sle_scaffalatura(spec, context_sle, passaggi)

    return RisultatoScaffalatura(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_scaffalatura_completa",
    "ScaffalaturaSpec",
    "RisultatoScaffalatura",
    "TipoScaffalatura",
]
