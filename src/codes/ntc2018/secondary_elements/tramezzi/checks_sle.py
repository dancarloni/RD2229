from __future__ import annotations

from ..common import classifica_danno_da_rapporto
from .models import ContestoSLETramezzo, RisultatoSLETramezzo, SistemaTramezzo, TramezzoSpec


def drift_capacita_effettivo(spec: TramezzoSpec) -> float:
    bonus_guida = 0.35 if spec.guida_superiore_scorrimento else 0.0
    malus_impianti = 0.20 if spec.impianti_integrati else 0.0
    base = spec.drift_capacita_perc
    if spec.sistema == SistemaTramezzo.CARTONGESSO_DOPPIA_LASTRA:
        base += 0.15
    if spec.sistema == SistemaTramezzo.LATERIZIO_FORATO:
        base -= 0.10
    return max(0.30, base + bonus_guida - malus_impianti)


def verifica_sle_tramezzo(
    spec: TramezzoSpec, contesto: ContestoSLETramezzo, passaggi: list[str]
) -> RisultatoSLETramezzo:
    passaggi.append("=== VERIFICA SLE TRAMEZZO ===")
    capacita = drift_capacita_effettivo(spec)
    rapporto = contesto.drift_calcolato_perc / capacita if capacita > 0 else float("inf")
    stato, danno_giunti, danno_pannello, intervento, nota = classifica_danno_da_rapporto(rapporto)
    passaggi.append(
        f"Drift calcolato = {contesto.drift_calcolato_perc:.3f}% ; capacita = {capacita:.3f}% ; rapporto = {rapporto:.3f}"
    )
    passaggi.append(f"Stato danno = {stato.value}")
    return RisultatoSLETramezzo(
        stato_danno=stato,
        drift_calcolato_perc=contesto.drift_calcolato_perc,
        drift_capacita_perc=capacita,
        danno_ai_giunti=danno_giunti,
        danno_al_pannello=danno_pannello,
        intervento_necessario=intervento,
        note=nota,
    )
