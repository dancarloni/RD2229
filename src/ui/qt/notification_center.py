"""Notification center for user-facing events (Qt6)."""

from __future__ import annotations

from datetime import datetime

try:
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtWidgets import (
        QComboBox,
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
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QComboBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )


class NotificationCenterWindow(QWidget):
    message_added = Signal(str, str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("RD2229 - Centro notifiche")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.addWidget(QLabel("<b>Centro notifiche</b>"))

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filtro livello:"))
        self.cmb_level = QComboBox()
        self.cmb_level.addItems(["all", "info", "warning", "error"])
        self.cmb_level.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(self.cmb_level)

        self.btn_clear = QPushButton("Pulisci")
        self.btn_clear.clicked.connect(self._clear)
        filter_row.addWidget(self.btn_clear)
        filter_row.addStretch(1)

        root.addLayout(filter_row)
        self.list_widget = QListWidget()
        root.addWidget(self.list_widget)

        self._events: list[tuple[str, str]] = []
        self.message_added.connect(self.notify)

    def notify(self, level: str, message: str) -> None:
        lvl = str(level).lower().strip() or "info"
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {lvl.upper()} - {message}"
        self._events.append((lvl, formatted))
        self._apply_filter(self.cmb_level.currentText())

    def _apply_filter(self, selected: str) -> None:
        self.list_widget.clear()
        wanted = selected.lower().strip()
        for lvl, text in self._events:
            if wanted in {"", "all"} or lvl == wanted:
                self.list_widget.addItem(QListWidgetItem(text))

    def _clear(self) -> None:
        self._events.clear()
        self.list_widget.clear()


MODULE_SPEC = {
    "key": "notification_center",
    "name": "Notification Center",
    "description": "Centro notifiche e log utente (Qt6)",
}


def create_module(master=None, **context):
    return NotificationCenterWindow(parent=master)
