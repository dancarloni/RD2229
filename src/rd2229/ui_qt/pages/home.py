"""Home page for Qt shell: minimal QWidget exposing set_project API."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
except Exception:  # pragma: no cover - optional dependency
    QWidget = object


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Home"))

    def set_project(self, project):
        self._project = project
