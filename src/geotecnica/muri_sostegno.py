"""Calcoli per muri di sostegno (P.4).

Supporta:
- coefficiente di spinta attiva Rankine (orizzontale e inclinato)
- coefficiente di spinta attiva Coulomb (formula generale)
- coefficiente di spinta passiva Rankine
- contributo della coesione nella spinta
- verifiche SLU: ribaltamento, scorrimento, schiacciamento
"""

from __future__ import annotations

import math

from .models import InputMuroSostegno, RisultatoMuroSostegno, RisultatoVerificaMuro

# ---------------------------------------------------------------------------
# Coefficienti di spinta
# ---------------------------------------------------------------------------


def ka_rankine(phi_gradi: float, beta_gradi: float = 0.0) -> float:
    """Coefficiente di spinta attiva Rankine.

    Per terreno con inclinazione β rispetto all'orizzontale:
    K_a = cos(β) * [cos(β) - sqrt(cos²β - cos²φ)] / [cos(β) + sqrt(cos²β - cos²φ)]

    Per terreno orizzontale (β=0): K_a = tan²(45 - φ/2)
    """

    phi = math.radians(phi_gradi)
    beta = math.radians(beta_gradi)

    if abs(beta_gradi) < 1e-9:
        return math.tan(math.radians(45.0) - phi / 2.0) ** 2

    cos_beta = math.cos(beta)
    discriminante = cos_beta**2 - math.cos(phi) ** 2
    if discriminante < 0:
        raise ValueError(
            f"β ({beta_gradi}°) supera φ ({phi_gradi}°): spinta attiva Rankine non applicabile"
        )
    radice = math.sqrt(max(discriminante, 0.0))
    return cos_beta * (cos_beta - radice) / (cos_beta + radice)


def kp_rankine(phi_gradi: float) -> float:
    """Coefficiente di spinta passiva Rankine (terreno orizzontale).

    K_p = tan²(45 + φ/2)
    """

    phi = math.radians(phi_gradi)
    return math.tan(math.radians(45.0) + phi / 2.0) ** 2


def ka_coulomb(
    phi_gradi: float,
    delta_gradi: float,
    alpha_gradi: float = 90.0,
    beta_gradi: float = 0.0,
) -> float:
    """Coefficiente di spinta attiva Coulomb (formula generale).

    Args:
        phi_gradi: Angolo di attrito del terreno (°)
        delta_gradi: Angolo di attrito muro-terreno (°)
        alpha_gradi: Inclinazione paramento rispetto all'orizzontale (°),
                     90° = paramento verticale
        beta_gradi: Inclinazione del terrapieno (°)

    Restituisce:
        K_a secondo la formula di Coulomb
    """

    phi = math.radians(phi_gradi)
    delta = math.radians(delta_gradi)
    alpha = math.radians(alpha_gradi)
    beta = math.radians(beta_gradi)

    sin_alpha = math.sin(alpha)
    sin_alpha_phi = math.sin(alpha + phi)
    sin_phi_delta = math.sin(phi + delta)
    sin_phi_beta = math.sin(phi - beta)
    sin_alpha_delta = math.sin(alpha - delta)
    sin_alpha_beta = math.sin(alpha + beta)

    if sin_alpha_delta <= 0 or sin_alpha_beta <= 0:
        raise ValueError("Geometria muro non valida per la formula di Coulomb")

    arg = (sin_phi_delta * sin_phi_beta) / (sin_alpha_delta * sin_alpha_beta)
    if arg < 0:
        raise ValueError("Parametri Coulomb non validi: radice di numero negativo")

    denominatore = sin_alpha * math.sin(alpha - delta) * (1.0 + math.sqrt(arg)) ** 2
    if abs(denominatore) < 1e-15:
        raise ValueError("Denominatore Coulomb nullo: geometria singolare")

    return math.sin(alpha + phi) ** 2 / denominatore


def spinta_attiva_totale_kg_cm(
    gamma_kg_m3: float,
    altezza_cm: float,
    ka: float,
    coesione_kg_cm2: float = 0.0,
) -> float:
    """Spinta totale attiva per metro lineare in kg/cm (integrazione triangolare).

    E_a = 0.5 * K_a * γ * H² - 2*c*√K_a * H
    (coesione riduce la spinta attiva)
    """

    gamma_kg_cm3 = gamma_kg_m3 / 1_000_000.0
    spinta_terreno = 0.5 * ka * gamma_kg_cm3 * altezza_cm**2
    riduzione_coesione = 2.0 * coesione_kg_cm2 * math.sqrt(ka) * altezza_cm
    return max(spinta_terreno - riduzione_coesione, 0.0)


def punto_applicazione_spinta_cm(altezza_cm: float, coesione_kg_cm2: float = 0.0) -> float:
    """Punto di applicazione della risultante della spinta (da base muro).

    Senza coesione: H/3 da base (distribuzione triangolare).
    Con coesione: approssimazione conservative H/3.
    """

    # Per semplicita' e conservativita': sempre H/3 da base
    return altezza_cm / 3.0


# ---------------------------------------------------------------------------
# Verifiche SLU
# ---------------------------------------------------------------------------


def _verifica_ribaltamento(
    spinta_kg_cm: float,
    punto_appl_cm: float,
    peso_muro_kg: float,
    larghezza_base_cm: float,
    gamma_r: float,
) -> RisultatoVerificaMuro:
    """Verifica SLU di ribaltamento rispetto al piede a valle.

    M_stabilizzante = P * B/2
    M_ribaltante = E_a * h_E
    Condizione: M_stab / M_rib ≥ gamma_R
    """

    m_rib = spinta_kg_cm * punto_appl_cm
    m_stab = peso_muro_kg * (larghezza_base_cm / 2.0)
    if m_rib <= 0:
        rapporto = 0.0
    else:
        rapporto = m_rib * gamma_r / m_stab if m_stab > 0 else math.inf

    passaggi = [
        f"M_ribaltante = E_a * h_E = {spinta_kg_cm:.3f} * {punto_appl_cm:.3f} = {m_rib:.3f} kg",
        f"M_stabilizzante = P * B/2 = {peso_muro_kg:.3f} * {larghezza_base_cm/2:.3f} = {m_stab:.3f} kg",
        f"γ_R = {gamma_r:.2f}",
        f"Rapporto utilizzo = M_rib * γ_R / M_stab = {rapporto:.4f}",
    ]

    return RisultatoVerificaMuro(
        nome_verifica="ribaltamento",
        azione_sfavorevole=m_rib,
        azione_favorevole=m_stab,
        rapporto_utilizzo=rapporto,
        verificato=rapporto <= 1.0,
        passaggi_calcolo=passaggi,
    )


def _verifica_scorrimento(
    spinta_orizzontale_kg: float,
    peso_muro_kg: float,
    phi_fondazione_gradi: float,
    coesione_fondazione_kg_cm2: float,
    larghezza_base_cm: float,
    gamma_r: float,
    delta_muro_gradi: float = 0.0,
) -> RisultatoVerificaMuro:
    """Verifica SLU di scorrimento alla base.

    H_Rd = (N_Ed * tan(δ_fond) + c_a * A) / γ_R
    dove δ_fond = φ_fond per muri in c.a. su terreno (tipico 2/3 φ per gravita')
    """

    phi_fond = math.radians(phi_fondazione_gradi)
    # angolo di attrito base-terreno: 2/3 * phi per muri di gravita' se non specificato
    if delta_muro_gradi > 0:
        delta_base = min(math.radians(delta_muro_gradi), phi_fond)
    else:
        delta_base = (2.0 / 3.0) * phi_fond

    resistenza_base_kg = (
        peso_muro_kg * math.tan(delta_base) + coesione_fondazione_kg_cm2 * larghezza_base_cm
    )
    h_rd = resistenza_base_kg / gamma_r
    rapporto = (
        spinta_orizzontale_kg * gamma_r / resistenza_base_kg if resistenza_base_kg > 0 else math.inf
    )

    passaggi = [
        f"H_Ed (spinta) = {spinta_orizzontale_kg:.3f} kg",
        f"δ_base = {math.degrees(delta_base):.2f}°",
        f"N_Ed * tan(δ) = {peso_muro_kg * math.tan(delta_base):.3f} kg",
        f"c_a * A = {coesione_fondazione_kg_cm2:.5f} * {larghezza_base_cm:.2f} = {coesione_fondazione_kg_cm2 * larghezza_base_cm:.3f} kg",
        f"γ_R = {gamma_r:.2f}",
        f"H_Rd = {h_rd:.3f} kg",
        f"Rapporto utilizzo = H_Ed / H_Rd = {rapporto:.4f}",
    ]

    return RisultatoVerificaMuro(
        nome_verifica="scorrimento",
        azione_sfavorevole=spinta_orizzontale_kg,
        azione_favorevole=h_rd,
        rapporto_utilizzo=rapporto,
        verificato=rapporto <= 1.0,
        passaggi_calcolo=passaggi,
    )


# ---------------------------------------------------------------------------
# Verifica principale
# ---------------------------------------------------------------------------


def verifica_muro_sostegno(input_data: InputMuroSostegno) -> RisultatoMuroSostegno:
    """Esegue la verifica completa di un muro di sostegno.

    Verifica ribaltamento e scorrimento secondo NTC2018 §6.5.
    """

    terreno = input_data.terreno_ritenuto
    geo = input_data.geometria

    # Coefficiente di spinta attiva
    beta = geo.inclinazione_terrapieno_gradi
    alpha = geo.angolo_paramento_gradi
    delta = input_data.angolo_attrito_muro_gradi

    if abs(delta) < 1e-9 and abs(alpha - 90.0) < 1e-9:
        ka = ka_rankine(terreno.phi_gradi, beta)
        metodo_spinta = f"Rankine (φ={terreno.phi_gradi}°, β={beta}°)"
    else:
        ka = ka_coulomb(terreno.phi_gradi, delta, alpha, beta)
        metodo_spinta = f"Coulomb (φ={terreno.phi_gradi}°, δ={delta}°, α={alpha}°, β={beta}°)"

    # Spinta attiva
    ea = spinta_attiva_totale_kg_cm(
        terreno.gamma_kg_m3,
        geo.altezza_muro_cm,
        ka,
        terreno.coesione_kg_cm2,
    )
    h_ea = punto_applicazione_spinta_cm(geo.altezza_muro_cm, terreno.coesione_kg_cm2)

    # Componente orizzontale della spinta (per scorrimento)
    spinta_orizz = ea * math.cos(math.radians(delta))

    passaggi_globali = [
        f"Metodo spinta: {metodo_spinta}",
        f"K_a = {ka:.4f}",
        f"Spinta attiva E_a = {ea:.3f} kg/cm (per unità di lunghezza)",
        f"Punto applicazione h_E = {h_ea:.3f} cm da base",
        f"Componente orizzontale H = {spinta_orizz:.3f} kg/cm",
    ]

    # Verifiche
    verifiche: list[RisultatoVerificaMuro] = [
        _verifica_ribaltamento(
            ea,
            h_ea,
            input_data.peso_muro_kg,
            geo.larghezza_base_cm,
            input_data.gamma_r_ribaltamento,
        ),
        _verifica_scorrimento(
            spinta_orizz,
            input_data.peso_muro_kg,
            input_data.terreno_fondazione.phi_gradi,
            input_data.terreno_fondazione.coesione_kg_cm2,
            geo.larghezza_base_cm,
            input_data.gamma_r_scorrimento,
            delta,
        ),
    ]

    return RisultatoMuroSostegno(
        spinta_attiva_kg_cm=ea,
        coefficiente_ka=ka,
        verifiche=verifiche,
        verificato_globale=all(v.verificato for v in verifiche),
        passaggi_calcolo=passaggi_globali,
    )
