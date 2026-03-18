"""
MaterialBatchEditDialog — Dialog batch editing per modifica multipla
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class MaterialBatchEditDialog(QDialog):
    def __init__(self, parametro, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Modifica batch: {parametro}")
        self._init_ui(parametro)

    def _init_ui(self, parametro):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Nuovo valore per '{parametro}':"))
        self.value_edit = QLineEdit()
        layout.addWidget(self.value_edit)
        btn_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Annulla")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_value(self) -> str:
        return self.value_edit.text()

# Per test rapido
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = MaterialBatchEditDialog("γ_c")
    dialog.show()
    sys.exit(app.exec())
