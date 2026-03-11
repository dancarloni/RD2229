"""
Pacchetto Fase S1 — Verifiche per tamponamenti secondari (NTC2018 §7.2.3).

Moduli:
- models: TamponamentoSpec, RisultatoSLU, RisultatoSLE, StatoDannoSLE
- checks_slu: ContextoSLU, verifica_slu_tamponamento
- checks_sle: ContextoSLE, calcola_stato_danno_sle
- presets: caricamento e gestione preset
- report_adapter: esportazione per report HTML/MD
"""

from .checks_sle import ContextoSLE, calcola_stato_danno_sle, verifica_compatibilita_deformativa
from .checks_slu import (
    ContextoSLU,
    calcola_fa_locale,
    calcola_resistenza_ancoraggi,
    calcola_resistenza_pannello_fuori_piano,
    verifica_slu_tamponamento,
)
from .models import (
    RisultatoSLE,
    RisultatoSLU,
    RisultatoTamponamento,
    SpecAncoraggio,
    StatoDannoSLE,
    TamponamentoSpec,
    TipoAncoraggio,
    TipoVincolo,
)
from .presets import (
    PRESET_CLS_PREFABBRICATO,
    PRESET_FACCIATA_LEGGERA,
    PRESET_MURATURA_TRADIZIONALE,
    get_preset,
    lista_preset_disponibili,
)
from .report_adapter import (
    SezioneReportTamponamento,
    adatta_per_report,
    export_html_table,
    export_markdown,
)


def verifica_tamponamento_completa(
    spec: TamponamentoSpec,
    contesto_slu: ContextoSLU,
    contesto_sle: ContextoSLE,
) -> RisultatoTamponamento:
    """
    Pipeline completa di verifica SLU + SLE per tamponamento.

    Ritorna: RisultatoTamponamento con esiti, passaggi, adattamenti report.
    """
    passaggi = []

    # SLU
    risultato_slu = verifica_slu_tamponamento(spec, contesto_slu, passaggi)

    # SLE
    risultato_sle = calcola_stato_danno_sle(spec, contesto_sle, passaggi)

    return RisultatoTamponamento(
        spec=spec,
        risultato_slu=risultato_slu,
        risultato_sle=risultato_sle,
        passaggi_calcolo=passaggi,
    )


__all__ = [
    # Models
    "TamponamentoSpec",
    "SpecAncoraggio",
    "RisultatoSLU",
    "RisultatoSLE",
    "RisultatoTamponamento",
    "TipoVincolo",
    "TipoAncoraggio",
    "StatoDannoSLE",
    # SLU
    "ContextoSLU",
    "verifica_slu_tamponamento",
    "calcola_fa_locale",
    "calcola_resistenza_pannello_fuori_piano",
    "calcola_resistenza_ancoraggi",
    # SLE
    "ContextoSLE",
    "calcola_stato_danno_sle",
    "verifica_compatibilita_deformativa",
    # Presets
    "get_preset",
    "lista_preset_disponibili",
    "PRESET_MURATURA_TRADIZIONALE",
    "PRESET_CLS_PREFABBRICATO",
    "PRESET_FACCIATA_LEGGERA",
    # Report
    "SezioneReportTamponamento",
    "adatta_per_report",
    "export_markdown",
    "export_html_table",
    # Pipeline
    "verifica_tamponamento_completa",
]
