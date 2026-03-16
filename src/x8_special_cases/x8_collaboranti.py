"""Valutazione preliminare X8 - Solai collaboranti acciaio-calcestruzzo."""

from __future__ import annotations

from .x8_models import SpecialCaseInput, SpecialCaseResult
from .x8_warnings import X8WarningCode, make_warning


def evaluate_collaborante(
    data: SpecialCaseInput,
    *,
    strict_blocking: bool = True,
) -> SpecialCaseResult:
    """Valuta preliminarmente un solaio collaborante acciaio-calcestruzzo."""
    refs = [
        "EN 1994-1-1",
        "NTC2018 §4.2",
        "EN 1992-1-1 §9.3 (componenti c.a.)",
    ]

    base_warning = make_warning(
        X8WarningCode.OUT_OF_V1_SCOPE,
        message="Solaio collaborante fuori perimetro V1.",
        norm_ref="EN1994",
    )

    if strict_blocking:
        return SpecialCaseResult(
            case_type=data.case_type.value,
            in_scope_v1=False,
            blocked=True,
            warnings=[
                base_warning,
                make_warning(
                    X8WarningCode.ADVANCED_MODEL_REQUIRED,
                    message=(
                        "Richiesta modellazione composita con verifica connettori, "
                        "slip e interazione acciaio-calcestruzzo."
                    ),
                    norm_ref="EN1994",
                ),
            ],
            assumptions=["Calcolo non eseguito in V1."],
            benchmark_values={},
            recommended_actions=[
                "Impostare modulo composito dedicato (connettori + slip).",
                "Importare risultati da software esterno validato.",
            ],
            normative_refs=refs,
        )

    q_tot = data.gk_kg_m2 + data.qk_kg_m2
    coeff_n = float(data.advanced_inputs.get("n_equiv", 6.0))
    e_eq = 2.1e6 / coeff_n
    return SpecialCaseResult(
        case_type=data.case_type.value,
        in_scope_v1=False,
        blocked=False,
        warnings=[
            base_warning,
            make_warning(
                X8WarningCode.FALLBACK_SIMPLIFIED,
                message="Usata sezione equivalente semplificata senza slip.",
                norm_ref="EN1994",
            ),
        ],
        assumptions=[
            "Perfetta aderenza acciaio-calcestruzzo.",
            "Connettori efficaci al 100%.",
        ],
        benchmark_values={
            "q_tot_kg_m2": q_tot,
            "e_eq_kg_cm2": e_eq,
        },
        recommended_actions=[
            "Confermare con modulo EN1994 completo prima di uso progettuale.",
        ],
        normative_refs=refs,
    )
