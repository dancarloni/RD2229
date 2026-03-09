"""Sezione composta acciaio-cls (FASE I).

Calcola le proprieta' della sezione composta IPE (acciaio) + soletta (cls).

Modello:
    - Trave IPE con caratteristiche standard
    - Soletta in cls (larghezza efficace b_eff, spessore t_s)
    - Coefficiente di omogeneizzazione n = E_a / E_c

Convenzioni:
    y = 0 al lembo inferiore della trave acciaio (per uniformita' con IPE standard)
    Unita': cm, kg/cm², kg, kg·cm.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Dati profili IPE standard (cm, cm⁴, cm³)
# (Fonte: EN 10034, valori da manuale Carpinteri/Casini)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DatiIPE:
    """Proprieta' geometriche profilo IPE."""
    nome: str
    h: float    # altezza totale [cm]
    b: float    # larghezza flangia [cm]
    tf: float   # spessore flangia [cm]
    tw: float   # spessore anima [cm]
    A: float    # area [cm²]
    Iy: float   # inerzia rispetto all'asse baricentrico y [cm⁴]
    Wy: float   # modulo resistente Wy = Iy / (h/2) [cm³]
    iy: float   # raggio di gyrazione [cm]


# Tabella IPE (valori nominali, EN 10034)
IPE_TABLE: dict[str, DatiIPE] = {
    "IPE80":   DatiIPE("IPE80",   8.0,  4.6, 0.59, 0.38,  7.64,   80.1,   20.0,  3.24),
    "IPE100":  DatiIPE("IPE100", 10.0,  5.5, 0.68, 0.41,  10.3,   171.0,  34.2,  4.07),
    "IPE120":  DatiIPE("IPE120", 12.0,  6.4, 0.79, 0.44,  13.2,   317.8,  53.0,  4.90),
    "IPE140":  DatiIPE("IPE140", 14.0,  7.3, 0.89, 0.47,  16.4,   541.2,  77.3,  5.74),
    "IPE160":  DatiIPE("IPE160", 16.0,  8.2, 1.00, 0.50,  20.1,   869.3, 108.7,  6.58),
    "IPE180":  DatiIPE("IPE180", 18.0,  9.1, 1.11, 0.53,  23.9,  1317.0, 146.3,  7.42),
    "IPE200":  DatiIPE("IPE200", 20.0, 10.0, 1.23, 0.56,  28.5,  1943.0, 194.3,  8.26),
    "IPE220":  DatiIPE("IPE220", 22.0, 11.0, 1.36, 0.59,  33.4,  2772.0, 252.0,  9.11),
    "IPE240":  DatiIPE("IPE240", 24.0, 12.0, 1.48, 0.62,  39.1,  3892.0, 324.3,  9.97),
    "IPE270":  DatiIPE("IPE270", 27.0, 13.5, 1.66, 0.66,  45.9,  5790.0, 428.9, 11.23),
    "IPE300":  DatiIPE("IPE300", 30.0, 15.0, 1.81, 0.71,  53.8,  8356.0, 557.1, 12.47),
    "IPE330":  DatiIPE("IPE330", 33.0, 16.0, 1.96, 0.75,  62.6, 11770.0, 713.1, 13.71),
    "IPE360":  DatiIPE("IPE360", 36.0, 17.0, 1.97, 0.80,  72.7, 16270.0, 903.6, 14.95),
    "IPE400":  DatiIPE("IPE400", 40.0, 18.0, 2.13, 0.86,  84.5, 23130.0, 1156.0, 16.55),
    "IPE450":  DatiIPE("IPE450", 45.0, 19.0, 2.31, 0.94,  98.8, 33740.0, 1499.0, 18.48),
    "IPE500":  DatiIPE("IPE500", 50.0, 20.0, 2.60, 1.02, 116.0, 48200.0, 1928.0, 20.43),
    "IPE550":  DatiIPE("IPE550", 55.0, 21.0, 2.72, 1.11, 134.0, 67120.0, 2441.0, 22.37),
    "IPE600":  DatiIPE("IPE600", 60.0, 22.0, 2.80, 1.20, 156.0, 92080.0, 3069.0, 24.29),
}


# ---------------------------------------------------------------------------
# Calcolo sezione composta
# ---------------------------------------------------------------------------

def _base_contract() -> dict[str, Any]:
    return {
        "esito": "OK",
        "norm_references": [],
        "decision_log": [],
        "trace": {"run_id": str(uuid.uuid4())},
    }


def calcola_sezione_composta(
    *,
    ipe: str | DatiIPE,
    b_eff: float,
    t_s: float,
    n: float,
    delta_s: float = 0.0,
) -> dict[str, Any]:
    """Calcola le proprieta' della sezione composta IPE + soletta.

    Convenzione assi: y = 0 al lembo inferiore della trave IPE.
    La soletta si trova sopra la trave.

    Args:
        ipe:     nome profilo IPE (es. "IPE300") o DatiIPE
        b_eff:   larghezza efficace soletta [cm]
        t_s:     spessore soletta [cm]
        n:       rapporto di omogeneizzazione E_a / E_c
        delta_s: traslazione soletta rispetto al lembo superiore trave
                 (positivo = soletta spostata verso l'alto rispetto alla
                 posizione adiacente alla flangia; default 0 = soletta
                 direttamente sulla flangia superiore della trave)

    Returns:
        dict con contratto base + proprieta' sezione composta.
    """
    result = _base_contract()
    log = result["decision_log"]

    # Recupera dati IPE
    if isinstance(ipe, str):
        key = ipe.upper().replace(" ", "")
        if key not in IPE_TABLE:
            result["esito"] = "ERRORE"
            log.append(f"Profilo IPE '{ipe}' non trovato. Disponibili: {sorted(IPE_TABLE.keys())}")
            return result
        dati = IPE_TABLE[key]
    else:
        dati = ipe

    if n <= 0.0:
        result["esito"] = "ERRORE"
        log.append(f"n={n} non valido (deve essere > 0)")
        return result
    if b_eff <= 0.0 or t_s <= 0.0:
        result["esito"] = "ERRORE"
        log.append(f"b_eff={b_eff} o t_s={t_s} non validi")
        return result

    # --- Contributi dei singoli elementi ---
    # Trave IPE (origine: lembo inferiore trave)
    y_G_ipe = dati.h / 2.0          # baricentro trave dal basso
    A_ipe = dati.A
    I_ipe = dati.Iy                  # inerzia baricentrica

    # Soletta (origine: lembo inferiore trave)
    # Il lembo inferiore della soletta e' a dati.h + delta_s
    y_bot_sol = dati.h + delta_s
    y_top_sol = y_bot_sol + t_s
    y_G_sol = y_bot_sol + t_s / 2.0  # baricentro soletta dal basso

    # Contributo soletta ridotto per n
    A_sol_rid = (b_eff * t_s) / n
    I_sol_rid = (b_eff * t_s ** 3) / (12.0 * n)

    log.append(
        f"IPE {dati.nome}: A={A_ipe:.2f} cm², I={I_ipe:.2f} cm⁴, y_G={y_G_ipe:.2f} cm"
    )
    log.append(
        f"Soletta: b_eff={b_eff:.1f} cm, t_s={t_s:.1f} cm, "
        f"y_G_sol={y_G_sol:.2f} cm, A_rid={A_sol_rid:.3f} cm², n={n}"
    )

    # --- Sezione composta ---
    A_comp = A_ipe + A_sol_rid
    y_G_comp = (A_ipe * y_G_ipe + A_sol_rid * y_G_sol) / A_comp

    # Inerzia composta (Steiner)
    I_comp = (
        I_ipe + A_ipe * (y_G_ipe - y_G_comp) ** 2
        + I_sol_rid + A_sol_rid * (y_G_sol - y_G_comp) ** 2
    )

    # Moduli resistenti
    h_tot = y_top_sol          # altezza totale sezione composta (da lembo inf. trave)
    y_inf = y_G_comp           # distanza baricentro → lembo inferiore trave
    y_sup = h_tot - y_G_comp   # distanza baricentro → lembo superiore soletta

    W_inf = I_comp / y_inf if y_inf > 1e-9 else 0.0  # modulo inf (acciaio)
    W_sup = I_comp / y_sup if y_sup > 1e-9 else 0.0  # modulo sup (cls)

    # Modulo acciaio (lembo inferiore IPE)
    W_a_inf = I_comp / y_G_comp if y_G_comp > 1e-9 else 0.0

    # Modulo cls (lembo superiore soletta, in termini di cls → dividi per n)
    W_c_sup = (I_comp / y_sup) / n if y_sup > 1e-9 else 0.0

    log.append(
        f"Composta: A_comp={A_comp:.3f} cm², y_G={y_G_comp:.4f} cm, "
        f"I_comp={I_comp:.2f} cm⁴"
    )

    result.update({
        "A_composta_cm2": round(A_comp, 4),
        "y_G_composta_cm": round(y_G_comp, 6),
        "I_composta_cm4": round(I_comp, 4),
        "W_inferiore_cm3": round(W_inf, 4),
        "W_superiore_cm3": round(W_sup, 4),
        "W_acciaio_inf_cm3": round(W_a_inf, 4),
        "W_cls_sup_cm3": round(W_c_sup, 4),
        "n": n,
        "ipe": dati.nome,
        "h_ipe_cm": dati.h,
        "A_ipe_cm2": dati.A,
        "I_ipe_cm4": dati.Iy,
        "b_eff_cm": b_eff,
        "t_s_cm": t_s,
        "y_G_ipe_cm": round(y_G_ipe, 4),
        "y_G_sol_cm": round(y_G_sol, 4),
        "h_tot_cm": round(h_tot, 4),
    })
    return result


def calcola_tensioni_sle_composita(
    y_G_comp: float,
    I_comp: float,
    M_kgcm: float,
    h_ipe: float,
    t_s: float,
    delta_s: float,
    n: float,
) -> dict[str, Any]:
    """Calcola tensioni SLE nella sezione composta.

    Args:
        y_G_comp: baricentro sezione composta dal lembo inferiore trave [cm]
        I_comp:   inerzia sezione composta [cm⁴]
        M_kgcm:   momento flettente [kg·cm] (>0 se zona sup. compressa)
        h_ipe:    altezza profilo IPE [cm]
        t_s:      spessore soletta [cm]
        delta_s:  traslazione soletta [cm]
        n:        rapporto di omogeneizzazione

    Returns:
        dict con tensioni acciaio inf/sup e cls sup.
    """
    result = _base_contract()
    log = result["decision_log"]

    if I_comp <= 0.0:
        result["esito"] = "ERRORE"
        log.append("I_comp <= 0: impossibile calcolare tensioni SLE composita")
        return result

    y_inf = y_G_comp                              # distanza dal baricentro al lembo inf. trave
    y_top_sol = h_ipe + delta_s + t_s            # altezza totale
    y_sup = y_top_sol - y_G_comp                  # distanza baricentro → lembo sup. soletta

    # Tensione acciaio lembo inferiore (trattiva se M>0)
    sigma_a_inf = M_kgcm * y_inf / I_comp

    # Tensione acciaio lembo superiore trave (compressiva se M>0 e sotto AN)
    y_a_sup_dist = y_G_comp - h_ipe               # negativo se trave sotto baricentro
    sigma_a_sup = M_kgcm * (-y_a_sup_dist) / I_comp

    # Tensione cls lembo superiore soletta (in cls → dividi per n)
    sigma_c_sup = M_kgcm * y_sup / (I_comp * n)

    log.append(
        f"SLE composita: sigma_a_inf={sigma_a_inf:.4f} kg/cm², "
        f"sigma_c_sup={sigma_c_sup:.4f} kg/cm²"
    )

    result.update({
        "sigma_a_inf_kgcm2": round(sigma_a_inf, 4),
        "sigma_a_sup_kgcm2": round(sigma_a_sup, 4),
        "sigma_c_sup_kgcm2": round(sigma_c_sup, 4),
        "M_kgcm": M_kgcm,
        "y_G_comp_cm": y_G_comp,
        "I_comp_cm4": I_comp,
        "n": n,
    })
    return result
