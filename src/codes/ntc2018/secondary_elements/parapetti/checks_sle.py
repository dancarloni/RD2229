from __future__ import annotations

from ..common import StatoDannoSLE, classifica_danno_da_rapporto
from .models import ContestoSLEParapetto, ParapettoSpec, RisultatoSLEParapetto


def calcola_spostamento_ammissibile(spec: ParapettoSpec) -> float:
    """
    Calculate admissible displacement at parapetto edge based on type.
    Continuous systems: 2.0 cm, Modular: 1.5 cm, Brittle: 0.8 cm
    """
    if spec.comportamento_fragile:
        return 0.8
    if spec.tipo.value in ["continuo_muratura", "continuo_acciaio", "cordolo_integrato"]:
        return 2.0
    return 1.5


def verifica_sle_parapetto(
    spec: ParapettoSpec, contesto: ContestoSLEParapetto, passaggi: list[str]
) -> RisultatoSLEParapetto:
    passaggi.append("=== VERIFICA SLE PARAPETTO ===")

    spostamento_bordo = contesto.spostamento_bordo_cm
    spostamento_ammissibile = calcola_spostamento_ammissibile(spec)

    passaggi.append(f"Spostamento bordo = {spostamento_bordo:.2f} cm")
    passaggi.append(f"Spostamento ammissibile = {spostamento_ammissibile:.2f} cm")

    rapporto = (
        spostamento_bordo / spostamento_ammissibile if spostamento_ammissibile > 0 else float("inf")
    )
    passaggi.append(f"Rapporto spostamento = {rapporto:.3f}")

    # Damage classification
    stato_danno, danno_giunti, danno_pannelli, intervento, note = classifica_danno_da_rapporto(
        rapporto
    )
    passaggi.append(f"Stato danno = {stato_danno.value}")
    passaggi.append(f"Danno giunti: {danno_giunti}, Danno pannelli: {danno_pannelli}")
    passaggi.append(f"Note: {note}")

    integrita = not danno_pannelli
    esito_sle = stato_danno != StatoDannoSLE.INSICUREZZA

    return RisultatoSLEParapetto(
        stato_danno=stato_danno,
        spostamento_bordo_cm=spostamento_bordo,
        spostamento_ammissibile_cm=spostamento_ammissibile,
        danno_ai_giunti=danno_giunti,
        integrita_pannelli=integrita,
        intervento_necessario=intervento,
        note=note,
    )
