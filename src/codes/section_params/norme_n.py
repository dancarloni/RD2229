"""Rapporti di omogeneizzazione n per norma (FASE I).

Per ogni normativa, definisce i valori di n (E_s / E_c) da utilizzare
nel calcolo della sezione omogeneizzata.

Unita':
    Moduli elastici in kg/cm² (sistema storico) o MPa (NTC2018, EC2);
    n e' adimensionale.

Riferimenti normativi:
    RD2229    — uso professionale storico; opzioni n = 8, 10, 12, 15
    DM92/DM96 — n = E_s / E_c (automatico); default n = 10
    NTC2008   — NTC2008 §4.1.2.1.4.2 (stessa logica NTC2018)
    NTC2018   — NTC2018 §4.1.2.1.4.2; n ≈ 15 per long-term (quasi-permanente)
    EC2       — EC2 §7.4.3; n = E_s / E_c_eff = E_s / (E_cm / (1 + phi))
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Costanti moduli elastici
# ---------------------------------------------------------------------------

# Acciaio (sistema storico, kg/cm²)
E_ACCIAIO_STORICO_KGCM2: float = 2_100_000.0

# Acciaio (moderno, MPa — NTC2018, EC2)
E_ACCIAIO_MODERNO_MPA: float = 200_000.0

# Cls C25/30 (valore medio, kg/cm²)
E_CLS_C25_KGCM2: float = 310_000.0

# ---------------------------------------------------------------------------
# Valori n per norma
# ---------------------------------------------------------------------------

#: RD2229 — 4 opzioni storiche selezionabili dall'utente
RD2229_N_OPTIONS: list[int] = [8, 10, 12, 15]

#: Default RD2229 (valore piu' conservativo classico)
RD2229_N_DEFAULT: int = 15

#: NTC2018 §4.1.2.1.4.2 — long-term quasi-permanente
NTC2018_N_DEFAULT: int = 15

#: NTC2008 — stessa logica NTC2018
NTC2008_N_DEFAULT: int = 15

#: DM96 / DM92 — nessun valore esplicito; default professionale
DM_N_DEFAULT: int = 10

#: EC2 §7.4.3 — default
EC2_N_DEFAULT: int = 15

# Norme supportate
NORME_SUPPORTATE: frozenset[str] = frozenset({
    "RD2229", "DM92", "DM96", "NTC2008", "NTC2018", "EC2",
})


@dataclass(frozen=True)
class NormaHnParams:
    """Risultato del calcolo di n per una normativa."""

    n: float
    fonte: str
    note: str = ""


def get_n_for_norm(
    norma: str,
    *,
    n_user: float | None = None,
    E_s: float | None = None,
    E_c: float | None = None,
    phi: float | None = None,
) -> NormaHnParams:
    """Restituisce il rapporto di omogeneizzazione n per la norma specificata.

    Args:
        norma:  codice norma (RD2229, DM92, DM96, NTC2008, NTC2018, EC2),
                case-insensitive.
        n_user: valore n scelto dall'utente (ha precedenza su tutto se fornito).
        E_s:    modulo elastico acciaio [stesse unita' di E_c].
        E_c:    modulo elastico cls [stesse unita' di E_s].
        phi:    coefficiente di viscosita' (solo EC2; default 0).

    Returns:
        NormaHnParams con n, fonte normativa, note.

    Raises:
        ValueError: se norma non riconosciuta.
    """
    norma_up = norma.strip().upper()

    if norma_up not in NORME_SUPPORTATE:
        raise ValueError(
            f"Norma '{norma}' non supportata. "
            f"Valori ammessi: {sorted(NORME_SUPPORTATE)}"
        )

    # Valore utente: precedenza assoluta
    if n_user is not None:
        return NormaHnParams(
            n=float(n_user),
            fonte=norma_up,
            note=f"Valore n={n_user} specificato dall'utente",
        )

    # Calcolo automatico se E_s ed E_c forniti
    if E_s is not None and E_c is not None and E_c > 0:
        if norma_up == "EC2" and phi is not None:
            phi_eff = max(0.0, float(phi))
            E_c_eff = E_c / (1.0 + phi_eff)
            n_calc = E_s / E_c_eff if E_c_eff > 0 else float(EC2_N_DEFAULT)
            return NormaHnParams(
                n=round(n_calc, 3),
                fonte="EC2 §7.4.3",
                note=(
                    f"n = E_s/E_c_eff = {E_s:.0f}/{E_c_eff:.0f}; "
                    f"E_c_eff = E_c/(1+phi) = {E_c:.0f}/(1+{phi_eff:.2f})"
                ),
            )
        n_calc = E_s / E_c
        _norma_fonti = {
            "RD2229": "RD2229 — calcolo E_s/E_c",
            "DM92": "DM92 — calcolo automatico E_s/E_c",
            "DM96": "DM96 — calcolo automatico E_s/E_c",
            "NTC2008": "NTC2008 §4.1.2.1.4.2 — calcolo E_s/E_c",
            "NTC2018": "NTC2018 §4.1.2.1.4.2 — calcolo E_s/E_c",
            "EC2": "EC2 §7.4.3 — calcolo E_s/E_c (phi non fornito)",
        }
        return NormaHnParams(
            n=round(n_calc, 3),
            fonte=_norma_fonti.get(norma_up, norma_up),
            note=f"E_s={E_s:.0f}, E_c={E_c:.0f}",
        )

    # Default per norma
    _defaults = {
        "RD2229": (RD2229_N_DEFAULT, "RD2229 — default storico n=15; opzioni: 8/10/12/15"),
        "DM92": (DM_N_DEFAULT, "DM92 — default professionale n=10; fornire E_s/E_c per calcolo preciso"),
        "DM96": (DM_N_DEFAULT, "DM96 — default professionale n=10; fornire E_s/E_c per calcolo preciso"),
        "NTC2008": (NTC2008_N_DEFAULT, "NTC2008 §4.1.2.1.4.2 — n=15 per combinazioni quasi-permanenti"),
        "NTC2018": (NTC2018_N_DEFAULT, "NTC2018 §4.1.2.1.4.2 — n=15 per combinazioni quasi-permanenti"),
        "EC2": (EC2_N_DEFAULT, "EC2 §7.4.3 — default n=15; fornire E_s/E_c/phi per calcolo preciso"),
    }
    n_def, note = _defaults[norma_up]
    return NormaHnParams(n=float(n_def), fonte=norma_up, note=note)
