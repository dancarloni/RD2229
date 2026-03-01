from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .contracts import validate_result_contract
from .jsoncode_loader import JsonCodeConfig
from .models import CheckRequest, Combination, Element, LoadCase, TraceRecord, VerificationResult


@dataclass(frozen=True)
class PlaceholderVerificationEngine:
    check_code: str = "MVP_PLACEHOLDER"

    def run(
        self,
        *,
        request: CheckRequest,
        element: Element,
        load_case: LoadCase,
        combination: Combination,
        config: JsonCodeConfig,
    ) -> VerificationResult:
        threshold = self._threshold(config)
        axial = float(load_case.actions.get("N", 0.0))
        factor = float(combination.factors.get(load_case.id, 1.0))
        requested_check = request.check_code.strip() or config.check_code
        active_check = (
            requested_check
            if requested_check in {"MVP_PLACEHOLDER", "MVP_REAL_MIN"}
            else self.check_code
        )

        value, status = self._compute_result(
            check_code=active_check,
            axial=axial,
            factor=factor,
            threshold=threshold,
        )
        refs = self._norm_refs(config)
        provenance_summary = ", ".join(
            f"{key}:{value}" for key, value in sorted(config.provenance.items())
        )
        trace = TraceRecord(
            run_id=uuid4().hex,
            norm_code=config.namespace,
            norm_references=refs,
            method_id=active_check,
            assumptions=[
                f"element_role={element.role}",
                f"axial={axial}",
                f"combination_factor={factor}",
                f"threshold={threshold}",
                f"provenance={provenance_summary or 'default:TODO(NTC/EC/RD)'}",
            ],
            warnings=[] if refs and refs[0] != "TODO:NORM_REF" else ["normative references TODO"],
        )
        result = VerificationResult(
            id=uuid4().hex,
            request_id=request.id,
            project_id=request.project_id,
            status=status,
            value=value,
            trace=trace,
        )
        validate_result_contract(result)
        return result

    @staticmethod
    def _compute_result(
        *,
        check_code: str,
        axial: float,
        factor: float,
        threshold: float,
    ) -> tuple[float, str]:
        demand = abs(axial * factor)
        if check_code == "MVP_REAL_MIN":
            utilization = demand / threshold
            if utilization <= 0.80:
                return utilization, "OK"
            if utilization <= 1.00:
                return utilization, "WARN"
            return utilization, "FAIL"

        status = "OK" if demand <= threshold else "WARN"
        return demand, status

    @staticmethod
    def _threshold(config: JsonCodeConfig) -> float:
        value = config.payload.get("threshold")
        if value is None:
            return 1_000.0
        return float(value)

    @staticmethod
    def _norm_refs(config: JsonCodeConfig) -> list[str]:
        refs = config.payload.get("norm_references")
        if isinstance(refs, list) and refs:
            return [str(item) for item in refs]
        return ["TODO(NTC/EC/RD):NORM_REF"]
