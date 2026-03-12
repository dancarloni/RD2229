"""Verifica pressoflessione deviata TA calcestruzzo (FASE J).

Norme coperte: RD2229 (Art. 29), DM92 (§7), DM96 (§3.4).

Due metodi selezionabili:
  1. Sovrapposizione elastica: sigma_c_max = N/A_om + |Mx|*y/I_x + |My|*x/I_y
  2. Bresler TA: |Mx|/M_Rdx + |My|/M_Rdy <= 1 (alpha=1.0 o 4/3 Giangreco)

Sezione lorda se barre vuote, omogenizzata se barre presenti.
Duck-typed per tutti i tipi di sezione via section_fiber.

Unita': cm, kg/cm², kg, kg·cm.
"""

from __future__ import annotations

from typing import Any

from .base import PressoflessResult, PressoflessSpec, calcola_omogenizzata_biassiale

# Riferimenti normativi per norma
_NORM_REFS: dict[str, list[str]] = {
    "RD2229": ["RD 2229/39 Art. 29 — Sovrapposizione elastica N-Mx-My"],
    "DM92": ["DM 1992 §7 — Verifiche a pressoflessione TA"],
    "DM96": ["DM 16/01/1996 §3.4 — Verifiche a pressoflessione TA"],
}


def _get_biax_props(
    spec: PressoflessSpec,
) -> dict[str, Any] | None:
    """Calcola proprieta' omogenizzata biassiale (o lorda se barre vuote)."""
    return calcola_omogenizzata_biassiale(
        spec.section,
        spec.barre,
        spec.n,
    )


def verifica_sovrapposizione_elastica(spec: PressoflessSpec) -> PressoflessResult:
    """Verifica con sovrapposizione elastica: sigma = N/A + Mx*y/Ix + My*x/Iy.

    Args:
        spec: input con sezione, barre, sollecitazioni, sigma_adm

    Returns:
        PressoflessResult con sigma_c_max e utilizzazione.
    """
    props = _get_biax_props(spec)
    if props is None or props.get("esito") != "OK":
        return PressoflessResult(
            esito="ERRORE",
            utilisation=0.0,
            metodo="SOVRAPPOSIZIONE_ELASTICA",
            norma=spec.norma,
            decision_log=props.get("decision_log", []) if props else [],
        )

    A_om = props["A_om_cm2"]
    I_x = props["I_x_om_cm4"]
    I_y = props["I_y_om_cm4"]
    y_G = props["y_G_om_cm"]
    h = props["h_cm"]
    w = props["w_cm"]
    x_G = props.get("x_G_om_cm", 0.0)

    # Distanze massime dai baricentri ai lembi
    y_ext = max(y_G, h - y_G)
    x_ext = max(w / 2.0 + x_G, w / 2.0 - x_G)

    N = spec.N_kg
    Mx = spec.Mx_kgcm
    My = spec.My_kgcm

    # Tensione al bordo piu' compresso
    sigma_N = abs(N) / A_om if A_om > 0 else 0.0
    sigma_Mx = abs(Mx) * y_ext / I_x if I_x > 0 else 0.0
    sigma_My = abs(My) * x_ext / I_y if I_y > 0 else 0.0
    sigma_c_max = sigma_N + sigma_Mx + sigma_My

    sigma_adm = spec.sigma_c_adm_kgcm2
    ok = sigma_c_max <= sigma_adm
    util = sigma_c_max / sigma_adm if sigma_adm > 0 else 999.0

    passaggi = [
        f"Sezione omogenizzata biassiale: A_om={A_om:.2f} cm², "
        f"I_x={I_x:.2f} cm⁴, I_y={I_y:.2f} cm⁴",
        f"N={N:.1f} kg, Mx={Mx:.1f} kg·cm, My={My:.1f} kg·cm",
        f"sigma_N = |N|/A_om = {sigma_N:.2f} kg/cm²",
        f"sigma_Mx = |Mx|*y_ext/I_x = {sigma_Mx:.2f} kg/cm²",
        f"sigma_My = |My|*x_ext/I_y = {sigma_My:.2f} kg/cm²",
        f"sigma_c_max = {sigma_c_max:.2f} kg/cm²",
        f"sigma_c_adm = {sigma_adm:.2f} kg/cm²",
        f"Verifica: {sigma_c_max:.2f} {'<=' if ok else '>'} {sigma_adm:.2f}"
        f" -> {'OK' if ok else 'NON OK'}",
    ]

    return PressoflessResult(
        esito="OK" if ok else "NON_OK",
        utilisation=round(util, 6),
        metodo="SOVRAPPOSIZIONE_ELASTICA",
        norma=spec.norma,
        sigma_c_max_kgcm2=round(sigma_c_max, 4),
        sigma_c_adm_kgcm2=round(sigma_adm, 4),
        norm_references=_NORM_REFS.get(spec.norma, []),
        decision_log=props.get("decision_log", []),
        passaggi_calcolo=passaggi,
        details={
            "A_om_cm2": A_om,
            "I_x_om_cm4": I_x,
            "I_y_om_cm4": I_y,
            "y_ext_cm": y_ext,
            "x_ext_cm": x_ext,
            "sigma_N_kgcm2": round(sigma_N, 4),
            "sigma_Mx_kgcm2": round(sigma_Mx, 4),
            "sigma_My_kgcm2": round(sigma_My, 4),
        },
    )


def calcola_M_Rd_ta(
    A_om: float,
    W_cm3: float,
    N_kg: float,
    sigma_c_adm: float,
) -> float:
    """Momento resistente TA uniassiale per dato N.

    M_Rd = (sigma_c_adm - |N|/A_om) * W
    Se sigma_c_adm - |N|/A_om <= 0 (sezione esaurita da N): M_Rd = 0.

    Args:
        A_om: area omogenizzata [cm²]
        W_cm3: modulo resistente [cm³]
        N_kg: sforzo normale [kg] (positivo = compressione)
        sigma_c_adm: tensione ammissibile [kg/cm²]

    Returns:
        M_Rd [kg·cm], >= 0.
    """
    if A_om <= 0 or W_cm3 <= 0:
        return 0.0
    sigma_residua = sigma_c_adm - abs(N_kg) / A_om
    if sigma_residua <= 0:
        return 0.0
    return sigma_residua * W_cm3


def verifica_bresler_ta(spec: PressoflessSpec) -> PressoflessResult:
    """Verifica con formula di Bresler per metodo TA.

    (|Mx|/M_Rdx)^alpha + (|My|/M_Rdy)^alpha <= 1.0

    alpha = 1.0: conservativo (equivalente a sovrapposizione elastica)
    alpha = 4/3: Giangreco (meno conservativo per sezioni armate)

    Args:
        spec: input con sezione, barre, sollecitazioni, sigma_adm, alpha_bresler

    Returns:
        PressoflessResult con bresler_value e utilizzazione.
    """
    props = _get_biax_props(spec)
    if props is None or props.get("esito") != "OK":
        return PressoflessResult(
            esito="ERRORE",
            utilisation=0.0,
            metodo="BRESLER_TA",
            norma=spec.norma,
            decision_log=props.get("decision_log", []) if props else [],
        )

    A_om = props["A_om_cm2"]
    # Wx = min(Wx_sup, Wx_inf) per sicurezza
    Wx = min(props["Wx_sup_cm3"], props["Wx_inf_cm3"])
    Wy = min(props["Wy_sx_cm3"], props["Wy_dx_cm3"])

    N = spec.N_kg
    Mx = spec.Mx_kgcm
    My = spec.My_kgcm
    sigma_adm = spec.sigma_c_adm_kgcm2
    alpha = spec.alpha_bresler

    M_Rdx = calcola_M_Rd_ta(A_om, Wx, N, sigma_adm)
    M_Rdy = calcola_M_Rd_ta(A_om, Wy, N, sigma_adm)

    # Bresler
    if M_Rdx <= 0 and M_Rdy <= 0:
        bresler = 999.0
    elif M_Rdx <= 0:
        bresler = 999.0 if abs(Mx) > 1e-9 else (abs(My) / M_Rdy) ** alpha
    elif M_Rdy <= 0:
        bresler = 999.0 if abs(My) > 1e-9 else (abs(Mx) / M_Rdx) ** alpha
    else:
        bresler = (abs(Mx) / M_Rdx) ** alpha + (abs(My) / M_Rdy) ** alpha

    ok = bresler <= 1.0
    util = bresler

    passaggi = [
        f"Sezione omogenizzata: A_om={A_om:.2f}, Wx={Wx:.2f}, Wy={Wy:.2f}",
        f"N={N:.1f} kg, Mx={Mx:.1f} kg·cm, My={My:.1f} kg·cm",
        f"M_Rdx = (sigma_adm - |N|/A_om) * Wx = {M_Rdx:.1f} kg·cm",
        f"M_Rdy = (sigma_adm - |N|/A_om) * Wy = {M_Rdy:.1f} kg·cm",
        f"alpha = {alpha:.2f}",
        f"Bresler = (|Mx|/M_Rdx)^alpha + (|My|/M_Rdy)^alpha = {bresler:.4f}",
        f"Verifica: {bresler:.4f} {'<=' if ok else '>'} 1.0" f" -> {'OK' if ok else 'NON OK'}",
    ]

    return PressoflessResult(
        esito="OK" if ok else "NON_OK",
        utilisation=round(util, 6),
        metodo="BRESLER_TA",
        norma=spec.norma,
        bresler_value=round(bresler, 6),
        alpha_bresler=alpha,
        M_Rdx_kgcm=round(M_Rdx, 4),
        M_Rdy_kgcm=round(M_Rdy, 4),
        sigma_c_adm_kgcm2=round(sigma_adm, 4),
        norm_references=_NORM_REFS.get(spec.norma, []),
        decision_log=props.get("decision_log", []),
        passaggi_calcolo=passaggi,
        details={
            "A_om_cm2": A_om,
            "Wx_cm3": Wx,
            "Wy_cm3": Wy,
        },
    )


def verifica_pressofless_ta_cls(spec: PressoflessSpec) -> PressoflessResult:
    """Entry-point TA cls: routing su metodo (SOVRAPPOSIZIONE_ELASTICA o BRESLER_TA)."""
    if spec.metodo == "BRESLER_TA":
        return verifica_bresler_ta(spec)
    return verifica_sovrapposizione_elastica(spec)
