from __future__ import annotations

from ..common import StatoDannoSLE, classifica_danno_da_rapporto
from .models import CaminoSpec, ContestoSLECamino, RisultatoSLECamino


def verifica_sle_camino(
    spec: CaminoSpec, contesto: ContestoSLECamino, passaggi: list[str]
) -> RisultatoSLECamino:
    passaggi.append("=== VERIFICA SLE CAMINO ===")

    spostamento = contesto.spostamento_sommitale_cm
    spostamento_amm = spec.altezza_cm / 200.0
    rapporto = spostamento / spostamento_amm if spostamento_amm > 0 else float("inf")

    stato_danno, _, _, intervento, note = classifica_danno_da_rapporto(rapporto)
    danno_risonanza = spec.periodo_proprio_s() > 1.0

    return RisultatoSLECamino(
        stato_danno=stato_danno,
        spostamento_sommitale_cm=spostamento,
        spostamento_ammissibile_cm=spostamento_amm,
        danno_risonanza=danno_risonanza,
        intervento_necessario=intervento,
        note=note,
    )
