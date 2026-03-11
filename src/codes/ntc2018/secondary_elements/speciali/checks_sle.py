from __future__ import annotations

from ..common import StatoDannoSLE, classifica_danno_da_rapporto
from .models import ComponenteSpecialeSpec, ContestoSLESpeciale, RisultatoSLESpeciale


def verifica_sle_speciale(
    spec: ComponenteSpecialeSpec, contesto: ContestoSLESpeciale, passaggi: list[str]
) -> RisultatoSLESpeciale:
    passaggi.append("=== VERIFICA SLE COMPONENTE SPECIALE ===")

    spostamento = contesto.spostamento_relativo_cm
    spostamento_amm = 2.0 if spec.grado_mobilita == "fisso" else 3.5
    rapporto = spostamento / spostamento_amm if spostamento_amm > 0 else float("inf")

    stato_danno, _, _, intervento, note = classifica_danno_da_rapporto(rapporto)
    danni_locali = rapporto > 1.0

    return RisultatoSLESpeciale(
        stato_danno=stato_danno,
        spostamento_relativo_cm=spostamento,
        spostamento_ammissibile_cm=spostamento_amm,
        danni_locali=danni_locali,
        intervento_necessario=intervento,
        note=note,
    )
