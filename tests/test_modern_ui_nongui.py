"""Test per i ViewModel e Services della GUI moderna (non-GUI, no PySide6).

Verifica logica di stato senza richiedere un display.
"""

from __future__ import annotations

import json
import os

import pytest

from src.ui.modern.viewmodels import ProjectViewModel, ResultsViewModel, RunViewModel
from src.ui.modern.services import CalculationService, ProjectIOService
from src.ui.modern.features.registry import FeatureSpec, clear, get_all, register


# ---------------------------------------------------------------------------
# ProjectViewModel
# ---------------------------------------------------------------------------


def test_project_vm_initial_state():
    vm = ProjectViewModel()
    assert vm.dirty is False
    assert vm.path is None
    assert vm.recent_files == []


def test_project_vm_new_project():
    vm = ProjectViewModel()
    vm.mark_dirty()
    assert vm.dirty is True
    vm.new_project()
    assert vm.dirty is False


def test_project_vm_set_project_clears_dirty():
    from src.project.schema import ProjectModel
    vm = ProjectViewModel()
    vm.mark_dirty()
    vm.set_project(ProjectModel())
    assert vm.dirty is False


def test_project_vm_mark_saved_path(tmp_path):
    vm = ProjectViewModel()
    path = str(tmp_path / "proj.json")
    vm.mark_saved(path)
    assert vm.dirty is False
    assert vm.path == path
    assert path in vm.recent_files


def test_project_vm_recent_files_dedup(tmp_path):
    vm = ProjectViewModel()
    p = str(tmp_path / "p.json")
    vm.mark_saved(p)
    vm.mark_saved(p)  # duplicate
    assert vm.recent_files.count(p) == 1


def test_project_vm_recent_files_max():
    vm = ProjectViewModel()
    for i in range(15):
        vm._add_recent(f"/fake/project_{i}.json")
    assert len(vm.recent_files) <= ProjectViewModel.MAX_RECENT


def test_project_vm_on_change_callback():
    vm = ProjectViewModel()
    called = []
    vm.on_change(lambda: called.append(1))
    vm.mark_dirty()
    assert len(called) >= 1


def test_project_vm_save_load_recent(tmp_path):
    settings_path = str(tmp_path / "settings.json")
    vm = ProjectViewModel()

    # Crea file fittizi
    p1 = str(tmp_path / "proj1.json")
    p2 = str(tmp_path / "proj2.json")
    for p in (p1, p2):
        open(p, "w").close()

    vm._recent = [p1, p2]
    vm.save_recent(settings_path)

    vm2 = ProjectViewModel()
    vm2.load_recent(settings_path)
    assert p1 in vm2.recent_files
    assert p2 in vm2.recent_files


def test_project_vm_load_recent_missing_files(tmp_path):
    settings_path = str(tmp_path / "settings.json")
    with open(settings_path, "w") as f:
        json.dump({"recent_files": ["/nonexistent/path.json"]}, f)

    vm = ProjectViewModel()
    vm.load_recent(settings_path)
    # File inesistente deve essere filtrato
    assert "/nonexistent/path.json" not in vm.recent_files


# ---------------------------------------------------------------------------
# RunViewModel
# ---------------------------------------------------------------------------


def test_run_vm_initial_state():
    vm = RunViewModel()
    assert vm.running is False
    assert vm.error is None


def test_run_vm_set_running():
    vm = RunViewModel()
    vm.set_running(True)
    assert vm.running is True
    assert vm.error is None


def test_run_vm_set_done():
    vm = RunViewModel()
    vm.set_running(True)
    vm.set_done("OK")
    assert vm.running is False
    assert vm.status == "OK"


def test_run_vm_set_error():
    vm = RunViewModel()
    vm.set_error("Something broke")
    assert vm.running is False
    assert vm.error == "Something broke"
    assert vm.status == "Errore"


def test_run_vm_on_change():
    vm = RunViewModel()
    called = []
    vm.on_change(lambda: called.append(1))
    vm.set_running(True)
    assert len(called) >= 1


# ---------------------------------------------------------------------------
# ResultsViewModel
# ---------------------------------------------------------------------------


def test_results_vm_initial_state():
    vm = ResultsViewModel()
    assert vm.has_results is False
    assert vm.warnings == []
    assert vm.elements == []


def test_results_vm_set_results():
    from src.core.pipeline import run_pipeline
    from src.project.schema import (
        CodeSettings, GeometryEntry, LoadEntry, MaterialEntry, ProjectModel
    )
    project = ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]),
    )
    results = run_pipeline(project)

    vm = ResultsViewModel()
    vm.set_results(results)

    assert vm.has_results is True
    assert len(vm.elements) >= 1


def test_results_vm_clear():
    from src.core.results import ResultsModel
    vm = ResultsViewModel()
    vm.set_results(ResultsModel())
    vm.clear()
    assert vm.has_results is False


# ---------------------------------------------------------------------------
# Feature Registry
# ---------------------------------------------------------------------------


def test_registry_register_and_get():
    clear()
    spec = FeatureSpec(feature_id="test_feat", label="Test", order=10)
    register(spec)
    all_feats = get_all()
    assert any(f.feature_id == "test_feat" for f in all_feats)
    clear()


def test_registry_dedup():
    clear()
    spec1 = FeatureSpec(feature_id="dup", label="A", order=10)
    spec2 = FeatureSpec(feature_id="dup", label="B", order=20)
    register(spec1)
    register(spec2)
    all_feats = get_all()
    dups = [f for f in all_feats if f.feature_id == "dup"]
    assert len(dups) == 1
    assert dups[0].label == "B"
    clear()


def test_registry_order():
    clear()
    register(FeatureSpec(feature_id="b", label="B", order=20))
    register(FeatureSpec(feature_id="a", label="A", order=10))
    register(FeatureSpec(feature_id="c", label="C", order=30))
    all_feats = get_all()
    ids = [f.feature_id for f in all_feats]
    assert ids == ["a", "b", "c"]
    clear()


# ---------------------------------------------------------------------------
# ProjectIOService (non-GUI)
# ---------------------------------------------------------------------------


def test_project_io_service_new_project():
    svc = ProjectIOService()
    project = svc.new_project()
    from src.project.schema import ProjectModel
    assert isinstance(project, ProjectModel)


def test_project_io_service_save_load(tmp_path):
    svc = ProjectIOService()
    from src.project.schema import ProjectInfo, ProjectModel
    project = ProjectModel(project_info=ProjectInfo(name="IO Test"))

    path = str(tmp_path / "test.json")
    svc.save_project(project, path)
    loaded = svc.open_project(path)
    assert loaded.project_info.name == "IO Test"


# ---------------------------------------------------------------------------
# CalculationService (non-GUI)
# ---------------------------------------------------------------------------


def test_calculation_service_run():
    from src.project.schema import (
        CodeSettings, GeometryEntry, LoadEntry, MaterialEntry, ProjectModel
    )
    svc = CalculationService()
    project = ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229"),
    )
    results = svc.run(project)
    from src.core.results import ResultsModel
    assert isinstance(results, ResultsModel)


def test_calculation_service_export_results(tmp_path):
    from src.project.schema import (
        CodeSettings, GeometryEntry, LoadEntry, MaterialEntry, ProjectModel
    )
    svc = CalculationService()
    project = ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229"),
    )
    results = svc.run(project)
    path = str(tmp_path / "results.json")
    svc.export_results(results, path)
    assert os.path.exists(path)


def test_calculation_service_export_report_html(tmp_path):
    from src.project.schema import (
        CodeSettings, GeometryEntry, LoadEntry, MaterialEntry, ProjectModel
    )
    svc = CalculationService()
    project = ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229"),
    )
    results = svc.run(project)
    path = str(tmp_path / "report.html")
    svc.export_report(project, results, path, fmt="html")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "<html" in content.lower()
