import pytest

from src.rd2229.mvp.contracts import validate_result_contract, validate_trace_record
from src.rd2229.mvp.models import TraceRecord, VerificationResult


def test_trace_record_requires_run_id_and_norm_refs():
    with pytest.raises(ValueError):
        validate_trace_record(
            TraceRecord(
                run_id="",
                norm_code="NTC2018",
                norm_references=["TODO:REF"],
                method_id="MVP_PLACEHOLDER",
            )
        )

    with pytest.raises(ValueError):
        validate_trace_record(
            TraceRecord(
                run_id="r1",
                norm_code="NTC2018",
                norm_references=[],
                method_id="MVP_PLACEHOLDER",
            )
        )


def test_result_contract_accepts_valid_result():
    trace = TraceRecord(
        run_id="r1",
        norm_code="NTC2018",
        norm_references=["TODO:REF"],
        method_id="MVP_PLACEHOLDER",
    )
    result = VerificationResult(
        id="res1",
        request_id="req1",
        project_id="p1",
        status="OK",
        value=123.0,
        trace=trace,
    )

    validate_result_contract(result)
