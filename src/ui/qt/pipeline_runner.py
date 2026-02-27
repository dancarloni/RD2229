"""
PipelineRunnerWindow (PySide6 MVVM stub)
"""

from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class PipelineRunnerWindow(QWidget):
    def __init__(self, project_service=None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Pipeline Runner (work in progress)"))
        # Improve sizing and force initial repaint
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "pipeline_runner",
    "name": "Pipeline Runner",
    "description": "Avvia la pipeline, mostra barra di progresso e risultati (PySide6)",
}


def create_module(master=None, **context):
    return PipelineRunnerWindow(project_service=context.get("project_service"), parent=master)
