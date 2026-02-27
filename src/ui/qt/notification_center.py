"""NotificationCenterWindow (Qt6 MVVM stub)."""

try:
    from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class NotificationCenterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Notification Center (work in progress)"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "notification_center",
    "name": "Notification Center",
    "description": "Centro notifiche e log utente (Qt6)",
}


def create_module(master=None, **context):
    return NotificationCenterWindow(parent=master)
