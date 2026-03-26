"""Test Qt minimi per la shell della GUI moderna."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from src.core.user_config import UserConfig
from src.ui.modern.app import _load_qt_widgets
from src.ui.modern.main_window import build_main_window


@pytest.fixture
def main_window(tmp_path: Path, monkeypatch: Any) -> Any:
    monkeypatch.setattr(
        UserConfig, "default_path", classmethod(lambda cls: tmp_path / "config.json")
    )
    qt, _backend = _load_qt_widgets()
    QApplication = qt["QApplication"]
    app = QApplication.instance() or QApplication([])

    window = build_main_window(
        qt=qt,
        default_project=None,
        default_output=None,
        runner=lambda project_path, output_dir: {
            "ok": True,
            "report_md": output_dir or "",
            "report_html": output_dir or "",
        },
    )
    try:
        yield window
    finally:
        window.close()
        app.processEvents()


def test_main_window_exposes_project_tree_and_verify_tabs(main_window: Any) -> None:
    project_tree = main_window.findChild(object, "ProjectNavigationTree")
    verify_tabs = main_window.findChild(object, "VerifyWorkbenchTabs")
    pipeline_catalog = main_window.findChild(object, "PipelineCatalogList")

    assert project_tree is not None
    assert verify_tabs is not None
    assert pipeline_catalog is not None


def test_project_tree_contains_expected_navigation_nodes(main_window: Any) -> None:
    project_tree = main_window.findChild(object, "ProjectNavigationTree")

    labels = [project_tree.topLevelItem(i).text(0) for i in range(project_tree.topLevelItemCount())]

    assert "Progetto" in labels
    assert "Verifiche" in labels
    assert "Report e Tracciabilita" in labels
    assert "Moduli specialistici" in labels


def test_project_tree_displays_compact_state_badges(main_window: Any) -> None:
    project_tree = main_window.findChild(object, "ProjectNavigationTree")
    root_project = project_tree.topLevelItem(0)
    root_verify = project_tree.topLevelItem(1)

    assert root_project.text(1) != ""
    assert any(token in root_project.text(1) for token in ["Attesa", "Pronto", "OK", "KO", "Run"])
    assert root_verify.text(1) != ""


def test_pipeline_detail_panel_shows_fixed_sections(main_window: Any) -> None:
    pipeline_detail = main_window.findChild(object, "PipelineDetailPanel")

    plain = pipeline_detail.toPlainText()
    assert "Prerequisiti e gate" in plain
    assert "Hook codice reale" in plain
    assert "Artefatti prodotti" in plain


def test_tree_click_applies_report_filter(main_window: Any) -> None:
    project_tree = main_window.findChild(object, "ProjectNavigationTree")
    report_filter_label = main_window.findChild(object, "ReportFilterLabel")

    verify_root = project_tree.topLevelItem(1)
    normative_node = verify_root.child(1)
    project_tree.itemClicked.emit(normative_node, 0)

    assert "Normative base" in report_filter_label.text()


def test_tree_family_nodes_exist(main_window: Any) -> None:
    """I nodi Muratura, Fuoco e Vento, Sismica e Pushover devono essere presenti sotto Verifiche."""
    project_tree = main_window.findChild(object, "ProjectNavigationTree")
    verify_root = project_tree.topLevelItem(1)
    family_labels = [verify_root.child(i).text(0) for i in range(verify_root.childCount())]
    assert "Muratura" in family_labels
    assert "Fuoco e Vento" in family_labels
    assert "Sismica e Pushover" in family_labels


def test_pipeline_family_filter_combo_exists(main_window: Any) -> None:
    """Il combo PipelineFamilyFilter deve essere presente con le famiglie corrette."""
    family_filter = main_window.findChild(object, "PipelineFamilyFilter")
    assert family_filter is not None
    items = [family_filter.itemText(i) for i in range(family_filter.count())]
    assert "Tutte le famiglie" in items
    assert "Normative base" in items
    assert "Muratura" in items
    assert "Fuoco e Vento" in items
    assert "Sismica e Pushover" in items


def test_tree_click_muratura_applies_filter(main_window: Any) -> None:
    """Click sul nodo Muratura deve impostare il filtro report 'Muratura'."""
    project_tree = main_window.findChild(object, "ProjectNavigationTree")
    report_filter_label = main_window.findChild(object, "ReportFilterLabel")

    verify_root = project_tree.topLevelItem(1)
    family_labels = [verify_root.child(i).text(0) for i in range(verify_root.childCount())]
    muratura_idx = family_labels.index("Muratura")
    muratura_node = verify_root.child(muratura_idx)
    project_tree.itemClicked.emit(muratura_node, 0)

    assert "Muratura" in report_filter_label.text()


def test_pipeline_runner_has_run_started_signal() -> None:
    """PipelineRunnerWindow deve esporre il segnale run_started per live badge transitions."""
    from src.ui.qt.pipeline_runner import PipelineRunnerWindow

    assert hasattr(PipelineRunnerWindow, "run_started")
    assert hasattr(PipelineRunnerWindow, "run_failed")
