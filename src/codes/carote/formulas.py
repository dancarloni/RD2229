"""10 formulazioni di conversione carota -> resistenza in situ + custom engine.

Ogni formulazione riceve un CoreSample e restituisce un ConversionResult.
Registry FORMULATIONS mappa nome -> funzione.

Formulazioni: BS1881, ACI214, TR11, RILEM1979, MASI2005, FIORE2008,
              NTC2018, EN13791, GIACCHETTI, CUSTOM.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from src.codes.carote.core_sample import ConversionResult, CoreSample, CorrectionFactors

# ---------------------------------------------------------------------------
# Tabelle k_ld per formulazioni a lookup
# ---------------------------------------------------------------------------

_BS1881_KLD: dict[float, float] = {
    2.00: 1.00,
    1.75: 0.97,
    1.50: 0.92,
    1.25: 0.87,
    1.00: 0.80,
}

_TR11_KLD: dict[float, float] = {
    2.00: 1.00,
    1.75: 0.97,
    1.50: 0.92,
    1.25: 0.87,
    1.00: 0.80,
    0.75: 0.70,
}

_RILEM_KLD: dict[float, float] = {
    2.00: 1.00,
    1.50: 0.91,
    1.00: 0.80,
    0.75: 0.75,
}

_NTC2018_KLD: dict[float, float] = {
    2.00: 1.00,
    1.75: 0.98,
    1.50: 0.96,
    1.25: 0.93,
    1.00: 0.87,
}

_EN13791_KLD: dict[float, float] = {
    2.00: 1.00,
    1.75: 0.98,
    1.50: 0.95,
    1.25: 0.90,
    1.00: 0.85,
}


def _interp_table(table: dict[float, float], ld: float) -> float:
    """Interpolazione lineare in tabella k_ld.

    Estrapola costante fuori range.
    """
    keys = sorted(table.keys())
    if ld <= keys[0]:
        return table[keys[0]]
    if ld >= keys[-1]:
        return table[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] <= ld <= keys[i + 1]:
            x0, x1 = keys[i], keys[i + 1]
            y0, y1 = table[x0], table[x1]
            return y0 + (y1 - y0) * (ld - x0) / (x1 - x0)
    return 1.0  # pragma: no cover


# ---------------------------------------------------------------------------
# Fattori comuni (non k_ld)
# ---------------------------------------------------------------------------

def _k_dir(sample: CoreSample) -> float:
    """Fattore direzione estrazione."""
    return 1.06 if sample.direction == "orizzontale" else 1.0


def _k_arm(sample: CoreSample) -> float:
    """Fattore presenza armatura (BS 1881 / NTC2018 indicazione)."""
    if not sample.has_rebar:
        return 1.0
    ratio = sample.rebar_diameter_mm / sample.diameter_mm
    return 1.0 + 0.5 * ratio  # correzione approssimata


def _k_um(sample: CoreSample) -> float:
    """Fattore umidita'."""
    if sample.moisture == "saturo":
        return 1.0  # riferimento: cilindro saturo
    if sample.moisture == "asciutto":
        return 0.92  # asciutto in forno: resistenza apparente piu' alta, si riduce
    return 0.96  # naturale (intermedio)


def _k_diam(sample: CoreSample) -> float:
    """Normalizzazione a diametro standard 150 mm."""
    d = sample.diameter_mm
    if abs(d - 150.0) < 1.0:
        return 1.0
    if abs(d - 100.0) < 1.0:
        return 1.06  # carota piccola: resistenza apparente piu' alta
    if abs(d - 75.0) < 1.0:
        return 1.10
    # interpolazione lineare 75-150
    return max(0.95, min(1.15, 1.0 + (150.0 - d) * 0.001))


def _k_dd(sample: CoreSample) -> float:
    """Fattore danno da estrazione."""
    return 1.06 if sample.drilling_damage == "severo" else 1.00


def _build_factors(
    sample: CoreSample,
    k_ld: float,
    overrides: dict[str, float] | None = None,
) -> CorrectionFactors:
    """Costruisce CorrectionFactors con fattori standard + overrides."""
    return CorrectionFactors(
        k_ld=k_ld,
        k_dir=_k_dir(sample),
        k_arm=_k_arm(sample),
        k_um=_k_um(sample),
        k_diam=_k_diam(sample),
        k_dd=_k_dd(sample),
        overrides=overrides or {},
    )


def _make_result(
    sample: CoreSample,
    formulation: str,
    factors: CorrectionFactors,
    passaggi: list[str],
) -> ConversionResult:
    """Crea ConversionResult da sample + factors."""
    k = factors.k_total
    f_is = sample.f_core_mpa * k
    passaggi.append(f"f_is = f_core * k_total = {sample.f_core_mpa:.2f} * {k:.4f} = {f_is:.3f} MPa")
    return ConversionResult(
        sample_id=sample.sample_id,
        formulation=formulation,
        f_core_mpa=sample.f_core_mpa,
        correction_factors=factors,
        k_total=k,
        f_is_mpa=f_is,
        passaggi_calcolo=passaggi,
    )


# ---------------------------------------------------------------------------
# 10 formulazioni
# ---------------------------------------------------------------------------

def converti_bs1881(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """BS 1881:Part 120 — tabella k_ld."""
    k_ld = _interp_table(_BS1881_KLD, sample.ld_ratio)
    passaggi = [
        "Formulazione: BS 1881:Part 120",
        f"L/D = {sample.ld_ratio:.2f} -> k_ld = {k_ld:.4f} (tabella)",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "BS1881", factors, passaggi)


def converti_aci214(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """ACI 214.4R-10 — formula k = 2/(1.04 + 0.04*L/D) per L/D < 1.75."""
    ld = sample.ld_ratio
    if ld >= 1.75:
        k_ld = 1.0
        formula = f"L/D = {ld:.2f} >= 1.75 -> k_ld = 1.00"
    else:
        k_ld = 2.0 / (1.04 + 0.04 * ld)
        formula = f"k_ld = 2/(1.04+0.04*{ld:.2f}) = {k_ld:.4f}"
    passaggi = ["Formulazione: ACI 214.4R-10", formula]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "ACI214", factors, passaggi)


def converti_tr11(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """Concrete Society Technical Report 11 — tabella k_ld."""
    k_ld = _interp_table(_TR11_KLD, sample.ld_ratio)
    passaggi = [
        "Formulazione: Concrete Society TR11",
        f"L/D = {sample.ld_ratio:.2f} -> k_ld = {k_ld:.4f} (tabella)",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "TR11", factors, passaggi)


def converti_rilem1979(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """RILEM NDT 2 (1979) — tabella k_ld."""
    k_ld = _interp_table(_RILEM_KLD, sample.ld_ratio)
    passaggi = [
        "Formulazione: RILEM NDT 2 (1979)",
        f"L/D = {sample.ld_ratio:.2f} -> k_ld = {k_ld:.4f} (tabella)",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "RILEM1979", factors, passaggi)


def converti_masi2005(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """Masi A. (2005) — regressione lineare k_ld = 0.667 + 0.167*L/D."""
    ld = sample.ld_ratio
    k_ld = 0.667 + 0.167 * ld
    passaggi = [
        "Formulazione: Masi A. (2005)",
        f"k_ld = 0.667 + 0.167*{ld:.2f} = {k_ld:.4f}",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "MASI2005", factors, passaggi)


def converti_fiore2008(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """Fiore et al. (2008) — modello regressione per cls storico.

    k_ld = 0.634 + 0.183*L/D (valido per calcestruzzi storici italiani).
    """
    ld = sample.ld_ratio
    k_ld = 0.634 + 0.183 * ld
    passaggi = [
        "Formulazione: Fiore et al. (2008)",
        f"k_ld = 0.634 + 0.183*{ld:.2f} = {k_ld:.4f}",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "FIORE2008", factors, passaggi)


def converti_ntc2018(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """NTC2018 + Circolare n.7/2019 §C8.5.3 — tabella k_ld."""
    k_ld = _interp_table(_NTC2018_KLD, sample.ld_ratio)
    passaggi = [
        "Formulazione: NTC2018 + Circ.7/2019 §C8.5.3",
        f"L/D = {sample.ld_ratio:.2f} -> k_ld = {k_ld:.4f} (tabella)",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "NTC2018", factors, passaggi)


def converti_en13791(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """EN 13791:2019 — tabella k_ld da annesso."""
    k_ld = _interp_table(_EN13791_KLD, sample.ld_ratio)
    passaggi = [
        "Formulazione: EN 13791:2019",
        f"L/D = {sample.ld_ratio:.2f} -> k_ld = {k_ld:.4f} (tabella)",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "EN13791", factors, passaggi)


def converti_giacchetti(
    sample: CoreSample, overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """Giacchetti R. et al. — regressione pratica italiana.

    k_ld = 0.650 + 0.175*L/D (calibrata su campagne italiane).
    """
    ld = sample.ld_ratio
    k_ld = 0.650 + 0.175 * ld
    passaggi = [
        "Formulazione: Giacchetti R. et al.",
        f"k_ld = 0.650 + 0.175*{ld:.2f} = {k_ld:.4f}",
    ]
    factors = _build_factors(sample, k_ld, overrides)
    return _make_result(sample, "GIACCHETTI", factors, passaggi)


def converti_custom(
    sample: CoreSample,
    mode: str = "moltiplicatore",
    multiplier: float = 1.0,
    template_params: dict[str, float] | None = None,
    expression: str = "",
    overrides: dict[str, float] | None = None,
) -> ConversionResult:
    """Formula custom utente — 3 livelli.

    mode="moltiplicatore": f_is = f_core * multiplier
    mode="parametrica": f_is = f_core * (a + b*L/D) con a,b da template_params
    mode="espressione": eval sandboxed di expression Python
    """
    passaggi = [f"Formulazione: CUSTOM (mode={mode})"]

    if mode == "moltiplicatore":
        k_ld = multiplier
        passaggi.append(f"k_ld = multiplier = {multiplier:.4f}")
        factors = _build_factors(sample, k_ld, overrides)
        return _make_result(sample, "CUSTOM", factors, passaggi)

    if mode == "parametrica":
        params = template_params or {}
        a = params.get("a", 0.667)
        b = params.get("b", 0.167)
        ld = sample.ld_ratio
        k_ld = a + b * ld
        passaggi.append(f"k_ld = {a} + {b}*{ld:.2f} = {k_ld:.4f}")
        factors = _build_factors(sample, k_ld, overrides)
        return _make_result(sample, "CUSTOM", factors, passaggi)

    if mode == "espressione":
        factors = _build_factors(sample, 1.0, overrides)
        namespace: dict[str, Any] = {
            "math": math,
            "f_core": sample.f_core_mpa,
            "LD": sample.ld_ratio,
            "D": sample.diameter_mm,
            "L": sample.length_mm,
            "k_ld": factors.k_ld,
            "k_dir": factors.k_dir,
            "k_arm": factors.k_arm,
            "k_um": factors.k_um,
            "k_diam": factors.k_diam,
            "k_dd": factors.k_dd,
        }
        # Sandboxed eval: nessun builtin
        try:
            f_is = float(eval(expression, {"__builtins__": {}}, namespace))  # noqa: S307
        except Exception as exc:
            raise ValueError(
                f"Errore nell'espressione custom '{expression}': {exc}"
            ) from exc
        passaggi.append(f"espressione: {expression}")
        passaggi.append(f"f_is = {f_is:.3f} MPa")
        return ConversionResult(
            sample_id=sample.sample_id,
            formulation="CUSTOM",
            f_core_mpa=sample.f_core_mpa,
            correction_factors=factors,
            k_total=f_is / sample.f_core_mpa if sample.f_core_mpa > 0 else 0.0,
            f_is_mpa=f_is,
            passaggi_calcolo=passaggi,
        )

    raise ValueError(f"mode custom non valido: '{mode}'. Validi: moltiplicatore, parametrica, espressione")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

FORMULATIONS: dict[str, Callable[..., ConversionResult]] = {
    "BS1881": converti_bs1881,
    "ACI214": converti_aci214,
    "TR11": converti_tr11,
    "RILEM1979": converti_rilem1979,
    "MASI2005": converti_masi2005,
    "FIORE2008": converti_fiore2008,
    "NTC2018": converti_ntc2018,
    "EN13791": converti_en13791,
    "GIACCHETTI": converti_giacchetti,
    "CUSTOM": converti_custom,
}

STANDARD_FORMULATIONS = [k for k in FORMULATIONS if k != "CUSTOM"]


def converti_tutti(
    sample: CoreSample,
    overrides_per_formula: dict[str, dict[str, float]] | None = None,
) -> dict[str, ConversionResult]:
    """Applica tutte le formulazioni standard a una carota.

    Non include CUSTOM (richiede configurazione esplicita).

    Args:
        sample: carota da convertire
        overrides_per_formula: overrides specifici per formulazione

    Returns:
        dict formula_name -> ConversionResult
    """
    overrides_map = overrides_per_formula or {}
    results: dict[str, ConversionResult] = {}
    for name in STANDARD_FORMULATIONS:
        fn = FORMULATIONS[name]
        results[name] = fn(sample, overrides=overrides_map.get(name))
    return results
