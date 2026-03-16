"""Pipeline runner window with thread execution and exports (Qt6)."""

from __future__ import annotations

import csv
from pathlib import Path

try:
    from PyQt6.QtCore import QThread, pyqtSignal as Signal
    from PyQt6.QtWidgets import (
        QComboBox,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QSizePolicy,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import QThread, Signal
    from PySide6.QtWidgets import (
        QFileDialog,
        QComboBox,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QSizePolicy,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

from src.core.pipeline import run_pipeline
from src.core.results import ResultsModel, export_results
from src.core_calculus.normative_registry import list_norm_codes


class PipelineWorker(QThread):
    progress = Signal(int)
    log = Signal(str)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self._project = project

    def run(self) -> None:
        try:
            self.progress.emit(5)
            self.log.emit("Inizio esecuzione pipeline...")
            result = run_pipeline(self._project)
            self.progress.emit(100)
            self.log.emit(
                f"Pipeline completata: ok={result.ok}, elementi={len(result.elements)}, "
                f"warnings={len(result.warnings)}"
            )
            self.completed.emit(result)
        except Exception as exc:  # pragma: no cover - GUI runtime protection
            self.failed.emit(str(exc))


class PipelineRunnerWindow(QWidget):
    results_ready = Signal(object)

    def __init__(self, project_service=None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self._worker: PipelineWorker | None = None
        self._results = ResultsModel()

        self.setWindowTitle("RD2229 - Pipeline Runner")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Norma:"))
        self.cmb_norm = QComboBox()
        self.cmb_norm.addItems(list_norm_codes())
        top.addWidget(self.cmb_norm)

        self.btn_run = QPushButton("Esegui")
        self.btn_cancel = QPushButton("Annulla")
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_cancel.setEnabled(False)

        self.btn_run.clicked.connect(self._run)
        self.btn_cancel.clicked.connect(self._cancel)
        self.btn_export_csv.clicked.connect(self._export_csv)
        self.btn_export_json.clicked.connect(self._export_json)

        top.addWidget(self.btn_run)
        top.addWidget(self.btn_cancel)
        top.addWidget(self.btn_export_csv)
        top.addWidget(self.btn_export_json)
        top.addStretch(1)
        root.addLayout(top)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        root.addWidget(self.progress)

        self.tbl = QTableWidget(0, 7, self)
        self.tbl.setHorizontalHeaderLabels(
            ["Elemento", "Norma", "Verifica", "Valore", "Limite", "Utiliz.", "Esito"]
        )
        root.addWidget(self.tbl)

        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        root.addWidget(self.log)

    def _append_log(self, message: str) -> None:
        self.log.append(message)

    def _project(self):
        if self.project_service is not None and hasattr(self.project_service, "current_project"):
            return self.project_service.current_project
        return None

    def _run(self) -> None:
        project = self._project()
        if project is None:
            self._append_log("Nessun progetto disponibile nel ProjectService.")
            return
        project.code_settings.norm_code = self.cmb_norm.currentText()

        self._worker = PipelineWorker(project, self)
        self._worker.progress.connect(self.progress.setValue)
        self._worker.log.connect(self._append_log)
        self._worker.completed.connect(self._on_completed)
        self._worker.failed.connect(self._on_failed)

        self.btn_run.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress.setValue(0)
        self._worker.start()

    def _cancel(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.terminate()  # noqa: S606 - user-triggered cancel in GUI context
            self._append_log("Esecuzione annullata dall'utente.")
        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _on_completed(self, results: ResultsModel) -> None:
        self._results = results
        self._render_results(results)
        self.results_ready.emit(results)
        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _on_failed(self, error: str) -> None:
        self._append_log(f"Errore pipeline: {error}")
        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _render_results(self, results: ResultsModel) -> None:
        self.tbl.setRowCount(0)
        for row, elem in enumerate(results.elements):
            self.tbl.insertRow(row)
            status_text = "OK" if elem.ok else "NON OK"
            util = elem.metrics.get("utilizzazione", elem.metrics.get("utilization", ""))
            self.tbl.setItem(row, 0, QTableWidgetItem(elem.element_id))
            self.tbl.setItem(row, 1, QTableWidgetItem(self.cmb_norm.currentText()))
            self.tbl.setItem(row, 2, QTableWidgetItem(str(elem.metrics.get("status", "-"))))
            self.tbl.setItem(row, 3, QTableWidgetItem(str(elem.metrics.get("M_Ed_kNm", "-"))))
            self.tbl.setItem(row, 4, QTableWidgetItem(str(elem.metrics.get("M_Rd_kNm", "-"))))
            self.tbl.setItem(row, 5, QTableWidgetItem(str(util)))
            self.tbl.setItem(row, 6, QTableWidgetItem(status_text))

        for warning in results.warnings:
            self._append_log(f"WARNING: {warning}")

    def _export_csv(self) -> None:
        if self.tbl.rowCount() == 0:
            self._append_log("Nessun risultato da esportare in CSV.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV risultati",
            str(Path.cwd() / "pipeline_results.csv"),
            "CSV (*.csv)",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            headers = [
                self.tbl.horizontalHeaderItem(c).text() for c in range(self.tbl.columnCount())
            ]
            writer.writerow(headers)
            for r in range(self.tbl.rowCount()):
                writer.writerow(
                    [
                        self.tbl.item(r, c).text() if self.tbl.item(r, c) is not None else ""
                        for c in range(self.tbl.columnCount())
                    ]
                )
        self._append_log(f"CSV esportato: {path}")

    def _export_json(self) -> None:
        if self.tbl.rowCount() == 0:
            self._append_log("Nessun risultato da esportare in JSON.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON risultati",
            str(Path.cwd() / "pipeline_results.json"),
            "JSON (*.json)",
        )
        if not path:
            return
        export_results(self._results, path)
        self._append_log(f"JSON esportato: {path}")


MODULE_SPEC = {
    "key": "pipeline_runner",
    "name": "Pipeline Runner",
    "description": "Avvia la pipeline, mostra barra di progresso e risultati (Qt6)",
}


def create_module(master=None, **context):
    return PipelineRunnerWindow(project_service=context.get("project_service"), parent=master)
