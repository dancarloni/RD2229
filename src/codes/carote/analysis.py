"""Pipeline principale: list[CoreSample] -> CoreAnalysisResult.

Orchestratore che applica formulazioni, statistiche e parametri derivati.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.codes.carote.core_sample import ConversionResult, CoreSample
from src.codes.carote.derived_params import DerivedConcreteParams, calcola_parametri_derivati
from src.codes.carote.formulas import STANDARD_FORMULATIONS, converti_custom, converti_tutti
from src.codes.carote.statistics import FullStatisticalAnalysis, analisi_statistica_completa


@dataclass
class CoreAnalysisResult:
    """Risultato completo dell'analisi carote.

    Attributi:
        samples: lista carote analizzate
        conversions: formula -> lista ConversionResult (una per carota)
        statistics: formula -> FullStatisticalAnalysis
        derived: formula -> DerivedConcreteParams
        best_estimate: DerivedConcreteParams basato su NTC2018 LC2 (default)
        passaggi_calcolo: traccia pipeline
        timestamp: data/ora analisi
    """

    samples: list[CoreSample]
    conversions: dict[str, list[ConversionResult]]
    statistics: dict[str, FullStatisticalAnalysis]
    derived: dict[str, DerivedConcreteParams]
    best_estimate: DerivedConcreteParams | None
    passaggi_calcolo: list[str] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serializza per export JSON."""
        result: dict[str, Any] = {
            "timestamp": self.timestamp,
            "n_samples": len(self.samples),
            "formulations": {},
        }
        for formula, conv_list in self.conversions.items():
            stats = self.statistics.get(formula)
            derived = self.derived.get(formula)
            result["formulations"][formula] = {
                "conversions": [c.to_dict() for c in conv_list],
                "statistics": {
                    "mean": round(stats.summary.mean, 3) if stats else None,
                    "std": round(stats.summary.std, 3) if stats else None,
                    "cov": round(stats.summary.cov, 4) if stats else None,
                    "f_ck_is_ntc2018_lc2": (
                        round(stats.ntc2018["LC2"].f_ck_is, 3) if stats else None
                    ),
                    "classification": stats.classification if stats else None,
                },
                "derived": derived.to_dict() if derived else None,
            }
        if self.best_estimate:
            result["best_estimate"] = self.best_estimate.to_dict()
        result["passaggi_calcolo"] = self.passaggi_calcolo
        return result


def analizza_carote(
    samples: list[CoreSample],
    formulations: list[str] | None = None,
    lc: str = "LC2",
    custom_config: dict[str, Any] | None = None,
    overrides: dict[str, dict[str, float]] | None = None,
) -> CoreAnalysisResult:
    """Pipeline principale analisi carote.

    Args:
        samples: lista carote
        formulations: sottinsieme formulazioni (default: tutte standard)
        lc: livello di conoscenza per best_estimate (default LC2)
        custom_config: configurazione formula custom (mode, multiplier, ecc.)
        overrides: overrides per formulazione {formula: {k_name: value}}

    Returns:
        CoreAnalysisResult completo
    """
    if not samples:
        return CoreAnalysisResult(
            samples=[],
            conversions={},
            statistics={},
            derived={},
            best_estimate=None,
            passaggi_calcolo=["Nessuna carota fornita"],
            timestamp=datetime.now(tz=UTC).isoformat(),
        )

    passaggi: list[str] = [f"Analisi di {len(samples)} carote"]
    overrides_map = overrides or {}

    # Determina formulazioni da applicare
    formula_list = formulations or list(STANDARD_FORMULATIONS)
    passaggi.append(f"Formulazioni: {', '.join(formula_list)}")

    # Conversione per ogni carota e formulazione
    conversions: dict[str, list[ConversionResult]] = {}
    for sample in samples:
        all_conv = converti_tutti(sample, overrides_per_formula=overrides_map)
        for fname, conv in all_conv.items():
            if fname in formula_list:
                conversions.setdefault(fname, []).append(conv)

    # Custom se configurato
    if custom_config and "CUSTOM" in formula_list:
        custom_results = []
        for sample in samples:
            cr = converti_custom(sample, **custom_config)
            custom_results.append(cr)
        conversions["CUSTOM"] = custom_results

    # Statistiche e parametri derivati per ogni formulazione
    statistics: dict[str, FullStatisticalAnalysis] = {}
    derived: dict[str, DerivedConcreteParams] = {}

    for fname, conv_list in conversions.items():
        f_is_values = [c.f_is_mpa for c in conv_list]
        stats = analisi_statistica_completa(f_is_values)
        statistics[fname] = stats

        # Parametri derivati da f_ck,is NTC2018 del LC richiesto
        f_ck_is = stats.ntc2018[lc].f_ck_is
        if f_ck_is > 0:
            derived[fname] = calcola_parametri_derivati(f_ck_is, stats.classification)
        passaggi.append(f"{fname}: f_ck,is({lc}) = {f_ck_is:.3f} MPa -> {stats.classification}")

    # Best estimate: NTC2018 formulazione
    best = None
    if "NTC2018" in derived:
        best = derived["NTC2018"]
    elif derived:
        best = next(iter(derived.values()))

    return CoreAnalysisResult(
        samples=samples,
        conversions=conversions,
        statistics=statistics,
        derived=derived,
        best_estimate=best,
        passaggi_calcolo=passaggi,
        timestamp=datetime.now(tz=UTC).isoformat(),
    )
