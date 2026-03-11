"""
Verifiche SLE (Stato Limite di Esercizio) per tamponamenti secondari (Fase S1).

NTC2018 §7.2.3 + Circ. 7/2019 — Limitazione dei danni durante il terremoto.

Implementa:
- Valutazione della compatibilità deformativa (drift interpiano vs. capacità)
- Classificazione stato danno su scala 4-livelli (assente, locale, diffuso, insicurezza)
- Identificazione di danno ai giunti e al pannello
- Generazione di note SLE per il report
"""

from dataclasses import dataclass

from .models import RisultatoSLE, StatoDannoSLE, TamponamentoSpec


@dataclass
class ContextoSLE:
    """Contesto per la verifica SLE."""

    drift_calcolato_perc: float  # Drift interpiano in % di h
    periodo_fondamentale_s: float = 1.0  # T_1 per amplificazione dinamica


def calcola_stato_danno_sle(
    spec: TamponamentoSpec,
    contesto: ContextoSLE,
    passaggi: list[str],
) -> RisultatoSLE:
    """
    Valuta lo stato danno secondo scala 4-livelli.

    Scala di classificazione:
    - ASSENTE: drift < 50% capacità → assenza di danno visibile
    - LOCALE: 50% ≤ drift < 75% capacità → danno localizzato ai giunti e ancoraggi
    - DIFFUSO: 75% ≤ drift < 100% capacità → danno generalizzato al pannello
    - INSICUREZZA: drift ≥ 100% capacità → rischio di espulsione/crollo

    Ritorna: RisultatoSLE con stato danno, rapporto drift, flag danno.
    """

    passaggi.append("=== VERIFICA SLE ===")

    # Estrai capacità deformativa
    drift_capacita_perc = spec.drift_capacita_perc
    drift_calcolato = contesto.drift_calcolato_perc

    # Rapporto tra domanda e capacità
    rapporto_drift = (
        drift_calcolato / drift_capacita_perc if drift_capacita_perc > 0 else float("inf")
    )

    passaggi.append(
        f"Drift calcolato = {drift_calcolato:.2f}% "
        f"vs. capacità = {drift_capacita_perc:.2f}% "
        f"→ rapporto = {rapporto_drift:.3f}"
    )

    # Classificazione stato danno
    if rapporto_drift < 0.50:
        stato_danno = StatoDannoSLE.ASSENTE
        danno_giunti = False
        danno_pannello = False
        intervento = False
        nota = "Drift al di sotto della soglia di danno; tamponamento in condizioni di sicurezza."

    elif rapporto_drift < 0.75:
        stato_danno = StatoDannoSLE.LOCALE
        danno_giunti = True
        danno_pannello = False
        intervento = False
        nota = (
            "Danno localizzato ai giunti perimetrali e agli ancoraggi; "
            "integrità strutturale del pannello preservata. "
            "Ispezione consigliata per stabilire esigenza di ricementazione."
        )

    elif rapporto_drift < 1.00:
        stato_danno = StatoDannoSLE.DIFFUSO
        danno_giunti = True
        danno_pannello = True
        intervento = False
        nota = (
            "Danno diffuso al pannello e ai giunti; micro-fratture e separazioni visibili. "
            "Intervento di risarcimento/consolidamento consigliato prima del prossimo evento sismico."
        )

    else:  # rapporto_drift >= 1.00
        stato_danno = StatoDannoSLE.INSICUREZZA
        danno_giunti = True
        danno_pannello = True
        intervento = True
        nota = (
            "CRITICO: Capacità deformativa superata; rischio di espulsione del pannello. "
            "Intervento strutturale obbligatorio. Valutare rimpiazzo o consolidamento urgente."
        )

    passaggi.append(f"Stato danno: {stato_danno.value.upper()}")
    passaggi.append(nota)

    return RisultatoSLE(
        stato_danno=stato_danno,
        drift_calcolato_perc=drift_calcolato,
        drift_capacita_perc=drift_capacita_perc,
        danno_ai_giunti=danno_giunti,
        danno_al_pannello=danno_pannello,
        intervento_necessario=intervento,
        note_sle=nota,
    )


def verifica_compatibilita_deformativa(
    spec: TamponamentoSpec,
    contesto: ContextoSLE,
) -> bool:
    """
    Semplice verifica booleana della compatibilità tra drift calcolato e capacità.

    Ritorna: True se drift_calcolato ≤ drift_capacita
    """
    return contesto.drift_calcolato_perc <= spec.drift_capacita_perc
