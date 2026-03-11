from __future__ import annotations

from ..common import StatoDannoSLE, classifica_danno_da_rapporto
from .models import ContestoSLEScaffalatura, RisultatoSLEScaffalatura, ScaffalaturaSpec


def verifica_sle_scaffalatura(
    spec: ScaffalaturaSpec, contesto: ContestoSLEScaffalatura, passaggi: list[str]
) -> RisultatoSLEScaffalatura:
    passaggi.append("=== VERIFICA SLE SCAFFALATURA ===")

    spostamento = contesto.spostamento_relativo_cm
    spostamento_amm = min(spec.altezza_cm / 100.0, 2.0)
    rapporto = spostamento / spostamento_amm if spostamento_amm > 0 else float("inf")

    stato_danno, _, _, intervento, note = classifica_danno_da_rapporto(rapporto)
    perdita_contenuto = rapporto > 1.5

    return RisultatoSLEScaffalatura(
        stato_danno=stato_danno,
        spostamento_relativo_cm=spostamento,
        spostamento_ammissibile_cm=spostamento_amm,
        perdita_contenuto=perdita_contenuto,
        intervento_necessario=intervento,
        note=note,
    )
