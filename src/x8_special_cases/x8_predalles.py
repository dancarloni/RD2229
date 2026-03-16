"""Valutazione preliminare X8 - Predalles (EN 13747)."""

from __future__ import annotations

from .x8_models import SpecialCaseInput, SpecialCaseResult
from .x8_warnings import X8WarningCode, make_warning


def evaluate_predalles(
    data: SpecialCaseInput,
    *,
    strict_blocking: bool = True,
) -> SpecialCaseResult:
    """Valuta in modo preliminare un caso Predalles.

    In V1 il caso e fuori perimetro: in modalita strict il calcolo viene bloccato.
    In fallback (strict=False) viene stimata solo una rigidezza equivalente semplificata.
    """
    refs = [
        "EN 13747",
        "NTC2018 §7.2.6",
        "DM 9/1/96 (fallback storico)",
    ]

    base_warning = make_warning(
        X8WarningCode.OUT_OF_V1_SCOPE,
        message="Predalles avanzato fuori perimetro V1: attivare modulo dedicato X8.",
        norm_ref="EN13747",
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
                        "Richiesta modellazione avanzata per fasi costruttive "
                        "(prefabbricato + getto integrativo + connessioni)."
                    ),
                    norm_ref="EN13747",
                ),
            ],
            assumptions=[
                "Nessuna verifica resistente finale in V1.",
                "Il risultato deve essere importato da tool specialistico.",
            ],
            benchmark_values={},
            recommended_actions=[
                "Usare modello FEM staged construction.",
                "Fornire manualmente coefficiente di collaborazione e rigidezza equivalente.",
            ],
            normative_refs=refs,
        )

    q_tot = data.gk_kg_m2 + data.qk_kg_m2
    rigidezza_eq = max(data.height_cm, 1.0) ** 3 / 12.0
    return SpecialCaseResult(
        case_type=data.case_type.value,
        in_scope_v1=False,
        blocked=False,
        warnings=[
            base_warning,
            make_warning(
                X8WarningCode.FALLBACK_SIMPLIFIED,
                message="Applicata stima semplificata isotropa di rigidezza equivalente.",
                norm_ref="DM96",
            ),
        ],
        assumptions=[
            "Comportamento isotropo equivalente.",
            "Assenza scorrimento relativo prefabbricato/getto.",
        ],
        benchmark_values={
            "q_tot_kg_m2": q_tot,
            "rigidezza_eq_cm4": rigidezza_eq,
        },
        recommended_actions=[
            "Confermare risultato con modulo predalles dedicato.",
        ],
        normative_refs=refs,
    )
