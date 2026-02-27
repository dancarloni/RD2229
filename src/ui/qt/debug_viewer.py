"""DebugViewerWindow (Qt6 implementation)."""

import logging

try:
    from PyQt6.QtWidgets import QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class DebugViewerWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Debug Viewer (work in progress)"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "debug_viewer",
    "name": "Debug Viewer",
    "description": "Strumento per visualizzare log e debug (Qt6)",
}


def create_module(master=None, **context):
    return DebugViewerWindow(parent=master)
