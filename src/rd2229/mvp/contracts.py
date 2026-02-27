from __future__ import annotations

from .models import TraceRecord, VerificationResult


def validate_trace_record(trace: TraceRecord) -> None:
    if not trace.run_id.strip():
        raise ValueError("TraceRecord.run_id must be non-empty")
    if not trace.norm_references:
        raise ValueError("TraceRecord.norm_references must be non-empty")
    if not trace.method_id.strip():
        raise ValueError("TraceRecord.method_id must be non-empty")
    if trace.assumptions is None:
        raise ValueError("TraceRecord.assumptions must be a list")
    if trace.warnings is None:
        raise ValueError("TraceRecord.warnings must be a list")


def validate_result_contract(result: VerificationResult) -> None:
    validate_trace_record(result.trace)
    if result.status not in {"OK", "WARN", "FAIL"}:
        raise ValueError(f"Unsupported result status: {result.status}")
