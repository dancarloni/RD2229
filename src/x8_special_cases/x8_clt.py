"""Valutazione preliminare X8 - CLT (Cross-Laminated Timber)."""

from __future__ import annotations

from .x8_models import SpecialCaseInput, SpecialCaseResult
from .x8_warnings import X8WarningCode, make_warning


def evaluate_clt(
    data: SpecialCaseInput,
    *,
    strict_blocking: bool = True,
) -> SpecialCaseResult:
    """Valuta preliminarmente un solaio CLT.

    In strict mode blocca il calcolo per rischio anisotropia/connessioni non modellate.
    """
    refs = [
        "EN 1995-1-1",
        "DM 16/1/96 (fallback storico legno)",
        "NTC2018 §7.2.6 (serviceability)",
    ]

    base_warning = make_warning(
        X8WarningCode.OUT_OF_V1_SCOPE,
        message="Caso CLT fuori perimetro V1.",
        norm_ref="EN1995",
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
                        "Richiesta modellazione ortotropa e verifica connessioni "
                        "tra strati/pannelli."
                    ),
                    norm_ref="EN1995",
                ),
            ],
            assumptions=["Calcolo non eseguito in V1."],
            benchmark_values={},
            recommended_actions=[
                "Definire stratificazione e stiffness matrix ortotropa.",
                "Eseguire verifica vibrazionale dedicata CLT.",
            ],
            normative_refs=refs,
        )

    q_tot = data.gk_kg_m2 + data.qk_kg_m2
    e0_mean = float(data.advanced_inputs.get("E0_mean", 110000.0))
    k_ortho = float(data.advanced_inputs.get("k_ortho", 0.35))
    e_eq = e0_mean * k_ortho
    return SpecialCaseResult(
        case_type=data.case_type.value,
        in_scope_v1=False,
        blocked=False,
        warnings=[
            base_warning,
            make_warning(
                X8WarningCode.FALLBACK_SIMPLIFIED,
                message="Applicato modello isotropo equivalente a rigidezza ridotta.",
                norm_ref="DM16",
            ),
        ],
        assumptions=[
            "Omogeneizzazione isotropa equivalente.",
            "Connessioni pannello-pannello non esplicitamente modellate.",
        ],
        benchmark_values={
            "q_tot_kg_m2": q_tot,
            "e_eq_kg_cm2": e_eq,
        },
        recommended_actions=[
            "Confermare con modulo CLT ortotropo dedicato.",
        ],
        normative_refs=refs,
    )
