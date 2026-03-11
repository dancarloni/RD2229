from __future__ import annotations

from .checks_sle import verifica_sle_speciale
from .checks_slu import verifica_slu_speciale
from .models import (
    ComponenteSpecialeSpec,
    ContestoSLESpeciale,
    ContestoSLUSpeciale,
    FamigliaSpeciale,
    RisultatoComponenteSpeciale,
    StatoDannoSLE,
)


def spec_from_dict(inputs: dict) -> ComponenteSpecialeSpec:
    famiglia = FamigliaSpeciale(inputs.get("famiglia", FamigliaSpeciale.INSEGNA_BANDIERA.value))
    return ComponenteSpecialeSpec(
        famiglia=famiglia,
        massa_kg=float(inputs.get("massa_kg", 50.0)),
        schema_statico=inputs.get("schema_statico", "mensola"),
        esposizione_esterna=bool(inputs.get("esposizione_esterna", True)),
        tipo_supporto=inputs.get("tipo_supporto", "staffa"),
        grado_mobilita=inputs.get("grado_mobilita", "fisso"),
        supporti_numero=int(inputs.get("supporti_numero", 1)),
    )


def check_slu(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLUSpeciale(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        pressione_vento_kpa=float(inputs.get("P_vento", 0.8)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_speciale(spec, context, passaggi)

    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "speciali",
        "norm_references": ["NTC2018 §7.2.9", "Fase S9"],
        "decision_log": passaggi,
        "domanda_totale_kg": risultato.domanda_totale_kg,
        "resistenza_supporto_kg": risultato.resistenza_supporto_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
    }


def check_sle(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLESpeciale(
        spostamento_relativo_cm=float(inputs.get("spostamento_relativo_cm", 0.7))
    )
    passaggi: list[str] = []
    risultato = verifica_sle_speciale(spec, context, passaggi)

    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA

    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "speciali",
        "norm_references": ["NTC2018 §7.2.9", "Fase S9"],
        "decision_log": passaggi,
        "stato_danno": risultato.stato_danno.value,
        "danni_locali": risultato.danni_locali,
    }


def verifica_speciale_completa(inputs: dict) -> RisultatoComponenteSpeciale:
    spec = spec_from_dict(inputs)
    passaggi: list[str] = []

    context_slu = ContestoSLUSpeciale(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        pressione_vento_kpa=float(inputs.get("P_vento", 0.8)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    risultato_slu = verifica_slu_speciale(spec, context_slu, passaggi)

    context_sle = ContestoSLESpeciale(
        spostamento_relativo_cm=float(inputs.get("spostamento_relativo_cm", 0.7))
    )
    risultato_sle = verifica_sle_speciale(spec, context_sle, passaggi)

    return RisultatoComponenteSpeciale(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_speciale_completa",
    "ComponenteSpecialeSpec",
    "RisultatoComponenteSpeciale",
    "FamigliaSpeciale",
]
