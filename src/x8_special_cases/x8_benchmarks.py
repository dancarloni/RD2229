"""Casi benchmark preliminari X8 per test e documentazione."""

from __future__ import annotations

from .x8_models import SpecialCaseInput, SpecialCaseType


def benchmark_cases() -> list[SpecialCaseInput]:
    """Restituisce 6 casi benchmark (2 per tipologia)."""
    return [
        SpecialCaseInput(
            case_type=SpecialCaseType.PREDALLES,
            norm_code="EN13747",
            span_m=5.5,
            gk_kg_m2=250,
            qk_kg_m2=200,
            height_cm=25,
            notes="Predalles multi-campata - caso base",
        ),
        SpecialCaseInput(
            case_type=SpecialCaseType.PREDALLES,
            norm_code="EN13747",
            span_m=6.2,
            gk_kg_m2=320,
            qk_kg_m2=300,
            height_cm=28,
            notes="Predalles carico elevato",
        ),
        SpecialCaseInput(
            case_type=SpecialCaseType.COLLABORANTE,
            norm_code="EN1994",
            span_m=7.2,
            gk_kg_m2=280,
            qk_kg_m2=350,
            advanced_inputs={"n_equiv": 6.0},
            notes="Collaborante uffici - n standard",
        ),
        SpecialCaseInput(
            case_type=SpecialCaseType.COLLABORANTE,
            norm_code="EN1994",
            span_m=8.0,
            gk_kg_m2=300,
            qk_kg_m2=450,
            advanced_inputs={"n_equiv": 8.0},
            notes="Collaborante luce maggiore",
        ),
        SpecialCaseInput(
            case_type=SpecialCaseType.CLT,
            norm_code="EN1995",
            span_m=5.0,
            gk_kg_m2=160,
            qk_kg_m2=200,
            advanced_inputs={"E0_mean": 110000.0, "k_ortho": 0.35},
            notes="CLT residenziale",
        ),
        SpecialCaseInput(
            case_type=SpecialCaseType.CLT,
            norm_code="EN1995",
            span_m=6.5,
            gk_kg_m2=210,
            qk_kg_m2=300,
            advanced_inputs={"E0_mean": 120000.0, "k_ortho": 0.30},
            notes="CLT uffici",
        ),
    ]
