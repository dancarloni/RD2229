from src.rd2229.mvp.pipeline import run_mvp_demo
from src.rd2229.mvp.repositories import VerificationResultRepository
from src.rd2229.mvp.sqlite_store import SQLiteStore


def test_mvp_results_have_trace_run_id_and_norm_references(tmp_path):
    db_path = tmp_path / "trace.db"
    config_path = tmp_path / "mvp.jsoncode"
    config_path.write_text(
        (
            "{\n"
            '  "id": "MVP_PLACEHOLDER",\n'
            '  "version": "1.0.0",\n'
            '  "namespace": "NTC2018",\n'
            '  "payload": {\n'
            '    "check_code": "MVP_REAL_MIN",\n'
            '    "threshold": 2000.0,\n'
            '    "provenance": {"threshold": "project_profile"},\n'
            '    "norm_references": ["TODO(NTC/EC/RD):REF"]\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    summary = run_mvp_demo(str(db_path), str(config_path))
    assert summary["status"] in {"OK", "WARN", "FAIL"}

    store = SQLiteStore(str(db_path))
    with store.connect() as conn:
        repo = VerificationResultRepository(conn)
        results = repo.list_by_project(summary["project_id"])

    assert len(results) == 1
    trace = results[0].trace
    assert trace.run_id.strip() != ""
    assert len(trace.norm_references) > 0
    assert trace.method_id == "MVP_REAL_MIN"
    assert any("provenance=" in item for item in trace.assumptions)
