from __future__ import annotations

from .checks_sle import verifica_sle_impianto
from .checks_slu import verifica_slu_impianto
from .models import (
    CategoriaImpianto,
    ContestoSLEImpianto,
    ContestoSLUImpianto,
    ImpiantoSpec,
    RisultatoImpianto,
    StatoDannoSLE,
    TipoSupporto,
)
from .presets import (
    carica_presets_da_json,
    crea_spec_da_preset,
    get_preset,
    lista_preset_disponibili,
)
from .report_adapter import adatta_per_report, export_markdown


def spec_from_dict(inputs: dict) -> ImpiantoSpec:
    categoria = CategoriaImpianto(
        inputs.get("categoria", CategoriaImpianto.TUBAZIONE_SOSPESA.value)
    )
    tipo_supporto = TipoSupporto(inputs.get("tipo_supporto", TipoSupporto.SOSPENSIONE.value))

    return ImpiantoSpec(
        categoria=categoria,
        massa_kg=float(inputs.get("massa_kg", 50.0)),
        quota_cm=float(inputs.get("quota_cm", 300.0)),
        tipo_supporto=tipo_supporto,
        numero_ancoraggi=int(inputs.get("numero_ancoraggi", 2)),
        presenza_giunto_flessibile=bool(inputs.get("presenza_giunto_flessibile", True)),
        classe_funzione=inputs.get("classe_funzione"),
        resistenza_supporto_kn=inputs.get("resistenza_supporto_kn"),
        lunghezza_percorso_m=float(inputs.get("lunghezza_percorso_m", 1.0)),
    )


def check_slu(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLUImpianto(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    passaggi: list[str] = []
    risultato = verifica_slu_impianto(spec, context, passaggi)

    return {
        "esito": "OK" if risultato.esito else "NON OK",
        "ok": risultato.esito,
        "element_type": "impianti",
        "norm_references": ["NTC2018 §7.2.5", "Fase S5"],
        "decision_log": passaggi,
        "domanda_totale_kg": risultato.domanda_totale_kg,
        "resistenza_supporti_kg": risultato.resistenza_supporti_kg,
        "utilisation": round(risultato.rapporto_domanda_resistenza, 4),
        "continuita_funzionale": risultato.capacita_continuita_funzionale,
    }


def check_sle(inputs: dict) -> dict:
    spec = spec_from_dict(inputs)
    context = ContestoSLEImpianto(
        spostamento_relativo_cm=float(inputs.get("spostamento_relativo_cm", 0.8))
    )
    passaggi: list[str] = []
    risultato = verifica_sle_impianto(spec, context, passaggi)

    esito = risultato.stato_danno != StatoDannoSLE.INSICUREZZA

    return {
        "esito": "OK" if esito else "NON OK",
        "ok": esito,
        "element_type": "impianti",
        "norm_references": ["NTC2018 §7.2.5", "Fase S5"],
        "decision_log": passaggi,
        "stato_danno": risultato.stato_danno.value,
        "collisione_rischio": risultato.collisione_rischio,
        "perdita_funzionalita": risultato.perdita_funzionalita,
    }


def verifica_impianto_completa(inputs: dict) -> RisultatoImpianto:
    spec = spec_from_dict(inputs)
    passaggi: list[str] = []

    context_slu = ContestoSLUImpianto(
        accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
        gamma_i=float(inputs.get("gamma_i", 1.0)),
    )
    risultato_slu = verifica_slu_impianto(spec, context_slu, passaggi)

    context_sle = ContestoSLEImpianto(
        spostamento_relativo_cm=float(inputs.get("spostamento_relativo_cm", 0.8))
    )
    risultato_sle = verifica_sle_impianto(spec, context_sle, passaggi)

    return RisultatoImpianto(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_impianto_completa",
    "ImpiantoSpec",
    "RisultatoImpianto",
    "CategoriaImpianto",
    "TipoSupporto",
    "get_preset",
    "lista_preset_disponibili",
    "carica_presets_da_json",
    "crea_spec_da_preset",
    "adatta_per_report",
    "export_markdown",
]
