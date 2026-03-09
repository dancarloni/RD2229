"""Analisi statistica resistenze in situ da carote.

Metodi implementati:
- NTC2018 Circ.7/2019 §C8.5.3: f_ck,is = f_m*(1 - k*CoV)
- EN 13791:2019 Metodo A (n >= 15): f_ck,is = f_m - k_A*s
- EN 13791:2019 Metodo B (3 <= n <= 14): f_ck,is = f_m - k_B*s  oppure  f_is,lowest + 4
- Grubbs: test outlier a livello alpha
- Chauvenet: test outlier per criterio probabilistico
- Classificazione calcestruzzo (C8/10 ... C90/105)
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Dataclass risultati
# ---------------------------------------------------------------------------


@dataclass
class StatisticalSummary:
    """Statistiche descrittive base."""

    n: int
    mean: float
    std: float
    cov: float
    min_val: float
    max_val: float


@dataclass
class NTC2018Result:
    """Risultato analisi NTC2018 per un livello di conoscenza."""

    lc: str
    k: float          # 1.64 per distribuzione normale
    f_m: float        # media f_is [MPa]
    cov: float        # CoV
    f_ck_is: float    # f_m * (1 - k*CoV) [MPa]
    passaggi: list[str] = field(default_factory=list)


@dataclass
class EN13791Result:
    """Risultato analisi EN 13791."""

    method: str       # "A" o "B"
    f_m: float
    s: float
    k: float
    f_ck_is_1: float  # f_m - k*s
    f_ck_is_2: float  # f_is,lowest + 4  (solo metodo B)
    f_ck_is: float    # min dei due
    passaggi: list[str] = field(default_factory=list)


@dataclass
class OutlierResult:
    """Risultato test outlier per un singolo valore."""

    value: float
    index: int
    is_outlier: bool
    test_statistic: float
    critical_value: float
    test_name: str


@dataclass
class FullStatisticalAnalysis:
    """Analisi statistica completa per un set di f_is."""

    summary: StatisticalSummary
    ntc2018: dict[str, NTC2018Result]       # LC1, LC2, LC3
    en13791_a: EN13791Result | None          # None se n < 15
    en13791_b: EN13791Result | None          # None se n < 3
    outliers_grubbs: list[OutlierResult]
    outliers_chauvenet: list[OutlierResult]
    classification: str                     # "C20/25" ecc.
    passaggi_calcolo: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Statistiche descrittive
# ---------------------------------------------------------------------------


def calcola_summary(values: Sequence[float]) -> StatisticalSummary:
    """Calcola statistiche descrittive base."""
    n = len(values)
    if n == 0:
        raise ValueError("Nessun valore fornito per l'analisi statistica")
    mean = sum(values) / n
    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std = math.sqrt(variance)
    else:
        std = 0.0
    cov = std / mean if mean > 0 else 0.0
    return StatisticalSummary(
        n=n, mean=mean, std=std, cov=cov,
        min_val=min(values), max_val=max(values),
    )


# ---------------------------------------------------------------------------
# NTC2018 Circ.7/2019 §C8.5.3
# ---------------------------------------------------------------------------


def analisi_ntc2018(values: Sequence[float], lc: str = "LC2") -> NTC2018Result:
    """f_ck,is = f_m * (1 - k * CoV).

    k = 1.64 per distribuzione normale (frattile 5%).
    """
    s = calcola_summary(values)
    k = 1.64
    f_ck_is = s.mean * (1.0 - k * s.cov)
    passaggi = [
        f"NTC2018 Circ.7 §C8.5.3, LC={lc}",
        f"n = {s.n}, f_m = {s.mean:.3f} MPa, s = {s.std:.3f}, CoV = {s.cov:.4f}",
        f"k = {k} (frattile 5%)",
        f"f_ck,is = f_m*(1-k*CoV) = {s.mean:.3f}*(1-{k}*{s.cov:.4f}) = {f_ck_is:.3f} MPa",
    ]
    return NTC2018Result(
        lc=lc, k=k, f_m=s.mean, cov=s.cov,
        f_ck_is=f_ck_is, passaggi=passaggi,
    )


# ---------------------------------------------------------------------------
# EN 13791:2019
# ---------------------------------------------------------------------------

_EN13791_B_K: dict[int, float] = {
    3: 3.37,
    5: 2.27,
    8: 1.90,
    10: 1.73,
    12: 1.62,
    14: 1.55,
}


def _en13791_b_k(n: int) -> float:
    """Coefficiente k per Metodo B (interpolazione lineare tra valori tabulati)."""
    keys = sorted(_EN13791_B_K.keys())
    if n <= keys[0]:
        return _EN13791_B_K[keys[0]]
    if n >= keys[-1]:
        return _EN13791_B_K[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] <= n <= keys[i + 1]:
            n0, n1 = keys[i], keys[i + 1]
            k0, k1 = _EN13791_B_K[n0], _EN13791_B_K[n1]
            return k0 + (k1 - k0) * (n - n0) / (n1 - n0)
    return _EN13791_B_K[keys[-1]]  # pragma: no cover


def analisi_en13791_a(values: Sequence[float]) -> EN13791Result | None:
    """EN 13791 Metodo A — richiede n >= 15.

    f_ck,is = f_m - 1.48*s  (k_A = 1.48)
    """
    s = calcola_summary(values)
    if s.n < 15:
        return None
    k = 1.48
    f_ck_is = s.mean - k * s.std
    passaggi = [
        f"EN 13791:2019 Metodo A (n={s.n} >= 15)",
        f"f_m = {s.mean:.3f}, s = {s.std:.3f}",
        f"f_ck,is = f_m - 1.48*s = {s.mean:.3f} - 1.48*{s.std:.3f} = {f_ck_is:.3f} MPa",
    ]
    return EN13791Result(
        method="A", f_m=s.mean, s=s.std, k=k,
        f_ck_is_1=f_ck_is, f_ck_is_2=0.0,
        f_ck_is=f_ck_is, passaggi=passaggi,
    )


def analisi_en13791_b(values: Sequence[float]) -> EN13791Result | None:
    """EN 13791 Metodo B — 3 <= n <= 14.

    f_ck,is = min(f_m - k*s, f_is,lowest + 4)
    """
    s = calcola_summary(values)
    if s.n < 3:
        return None
    k = _en13791_b_k(s.n)
    f_ck_1 = s.mean - k * s.std
    f_ck_2 = s.min_val + 4.0
    f_ck_is = min(f_ck_1, f_ck_2)
    passaggi = [
        f"EN 13791:2019 Metodo B (n={s.n})",
        f"f_m = {s.mean:.3f}, s = {s.std:.3f}, k(n={s.n}) = {k:.2f}",
        f"Criterio 1: f_m - k*s = {s.mean:.3f} - {k:.2f}*{s.std:.3f} = {f_ck_1:.3f} MPa",
        f"Criterio 2: f_is,lowest + 4 = {s.min_val:.3f} + 4 = {f_ck_2:.3f} MPa",
        f"f_ck,is = min({f_ck_1:.3f}, {f_ck_2:.3f}) = {f_ck_is:.3f} MPa",
    ]
    return EN13791Result(
        method="B", f_m=s.mean, s=s.std, k=k,
        f_ck_is_1=f_ck_1, f_ck_is_2=f_ck_2,
        f_ck_is=f_ck_is, passaggi=passaggi,
    )


# ---------------------------------------------------------------------------
# Outlier detection
# ---------------------------------------------------------------------------


def test_grubbs(values: Sequence[float], alpha: float = 0.05) -> list[OutlierResult]:
    """Test di Grubbs per outlier (two-sided).

    G = max|x_i - mean| / s
    Critical value da distribuzione t di Student.
    """
    from scipy.stats import t as t_dist

    vals = list(values)
    n = len(vals)
    if n < 3:
        return []

    mean = sum(vals) / n
    std = math.sqrt(sum((x - mean) ** 2 for x in vals) / (n - 1))
    if std < 1e-12:
        return [
            OutlierResult(v, i, False, 0.0, 0.0, "Grubbs")
            for i, v in enumerate(vals)
        ]

    # Valore critico Grubbs (two-sided)
    t_crit = t_dist.ppf(1.0 - alpha / (2.0 * n), n - 2)
    g_crit = ((n - 1) / math.sqrt(n)) * math.sqrt(t_crit**2 / (n - 2 + t_crit**2))

    results = []
    for i, v in enumerate(vals):
        g = abs(v - mean) / std
        results.append(OutlierResult(
            value=v, index=i, is_outlier=(g > g_crit),
            test_statistic=g, critical_value=g_crit, test_name="Grubbs",
        ))
    return results


def test_chauvenet(values: Sequence[float]) -> list[OutlierResult]:
    """Criterio di Chauvenet per outlier.

    Un valore e' outlier se la probabilita' di osservarlo e' < 1/(2*n).
    """
    from scipy.stats import norm

    vals = list(values)
    n = len(vals)
    if n < 3:
        return []

    mean = sum(vals) / n
    std = math.sqrt(sum((x - mean) ** 2 for x in vals) / (n - 1))
    if std < 1e-12:
        return [
            OutlierResult(v, i, False, 0.0, 0.0, "Chauvenet")
            for i, v in enumerate(vals)
        ]

    threshold = 1.0 / (2.0 * n)
    results = []
    for i, v in enumerate(vals):
        z = abs(v - mean) / std
        p = 2.0 * (1.0 - norm.cdf(z))  # probabilita' bilaterale
        results.append(OutlierResult(
            value=v, index=i, is_outlier=(p < threshold),
            test_statistic=z, critical_value=norm.ppf(1.0 - threshold / 2.0),
            test_name="Chauvenet",
        ))
    return results


# ---------------------------------------------------------------------------
# Classificazione calcestruzzo
# ---------------------------------------------------------------------------

_CLASSI_CLS: list[tuple[float, str]] = [
    (8, "C8/10"),
    (12, "C12/15"),
    (16, "C16/20"),
    (20, "C20/25"),
    (25, "C25/30"),
    (28, "C28/35"),
    (30, "C30/37"),
    (32, "C32/40"),
    (35, "C35/45"),
    (40, "C40/50"),
    (45, "C45/55"),
    (50, "C50/60"),
    (55, "C55/67"),
    (60, "C60/75"),
    (70, "C70/85"),
    (80, "C80/95"),
    (90, "C90/105"),
]


def classifica_calcestruzzo(f_ck_is: float) -> str:
    """Restituisce la classe di resistenza (es. 'C20/25') corrispondente a f_ck,is."""
    if f_ck_is < _CLASSI_CLS[0][0]:
        return f"< {_CLASSI_CLS[0][1]}"
    for fck, label in reversed(_CLASSI_CLS):
        if f_ck_is >= fck:
            return label
    return f"< {_CLASSI_CLS[0][1]}"  # pragma: no cover


# ---------------------------------------------------------------------------
# Pipeline completa
# ---------------------------------------------------------------------------


def analisi_statistica_completa(values: Sequence[float]) -> FullStatisticalAnalysis:
    """Esegue tutti i metodi statistici contemporaneamente.

    Args:
        values: valori f_is [MPa] da una singola formulazione

    Returns:
        FullStatisticalAnalysis con tutti i risultati
    """
    summary = calcola_summary(values)

    # NTC2018 per tutti i LC
    ntc = {}
    for lc in ("LC1", "LC2", "LC3"):
        ntc[lc] = analisi_ntc2018(values, lc)

    # EN 13791
    en_a = analisi_en13791_a(values)
    en_b = analisi_en13791_b(values)

    # Outlier
    grubbs = test_grubbs(values)
    chauvenet = test_chauvenet(values)

    # f_ck,is di riferimento per classificazione (NTC2018 LC2)
    f_ck_ref = ntc["LC2"].f_ck_is
    classification = classifica_calcestruzzo(f_ck_ref)

    passaggi = [
        f"Analisi statistica completa su {summary.n} valori",
        f"Media = {summary.mean:.3f} MPa, s = {summary.std:.3f}, CoV = {summary.cov:.4f}",
        f"NTC2018 LC2: f_ck,is = {f_ck_ref:.3f} MPa",
    ]
    if en_b is not None:
        passaggi.append(f"EN 13791 B: f_ck,is = {en_b.f_ck_is:.3f} MPa")
    if en_a is not None:
        passaggi.append(f"EN 13791 A: f_ck,is = {en_a.f_ck_is:.3f} MPa")
    passaggi.append(f"Classificazione: {classification}")

    return FullStatisticalAnalysis(
        summary=summary,
        ntc2018=ntc,
        en13791_a=en_a,
        en13791_b=en_b,
        outliers_grubbs=grubbs,
        outliers_chauvenet=chauvenet,
        classification=classification,
        passaggi_calcolo=passaggi,
    )
