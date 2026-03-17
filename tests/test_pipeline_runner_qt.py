"""Test Qt dedicati per PipelineRunnerWindow (progress/log/mock worker)."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportPrivateUsage=false

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch

pytest.importorskip("pytestqt")

from src.core.results import ElementResult, ResultsModel
from src.project.schema import CodeSettings, ProjectModel
from src.ui.qt.pipeline_runner import PipelineRunnerWindow, PipelineWorker


@pytest.fixture
def runner_widget(qtbot: Any) -> PipelineRunnerWindow:
    project = ProjectModel(code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]))
    service = SimpleNamespace(current_project=project)
    widget = PipelineRunnerWindow(project_service=service)
    qtbot.addWidget(widget)
    return widget


def test_run_transitions_progress_modes(
    runner_widget: PipelineRunnerWindow, monkeypatch: MonkeyPatch
) -> None:
    def fake_start(self: PipelineWorker) -> None:
        self.log.emit("Mock start")
        self.progress.emit(35)
        result = ResultsModel(
            ok=True,
            elements=[ElementResult(element_id="E1", ok=True, metrics={"status": "OK"})],
        )
        self.completed.emit(result)

    monkeypatch.setattr(PipelineWorker, "start", fake_start)

    runner_widget._run()

    assert runner_widget.progress.minimum() == 0
    assert runner_widget.progress.maximum() == 100
    assert runner_widget.progress.value() == 100
    assert runner_widget.btn_run.isEnabled() is True


def test_log_coloring_levels(runner_widget: PipelineRunnerWindow) -> None:
    runner_widget._append_log("Messaggio warning", "warning")
    runner_widget._append_log("Messaggio errore", "error")

    plain = runner_widget.log.toPlainText().upper()
    assert "WARNING" in plain
    assert "ERROR" in plain


def test_render_results_warnings_logged(runner_widget: PipelineRunnerWindow) -> None:
    results = ResultsModel(
        ok=True,
        elements=[ElementResult(element_id="E1", ok=True, metrics={"status": "OK"})],
        warnings=["warning demo"],
    )

    runner_widget._on_completed(results)

    assert runner_widget.tbl.rowCount() == 1
    assert "WARNING" in runner_widget.log.toPlainText().upper()


# ---------------------------------------------------------------------------
# GUI-4.9: test headless con mock worker dedicati — cancel flow e failed signal
# ---------------------------------------------------------------------------


def test_cancel_flow_resets_state(
    runner_widget: PipelineRunnerWindow, monkeypatch: MonkeyPatch
) -> None:
    """Premere Annulla durante l'esecuzione ripristina btn_run e progress.

    Il fake_start non emette completed → simula worker ancora in corso.
    Dopo _cancel(), lo stato UI torna al default anche se il QThread
    non è realmente avviato (isRunning() == False per fake sincrono):
    _cancel() ripristina comunque progress e bottoni.
    """

    def fake_start_hanging(self: PipelineWorker) -> None:
        # Solo un log; niente completed → UI resta "in esecuzione"
        self.log.emit("Inizio simulato — in attesa")

    monkeypatch.setattr(PipelineWorker, "start", fake_start_hanging)
    runner_widget._run()

    # Dopo _run() con fake sincrono: btn_run disabilitato, btn_cancel abilitato
    assert runner_widget.btn_run.isEnabled() is False
    assert runner_widget.btn_cancel.isEnabled() is True

    # Ora si cancella
    runner_widget._cancel()

    assert runner_widget.btn_run.isEnabled() is True
    assert runner_widget.btn_cancel.isEnabled() is False
    assert runner_widget.progress.maximum() == 100
    assert runner_widget.progress.value() == 0


def test_failed_signal_logs_error_and_resets(
    runner_widget: PipelineRunnerWindow, monkeypatch: MonkeyPatch
) -> None:
    """Il segnale `failed` prodotto dal worker logga l'errore e ripristina l'UI.

    Il fake_start emette sincrono failed("errore simulato test"); il handler
    _on_failed deve: loggare ERROR, resettare progress a 0 e riabilitare btn_run.
    """

    def fake_start_error(self: PipelineWorker) -> None:
        self.failed.emit("errore simulato test")

    monkeypatch.setattr(PipelineWorker, "start", fake_start_error)
    runner_widget._run()

    plain = runner_widget.log.toPlainText().upper()
    assert "ERROR" in plain
    assert "ERRORE SIMULATO TEST" in plain
    assert runner_widget.btn_run.isEnabled() is True
    assert runner_widget.btn_cancel.isEnabled() is False
    assert runner_widget.progress.value() == 0


def test_norm_change_updates_limit_states_label(runner_widget: PipelineRunnerWindow) -> None:
    """GUI-5.3: cambio norma aggiorna il label degli stati limite disponibili."""
    runner_widget._on_norm_changed("RD2229")
    assert "TA" in runner_widget.lbl_states.text()

    runner_widget._on_norm_changed("NTC2018")
    label = runner_widget.lbl_states.text().upper()
    assert "SLU" in label
    assert "SLE" in label


def test_filter_by_norm_hides_non_matching_rows(runner_widget: PipelineRunnerWindow) -> None:
    """GUI-5.4: filtro norma mostra solo le righe corrispondenti."""
    results = ResultsModel(
        ok=True,
        elements=[
            ElementResult(
                element_id="E1",
                ok=True,
                metrics={"status": "OK", "norm_code": "RD2229", "utilizzazione": 0.5},
            ),
            ElementResult(
                element_id="E2",
                ok=True,
                metrics={"status": "OK", "norm_code": "NTC2018", "utilizzazione": 0.6},
            ),
        ],
    )
    runner_widget._on_completed(results)

    # Deve popolare il filtro con entrambe le norme
    filter_items = [
        runner_widget.cmb_filter_norm.itemText(i)
        for i in range(runner_widget.cmb_filter_norm.count())
    ]
    assert "Tutte" in filter_items
    assert "RD2229" in filter_items
    assert "NTC2018" in filter_items

    runner_widget._on_filter_norm_changed("RD2229")
    assert runner_widget.tbl.isRowHidden(0) is False
    assert runner_widget.tbl.isRowHidden(1) is True

    runner_widget._on_filter_norm_changed("Tutte")
    assert runner_widget.tbl.isRowHidden(0) is False
    assert runner_widget.tbl.isRowHidden(1) is False
