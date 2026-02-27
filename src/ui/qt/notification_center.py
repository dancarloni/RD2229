"""
NotificationCenterWindow (PySide6 MVVM stub)
"""

from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class NotificationCenterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Notification Center (work in progress)"))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "notification_center",
    "name": "Notification Center",
    "description": "Centro notifiche e log utente (PySide6)",
}


def create_module(master=None, **context):
    return NotificationCenterWindow(parent=master)
