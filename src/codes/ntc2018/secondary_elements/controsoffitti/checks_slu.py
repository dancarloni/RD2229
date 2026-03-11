from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import (
    ContestoSLUControsoffitto,
    ControsoffittoSpec,
    RisultatoSLUControsoffitto,
    TipoControsoffitto,
)

_RESISTENZE_PENDINI_KG: dict[TipoControsoffitto, float] = {
    TipoControsoffitto.MODULARE_GESSO: 25.0,
    TipoControsoffitto.LASTRA_CONTINUA: 35.0,
    TipoControsoffitto.TECNICO_APERTO: 30.0,
    TipoControsoffitto.SISTEMA_MISTO: 28.0,
}


def calcola_resistenza_pendini(spec: ControsoffittoSpec) -> float:
    base = _RESISTENZE_PENDINI_KG[spec.tipo]
    if spec.numero_pendini:
        base *= spec.numero_pendini
    return max(100.0, base)


def calcola_resistenza_controventi(spec: ControsoffittoSpec) -> float:
    if not spec.presenza_controventi:
        return float("inf")
    base = (
        40.0
        if spec.tipo in [TipoControsoffitto.MODULARE_GESSO, TipoControsoffitto.TECNICO_APERTO]
        else 50.0
    )
    if spec.lunghezza_controventi_m:
        base *= spec.lunghezza_controventi_m / 2.0
    return max(50.0, base)


def verifica_slu_controsoffitto(
    spec: ControsoffittoSpec, contesto: ContestoSLUControsoffitto, passaggi: list[str]
) -> RisultatoSLUControsoffitto:
    passaggi.append("=== VERIFICA SLU CONTROSOFFITTO ===")

    domanda = calcola_forza_sismica_locale(
        spec.massa_totale_kg(), contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    passaggi.append(f"Domanda sismica = {domanda:.2f} kg")

    r_pendini = calcola_resistenza_pendini(spec)
    r_controventi = calcola_resistenza_controventi(spec)
    passaggi.append(f"Resistenza pendini = {r_pendini:.2f} kg")
    passaggi.append(f"Resistenza controventi = {r_controventi:.2f} kg")

    capacita_gioco = spec.gioco_perimetrale_mm >= 25
    passaggi.append(
        f"Gioco perimetrale {spec.gioco_perimetrale_mm} mm: {'ADEGUATO' if capacita_gioco else 'INSUFFICIENTE'}"
    )

    resistenza = min(r_pendini, r_controventi) if r_controventi != float("inf") else r_pendini
    esito = (domanda <= resistenza) and capacita_gioco
    passaggi.append(f"Rapporto D/R = {domanda / resistenza:.3f}")

    return RisultatoSLUControsoffitto(
        esito=esito,
        domanda_totale_kg=domanda,
        resistenza_pendini_kg=r_pendini,
        resistenza_controventi_kg=r_controventi,
        capacita_gioco_perimetrale=capacita_gioco,
    )
