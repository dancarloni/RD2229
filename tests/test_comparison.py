"""Test confronto multi-norma (Q.7)."""

from src.core.results import ResultsModel
from src.report.comparison import build_norms_table


def test_build_norms_table_empty_when_missing_payload():
    result = build_norms_table(ResultsModel())
    assert result == ""


def test_build_norms_table_with_payload():
    results = ResultsModel(
        extra={
            "norm_comparison": {
                "P1": {
                    "NTC2018": {"M_Rd": 100.0, "V_Rd": 50.0, "N_Rd": 200.0, "ok": True},
                    "DM96": {"M_Rd": 85.0, "V_Rd": 42.0, "N_Rd": 180.0, "ok": False, "delta_pct": -15.0},
                }
            }
        }
    )

    table = build_norms_table(results)

    assert "## Confronto multi-norma" in table
    assert "| P1 | NTC2018 |" in table
    assert "Delta -15.0%" in table
