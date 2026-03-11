from __future__ import annotations

from ..common import StatoDannoSLE, classifica_danno_da_rapporto
from .models import ContestoSLEControsoffitto, ControsoffittoSpec, RisultatoSLEControsoffitto


def calcola_drift_ammissibile(spec: ControsoffittoSpec) -> float:
    """Calculate admissible drift for ceiling type"""
    if spec.tipo == "lastra_continua":
        return 1.5
    elif spec.tipo == "tecnico_aperto":
        return 2.0
    else:
        return 1.2


def verifica_sle_controsoffitto(
    spec: ControsoffittoSpec, contesto: ContestoSLEControsoffitto, passaggi: list[str]
) -> RisultatoSLEControsoffitto:
    passaggi.append("=== VERIFICA SLE CONTROSOFFITTO ===")

    drift_calc = contesto.drift_calcolato_perc
    drift_amm = calcola_drift_ammissibile(spec)

    passaggi.append(f"Drift calcolato = {drift_calc:.3f} %")
    passaggi.append(f"Drift ammissibile = {drift_amm:.3f} %")

    rapporto = drift_calc / drift_amm if drift_amm > 0 else float("inf")

    stato_danno, danno_giunti, danno_pannelli, intervento, note = classifica_danno_da_rapporto(
        rapporto
    )
    passaggi.append(f"Stato danno = {stato_danno.value}")

    perdita_appoggio = rapporto > 1.5
    danno_bordo = danno_giunti

    return RisultatoSLEControsoffitto(
        stato_danno=stato_danno,
        drift_calcolato_perc=drift_calc,
        drift_ammissibile_perc=drift_amm,
        perdita_appoggio_rischio=perdita_appoggio,
        danno_bordo=danno_bordo,
        intervento_necessario=intervento,
        note=note,
    )
