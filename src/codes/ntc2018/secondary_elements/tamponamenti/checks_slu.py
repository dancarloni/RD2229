"""
Verifiche SLU (Stato Limite Ultimo) per tamponamenti secondari (Fase S1).

NTC2018 §7.2.3 — Valutazione dell'azione sismica locale e della capacità strutturale.

Implementa:
- Calcolo della domanda sismica locale (F_a) basato su accelerazione spettrale
- Verifica della resistenza fuori piano del pannello
- Verifica della resistenza degli ancoraggi (vite, tassello, saldatura)
- Identificazione del meccanismo critico
"""

import math
from dataclasses import dataclass

from .models import (
    RisultatoSLE,
    RisultatoSLU,
    RisultatoTamponamento,
    StatoDannoSLE,
    TamponamentoSpec,
    TipoAncoraggio,
)

# Costanti NTC2018 per azioni sismiche
FATTORE_AMPLIFICAZIONE_LOCALE_DEFAULT = 2.0  # S_a(T) / a_g per T piccoli


@dataclass
class ContextoSLU:
    """Contesto per la verifica SLU."""

    accelerazione_spettrale_mg: float  # S_a(T) in g
    accelerazione_progettuale_g: float  # a_g (da analisi sismica)
    fattore_importanza_gamma_i: float = 1.0
    fattore_smorzamento: float = 1.0  # ζ = 5% (default)
    profondita_fondazione_m: float = 0.0  # Per effetti p-delta


def calcola_fa_locale(spec: TamponamentoSpec, contesto: ContextoSLU) -> float:
    """
    Calcola la forza sismica locale (F_a) per il tamponamento.

    NTC2018 §7.2.3:
        F_a = S_a(T_cm) * M_cm * γ_i

    dove:
    - S_a(T_cm) è l'accelerazione spettrale per periodo T_cm del componente
    - M_cm è la massa del componente
    - γ_i è il fattore di importanza

    Per tamponamenti a bassa periodicità, T_cm ≈ 0.1-0.3 s,
    quindi S_a(T) ≈ 2-3 * a_g

    Ritorna: F_a in kg
    """

    massa_kg = spec.massa_totale_kg()

    # Conversione accelerazione spettrale da g a cm/s²
    accel_spettrale_cm_s2 = contesto.accelerazione_spettrale_mg * 9.81 * 10.0

    # F_a = (S_a / g) * m * g_i * ζ_fattore
    f_a = (accel_spettrale_cm_s2 / 980.0) * massa_kg * contesto.fattore_importanza_gamma_i

    return f_a


def calcola_resistenza_pannello_fuori_piano(spec: TamponamentoSpec) -> float:
    """
    Calcola la resistenza fuori piano del pannello (come trave orizzontale a sbalzo).

    Modello semplificato:
    - Pannello = trave continua con vincoli agli estremi
    - Resistenza limitata da:
        1. Resistenza a trazione della muratura/cls
        2. Resistenza al taglio
        3. Ribaltamento fuori piano

    Ritorna: Resistenza in kg
    """

    # Per muratura tradizionale: f_t,k ≈ 0.10 f_c (basso!)
    # Per cls: f_t,k ≈ 0.1 f_c
    # Usiamo una stima cautelativa

    if spec.resistenza_compressione_mpa is None:
        # Muratura tradizionale: fc ≈ 2-4 MPa
        fc_mpa = 2.5
    else:
        fc_mpa = spec.resistenza_compressione_mpa

    f_t_k = max(0.10 * fc_mpa, 0.1)  # kg/cm² ≈ 0.01 MPa
    f_t_k_kg_cm2 = f_t_k / 0.0980665  # Conversione

    # Momento resistente della sezione (spessore × larghezza × larghezza/6)
    m_resisten = (spec.spessore_cm * spec.larghezza_cm**2) / 6.0  # cm³

    # Coppia resistente (M = f_t_k × M_resisten)
    coppia_resistente = f_t_k_kg_cm2 * m_resisten  # kg·cm

    # Forza orizzontale equivalente per vincolo a luce L (altezza pannello)
    # M = F × L / 4 (per trave biappoggiata con carico al centro)
    # F = 4 × M / L
    resistenza_fuori_piano = 4.0 * coppia_resistente / spec.altezza_cm

    return resistenza_fuori_piano


def calcola_resistenza_ancoraggi(spec: TamponamentoSpec) -> float:
    """
    Calcola la resistenza complessiva degli ancoraggi a taglio e trazione.

    Per ogni ancoraggio, la resistenza è il minimo tra:
    - Resistenza del tassello/vite/saldatura
    - Resistenza dell'acciaio di ancoraggio
    - Resistenza della base (pannello/struttura)

    Ritorna: Resistenza totale in kg
    """

    resistenza_totale_kg = 0.0

    for ancoraggio in spec.ancoraggi:

        if ancoraggio.tipo == TipoAncoraggio.VITE_METALLO:
            # Resistenza: area filettata × resistenza del materiale
            # Area nominale (diametro × 0.75 per filettatura)
            area_mm2 = math.pi * (ancoraggio.diametro_mm / 2.0) ** 2 * 0.75
            resistenza_una_vite = (area_mm2 * ancoraggio.resistenza_trazione_mpa) / 10.0  # in kg
            resistenza_totale_kg += resistenza_una_vite * ancoraggio.numero_fissaggi

        elif ancoraggio.tipo == TipoAncoraggio.TASSELLO_CHIMICO:
            # Resistenza: carico ammissibile del tassello (da catalogo)
            # Approssimazione: R_chem ≈ 0.6 × ∅ × resistenza materiale
            resistenza_una_unit = (
                0.6
                * ancoraggio.diametro_mm
                * ancoraggio.resistenza_trazione_mpa
                * 0.01  # Fattore di scala
            )
            resistenza_totale_kg += resistenza_una_unit * ancoraggio.numero_fissaggi * 0.1  # in kg

        elif ancoraggio.tipo == TipoAncoraggio.TASSELLO_MECCANICO:
            # Resistenza: simile al chimico, leggermente inferiore
            resistenza_una_unit = (
                0.5 * ancoraggio.diametro_mm * ancoraggio.resistenza_trazione_mpa * 0.01
            )
            resistenza_totale_kg += resistenza_una_unit * ancoraggio.numero_fissaggi * 0.1

        elif ancoraggio.tipo == TipoAncoraggio.SALDATURA:
            # Resistenza saldatura: lunghezza cordone × spessore × resistenza acciaio
            # Approssimazione per cordone d'angolo
            lunghezza_cordone_mm = (
                2 * (spec.larghezza_cm * 10)
                if ancoraggio.numero_fissaggi == 1
                else (spec.larghezza_cm * 10) / ancoraggio.numero_fissaggi
            )
            spessore_cordone_mm = ancoraggio.spessore_acciaio_mm or 5.0

            resistenza_cordone = (
                lunghezza_cordone_mm * spessore_cordone_mm * ancoraggio.resistenza_trazione_mpa
            ) / 100.0
            resistenza_totale_kg += resistenza_cordone * ancoraggio.numero_fissaggi * 0.1

    return max(resistenza_totale_kg, 1.0)  # Minimo 1 kg per sicurezza


def verifica_slu_tamponamento(
    spec: TamponamentoSpec,
    contesto: ContextoSLU,
    passaggi: list[str],
) -> RisultatoSLU:
    """
    Esegue la verifica SLU per il tamponamento.

    Procedura:
    1. Calcola domanda sismica locale (F_a)
    2. Calcola resistenza pannello fuori piano
    3. Calcola resistenza complessiva ancoraggi
    4. Verifica domanda ≤ resistenza
    5. Identifica meccanismo critico
    """

    passaggi.append("=== VERIFICA SLU ===")

    # Passo 1: Calcola domanda
    f_a = calcola_fa_locale(spec, contesto)
    passaggi.append(f"Domanda sismica locale F_a = {f_a:.1f} kg")

    # Passo 2: Resistenza pannello fuori piano
    r_pannello = calcola_resistenza_pannello_fuori_piano(spec)
    passaggi.append(f"Resistenza pannello fuori piano = {r_pannello:.1f} kg")

    # Passo 3: Resistenza ancoraggi
    r_ancoraggi = calcola_resistenza_ancoraggi(spec)
    passaggi.append(f"Resistenza ancoraggi = {r_ancoraggi:.1f} kg")

    # Passo 4: Resistenza complessiva (minimo tra pannello e ancoraggi)
    r_totale = min(r_pannello, r_ancoraggi)
    passaggi.append(
        f"Resistenza complessiva = min({r_pannello:.1f}, {r_ancoraggi:.1f}) = {r_totale:.1f} kg"
    )

    # Passo 5: Verifica
    rapporto = f_a / r_totale if r_totale > 0 else float("inf")
    esito = rapporto <= 1.0

    # Identifica meccanismo critico
    if r_pannello < r_ancoraggi:
        meccanismo = "ribaltamento_fuori_piano_pannello"
    else:
        meccanismo = "rottura_ancoraggi"

    passaggi.append(f"Verifica: F_a / R = {rapporto:.3f} {'≤ 1.0 ✓' if esito else '> 1.0 ✗'}")
    passaggi.append(f"Meccanismo critico: {meccanismo}")

    return RisultatoSLU(
        esito=esito,
        domanda_fuori_piano_kg=f_a,
        resistenza_pannello_kg=r_pannello,
        resistenza_ancoraggi_kg=r_ancoraggi,
        meccanismo_critico=meccanismo,
    )
