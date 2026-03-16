"""Widget Qt per preview e export report X6 (tracciabilità auditabile).

Pannello PySide6 che permette di:
- visualizzare l'anteprima HTML del report X6
- esportare il report in formato HTML, Markdown o JSON
- ispezionare l'audit trail (hash SHA-256, decision trace)
- applicare un template di norma (NTC2018 / DM96 / RD2229)

Pattern: segue la struttura di ``src/ui/qt/report_widget.py`` (Fase Q).
"""

from __future__ import annotations

from pathlib import Path

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QComboBox,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPlainTextEdit,
        QPushButton,
        QSplitter,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QComboBox,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPlainTextEdit,
        QPushButton,
        QSplitter,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )

from src.reporting.export import export_report_html, export_report_json, export_report_md
from src.reporting.report_builder import ReportArtifact, build_report

_NORM_OPTIONS = ["NTC2018", "DM96", "DM92", "RD2229", "EC2"]


class X6ReportWidget(QWidget):
    """Pannello Qt per preview e export report X6 (tracciabilità Fase X6).

    Uso tipico::

        widget = X6ReportWidget()
        widget.set_data(project, results)
        widget.refresh()   # oppure clic su "Aggiorna"
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project = None
        self._results = None
        self._artifact: ReportArtifact | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # Interfaccia pubblica
    # ------------------------------------------------------------------

    def set_data(self, project, results) -> None:
        """Imposta progetto e risultati, abilita il pulsante Aggiorna."""
        self._project = project
        self._results = results
        self._btn_refresh.setEnabled(True)

    def refresh(self) -> None:
        """Ricalcola il report X6 e aggiorna la preview."""
        if self._project is None or self._results is None:
            return
        self._artifact = build_report(self._project, self._results)
        self._preview.setHtml(self._artifact.html)
        self._update_audit_panel()
        self._btn_export_html.setEnabled(True)
        self._btn_export_md.setEnabled(True)
        self._btn_export_json.setEnabled(True)

    # ------------------------------------------------------------------
    # UI costruzione
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        # Barra strumenti in alto
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Normativa:"))
        self._combo_norm = QComboBox()
        self._combo_norm.addItems(_NORM_OPTIONS)
        toolbar.addWidget(self._combo_norm)
        toolbar.addStretch()

        self._btn_refresh = QPushButton("⟳ Aggiorna report")
        self._btn_refresh.setEnabled(False)
        self._btn_refresh.clicked.connect(self.refresh)
        toolbar.addWidget(self._btn_refresh)

        self._btn_export_html = QPushButton("Esporta HTML")
        self._btn_export_html.setEnabled(False)
        self._btn_export_html.clicked.connect(self._export_html)
        toolbar.addWidget(self._btn_export_html)

        self._btn_export_md = QPushButton("Esporta MD")
        self._btn_export_md.setEnabled(False)
        self._btn_export_md.clicked.connect(self._export_md)
        toolbar.addWidget(self._btn_export_md)

        self._btn_export_json = QPushButton("Esporta JSON")
        self._btn_export_json.setEnabled(False)
        self._btn_export_json.clicked.connect(self._export_json)
        toolbar.addWidget(self._btn_export_json)

        root.addLayout(toolbar)

        # Splitter verticale: preview sopra, audit trail sotto
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Pannello preview HTML
        preview_box = QGroupBox("Anteprima report X6")
        preview_layout = QVBoxLayout(preview_box)
        self._preview = QTextBrowser()
        self._preview.setOpenExternalLinks(False)
        preview_layout.addWidget(self._preview)
        splitter.addWidget(preview_box)

        # Pannello audit trail
        audit_box = QGroupBox("Audit Trail X6")
        audit_layout = QVBoxLayout(audit_box)
        self._audit_text = QPlainTextEdit()
        self._audit_text.setReadOnly(True)
        self._audit_text.setMaximumHeight(160)
        audit_layout.addWidget(self._audit_text)
        splitter.addWidget(audit_box)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

    # ------------------------------------------------------------------
    # Slot privati
    # ------------------------------------------------------------------

    def _update_audit_panel(self) -> None:
        if self._artifact is None:
            return
        trail = self._artifact.audit_trail
        lines = [
            f"Input hash  : {trail.get('input_hash', 'N/D')}",
            f"Output hash : {trail.get('output_hash', 'N/D')}",
            f"Generato    : {trail.get('generated_at', 'N/D')}",
            f"Norma       : {trail.get('norm_code', 'N/D')}",
            f"Elementi    : {trail.get('element_count', 0)}",
            f"Warning     : {trail.get('warnings_count', 0)}",
        ]
        if self._artifact.decision_trace:
            lines.append("")
            lines.append("Decision trace:")
            for step in self._artifact.decision_trace:
                lines.append(f"  • {step}")
        self._audit_text.setPlainText("\n".join(lines))

    def _export_html(self) -> None:
        if self._artifact is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Esporta report HTML", "", "HTML (*.html)")
        if path:
            export_report_html(self._artifact, path)

    def _export_md(self) -> None:
        if self._artifact is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Esporta report Markdown", "", "Markdown (*.md)"
        )
        if path:
            export_report_md(self._artifact, path)

    def _export_json(self) -> None:
        if self._artifact is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Esporta payload JSON X6", "", "JSON (*.json)")
        if path:
            export_report_json(self._artifact, path)
