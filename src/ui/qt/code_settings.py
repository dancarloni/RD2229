"""CodeSettingsWindow (Qt6 MVVM stub)."""

try:
    from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class CodeSettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Code Settings (work in progress)"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "code_settings",
    "name": "Code Settings Dialog",
    "description": "Dialog di configurazione codici (Qt6)",
}


def create_module(master=None, **context):
    # Return the window class implemented above. Some factories pass project_service.
    return CodeSettingsWindow(parent=master)
