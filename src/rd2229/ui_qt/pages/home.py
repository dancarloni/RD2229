"""Home page for Qt launcher."""

from __future__ import annotations

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget
except Exception:  # pragma: no cover - optional dependency
    QWidget = object


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel("RD2229 Alpha Launcher")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        status_box = QGroupBox("Stato corrente")
        status_layout = QVBoxLayout(status_box)
        status_layout.addWidget(QLabel("- Stream A/D/B: base tecnica avviata"))
        status_layout.addWidget(QLabel("- MVP Structural Check: eseguibile"))
        status_layout.addWidget(QLabel("- Stream C/E: pianificati"))
        layout.addWidget(status_box)

        quickstart_box = QGroupBox("Quick start")
        quickstart_layout = QVBoxLayout(quickstart_box)
        quickstart_layout.addWidget(QLabel("1) Vai su Verification"))
        quickstart_layout.addWidget(QLabel("2) Seleziona 'MVP Structural Check'"))
        quickstart_layout.addWidget(QLabel("3) Premi 'Run Module'"))
        layout.addWidget(quickstart_box)
        layout.addStretch(1)

    def set_project(self, project):
        self._project = project
