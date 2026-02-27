"""
HistoricalMaterialEditorWindow (PySide6 MVVM stub)
"""

from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class HistoricalMaterialEditorWindow(QWidget):
    def __init__(self, material_repository=None, parent=None):
        super().__init__(parent)
        self.material_repository = material_repository
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Material Editor (work in progress)"))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "material_editor",
    "name": "Historical Material Editor",
    "description": "Editor materiali storici (PySide6)",
}


def create_module(master=None, **context):
    return HistoricalMaterialEditorWindow(
        material_repository=context.get("material_repository"), parent=master
    )
