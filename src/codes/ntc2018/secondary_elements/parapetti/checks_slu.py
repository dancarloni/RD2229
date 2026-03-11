from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import ContestoSLUParapetto, ParapettoSpec, RisultatoSLUParapetto, TipoParapetto

_RESISTENZE_BASE_KN: dict[TipoParapetto, float] = {
    TipoParapetto.CONTINUO_MURATURA: 8.5,
    TipoParapetto.CONTINUO_ACCIAIO: 12.0,
    TipoParapetto.MONTANTI_ACCIAIO: 10.5,
    TipoParapetto.VETRATO: 7.5,
    TipoParapetto.MISTO_ACCIAIO_VETRO: 9.0,
    TipoParapetto.RECINZIONE_METALLICA: 6.5,
}


def calcola_resistenza_ancoraggio(spec: ParapettoSpec) -> float:
    if spec.resistenza_ancoraggio_kn is not None:
        return spec.resistenza_ancoraggio_kn * 1000.0  # Convert kN to kg

    base_kn = _RESISTENZE_BASE_KN[spec.tipo]
    base_kg = base_kn * 1000.0

    # Modifiers based on anchorage type
    if spec.tipo_ancoraggio.value == "tasselli_puntuali" and spec.numero_montanti:
        base_kg *= spec.numero_montanti / max(1, spec.numero_montanti - 1)

    if spec.tipo_ancoraggio.value == "chimico":
        base_kg *= 1.15

    if spec.tipo_ancoraggio.value == "cordolo_integrato":
        base_kg *= 1.25

    if not spec.vincoli_laterali:
        base_kg *= 0.85

    if spec.comportamento_fragile:
        base_kg *= 0.80

    return max(500.0, base_kg)


def verifica_slu_parapetto(
    spec: ParapettoSpec, contesto: ContestoSLUParapetto, passaggi: list[str]
) -> RisultatoSLUParapetto:
    passaggi.append("=== VERIFICA SLU PARAPETTO ===")

    # Seismic demand
    domanda_sismica = calcola_forza_sismica_locale(
        spec.massa_totale_kg(), contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    passaggi.append(f"Domanda sismica = {domanda_sismica:.2f} kg")

    # Service load demand (horizontal)
    domanda_servizio = contesto.carico_orizzontale_servizio_kg
    passaggi.append(f"Domanda d'uso (carico orizzontale) = {domanda_servizio:.2f} kg")

    # Combined demand (envelope)
    domanda_combinata = max(domanda_sismica, domanda_servizio)
    passaggi.append(f"Domanda combinata (inviluppo) = {domanda_combinata:.2f} kg")

    # Anchorage resistance
    resistenza = calcola_resistenza_ancoraggio(spec)
    passaggi.append(f"Resistenza ancoraggio = {resistenza:.2f} kg")

    meccanismo = "rottura_ancoraggio"
    esito = domanda_combinata <= resistenza
    passaggi.append(
        f"Rapporto D/R = {domanda_combinata / resistenza:.3f} {'<= 1.0' if esito else '> 1.0'}"
    )

    return RisultatoSLUParapetto(
        esito=esito,
        domanda_sismica_kg=domanda_sismica,
        domanda_servizio_kg=domanda_servizio,
        domanda_combinata_kg=domanda_combinata,
        resistenza_ancoraggio_kg=resistenza,
        meccanismo_critico=meccanismo,
    )
