"""Test per il fix Step5: merge deterministico e prefisso step5.

Verifica:
- merge_element_results preserva ok dal base (step3)
- Le metriche step5 hanno prefisso "step5."
- Le metriche base non vengono sovrascritte
"""

from __future__ import annotations

from src.core.pipeline import merge_element_results, run_pipeline
from src.core.results import ElementResult
from src.project.schema import (
    CodeSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectModel,
)

# ---------------------------------------------------------------------------
# merge_element_results
# ---------------------------------------------------------------------------


def test_merge_preserves_base_ok_true():
    """ok=True dal base deve essere preservato indipendentemente da step5.ok."""
    base = ElementResult(element_id="P1", ok=True, metrics={"norm_code": "RD2229"})
    step5 = ElementResult(element_id="P1", ok=False, metrics={"step5.status": "KO"})

    merged = merge_element_results(base, step5)

    assert merged.ok is True, "ok dal base deve essere preservato"


def test_merge_preserves_base_ok_false():
    """ok=False dal base deve essere preservato."""
    base = ElementResult(element_id="P1", ok=False, metrics={"norm_code": "RD2229"})
    step5 = ElementResult(element_id="P1", ok=True, metrics={"step5.status": "OK"})

    merged = merge_element_results(base, step5)

    assert merged.ok is False


def test_merge_step5_none_returns_base():
    """Se step5 è None, deve restituire il base invariato."""
    base = ElementResult(element_id="P1", ok=True, metrics={"norm_code": "X"})
    merged = merge_element_results(base, None)

    assert merged is base


def test_merge_prefixes_step5_metrics():
    """Le metriche step5 devono avere prefisso 'step5.'."""
    base = ElementResult(element_id="P1", ok=True, metrics={"norm_code": "RD2229"})
    step5 = ElementResult(
        element_id="P1",
        ok=True,
        metrics={"norm_code": "RD2229", "num_verifiche_eseguite": 3, "status": "OK"},
    )

    merged = merge_element_results(base, step5)

    # Le metriche step5 devono essere prefissate
    assert "step5.norm_code" in merged.metrics
    assert "step5.num_verifiche_eseguite" in merged.metrics
    assert "step5.status" in merged.metrics


def test_merge_base_metrics_not_overwritten():
    """Le metriche base non devono essere sovrascritte da step5."""
    base = ElementResult(
        element_id="P1",
        ok=True,
        metrics={"norm_code": "BASE_VALUE", "width": 30.0},
    )
    step5 = ElementResult(
        element_id="P1",
        ok=True,
        metrics={"norm_code": "STEP5_VALUE", "extra_metric": 42},
    )

    merged = merge_element_results(base, step5)

    # norm_code base deve essere preservato
    assert merged.metrics["norm_code"] == "BASE_VALUE"
    # step5 metric è prefissata
    assert merged.metrics["step5.norm_code"] == "STEP5_VALUE"


def test_merge_messages_deduplicated():
    """I messaggi step5 non devono essere duplicati se già presenti nel base."""
    msg_shared = "Messaggio condiviso"
    base = ElementResult(element_id="P1", ok=True, messages=[msg_shared, "solo_base"])
    step5 = ElementResult(
        element_id="P1",
        ok=True,
        messages=[msg_shared, "solo_step5"],
    )

    merged = merge_element_results(base, step5)

    # Il messaggio condiviso non deve essere duplicato
    count_shared = merged.messages.count(msg_shared)
    assert count_shared == 1, f"Messaggio duplicato: count={count_shared}"
    assert "solo_base" in merged.messages
    assert "solo_step5" in merged.messages


def test_merge_element_id_preserved():
    """element_id deve essere preservato dal base."""
    base = ElementResult(element_id="P1", ok=True)
    step5 = ElementResult(element_id="P1", ok=True)
    merged = merge_element_results(base, step5)
    assert merged.element_id == "P1"


# ---------------------------------------------------------------------------
# Pipeline: existing_structure + LC gating
# ---------------------------------------------------------------------------


def _project_with_existing(existing: bool, lc: str | None) -> ProjectModel:
    return ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(
            norm_code="RD2229",
            limit_states=["TA"],
            existing_structure=existing,
            lc=lc,
        ),
    )


def test_pipeline_step5_skipped_when_not_existing_structure():
    """Senza existing_structure=True, i template RD2229 devono essere saltati con warning."""
    project = _project_with_existing(existing=False, lc=None)
    results = run_pipeline(project)

    # La pipeline non deve crashare
    assert isinstance(results.ok, bool)
    # Deve esserci un warning sull'existing_structure
    has_warning = any("existing_structure" in w or "struttura esistente" in w.lower() for w in results.warnings)
    # O lo skip viene registrato nella traccia
    has_trace = any("existing_structure" in t or "no_applicable_templates" in t for t in results.trace)
    assert has_warning or has_trace, (
        f"Atteso warning/trace per existing_structure; " f"warnings={results.warnings}, trace={results.trace}"
    )


def test_pipeline_step5_skipped_when_lc_none():
    """Con existing_structure=True ma lc=None, i template devono essere saltati con warning."""
    project = _project_with_existing(existing=True, lc=None)
    results = run_pipeline(project)

    # Deve esserci un warning su lc=None
    has_warning = any("lc" in w.lower() or "livello di conoscenza" in w.lower() or "LC" in w for w in results.warnings)
    has_trace = any("lc_None" in t or "no_applicable_templates" in t for t in results.trace)
    assert has_warning or has_trace, (
        f"Atteso warning/trace per lc=None; " f"warnings={results.warnings}, trace={results.trace}"
    )


def test_pipeline_ok_invariant_without_step5():
    """ok dalla pipeline step3 deve essere preservato anche se step5 non gira."""
    # Progetto con geometria e carichi → step3 ok=True
    project = _project_with_existing(existing=False, lc=None)
    results = run_pipeline(project)

    # ok dipende da step3 (geometria+carichi presenti), non da step5
    assert results.ok is True


def test_pipeline_step5_runs_with_correct_settings():
    """Con existing_structure=True e lc='LC1', step5 deve tentare di girare."""
    project = _project_with_existing(existing=True, lc="LC1")
    results = run_pipeline(project)

    # step5 deve essere nella traccia (anche se produce 0 risultati per altri motivi)
    has_step5 = any("step5" in t for t in results.trace)
    assert has_step5
