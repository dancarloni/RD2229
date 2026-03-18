"""
MaterialExportWidget — Esportazione rapida, formato selezionabile
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QLabel, QApplication
from PySide6.QtCore import Qt, Signal, QSettings

class MaterialExportWidget(QWidget):
    formatChanged = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Formato esportazione:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "Markdown", "CSV", "Testo semplice"])
        # restore previously selected format (persisted via QSettings)
        try:
            settings = QSettings("RD2229", "MaterialEditor")
            saved = settings.value("export_format", "") or ""
            if saved:
                idx = self.format_combo.findText(str(saved))
                if idx >= 0:
                    self.format_combo.setCurrentIndex(idx)
        except Exception:
            pass
        # persist selection and emit signal
        try:
            self.format_combo.currentTextChanged.connect(self._on_format_changed)
        except Exception:
            pass
        layout.addWidget(self.format_combo)
        self.export_text = QTextEdit()
        layout.addWidget(self.export_text)
        self.copy_button = QPushButton("Copia")
        layout.addWidget(self.copy_button)
        self.setLayout(layout)

    def _on_format_changed(self, text: str) -> None:
        try:
            settings = QSettings("RD2229", "MaterialEditor")
            settings.setValue("export_format", text)
        except Exception:
            pass
        try:
            self.formatChanged.emit(text)
        except Exception:
            pass

# Per test rapido
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    widget = MaterialExportWidget()
    widget.show()
    sys.exit(app.exec())
