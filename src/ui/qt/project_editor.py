"""ProjectEditorWindow (Qt6 MVVM stub)."""

try:
    from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class ProjectEditorWindow(QWidget):
    def __init__(self, project_service=None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Project Editor (work in progress)"))
        # Improve sizing to avoid layout overlap
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "project_editor",
    "name": "Project Editor",
    "description": "GUI per creare/caricare/salvare ProjectModel (Qt6)",
}


def create_module(master=None, **context):
    return ProjectEditorWindow(project_service=context.get("project_service"), parent=master)
