"""Notification center for user-facing events (Qt6)."""

from __future__ import annotations

from datetime import datetime

try:
    from PyQt6.QtCore import QPropertyAnimation, QTimer, pyqtSignal as Signal
    from PyQt6.QtGui import QColor
    from PyQt6.QtWidgets import (
        QComboBox,
        QFrame,
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
    from PySide6.QtCore import QPropertyAnimation, QTimer, Signal
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import (
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )


class ToastOverlay(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("NotificationToast")
        self.setStyleSheet(
            "QFrame#NotificationToast {"
            "background-color: rgba(21, 26, 31, 220);"
            "border: 1px solid rgba(255, 255, 255, 35);"
            "border-radius: 8px;"
            "padding: 6px;"
            "}"
            "QLabel#NotificationToastText { color: #f3f5f7; font-weight: 600; }"
        )
        self._label = QLabel("", self)
        self._label.setObjectName("NotificationToastText")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.addWidget(self._label)
        self.hide()

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_toast)

        self._anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim.setDuration(220)
        self._anim.finished.connect(self._on_animation_finished)

    def show_toast(self, message: str, level: str = "info", duration_ms: int = 2200) -> None:
        palette = {
            "info": QColor("#1565C0"),
            "warning": QColor("#B26A00"),
            "error": QColor("#B71C1C"),
            "debug": QColor("#546E7A"),
        }
        lvl = str(level).lower().strip() or "info"
        color = palette.get(lvl, palette["info"])
        self._label.setText(f"{lvl.upper()}: {message}")
        self.setStyleSheet(
            "QFrame#NotificationToast {"
            "background-color: rgba(21, 26, 31, 220);"
            f"border: 1px solid rgba({color.red()}, {color.green()}, {color.blue()}, 180);"
            "border-radius: 8px;"
            "padding: 6px;"
            "}"
            "QLabel#NotificationToastText { color: #f3f5f7; font-weight: 600; }"
        )

        parent = self.parentWidget()
        if parent is not None:
            width = min(520, max(260, parent.width() - 40))
            self.setGeometry(16, 16, width, 42)

        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self._hide_timer.start(max(400, int(duration_ms)))

    def _hide_toast(self) -> None:
        self._anim.stop()
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.0)
        self._anim.start()

    def _on_animation_finished(self) -> None:
        if self.windowOpacity() <= 0.01:
            self.hide()


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
        self._toast = ToastOverlay(self)
        self.message_added.connect(self.notify)

    def notify(self, level: str, message: str) -> None:
        lvl = str(level).lower().strip() or "info"
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {lvl.upper()} - {message}"
        self._events.append((lvl, formatted))
        self._apply_filter(self.cmb_level.currentText())
        self._toast.show_toast(message, lvl)

    def show_toast(self, level: str, message: str, duration_ms: int = 2200) -> None:
        self._toast.show_toast(message, level, duration_ms)

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
