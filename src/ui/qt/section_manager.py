"""
SectionManagerWindow (PySide6 MVVM stub)
"""

from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class SectionManagerWindow(QWidget):
    def __init__(self, project_service=None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Section Manager (work in progress)"))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "section_manager",
    "name": "Section Manager",
    "description": "Gestione/import/rotazione sezioni CSV (PySide6)",
}


def create_module(master=None, **context):
    return SectionManagerWindow(project_service=context.get("project_service"), parent=master)
