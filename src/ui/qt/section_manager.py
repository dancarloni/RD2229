"""Section manager window with live preview (Qt6)."""

from __future__ import annotations

try:
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

from src.ui.qt.visualizzatore_sezione import VisualizzatoreSezione


class SectionManagerWindow(QWidget):
    def __init__(self, project_service=None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.setWindowTitle("RD2229 - Gestione sezioni")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root = QHBoxLayout(self)
        left = QVBoxLayout()
        right = QVBoxLayout()
        root.addLayout(left, 1)
        root.addLayout(right, 2)

        left.addWidget(QLabel("<b>Sezioni progetto</b>"))
        self.lst_sections = QListWidget()
        self.lst_sections.currentItemChanged.connect(self._on_selected)
        left.addWidget(self.lst_sections)

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.refresh_from_project)
        left.addWidget(btn_refresh)

        self.preview = VisualizzatoreSezione(self)
        right.addWidget(QLabel("<b>Preview sezione</b>"))
        right.addWidget(self.preview)

        self.refresh_from_project()

    def refresh_from_project(self) -> None:
        self.lst_sections.clear()
        project = getattr(self.project_service, "current_project", None)
        if project is None:
            return
        for entry in getattr(project, "geometry", []):
            label = (
                f"{entry.id or '-'} | {entry.type or 'UNKNOWN'} | {entry.width}x{entry.height} cm"
            )
            item = QListWidgetItem(label)
            item.setData(32, entry)
            self.lst_sections.addItem(item)

    def _on_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            return
        entry = current.data(32)
        if entry is None:
            return
        width = float(getattr(entry, "width", 0.0) or 0.0)
        height = float(getattr(entry, "height", 0.0) or 0.0)
        if width <= 0 or height <= 0:
            return

        self.preview.imposta_sezione_rettangolare(width, height, copriferro=3.0)
        self.preview.imposta_armatura(
            [
                {"x": 3.0, "y": 3.0, "diametro": 1.2},
                {"x": max(3.0, width - 3.0), "y": 3.0, "diametro": 1.2},
                {"x": 3.0, "y": max(3.0, height - 3.0), "diametro": 1.2},
                {
                    "x": max(3.0, width - 3.0),
                    "y": max(3.0, height - 3.0),
                    "diametro": 1.2,
                },
            ]
        )
        self.preview.imposta_risultati_calcolo(
            asse_neutro_y=height / 2.0,
            deformazioni={"eps_c": -0.0035, "eps_s": 0.0020},
            tensioni={"sigma_c_max": -120.0, "sigma_s": 2600.0},
        )


MODULE_SPEC = {
    "key": "section_manager",
    "name": "Section Manager",
    "description": "Gestione/import/rotazione sezioni CSV (Qt6)",
}


def create_module(master=None, **context):
    return SectionManagerWindow(project_service=context.get("project_service"), parent=master)
