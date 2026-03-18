"""
MaterialDetailFrame — Frame dettaglio materiale, editing rapido, override
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton
from PySide6.QtCore import Qt

class MaterialDetailFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        # area warning
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #b35f00;")
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)
        # Esempio campi
        self.code_edit = QLineEdit()
        self.desc_edit = QLineEdit()
        self.norma_edit = QLineEdit()
        self.fck_edit = QLineEdit()
        self.fck_override = QCheckBox("Override manuale f_ck")
        self.gamma_c_edit = QLineEdit()
        self.gamma_c_override = QCheckBox("Override manuale γ_c")
        # ...aggiungi altri parametri e override...
        layout.addWidget(QLabel("Codice:"))
        layout.addWidget(self.code_edit)
        layout.addWidget(QLabel("Descrizione:"))
        layout.addWidget(self.desc_edit)
        layout.addWidget(QLabel("Norma:"))
        layout.addWidget(self.norma_edit)
        layout.addWidget(QLabel("f_ck:"))
        row_fck = QHBoxLayout()
        row_fck.addWidget(self.fck_edit)
        row_fck.addWidget(self.fck_override)
        layout.addLayout(row_fck)
        layout.addWidget(QLabel("γ_c:"))
        row_gamma = QHBoxLayout()
        row_gamma.addWidget(self.gamma_c_edit)
        row_gamma.addWidget(self.gamma_c_override)
        layout.addLayout(row_gamma)
        # Pulsanti
        btn_layout = QHBoxLayout()
        self.save_button = QPushButton("Salva")
        btn_layout.addWidget(self.save_button)
        self.cancel_button = QPushButton("Annulla")
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def set_warning(self, text: str) -> None:
        if text:
            self.warning_label.setText(text)
            self.warning_label.setVisible(True)
        else:
            self.warning_label.setText("")
            self.warning_label.setVisible(False)
        # keyboard: Enter in QLineEdit moves focus to next widget
        try:
            self.code_edit.returnPressed.connect(self.focusNextChild)
            self.desc_edit.returnPressed.connect(self.focusNextChild)
            self.norma_edit.returnPressed.connect(self.focusNextChild)
            self.fck_edit.returnPressed.connect(self.focusNextChild)
            self.gamma_c_edit.returnPressed.connect(self.focusNextChild)
        except Exception:
            pass

# Per test rapido
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    frame = MaterialDetailFrame()
    frame.show()
    sys.exit(app.exec())
