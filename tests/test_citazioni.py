"""Test utilities citazioni normative (Fase Q.3)."""

from src.core_calculus.contracts import CalcOutput, NormReference, SingleCheckResult
from src.report.citazioni_normative import (
    build_citation_index,
    collect_citations,
    render_appendice,
    render_formula_note,
)


def test_collect_citations_from_calc_output_dataclasses():
    ref_1 = NormReference(norm_code="NTC2018", chapter="4.1", paragraph="4.1.2.1.3")
    ref_2 = NormReference(norm_code="DM96", chapter="3", paragraph="3.4")

    check = SingleCheckResult(template_id="chk-1", ok=True, norm_references=[ref_1, ref_2])
    output = CalcOutput(per_template_results={"chk-1": check})

    citations = collect_citations(output)

    assert citations == ["DM96 \u00a73.4", "NTC2018 \u00a74.1.2.1.3"]


def test_collect_citations_from_dict_structure_deduplicates():
    payload = {
        "checks": {
            "flessione": {
                "norm_references": [
                    {"norm_code": "NTC2018", "paragraph": "4.1.2.1.3"},
                    {"norm_code": "NTC2018", "paragraph": "4.1.2.1.3"},
                    "EC2 §6.2.2",
                ]
            },
            "taglio": {"norm_references": ["DM96 §3.2", "EC2 §6.2.2"]},
        }
    }

    citations = collect_citations(payload)

    assert citations == ["DM96 §3.2", "EC2 §6.2.2", "NTC2018 §4.1.2.1.3"]


def test_build_index_and_formula_note():
    citation_index = build_citation_index(["NTC2018 §4.1.2.1.3", "DM96 §3.2"])

    assert citation_index == {"DM96 §3.2": 1, "NTC2018 §4.1.2.1.3": 2}
    assert render_formula_note("NTC2018 §4.1.2.1.3", citation_index) == "<sup>[2]</sup>"
    assert render_formula_note("EC2 §6.2.2", citation_index) == ""


def test_render_appendice_with_and_without_data():
    appendix = render_appendice(["NTC2018 §4.1.2.1.3", "DM96 §3.2"])
    empty_appendix = render_appendice([])

    assert "## Appendice normativa" in appendix
    assert "1. [DM96 §3.2]" in appendix
    assert "2. [NTC2018 §4.1.2.1.3]" in appendix
    assert "Nessuna citazione normativa rilevata." in empty_appendix
