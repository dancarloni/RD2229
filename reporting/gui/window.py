"""
Finestra GUI per generazione e visualizzazione relazioni tecniche.
"""

try:
    from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget


class ReportWindow(QMainWindow):
    """Finestra per generazione e visualizzazione relazioni."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relazione Tecnica — RD2229")
        self.resize(1000, 700)

        # Widget principale
        central = QWidget()
        layout = QVBoxLayout()

        # Area anteprima
        layout.addWidget(QLabel("Anteprima Relazione"))
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        layout.addWidget(self.text_preview)

        # Pulsanti export
        btn_export_md = QPushButton("📤 Export Markdown")
        btn_export_html = QPushButton("📤 Export HTML")
        layout.addWidget(btn_export_md)
        layout.addWidget(btn_export_html)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def show_preview(self, text: str) -> None:
        """Mostra anteprima della relazione."""
        self.text_preview.setText(text)


__all__ = ["ReportWindow"]
