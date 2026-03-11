from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import ContestoSLUTramezzo, RisultatoSLUTramezzo, SistemaTramezzo, TramezzoSpec

_RESISTENZE_BASE_KG: dict[SistemaTramezzo, float] = {
    SistemaTramezzo.CARTONGESSO_STANDARD: 140.0,
    SistemaTramezzo.CARTONGESSO_DOPPIA_LASTRA: 190.0,
    SistemaTramezzo.LATERIZIO_FORATO: 260.0,
    SistemaTramezzo.SISTEMA_MISTO: 210.0,
}


def calcola_resistenza_fuori_piano(spec: TramezzoSpec) -> float:
    base = spec.resistenza_fuori_piano_kg or _RESISTENZE_BASE_KG[spec.sistema]
    fattore_aperture = max(0.55, 1.0 - (spec.area_aperture_cm2 / max(spec.area_lorda_cm2(), 1.0)))
    fattore_altezza = min(1.0, 300.0 / max(spec.altezza_cm, 1.0))
    fattore_guide = (
        1.10
        if spec.guida_superiore_scorrimento and spec.sistema != SistemaTramezzo.LATERIZIO_FORATO
        else 1.0
    )
    return max(25.0, base * fattore_aperture * fattore_altezza * fattore_guide)


def calcola_resistenza_ancoraggi(spec: TramezzoSpec) -> float:
    if spec.resistenza_ancoraggi_kg is not None:
        return spec.resistenza_ancoraggi_kg
    base = 180.0 if spec.ancorato_lateralmente else 110.0
    if spec.vincolo_superiore.value == "scorrevole":
        base *= 0.95
    if spec.impianti_integrati:
        base *= 0.92
    return max(30.0, base)


def verifica_slu_tramezzo(
    spec: TramezzoSpec, contesto: ContestoSLUTramezzo, passaggi: list[str]
) -> RisultatoSLUTramezzo:
    passaggi.append("=== VERIFICA SLU TRAMEZZO ===")
    domanda = calcola_forza_sismica_locale(
        spec.massa_totale_kg(), contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    passaggi.append(f"Domanda fuori piano = {domanda:.2f} kg")
    resistenza_fuori_piano = calcola_resistenza_fuori_piano(spec)
    resistenza_ancoraggi = calcola_resistenza_ancoraggi(spec)
    passaggi.append(f"Resistenza fuori piano = {resistenza_fuori_piano:.2f} kg")
    passaggi.append(f"Resistenza ancoraggi = {resistenza_ancoraggi:.2f} kg")
    meccanismo = (
        "rottura_ancoraggi"
        if resistenza_ancoraggi <= resistenza_fuori_piano
        else "instabilita_fuori_piano"
    )
    resistenza_governante = min(resistenza_fuori_piano, resistenza_ancoraggi)
    esito = domanda <= resistenza_governante
    passaggi.append(
        f"Rapporto D/R = {domanda / resistenza_governante:.3f} {'<= 1.0' if esito else '> 1.0'}"
    )
    return RisultatoSLUTramezzo(
        esito=esito,
        domanda_fuori_piano_kg=domanda,
        resistenza_fuori_piano_kg=resistenza_fuori_piano,
        resistenza_ancoraggi_kg=resistenza_ancoraggi,
        meccanismo_critico=meccanismo,
    )
