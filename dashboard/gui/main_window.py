"""
Dashboard principale — Entry point GUI di RD2229.

Fornisce:
- Launcher per moduli disponibili
- Selezione/apertura progetti
- Monitor stato pipeline
- Accesso a relazioni
"""

try:
    from PySide6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PyQt6.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QListWidget,
        QListWidgetItem,
    )

from pipeline.module_registry import ModuleRegistry


class DashboardMainWindow(QMainWindow):
    """Finestra principale dashboard."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RD2229 — Centro Operativo")
        self.resize(1200, 700)

        self.registry = ModuleRegistry()

        # Widget principale
        central = QWidget()
        layout = QHBoxLayout()

        # Sinistra: Azioni
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("AZIONI"))
        left_layout.addWidget(QPushButton("+ Nuovo Progetto"))
        left_layout.addWidget(QPushButton("📂 Apri Progetto"))
        left_layout.addWidget(QPushButton("💾 Salva"))
        left_layout.addWidget(QPushButton("▶ Esegui Pipeline"))
        left_layout.addWidget(QPushButton("📜 Report"))
        left_layout.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)

        # Destra: Elenco moduli
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("MODULI DI CALCOLO"))

        # Lista moduli registrati
        self.module_list = QListWidget()
        for module_info in self.registry.list_all():
            item = QListWidgetItem(f"{module_info.icon} {module_info.name}")
            self.module_list.addItem(item)

        right_layout.addWidget(self.module_list)
        right_layout.addWidget(QPushButton("▶ Apri Modulo"))

        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)

        central.setLayout(layout)
        self.setCentralWidget(central)


__all__ = ["DashboardMainWindow"]
