"""
CodeSettingsDialog (PySide6 MVVM stub)
"""

"""
CodeSettingsWindow (PySide6 MVVM stub)
"""

from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class CodeSettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Code Settings (work in progress)"))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "code_settings",
    "name": "Code Settings Dialog",
    "description": "Dialog di configurazione codici (PySide6)",
}


def create_module(master=None, **context):
    # Return the window class implemented above. Some factories pass project_service.
    return CodeSettingsWindow(parent=master)
