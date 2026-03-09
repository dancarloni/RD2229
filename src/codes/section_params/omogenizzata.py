"""Sezione omogeneizzata e asse neutro fessurato (FASE I).

Calcola le proprieta' della sezione in c.a. omogeneizzata per:
  - Integra (non fessurata): A_om, y_G_om, I_om
  - Fessurata: asse neutro x_na, inerzia I_fess
  - Tensioni SLE: sigma_c (cls), sigma_s (acciaio)

Supporta tutti i tipi di sezione tramite integrazione a strisce
usando le stesse funzioni duck-typed di section_fiber.py.

Convenzioni:
    y = 0 al lembo compresso superiore, y = h al lembo teso inferiore.
    N [kg]: positiva se compressione (storicamente N > 0 = trazione; qui
            si usa N_comp > 0 per semplificare le formule SLE).
    M [kg·cm]: positivo se zona superiore compressa.
    Unita' geometria: cm; tensioni: kg/cm².
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Tipo barra armatura
# ---------------------------------------------------------------------------

@dataclass
class BarraArmatura:
    """Singolo livello di armatura nella sezione.

    Attributi:
        y: distanza dal lembo compresso [cm]
        A: area totale barre a questo livello [cm²]
        zona: "tesa" | "compressa" (informativo)
        x: posizione orizzontale dal baricentro sezione [cm] (0 = centrata)
    """

    y: float       # distanza dal lembo compresso [cm]
    A: float       # area totale barre [cm²]
    zona: str = "tesa"  # "tesa" | "compressa" (informativo, non usato nel calcolo)
    x: float = 0.0  # posizione orizzontale dal baricentro [cm]


# ---------------------------------------------------------------------------
# Helper interni
# ---------------------------------------------------------------------------

def _width_at(section: Any, y: float) -> float:
    """Larghezza sezione a profondita' y [cm] dal lembo compresso."""
    from src.methods.section_fiber import width_at_depth
    return width_at_depth(section, y)


def _get_height(section: Any) -> float:
    """Altezza totale sezione [cm]."""
    from src.methods.section_fiber import get_section_height
    return get_section_height(section)


def _compute_concrete_props(
    section: Any,
    n_strips: int = 400,
) -> tuple[float, float, float, float]:
    """Calcola A_c, y_G_c, I_c, h_tot tramite integrazione a strisce.

    Returns:
        (A_c [cm²], y_G_c [cm da top], I_c [cm⁴ baricentrico], h_tot [cm])
    """
    h = _get_height(section)
    dy = h / n_strips

    # Primo momento: A_c e Q_c
    A_c = 0.0
    Q_c = 0.0
    for i in range(n_strips):
        y_mid = (i + 0.5) * dy
        b = _width_at(section, y_mid)
        dA = b * dy
        A_c += dA
        Q_c += dA * y_mid

    if A_c <= 0.0:
        return (0.0, h / 2.0, 0.0, h)

    y_G = Q_c / A_c

    # Secondo momento: I_c rispetto al baricentro
    I_c = 0.0
    for i in range(n_strips):
        y_mid = (i + 0.5) * dy
        b = _width_at(section, y_mid)
        dA = b * dy
        I_c += dA * (y_mid - y_G) ** 2

    return (A_c, y_G, I_c, h)


def _base_contract() -> dict[str, Any]:
    return {
        "esito": "OK",
        "norm_references": [],
        "decision_log": [],
        "trace": {"run_id": str(uuid.uuid4())},
    }


# ---------------------------------------------------------------------------
# Sezione omogenizzata integra
# ---------------------------------------------------------------------------

def calcola_sezione_omogenizzata(
    section: Any,
    barre: list[BarraArmatura],
    n: float,
    n_strips: int = 400,
) -> dict[str, Any]:
    """Calcola le proprieta' della sezione omogeneizzata (integra, non fessurata).

    Formule:
        A_om = A_c + (n-1) * sum(A_si)
        y_G_om = [A_c * y_Gc + (n-1) * sum(A_si * y_i)] / A_om
        I_om = I_c + A_c*(y_Gc-y_Gom)^2 + (n-1)*sum(A_si*(y_i-y_Gom)^2)

    Riferimento:
        Santarella, "Il cemento armato" (ed. storiche); NTC2018 §4.1.2.1.4.2.

    Args:
        section:  oggetto sezione (duck-typed su section_type/attributi geom.)
        barre:    lista livelli di armatura
        n:        rapporto di omogeneizzazione
        n_strips: numero strisce per integrazione numerica

    Returns:
        dict con contratto base + proprieta' sez. omogeneizzata.
    """
    result = _base_contract()
    log = result["decision_log"]

    A_c, y_G_c, I_c, h = _compute_concrete_props(section, n_strips)
    log.append(f"Cls: A_c={A_c:.3f} cm², y_G_c={y_G_c:.3f} cm, I_c={I_c:.3f} cm⁴, h={h:.3f} cm")

    sum_As = sum(b.A for b in barre)
    sum_As_y = sum(b.A * b.y for b in barre)

    A_om = A_c + (n - 1.0) * sum_As
    if A_om <= 0.0:
        result["esito"] = "ERRORE"
        log.append("Errore: area sezione omogenizzata nulla")
        return result

    y_G_om = (A_c * y_G_c + (n - 1.0) * sum_As_y) / A_om

    # Inerzia rispetto al baricentro omogenizzato
    I_om = (
        I_c
        + A_c * (y_G_c - y_G_om) ** 2
        + (n - 1.0) * sum(b.A * (b.y - y_G_om) ** 2 for b in barre)
    )

    # Moduli resistenti (distanze dai lembi)
    y_lembo_sup = y_G_om
    y_lembo_inf = h - y_G_om
    W_sup = I_om / y_lembo_sup if y_lembo_sup > 1e-9 else 0.0
    W_inf = I_om / y_lembo_inf if y_lembo_inf > 1e-9 else 0.0

    log.append(
        f"Sez. omogen.: A_om={A_om:.3f} cm², y_G_om={y_G_om:.4f} cm, "
        f"I_om={I_om:.3f} cm⁴, n={n}"
    )

    result.update({
        "A_omogenizzata_cm2": round(A_om, 4),
        "y_G_omogenizzata_cm": round(y_G_om, 6),
        "I_omogenizzata_cm4": round(I_om, 4),
        "W_superiore_cm3": round(W_sup, 4),
        "W_inferiore_cm3": round(W_inf, 4),
        "n": n,
        "A_cls_cm2": round(A_c, 4),
        "y_G_cls_cm": round(y_G_c, 6),
        "I_cls_cm4": round(I_c, 4),
        "h_tot_cm": round(h, 4),
        "barre": [{"y_cm": b.y, "A_cm2": b.A, "zona": b.zona} for b in barre],
    })
    return result


# ---------------------------------------------------------------------------
# Asse neutro fessurato
# ---------------------------------------------------------------------------

def calcola_asse_neutro_fessurato(
    section: Any,
    barre: list[BarraArmatura],
    n: float,
    N_kg: float = 0.0,
    n_strips: int = 400,
    tol: float = 1e-6,
    max_iter: int = 300,
) -> dict[str, Any]:
    """Calcola asse neutro fessurato tramite formula analitica (rettangolare, N=0)
    o iterazione bisect (caso generale).

    La zona tesa del cls e' ignorata; la zona compressa contribuisce integralmente.
    Le armature compresse contribuiscono con (n-1), quelle tese con n.

    Ipotesi: piano di deformazione (Bernoulli); small strains.

    Args:
        section: oggetto sezione
        barre:   lista livelli di armatura
        n:       rapporto di omogeneizzazione
        N_kg:    forza normale [kg] (pos. = compressione; default 0)
        n_strips: strisce integrazione numerica per I_fess
        tol:     tolleranza sull'asse neutro [cm]
        max_iter: iterazioni massime bisect

    Returns:
        dict con y_na_cm, I_fess_cm4, metodo_calcolo.
        Se sezione interamente compressa: esito="SEZIONE_INTERAMENTE_COMPRESSA".
    """
    result = _base_contract()
    log = result["decision_log"]

    h = _get_height(section)
    st = getattr(section, "section_type", "")

    # --- Formula analitica: rettangolare, N=0, singola fila armatura tesa ---
    barre_tese = [b for b in barre if b.y > 0]
    if (
        st == "RECTANGULAR"
        and abs(N_kg) < 1e-9
        and len(barre_tese) == 1
        and len([b for b in barre if b.y > 0 and b.y < h]) == 1
    ):
        b_rect = float(section.width)
        d = barre_tese[0].y
        As = barre_tese[0].A
        # Equazione: (b/2)*x^2 + n*As*x - n*As*d = 0
        a_q = b_rect / 2.0
        b_q = n * As
        c_q = -n * As * d
        discriminant = b_q ** 2 - 4.0 * a_q * c_q
        if discriminant < 0.0:
            result["esito"] = "ERRORE"
            log.append("Discriminante negativo nel calcolo asse neutro analitico")
            return result
        x = (-b_q + math.sqrt(discriminant)) / (2.0 * a_q)
        if x <= 0.0 or x >= h:
            result["esito"] = "ERRORE"
            log.append(f"Asse neutro fuori dalla sezione: x={x:.4f} cm, h={h:.4f} cm")
            return result
        I_fess = b_rect * x ** 3 / 3.0 + n * As * (d - x) ** 2
        log.append(f"Analitico (rettangolare): x_na={x:.6f} cm, I_fess={I_fess:.4f} cm⁴")
        result.update({
            "y_na_cm": round(x, 6),
            "I_fess_cm4": round(I_fess, 4),
            "metodo_calcolo": "ANALITICO_RETTANGOLARE",
            "n": n,
        })
        return result

    # --- Caso generale: bisect sul momento primo rispetto all'asse neutro ---
    # Equazione di compatibilita' (N=0):
    #   S_c(x) + (n-1)*sum_As_comp*(x - y_comp) = n*sum_As_tese*(y_tese - x)
    # Con N != 0:
    #   Ag*ec_mean + arm_forces = N_ext  →  non implementato qui (TODO)
    # Per ora usiamo N=0 generale (iterazione).

    def _static_moment(x_na: float) -> float:
        """Momento primo della sezione trasformata rispetto ad x_na.
        Zero quando x_na e' l'asse neutro.
        """
        # Contributo cls compresso (zona [0, x_na])
        S = 0.0
        strips_c = max(1, int(x_na * n_strips / h))
        if x_na > 0.0:
            dy_c = x_na / strips_c
            for i in range(strips_c):
                y_m = (i + 0.5) * dy_c
                if y_m > x_na:
                    break
                b = _width_at(section, y_m)
                S += b * dy_c * (x_na - y_m)
        # Armature compresse: (n-1)*A*(x_na - y)
        for bar in barre:
            if bar.y < x_na:
                S += (n - 1.0) * bar.A * (x_na - bar.y)
        # Armature tese: -n*A*(y - x_na)
        for bar in barre:
            if bar.y >= x_na:
                S -= n * bar.A * (bar.y - x_na)
        # Aggiunta forza normale: N / sigma_c = N * I / (M * x_na)
        # Per N=0 non serve; aggiungi offset per N != 0 (todo)
        return S

    x_lo = h * 1e-5
    x_hi = h * (1.0 - 1e-5)
    f_lo = _static_moment(x_lo)
    f_hi = _static_moment(x_hi)

    if f_lo * f_hi > 0.0:
        result["esito"] = "SEZIONE_INTERAMENTE_COMPRESSA"
        log.append("Sezione interamente compressa o tensione dominante: usa sez. integra")
        result.update({"y_na_cm": None, "I_fess_cm4": None, "n": n})
        return result

    # Bisect
    for _ in range(max_iter):
        x_mid = (x_lo + x_hi) / 2.0
        f_mid = _static_moment(x_mid)
        if abs(x_hi - x_lo) < tol:
            break
        if f_lo * f_mid <= 0.0:
            x_hi = x_mid
            f_hi = f_mid
        else:
            x_lo = x_mid
            f_lo = f_mid

    x_na = (x_lo + x_hi) / 2.0

    # Calcola I_fess rispetto all'asse neutro trovato
    I_fess = 0.0
    if x_na > 0.0:
        strips_c = max(1, int(x_na * n_strips / h))
        dy_c = x_na / strips_c
        for i in range(strips_c):
            y_m = (i + 0.5) * dy_c
            if y_m > x_na:
                break
            b = _width_at(section, y_m)
            I_fess += b * dy_c * (x_na - y_m) ** 2
    for bar in barre:
        if bar.y < x_na:
            I_fess += (n - 1.0) * bar.A * (x_na - bar.y) ** 2
        else:
            I_fess += n * bar.A * (bar.y - x_na) ** 2

    log.append(f"Iterativo (bisect): x_na={x_na:.6f} cm, I_fess={I_fess:.4f} cm⁴")
    result.update({
        "y_na_cm": round(x_na, 6),
        "I_fess_cm4": round(I_fess, 4),
        "metodo_calcolo": "ITERATIVO_BISECT",
        "n": n,
    })
    return result


# ---------------------------------------------------------------------------
# Tensioni SLE (stato limite di esercizio)
# ---------------------------------------------------------------------------

def calcola_tensioni_sle(
    y_na: float,
    I_fess: float,
    M_kgcm: float,
    barre: list[BarraArmatura],
    n: float,
    N_kg: float = 0.0,
) -> dict[str, Any]:
    """Calcola tensioni SLE nella sezione fessurata.

    Formule:
        sigma_c(y) = M * (y_na - y) / I_fess   (compressiva se y < y_na)
        sigma_s_i  = n * M * (y_i - y_na) / I_fess  (trattiva se y_i > y_na)

    Args:
        y_na:    asse neutro dal lembo compresso [cm]
        I_fess:  inerzia sezione fessurata rispetto all'asse neutro [cm⁴]
        M_kgcm:  momento flettente [kg·cm] (>0 se zona sup. compressa)
        barre:   lista livelli di armatura
        n:       rapporto di omogeneizzazione
        N_kg:    forza normale [kg] (non ancora implementata; ignorata)

    Returns:
        dict con sigma_c_max, barre_sigma.
    """
    result = _base_contract()
    log = result["decision_log"]

    if I_fess is None or I_fess <= 0.0:
        result["esito"] = "ERRORE"
        log.append("I_fess <= 0: impossibile calcolare le tensioni SLE")
        return result

    # Tensione max cls al lembo compresso
    sigma_c_max = M_kgcm * y_na / I_fess

    # Tensioni nelle barre
    barre_sigma: list[dict[str, Any]] = []
    for bar in barre:
        dist = bar.y - y_na  # positiva se teso
        sigma_s = n * M_kgcm * dist / I_fess
        barre_sigma.append({
            "y_cm": bar.y,
            "A_cm2": bar.A,
            "zona": bar.zona,
            "sigma_s_kgcm2": round(sigma_s, 4),
        })

    sigma_s_max = max((abs(b["sigma_s_kgcm2"]) for b in barre_sigma), default=0.0)
    log.append(
        f"SLE: sigma_c_max={sigma_c_max:.4f} kg/cm², "
        f"|sigma_s|_max={sigma_s_max:.4f} kg/cm²"
    )

    result.update({
        "sigma_c_max_kgcm2": round(sigma_c_max, 4),
        "barre_sigma": barre_sigma,
        "M_kgcm": M_kgcm,
        "y_na_cm": y_na,
        "I_fess_cm4": I_fess,
        "n": n,
    })
    return result


# ---------------------------------------------------------------------------
# Pipeline completa: omogenizzata + fessurata + tensioni
# ---------------------------------------------------------------------------

def calcola_parametri_sezione_completi(
    section: Any,
    barre: list[BarraArmatura],
    n: float,
    M_kgcm: float = 0.0,
    N_kg: float = 0.0,
    norma: str = "",
    n_strips: int = 400,
) -> dict[str, Any]:
    """Pipeline completa: integra + fessurata + tensioni SLE.

    Args:
        section: oggetto sezione
        barre:   lista livelli di armatura
        n:       rapporto di omogeneizzazione
        M_kgcm:  momento flettente SLE [kg·cm]
        N_kg:    forza normale SLE [kg]
        norma:   codice norma (informativo, entra in norm_references)
        n_strips: strisce di integrazione

    Returns:
        dict unificato con tutte le proprieta'.
    """
    result = _base_contract()
    if norma:
        result["norm_references"] = [norma]
    log = result["decision_log"]

    # Integra
    res_int = calcola_sezione_omogenizzata(section, barre, n, n_strips)
    if res_int["esito"] != "OK":
        result["esito"] = res_int["esito"]
        result["decision_log"] += res_int["decision_log"]
        return result
    log += res_int["decision_log"]
    result["integra"] = {
        k: v for k, v in res_int.items()
        if k not in ("esito", "norm_references", "decision_log", "trace")
    }

    # Fessurata
    res_fess = calcola_asse_neutro_fessurato(section, barre, n, N_kg, n_strips)
    log += res_fess["decision_log"]
    if res_fess["esito"] == "OK":
        result["fessurata"] = {
            k: v for k, v in res_fess.items()
            if k not in ("esito", "norm_references", "decision_log", "trace")
        }
        # Tensioni SLE se richiesto
        if abs(M_kgcm) > 1e-9 and res_fess.get("y_na_cm") is not None:
            res_sle = calcola_tensioni_sle(
                res_fess["y_na_cm"],
                res_fess["I_fess_cm4"],
                M_kgcm,
                barre,
                n,
                N_kg,
            )
            log += res_sle["decision_log"]
            if res_sle["esito"] == "OK":
                result["tensioni_sle"] = {
                    k: v for k, v in res_sle.items()
                    if k not in ("esito", "norm_references", "decision_log", "trace")
                }
    else:
        result["fessurata"] = {"esito": res_fess["esito"]}

    return result
