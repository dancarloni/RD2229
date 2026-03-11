"""Widget Qt per generazione relazione professionale (Fase Q)."""

from __future__ import annotations

from pathlib import Path

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )

from src.report.custom import load_section_profile, save_section_profile
from src.report.export import export_ascii, export_docx, export_html, export_md, export_pdf
from src.report.images import image_html_block
from src.report.report_builder import ReportConfig, build_report


class ReportWidget(QWidget):
    """Pannello Qt per preview e export relazione."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project = None
        self._results = None
        self._last_artifact = None
        self._image_blocks: list[str] = []
        self._build_ui()

    def set_data(self, project, results) -> None:
        self._project = project
        self._results = results

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        controls = QGroupBox("Configurazione report")
        controls_layout = QGridLayout(controls)

        controls_layout.addWidget(QLabel("Sezioni incluse:"), 0, 0)
        self.section_list = QListWidget()
        self.section_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        for key in [
            "dati_generali",
            "materiali",
            "azioni",
            "analisi",
            "verifiche",
            "risultati",
            "conclusioni",
            "confronto_norme",
        ]:
            item = QListWidgetItem(key)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.section_list.addItem(item)
        controls_layout.addWidget(self.section_list, 1, 0, 1, 2)

        self.btn_generate = QPushButton("Genera anteprima")
        self.btn_generate.clicked.connect(self._on_generate)
        controls_layout.addWidget(self.btn_generate, 2, 0)

        self.btn_add_image = QPushButton("Carica immagine")
        self.btn_add_image.clicked.connect(self._on_add_image)
        controls_layout.addWidget(self.btn_add_image, 2, 1)

        self.btn_save_profile = QPushButton("Salva profilo")
        self.btn_save_profile.clicked.connect(self._save_profile)
        controls_layout.addWidget(self.btn_save_profile, 3, 0)

        self.btn_load_profile = QPushButton("Carica profilo")
        self.btn_load_profile.clicked.connect(self._load_profile)
        controls_layout.addWidget(self.btn_load_profile, 3, 1)

        root.addWidget(controls)

        self.preview = QTextBrowser()
        root.addWidget(self.preview, 1)

        export_row = QHBoxLayout()
        self.btn_export_html = QPushButton("Export HTML")
        self.btn_export_md = QPushButton("Export MD")
        self.btn_export_ascii = QPushButton("Export ASCII")
        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_export_docx = QPushButton("Export DOCX")
        self.btn_export_html.clicked.connect(lambda: self._export("html"))
        self.btn_export_md.clicked.connect(lambda: self._export("md"))
        self.btn_export_ascii.clicked.connect(lambda: self._export("ascii"))
        self.btn_export_pdf.clicked.connect(lambda: self._export("pdf"))
        self.btn_export_docx.clicked.connect(lambda: self._export("docx"))
        for btn in [
            self.btn_export_html,
            self.btn_export_md,
            self.btn_export_ascii,
            self.btn_export_pdf,
            self.btn_export_docx,
        ]:
            export_row.addWidget(btn)
        root.addLayout(export_row)

    def _selected_sections(self) -> list[str]:
        selected: list[str] = []
        for index in range(self.section_list.count()):
            item = self.section_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected

    def _on_generate(self) -> None:
        if self._project is None or self._results is None:
            self.preview.setHtml("<p><b>Dataset mancante</b>: impostare progetto e risultati.</p>")
            return

        config = ReportConfig(
            include_comparison=True,
            selected_sections=self._selected_sections(),
        )
        artifact = build_report(self._project, self._results, config=config)

        if self._image_blocks:
            artifact.html = artifact.html.replace(
                "</body>",
                "".join(self._image_blocks) + "</body>",
            )
        self._last_artifact = artifact
        self.preview.setHtml(artifact.html)

    def _on_add_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona immagine",
            "",
            "Images (*.png *.jpg *.jpeg *.svg *.gif)",
        )
        if not file_path:
            return
        image_block = image_html_block(file_path, caption=Path(file_path).name)
        self._image_blocks.append(image_block)

    def _export(self, kind: str) -> None:
        if self._last_artifact is None:
            self._on_generate()
        if self._last_artifact is None:
            return

        suffix = {
            "html": "*.html",
            "md": "*.md",
            "ascii": "*.txt",
            "pdf": "*.pdf",
            "docx": "*.docx",
        }[kind]
        path, _ = QFileDialog.getSaveFileName(self, f"Esporta {kind.upper()}", "", suffix)
        if not path:
            return

        try:
            if kind == "html":
                export_html(self._last_artifact, path)
            elif kind == "md":
                export_md(self._last_artifact, path)
            elif kind == "ascii":
                export_ascii(self._last_artifact, path)
            elif kind == "pdf":
                export_pdf(self._last_artifact, path)
            elif kind == "docx":
                export_docx(self._last_artifact, path)
        except Exception as exc:  # pragma: no cover - UI feedback path
            self.preview.setHtml(f"<p><b>Errore export:</b> {exc}</p>")

    def _save_profile(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva profilo sezioni",
            "report_profile.json",
            "JSON (*.json)",
        )
        if not path:
            return
        sections = self._selected_sections()
        save_section_profile(path, sections)

    def _load_profile(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Carica profilo sezioni",
            "",
            "JSON (*.json)",
        )
        if not path:
            return
        selected = set(load_section_profile(path))
        for index in range(self.section_list.count()):
            item = self.section_list.item(index)
            state = Qt.CheckState.Checked if item.text() in selected else Qt.CheckState.Unchecked
            item.setCheckState(state)


MODULE_SPEC = {
    "key": "report_widget",
    "name": "Relazione Professionale",
    "description": "Genera preview A4 e export multi-formato.",
}


def create_module(master=None, **context):
    widget = ReportWidget(parent=master)
    widget.set_data(context.get("project"), context.get("results"))
    return widget
