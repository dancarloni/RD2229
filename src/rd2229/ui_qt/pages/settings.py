"""Settings page widget for Qt shell (minimal)."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
except Exception:  # pragma: no cover - optional dependency
    QWidget = object


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings"))

    def set_project(self, project):
        self._project = project
