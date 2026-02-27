"""QMainWindow principale della GUI moderna RD2229 (PySide6).

Implementa il layout base MVVM:
    - Menu bar: File (New/Open/Save/Save-As/Recent/Exit), Run, Help
    - Barra di stato: dirty flag, percorso file, status pipeline
    - NavigationPanel: sidebar + stacked widget con le schede (features)

Aggiungere una nuova scheda::

    from src.ui.modern.features import FeatureSpec, register

    class MyFeature(FeatureSpec):
        feature_id = "my_feature"
        label = "📐 La Mia Scheda"
        order = 50

        def create_widget(self, parent, project_vm, run_vm, results_vm):
            return MyWidget(parent)

    register(MyFeature())
"""

from __future__ import annotations

import os
from typing import Any

try:
    from PySide6.QtCore import Qt, QThreadPool
    from PySide6.QtWidgets import (
        QFileDialog,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QProgressBar,
        QPushButton,
        QSizePolicy,
        QStatusBar,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    _PYSIDE6_AVAILABLE = True
except ImportError:
    _PYSIDE6_AVAILABLE = False


if not _PYSIDE6_AVAILABLE:

    class ModernMainWindow:  # type: ignore[no-redef]
        def __init__(self, *a: Any, **kw: Any) -> None:
            pass

else:
    from src.ui.modern.features.registry import get_all
    from src.ui.modern.navigation import NavigationPanel
    from src.ui.modern.services import CalculationService, ProjectIOService
    from src.ui.modern.viewmodels import ProjectViewModel, ResultsViewModel, RunViewModel
    from src.ui.modern.workers import PipelineWorker

    APP_TITLE = "RD2229 – Verifiche Strutturali"
    RECENT_SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".rd2229", "recent_files.json")

    class ModernMainWindow(QMainWindow):  # type: ignore[no-redef]
        """Finestra principale della GUI moderna RD2229."""

        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle(APP_TITLE)
            self.resize(1100, 700)

            # Services
            self._io = ProjectIOService()
            self._calc = CalculationService()

            # ViewModels
            self._project_vm = ProjectViewModel()
            self._run_vm = RunViewModel()
            self._results_vm = ResultsViewModel()

            # Carica recent files
            self._project_vm.load_recent(RECENT_SETTINGS_PATH)

            # Build UI
            self._build_menu()
            self._build_status_bar()
            self._build_central()

            # Connect ViewModel events
            self._project_vm.on_change(self._refresh_title)
            self._project_vm.on_change(self._refresh_recent_menu)
            self._run_vm.on_change(self._refresh_status)
            self._results_vm.on_change(self._refresh_status)

            self._refresh_title()

        # ------------------------------------------------------------------
        # Build UI
        # ------------------------------------------------------------------

        def _build_menu(self) -> None:
            mb = self.menuBar()

            # File menu
            file_menu = mb.addMenu("&File")

            new_a = file_menu.addAction("&Nuovo progetto")
            new_a.setShortcut("Ctrl+N")
            new_a.triggered.connect(self._on_new)

            open_a = file_menu.addAction("&Apri progetto…")
            open_a.setShortcut("Ctrl+O")
            open_a.triggered.connect(self._on_open)

            file_menu.addSeparator()

            save_a = file_menu.addAction("&Salva")
            save_a.setShortcut("Ctrl+S")
            save_a.triggered.connect(self._on_save)

            save_as_a = file_menu.addAction("Salva &come…")
            save_as_a.setShortcut("Ctrl+Shift+S")
            save_as_a.triggered.connect(self._on_save_as)

            file_menu.addSeparator()

            self._recent_menu = file_menu.addMenu("Recenti")
            self._refresh_recent_menu()

            file_menu.addSeparator()

            exit_a = file_menu.addAction("&Esci")
            exit_a.setShortcut("Ctrl+Q")
            exit_a.triggered.connect(self.close)

            # Run menu
            run_menu = mb.addMenu("&Esegui")
            run_a = run_menu.addAction("▶️ &Esegui calcolo")
            run_a.setShortcut("F5")
            run_a.triggered.connect(self._on_run)

            # Export menu
            export_menu = mb.addMenu("E&sport")
            export_json_a = export_menu.addAction("Esporta risultati JSON…")
            export_json_a.triggered.connect(self._on_export_json)
            export_html_a = export_menu.addAction("Esporta report HTML…")
            export_html_a.triggered.connect(lambda: self._on_export_report("html"))
            export_md_a = export_menu.addAction("Esporta report Markdown…")
            export_md_a.triggered.connect(lambda: self._on_export_report("md"))

        def _build_status_bar(self) -> None:
            sb = QStatusBar()
            self.setStatusBar(sb)
            self._status_label = QLabel("Pronto")
            sb.addPermanentWidget(self._status_label)

        def _build_central(self) -> None:
            """Costruisce il pannello centrale con navigation + features."""
            self._nav = NavigationPanel(self)

            # Aggiungi le feature registrate
            features = get_all()
            if features:
                for spec in features:
                    if not spec.enabled:
                        continue
                    try:
                        widget = spec.create_widget(
                            self._nav,
                            self._project_vm,
                            self._run_vm,
                            self._results_vm,
                        )
                    except Exception:
                        widget = _make_placeholder(self._nav, spec.label, spec.tooltip)
                    self._nav.add_feature(spec.feature_id, f"{spec.icon} {spec.label}", widget)
            else:
                # Nessuna feature registrata: mostra placeholder
                placeholder = _make_placeholder(
                    self._nav, "Nessuna scheda registrata", "Aggiungi features tramite src.ui.modern.features.register()"
                )
                self._nav.add_feature("_default", "📋 Home", placeholder)

            self.setCentralWidget(self._nav)

        # ------------------------------------------------------------------
        # Actions
        # ------------------------------------------------------------------

        def _on_new(self) -> None:
            if not self._confirm_discard():
                return
            self._project_vm.new_project()
            self._results_vm.clear()

        def _on_open(self) -> None:
            if not self._confirm_discard():
                return
            path, _ = QFileDialog.getOpenFileName(self, "Apri progetto", "", "Progetti RD2229 (*.json);;Tutti (*)")
            if path:
                self._load_project(path)

        def _on_save(self) -> None:
            if self._project_vm.path:
                self._save_project(self._project_vm.path)
            else:
                self._on_save_as()

        def _on_save_as(self) -> None:
            path, _ = QFileDialog.getSaveFileName(self, "Salva progetto come", "", "Progetti RD2229 (*.json)")
            if path:
                self._save_project(path)

        def _on_run(self) -> None:
            if self._run_vm.running:
                return
            self._run_vm.set_running(True, "Esecuzione in corso…")
            project = self._project_vm.project
            worker = PipelineWorker(project, self._calc)
            worker.signals.finished.connect(self._on_run_finished)
            worker.signals.error.connect(self._on_run_error)
            QThreadPool.globalInstance().start(worker)

        def _on_run_finished(self, results: Any) -> None:
            self._results_vm.set_results(results)
            n_ok = sum(1 for e in results.elements if e.ok)
            n_tot = len(results.elements)
            status = f"Calcolo completato: {n_ok}/{n_tot} OK"
            if results.warnings:
                status += f" | {len(results.warnings)} avvisi"
            self._run_vm.set_done(status)

        def _on_run_error(self, error: str) -> None:
            self._run_vm.set_error(error)
            QMessageBox.critical(self, "Errore calcolo", error)

        def _on_export_json(self) -> None:
            if not self._results_vm.has_results:
                QMessageBox.information(self, "Export", "Nessun risultato disponibile.")
                return
            path, _ = QFileDialog.getSaveFileName(self, "Esporta risultati JSON", "", "JSON (*.json)")
            if path:
                try:
                    self._calc.export_results(self._results_vm.results, path)
                    QMessageBox.information(self, "Export", f"Risultati esportati:\n{path}")
                except Exception as exc:
                    QMessageBox.critical(self, "Errore export", str(exc))

        def _on_export_report(self, fmt: str) -> None:
            if not self._results_vm.has_results:
                QMessageBox.information(self, "Export", "Nessun risultato disponibile.")
                return
            ext = "html" if fmt == "html" else "md"
            path, _ = QFileDialog.getSaveFileName(self, f"Esporta report {fmt.upper()}", "", f"{fmt.upper()} (*.{ext})")
            if path:
                try:
                    self._calc.export_report(
                        self._project_vm.project,
                        self._results_vm.results,
                        path,
                        fmt=fmt,
                    )
                    QMessageBox.information(self, "Export", f"Report esportato:\n{path}")
                except Exception as exc:
                    QMessageBox.critical(self, "Errore export", str(exc))

        # ------------------------------------------------------------------
        # Helpers
        # ------------------------------------------------------------------

        def _load_project(self, path: str) -> None:
            try:
                project = self._io.open_project(path)
                self._project_vm.set_project(project, path)
                self._results_vm.clear()
            except Exception as exc:
                QMessageBox.critical(self, "Errore apertura", str(exc))

        def _save_project(self, path: str) -> None:
            try:
                self._io.save_project(self._project_vm.project, path)
                self._project_vm.mark_saved(path)
            except Exception as exc:
                QMessageBox.critical(self, "Errore salvataggio", str(exc))

        def _confirm_discard(self) -> bool:
            """Chiede conferma se ci sono modifiche non salvate."""
            if not self._project_vm.dirty:
                return True
            reply = QMessageBox.question(
                self,
                "Modifiche non salvate",
                "Il progetto ha modifiche non salvate. Continuare senza salvare?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            return reply == QMessageBox.StandardButton.Yes

        def _refresh_title(self) -> None:
            path = self._project_vm.path or "(senza titolo)"
            dirty = " *" if self._project_vm.dirty else ""
            name = os.path.basename(path)
            self.setWindowTitle(f"{APP_TITLE} – {name}{dirty}")

        def _refresh_recent_menu(self) -> None:
            self._recent_menu.clear()
            for path in self._project_vm.recent_files:
                a = self._recent_menu.addAction(os.path.basename(path))

                # Capture path in closure
                def _open(checked: bool = False, p: str = path) -> None:
                    if self._confirm_discard():
                        self._load_project(p)

                a.triggered.connect(_open)

        def _refresh_status(self) -> None:
            parts: list[str] = [self._run_vm.status]
            if self._results_vm.has_results:
                n = len(self._results_vm.elements)
                n_ok = sum(1 for e in self._results_vm.elements if e.ok)
                parts.append(f"Elementi: {n_ok}/{n} OK")
            self._status_label.setText("  |  ".join(parts))

        def closeEvent(self, event: Any) -> None:  # type: ignore[override]
            if not self._confirm_discard():
                event.ignore()
                return
            self._project_vm.save_recent(RECENT_SETTINGS_PATH)
            event.accept()


def _make_placeholder(parent: Any, label: str, tooltip: str = "") -> Any:
    """Crea un widget placeholder per schede non ancora implementate."""
    if not _PYSIDE6_AVAILABLE:
        return None  # type: ignore[return-value]
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

    w = QWidget(parent)
    lay = QVBoxLayout(w)
    lbl = QLabel(f"<b>{label}</b><br><small>Placeholder – scheda non ancora implementata</small>")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    if tooltip:
        lbl.setToolTip(tooltip)
    lay.addWidget(lbl)
    return w
