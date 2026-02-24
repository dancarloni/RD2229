"""Features built-in per la GUI moderna RD2229.

Registra automaticamente le schede standard:
    - Project Info (ordine 10)
    - Run (ordine 40)
    - Results (ordine 50)

Importa questo modulo per registrare le schede built-in::

    import src.ui.modern.features.builtin_features  # noqa: F401
"""

from __future__ import annotations

from typing import Any

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
        QSizePolicy,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    _PYSIDE6_AVAILABLE = True
except ImportError:
    _PYSIDE6_AVAILABLE = False

from src.ui.modern.features.registry import FeatureSpec, register


# ---------------------------------------------------------------------------
# Project Info Feature
# ---------------------------------------------------------------------------


class _ProjectInfoWidget(QWidget):  # type: ignore[misc]
    def __init__(
        self, parent: Any, project_vm: Any, run_vm: Any, results_vm: Any
    ) -> None:
        super().__init__(parent)
        self._vm = project_vm
        lay = QVBoxLayout(self)

        form_group = QGroupBox("Informazioni Progetto")
        form = QFormLayout(form_group)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Nome progetto")
        self._name_edit.textChanged.connect(self._on_name_changed)
        form.addRow("Nome:", self._name_edit)

        self._desc_edit = QPlainTextEdit()
        self._desc_edit.setMaximumHeight(80)
        self._desc_edit.setPlaceholderText("Descrizione")
        form.addRow("Descrizione:", self._desc_edit)

        self._author_edit = QLineEdit()
        self._author_edit.setPlaceholderText("Autore")
        form.addRow("Autore:", self._author_edit)

        lay.addWidget(form_group)

        norm_group = QGroupBox("Impostazioni Normativa")
        norm_form = QFormLayout(norm_group)

        self._norm_edit = QLineEdit()
        self._norm_edit.setPlaceholderText("es. RD2229")
        norm_form.addRow("Normativa:", self._norm_edit)

        lay.addWidget(norm_group)
        lay.addStretch()

        # Carica valori iniziali
        self._refresh()
        project_vm.on_change(self._refresh)

    def _refresh(self) -> None:
        project = self._vm.project
        pi = project.project_info
        self._name_edit.blockSignals(True)
        self._name_edit.setText(pi.name)
        self._name_edit.blockSignals(False)
        self._author_edit.setText(pi.author)
        self._desc_edit.setPlainText(pi.description)
        self._norm_edit.setText(project.code_settings.norm_code)

    def _on_name_changed(self, text: str) -> None:
        self._vm.project.project_info.name = text
        self._vm.mark_dirty()


class ProjectInfoFeature(FeatureSpec):
    feature_id = "project_info"
    label = "Progetto"
    icon = "📁"
    order = 10

    def create_widget(
        self, parent: Any, project_vm: Any, run_vm: Any, results_vm: Any
    ) -> Any:
        if not _PYSIDE6_AVAILABLE:
            return None
        return _ProjectInfoWidget(parent, project_vm, run_vm, results_vm)


# ---------------------------------------------------------------------------
# Run Feature
# ---------------------------------------------------------------------------


class _RunWidget(QWidget):  # type: ignore[misc]
    def __init__(
        self, parent: Any, project_vm: Any, run_vm: Any, results_vm: Any
    ) -> None:
        super().__init__(parent)
        self._project_vm = project_vm
        self._run_vm = run_vm
        self._results_vm = results_vm

        lay = QVBoxLayout(self)

        self._run_btn = QPushButton("▶️  Esegui Calcolo  (F5)")
        self._run_btn.setMinimumHeight(48)
        self._run_btn.clicked.connect(self._on_run)
        lay.addWidget(self._run_btn)

        self._status_label = QLabel("Pronto")
        lay.addWidget(self._status_label)

        lay.addStretch()

        run_vm.on_change(self._refresh)

    def _refresh(self) -> None:
        self._run_btn.setEnabled(not self._run_vm.running)
        self._status_label.setText(self._run_vm.status)
        if self._run_vm.error:
            self._status_label.setText(f"❌ {self._run_vm.error}")

    def _on_run(self) -> None:
        # Delega al main window tramite menu / shortcut F5
        # Per ora lancia direttamente dalla service
        from src.ui.modern.services import CalculationService
        calc = CalculationService()
        self._run_vm.set_running(True)
        try:
            results = calc.run(self._project_vm.project)
            self._results_vm.set_results(results)
            n_ok = sum(1 for e in results.elements if e.ok)
            n_tot = len(results.elements)
            self._run_vm.set_done(f"Completato: {n_ok}/{n_tot} OK")
        except Exception as exc:
            self._run_vm.set_error(str(exc))


class RunFeature(FeatureSpec):
    feature_id = "run"
    label = "Esegui"
    icon = "▶️"
    order = 40

    def create_widget(
        self, parent: Any, project_vm: Any, run_vm: Any, results_vm: Any
    ) -> Any:
        if not _PYSIDE6_AVAILABLE:
            return None
        return _RunWidget(parent, project_vm, run_vm, results_vm)


# ---------------------------------------------------------------------------
# Results Feature
# ---------------------------------------------------------------------------


class _ResultsWidget(QWidget):  # type: ignore[misc]
    def __init__(
        self, parent: Any, project_vm: Any, run_vm: Any, results_vm: Any
    ) -> None:
        super().__init__(parent)
        self._results_vm = results_vm
        self._project_vm = project_vm

        lay = QVBoxLayout(self)

        self._status_label = QLabel("Nessun risultato disponibile.")
        lay.addWidget(self._status_label)

        # Tabella elementi
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Elemento", "Esito", "Metriche"])
        self._table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self._table)

        # Warnings
        self._warnings_label = QLabel("⚠️ Avvisi:")
        lay.addWidget(self._warnings_label)
        self._warnings_edit = QPlainTextEdit()
        self._warnings_edit.setReadOnly(True)
        self._warnings_edit.setMaximumHeight(120)
        lay.addWidget(self._warnings_edit)

        results_vm.on_change(self._refresh)

    def _refresh(self) -> None:
        if not self._results_vm.has_results:
            self._status_label.setText("Nessun risultato disponibile.")
            self._table.setRowCount(0)
            self._warnings_edit.clear()
            return

        results = self._results_vm.results
        esito = "✅ OK" if results.ok else "❌ NON OK"
        self._status_label.setText(f"Esito globale: {esito}")

        # Popola tabella
        elements = self._results_vm.elements
        self._table.setRowCount(len(elements))
        for row, elem in enumerate(elements):
            self._table.setItem(row, 0, QTableWidgetItem(elem.element_id))
            ok_text = "✅ OK" if elem.ok else "❌ NON OK"
            self._table.setItem(row, 1, QTableWidgetItem(ok_text))
            metrics_text = "; ".join(
                f"{k}={v}" for k, v in list(elem.metrics.items())[:4]
            )
            self._table.setItem(row, 2, QTableWidgetItem(metrics_text))

        # Warnings
        self._warnings_edit.setPlainText("\n".join(self._results_vm.warnings))


class ResultsFeature(FeatureSpec):
    feature_id = "results"
    label = "Risultati"
    icon = "📊"
    order = 50

    def create_widget(
        self, parent: Any, project_vm: Any, run_vm: Any, results_vm: Any
    ) -> Any:
        if not _PYSIDE6_AVAILABLE:
            return None
        return _ResultsWidget(parent, project_vm, run_vm, results_vm)


# ---------------------------------------------------------------------------
# Auto-register built-in features
# ---------------------------------------------------------------------------

def register_builtin_features() -> None:
    """Registra tutte le schede built-in nel registry globale."""
    register(ProjectInfoFeature())
    register(RunFeature())
    register(ResultsFeature())
