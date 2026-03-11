"""Calcoli per valutazione del rischio liquefazione (P.5).

Metodo semplificato Seed-Idriss (1971, aggiornamento Youd et al. 2001):
- CSR da accelerazione massima al suolo e tensioni geostatiche
- CRR da N_{1,60} SPT con correzione overburden e scala magnitudine (MSF)
- Fattore di sicurezza FS = CRR * MSF / CSR
- Indice di potenziale liquefazione IL (Iwasaki 1978)

Riferimenti:
  Seed & Idriss (1971), ASCE JSMFD 97(9):1249-1273
  Youd et al. (2001), JGGE 127(10):817-833
  Iwasaki et al. (1978), Proc. 2nd Int. Conf. Microzonation, pp. 885-896
  NTC2018 §7.11
"""

from __future__ import annotations

import math

from .models import (
    ClasseLiquefazione,
    InputLiquefazione,
    RisultatoLiquefazione,
    RisultatoStratoLiquefazione,
    StratoLiquefazione,
)

# ---------------------------------------------------------------------------
# Parametri limite
# ---------------------------------------------------------------------------

_PROFONDITA_MAX_VALUTAZIONE_M = 20.0  # Oltre i 20 m non si valuta (NTC2018 §7.11.3.4)
_N160_LIMITE = 30.0  # N_{1,60} ≥ 30: terreno non liquefacibile


# ---------------------------------------------------------------------------
# Funzioni ausiliarie
# ---------------------------------------------------------------------------


def fattore_riduzione_r_d(profondita_m: float) -> float:
    """Fattore di riduzione delle tensioni r_d(z) (Liao & Whitman 1986).

    r_d = 1.0 - 0.00765*z  per z ≤ 9.15 m
    r_d = 1.174 - 0.0267*z  per 9.15 < z ≤ 23 m
    r_d = 0.744 - 0.008*z   per 23 < z ≤ 30 m (estensione)
    r_d ≥ 0.1 (tronco inferiore)
    """

    z = profondita_m
    if z <= 9.15:
        rd = 1.0 - 0.00765 * z
    elif z <= 23.0:
        rd = 1.174 - 0.0267 * z
    else:
        rd = 0.744 - 0.008 * z
    return max(rd, 0.1)


def calcola_csr(
    sigma_v_kpa: float,
    sigma_v_eff_kpa: float,
    a_max_g: float,
    profondita_m: float,
) -> float:
    """Calcola il Cyclic Stress Ratio (CSR).

    CSR = 0.65 * (σ_v / σ'_v) * (a_max/g) * r_d
    """

    if sigma_v_eff_kpa <= 0:
        raise ValueError("sigma_v_eff_kpa deve essere > 0")

    r_d = fattore_riduzione_r_d(profondita_m)
    return 0.65 * (sigma_v_kpa / sigma_v_eff_kpa) * a_max_g * r_d


def correggi_n160(
    n_spt_grezzo: int,
    sigma_v_eff_kpa: float,
    ce: float = 1.0,
    cf: float = 1.0,
) -> float:
    """Calcola N_{1,60} da N_SPT grezzo.

    Correzione overburden: C_N = min(sqrt(100 / σ'_v), 1.7)  (σ'_v in kPa)
    N_{1,60} = N_spt * C_N * C_E * C_F
    """

    if sigma_v_eff_kpa <= 0:
        raise ValueError("sigma_v_eff_kpa deve essere > 0")

    c_n = min(math.sqrt(100.0 / sigma_v_eff_kpa), 1.7)
    return n_spt_grezzo * c_n * ce * cf


def calcola_crr_7_5(n160: float) -> float:
    """CRR per M=7.5 da N_{1,60} (Youd et al. 2001, eq. 1).

    CRR_7.5 = 1/(34 - N_{1,60}) + N_{1,60}/135 + 50/(10*N_{1,60}+45)^2 - 1/200

    Valido per N_{1,60} < 30 (terreno sabbia pulita).
    Per N_{1,60} ≥ 30: terreno non liquefacibile → CRR elevato (FS >> 1).
    """

    if n160 >= _N160_LIMITE:
        return 2.0  # CRR elevato → non liquefacibile

    n = n160
    return 1.0 / (34.0 - n) + n / 135.0 + 50.0 / (10.0 * n + 45.0) ** 2 - 1.0 / 200.0


def calcola_msf(magnitudo: float) -> float:
    """Fattore di scala magnitudine MSF (Youd et al. 2001).

    MSF = 10^2.24 / M^2.56
    """

    if magnitudo <= 0:
        raise ValueError("magnitudo deve essere > 0")
    return float((10.0**2.24) / (magnitudo**2.56))


# ---------------------------------------------------------------------------
# Indice di potenziale liquefazione (Iwasaki 1978)
# ---------------------------------------------------------------------------


def _funzione_f_fs(fs: float) -> float:
    """F(FS): contributo alla pericolosita' per FS dato.

    F = 1 - FS  per FS < 1
    F = 0       per FS ≥ 1
    """

    return max(1.0 - fs, 0.0)


def _funzione_peso_w(profondita_m: float) -> float:
    """W(z): peso decresce con la profondità.

    W(z) = 10 - 0.5*z  per z ≤ 20 m
    W(z) = 0            per z > 20 m
    """

    if profondita_m > _PROFONDITA_MAX_VALUTAZIONE_M:
        return 0.0
    return max(10.0 - 0.5 * profondita_m, 0.0)


def classifica_liquefazione(indice_il: float) -> ClasseLiquefazione:
    """Classifica il grado di pericolosita' di liquefazione.

    IL < 2  → BASSA
    2 ≤ IL < 15 → MEDIA
    IL ≥ 15 → ALTA
    """

    if indice_il < 2.0:
        return ClasseLiquefazione.BASSA
    if indice_il < 15.0:
        return ClasseLiquefazione.MEDIA
    return ClasseLiquefazione.ALTA


# ---------------------------------------------------------------------------
# Calcolo completo
# ---------------------------------------------------------------------------


def _valuta_strato(
    strato: StratoLiquefazione,
    a_max_g: float,
    magnitudo: float,
    ce: float,
    cf: float,
) -> RisultatoStratoLiquefazione:
    """Valuta il rischio liquefazione per un singolo strato."""

    z = strato.profondita_centro_m
    rd = fattore_riduzione_r_d(z)
    csr = calcola_csr(strato.sigma_v_kpa, strato.sigma_v_eff_kpa, a_max_g, z)
    n160 = correggi_n160(strato.n_spt_grezzo, strato.sigma_v_eff_kpa, ce, cf)
    crr_75 = calcola_crr_7_5(n160)
    msf = calcola_msf(magnitudo)
    crr_m = crr_75 * msf
    fs = crr_m / csr if csr > 0 else math.inf

    f_fs = _funzione_f_fs(fs)
    # W(z): peso per profondita'; F(FS) è già non-negativo per costruzione
    w_z = _funzione_peso_w(z)
    contributo_il = f_fs * w_z * strato.spessore_m

    passaggi = [
        f"z = {z:.2f} m, r_d = {rd:.4f}",
        f"σ_v = {strato.sigma_v_kpa:.2f} kPa, σ'_v = {strato.sigma_v_eff_kpa:.2f} kPa",
        f"CSR = 0.65 * (σ_v/σ'_v) * a_max * r_d = {csr:.4f}",
        f"C_N = min(sqrt(100/σ'_v), 1.7) = {min(math.sqrt(100.0/strato.sigma_v_eff_kpa), 1.7):.4f}",
        f"N_{{1,60}} = {n160:.2f}",
        f"CRR_7.5 = {crr_75:.4f}",
        f"MSF = 10^2.24 / M^2.56 = {msf:.4f}",
        f"CRR_M = CRR_7.5 * MSF = {crr_m:.4f}",
        f"FS = CRR_M / CSR = {fs:.3f}",
        f"F(FS) = {f_fs:.4f}, W(z) = {w_z:.2f}",
        f"Contributo IL = F * W * dz = {contributo_il:.4f}",
    ]

    return RisultatoStratoLiquefazione(
        profondita_m=z,
        n160=n160,
        csr=csr,
        crr_7_5=crr_75,
        msf=msf,
        crr_m=crr_m,
        fs=fs,
        contributo_il=contributo_il,
        passaggi_calcolo=passaggi,
    )


def calcola_liquefazione(input_data: InputLiquefazione) -> RisultatoLiquefazione:
    """Esegue la valutazione completa del rischio di liquefazione."""

    risultati_strati: list[RisultatoStratoLiquefazione] = []
    indice_il = 0.0

    passaggi_globali = [
        f"a_max/g = {input_data.a_max_g:.4f}",
        f"Magnitudo M = {input_data.magnitudo:.1f}",
        f"Numero strati valutati: {len(input_data.strati)}",
    ]

    for strato in input_data.strati:
        if strato.profondita_centro_m > _PROFONDITA_MAX_VALUTAZIONE_M:
            passaggi_globali.append(
                f"Strato a z={strato.profondita_centro_m:.1f} m escluso (oltre {_PROFONDITA_MAX_VALUTAZIONE_M} m)"
            )
            continue

        risultato_strato = _valuta_strato(
            strato,
            input_data.a_max_g,
            input_data.magnitudo,
            input_data.correzione_energia_ce,
            input_data.correzione_fines_cf,
        )
        risultati_strati.append(risultato_strato)
        indice_il += risultato_strato.contributo_il

    classe = classifica_liquefazione(indice_il)
    passaggi_globali += [
        f"Indice IL = Σ F(FS)*W(z)*dz = {indice_il:.4f}",
        f"Classe pericolosita' liquefazione: {classe.value}",
    ]

    return RisultatoLiquefazione(
        strati=risultati_strati,
        indice_il=indice_il,
        classe=classe,
        passaggi_calcolo=passaggi_globali,
    )
