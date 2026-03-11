from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import CaminoSpec, ContestoSLUCamino, RisultatoSLUCamino, TipoCamino

_RESISTENZE_BASE_KG: dict[TipoCamino, float] = {
    TipoCamino.MURATURA: 500.0,
    TipoCamino.ACCIAIO: 600.0,
    TipoCamino.PREFABBRICATO: 450.0,
    TipoCamino.COMPOSITO: 550.0,
}


def calcola_resistenza_camino(spec: CaminoSpec) -> float:
    base = _RESISTENZE_BASE_KG[spec.tipo]
    if spec.controventato:
        base *= 1.4
    return max(300.0, base)


def verifica_slu_camino(
    spec: CaminoSpec, contesto: ContestoSLUCamino, passaggi: list[str]
) -> RisultatoSLUCamino:
    passaggi.append("=== VERIFICA SLU CAMINO ===")

    domanda = calcola_forza_sismica_locale(
        spec.massa_totale_kg, contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    resistenza = calcola_resistenza_camino(spec)

    passaggi.append(f"Domanda = {domanda:.2f} kg, Resistenza = {resistenza:.2f} kg")

    esito = domanda <= resistenza
    return RisultatoSLUCamino(
        esito=esito,
        domanda_sismica_kg=domanda,
        resistenza_base_kg=resistenza,
        capacita_stabilita=esito,
    )
