from __future__ import annotations

from ..common import classifica_danno_da_rapporto
from .models import ContestoSLEFacciata, FacciataSpec, RisultatoSLEFacciata


def verifica_sle_facciata(
    spec: FacciataSpec, contesto: ContestoSLEFacciata, passaggi: list[str]
) -> RisultatoSLEFacciata:
    passaggi.append("=== VERIFICA SLE FACCIATA ===")

    drift_calc = contesto.drift_calcolato_perc
    drift_amm = spec.drift_capacita_perc or 1.0
    rapporto = drift_calc / drift_amm if drift_amm > 0 else float("inf")

    stato_danno, danno_giunti, danno_pannelli, intervento, note = classifica_danno_da_rapporto(
        rapporto
    )
    rischio_martellamento = rapporto > 2.0

    return RisultatoSLEFacciata(
        stato_danno=stato_danno,
        drift_calcolato_perc=drift_calc,
        drift_ammissibile_perc=drift_amm,
        danno_ai_giunti=danno_giunti,
        rischio_martellamento=rischio_martellamento,
        intervento_necessario=intervento,
        note=note,
    )
