"""Verification page skeleton with minimal QTableView exposure."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
except Exception:  # pragma: no cover - optional dependency
    QWidget = object


class VerificationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Verification"))

    def set_project(self, project):
        self._project = project
