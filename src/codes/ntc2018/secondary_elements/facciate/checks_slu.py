from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import ContestoSLUFacciata, FacciataSpec, RisultatoSLUFacciata

_RESISTENZE_BASE_KG: dict[str, float] = {
    "curtain_wall": 80.0,
    "ventilata": 65.0,
    "pannello_prefabbricato": 100.0,
    "rivestimento_pesante": 120.0,
}


def calcola_resistenza_ancoraggi_facciata(spec: FacciataSpec) -> float:
    base = _RESISTENZE_BASE_KG.get(spec.sistema.value, 80.0) * spec.area_m2
    if spec.tipo_ancoraggio == "regolabile":
        base *= 1.1
    return max(200.0, base)


def verifica_slu_facciata(
    spec: FacciataSpec, contesto: ContestoSLUFacciata, passaggi: list[str]
) -> RisultatoSLUFacciata:
    passaggi.append("=== VERIFICA SLU FACCIATA ===")

    domanda_sismica = calcola_forza_sismica_locale(
        spec.massa_totale_kg(), contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    domanda_vento = contesto.pressione_vento_kpa * spec.area_m2
    domanda_combinata = max(domanda_sismica, domanda_vento)

    passaggi.append(f"Domanda sismica = {domanda_sismica:.2f} kg")
    passaggi.append(f"Domanda vento = {domanda_vento:.2f} kg")

    resistenza = calcola_resistenza_ancoraggi_facciata(spec)
    esito = domanda_combinata <= resistenza

    passaggi.append(
        f"Resistenza = {resistenza:.2f} kg, Rapporto = {domanda_combinata / resistenza:.3f}"
    )

    return RisultatoSLUFacciata(
        esito=esito,
        domanda_sismica_kg=domanda_sismica,
        domanda_vento_kg=domanda_vento,
        domanda_combinata_kg=domanda_combinata,
        resistenza_ancoraggi_kg=resistenza,
    )
