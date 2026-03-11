from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import (
    ComponenteSpecialeSpec,
    ContestoSLUSpeciale,
    FamigliaSpeciale,
    RisultatoSLUSpeciale,
)

_RESISTENZE_BASE_KG: dict[FamigliaSpeciale, float] = {
    FamigliaSpeciale.INSEGNA_BANDIERA: 150.0,
    FamigliaSpeciale.CANCELLO_SCORREVOLE: 250.0,
    FamigliaSpeciale.PANNELLO_SOSPESO: 180.0,
    FamigliaSpeciale.MENSOLA_LEGGERA: 120.0,
    FamigliaSpeciale.CHIUSURA_TECNICA: 110.0,
}


def calcola_resistenza_supporto(spec: ComponenteSpecialeSpec) -> float:
    base = _RESISTENZE_BASE_KG[spec.famiglia]
    base *= spec.supporti_numero
    if spec.esposizione_esterna:
        base *= 0.9
    if spec.grado_mobilita == "fisso":
        base *= 1.2
    return max(100.0, base)


def verifica_slu_speciale(
    spec: ComponenteSpecialeSpec, contesto: ContestoSLUSpeciale, passaggi: list[str]
) -> RisultatoSLUSpeciale:
    passaggi.append("=== VERIFICA SLU COMPONENTE SPECIALE ===")

    domanda_sismica = calcola_forza_sismica_locale(
        spec.massa_kg, contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    domanda_vento = (
        contesto.pressione_vento_kpa * spec.massa_kg * 10.0
        if contesto.pressione_vento_kpa > 0
        else 0.0
    )
    domanda_tot = max(domanda_sismica, domanda_vento)

    resistenza = calcola_resistenza_supporto(spec)
    esito = domanda_tot <= resistenza

    passaggi.append(f"Domanda = {domanda_tot:.2f} kg, Resistenza = {resistenza:.2f} kg")

    interferenza = spec.grado_mobilita != "fisso" and domanda_tot > resistenza * 0.5

    return RisultatoSLUSpeciale(
        esito=esito,
        domanda_totale_kg=domanda_tot,
        resistenza_supporto_kg=resistenza,
        interferenza_funzionale=interferenza,
    )
