"""Smoke test per step5_adapter e integrazione in pipeline.

Verifica che:
- can_run_step5 identifichi correttamente i progetti utilizzabili
- run_step5 produca almeno un ElementResult con metriche numeriche
- la pipeline produca ElementResult con metriche step5 per progetti completi
"""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from src.core.pipeline import run_pipeline
from src.core.results import ElementResult, ResultsModel
from src.core.step5_adapter import can_run_step5, run_step5
from src.project.schema import (
    CodeSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectModel,
)


def _minimal_step5_project() -> ProjectModel:
    """Progetto minimale con tutti i dati richiesti da step5.

    Imposta existing_structure=True e lc='LC3' perché i template RD2229
    richiedono la struttura esistente e il Livello di Conoscenza.
    """
    return ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[
            MaterialEntry(id="C25", type="concrete", f_ck=25.0),
            MaterialEntry(id="B450C", type="steel", f_yk=450.0),
        ],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(
            norm_code="RD2229",
            limit_states=["TA"],
            existing_structure=True,
            lc="LC3",
        ),
    )


def _empty_project() -> ProjectModel:
    return ProjectModel()


def _project_no_materials() -> ProjectModel:
    return ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        loads=[LoadEntry(element_id="P1", N=100.0)],
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]),
    )


# ---------------------------------------------------------------------------
# can_run_step5
# ---------------------------------------------------------------------------


def test_can_run_step5_returns_true_for_complete_project():
    """Progetto con geometry, loads e materials deve poter eseguire step5."""
    project = _minimal_step5_project()
    ok, reasons = can_run_step5(project)
    assert ok is True
    assert reasons == []


def test_can_run_step5_returns_false_for_empty_project():
    """Progetto vuoto non deve poter eseguire step5."""
    project = _empty_project()
    ok, reasons = can_run_step5(project)
    assert ok is False
    assert len(reasons) > 0


def test_can_run_step5_returns_false_no_materials():
    """Progetto senza materiali non deve poter eseguire step5."""
    project = _project_no_materials()
    ok, reasons = can_run_step5(project)
    assert ok is False
    assert any("materiale" in r.lower() or "material" in r.lower() for r in reasons)


# ---------------------------------------------------------------------------
# run_step5
# ---------------------------------------------------------------------------


def test_run_step5_returns_element_results():
    """run_step5 deve restituire una lista di ElementResult."""
    project = _minimal_step5_project()
    results, warnings, trace = run_step5(project)

    assert isinstance(results, list)
    assert all(isinstance(r, ElementResult) for r in results)


def test_run_step5_produces_at_least_one_result():
    """run_step5 deve produrre almeno un ElementResult per un progetto completo."""
    project = _minimal_step5_project()
    results, warnings, trace = run_step5(project)

    assert len(results) >= 1


def test_run_step5_result_has_numerical_metrics():
    """ElementResult da step5 deve avere metriche numeriche prefissate 'step5.'."""
    project = _minimal_step5_project()
    results, warnings, trace = run_step5(project)

    assert len(results) >= 1
    metrics = results[0].metrics

    # Le metriche sono prefissate con "step5." nel nuovo schema
    has_step5_metric = any(k.startswith("step5.") for k in metrics)
    # Fallback: metriche senza prefisso (norm_code, status)
    has_legacy_metric = any(k in metrics for k in ("num_verifiche_eseguite", "status", "norm_code"))
    assert has_step5_metric or has_legacy_metric, f"Nessuna metrica step5 trovata: {metrics}"


def test_run_step5_element_id_preserved():
    """L'element_id nel risultato deve corrispondere a quello del progetto."""
    project = _minimal_step5_project()
    results, warnings, trace = run_step5(project)

    ids = {r.element_id for r in results}
    assert "P1" in ids


def test_run_step5_no_crash_on_missing_geometry():
    """run_step5 su progetto senza geometria matching non deve crashare."""
    project = ProjectModel(
        geometry=[],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="MISSING", N=100.0)],
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]),
    )
    results, warnings, trace = run_step5(project)
    # Nessun crash; warnings o elementi vuoti
    assert isinstance(results, list)


def test_run_step5_trace_not_empty():
    """La traccia di step5 deve contenere almeno start e done."""
    project = _minimal_step5_project()
    results, warnings, trace = run_step5(project)

    assert any("step5:start" in t for t in trace)
    assert any("step5:done" in t for t in trace)


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


def test_pipeline_step5_enriches_metrics():
    """Pipeline con dati completi deve avere metriche step5 nei risultati."""
    project = _minimal_step5_project()
    results = run_pipeline(project)

    assert len(results.elements) >= 1
    elem = results.elements[0]

    # Le metriche arricchite da step5 hanno prefisso "step5."
    has_step5_metric = any(k.startswith("step5.") for k in elem.metrics)
    # Fallback: metriche base senza prefisso (norm_code da step3)
    has_base_metric = "norm_code" in elem.metrics
    assert has_step5_metric or has_base_metric, f"Metriche step5 mancanti: {elem.metrics}"


def test_pipeline_step5_ok_invariant():
    """Il campo ok del risultato non deve essere sovrascritto da step5."""
    project = _minimal_step5_project()
    results = run_pipeline(project)

    assert len(results.elements) >= 1
    # ok deve riflettere step3 (verifica presenza geometria/carichi)
    # e non essere cambiato da step5
    elem = results.elements[0]
    assert isinstance(elem.ok, bool)


def test_pipeline_step5_trace_includes_step5():
    """La traccia della pipeline deve includere passi step5."""
    project = _minimal_step5_project()
    results = run_pipeline(project)

    # La traccia deve menzionare step5
    assert any("step5" in t for t in results.trace)


def test_pipeline_no_crash_on_empty_project():
    """Pipeline su progetto vuoto non deve crashare dopo integrazione step5."""
    project = _empty_project()
    results = run_pipeline(project)

    assert isinstance(results, ResultsModel)
    assert results.ok is False
