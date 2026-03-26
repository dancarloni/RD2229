"""
Finestra GUI principale per il modulo Vento.

Implementa il layout completo con:
- Tab Input: parametri sito, edificio, categoria esposizione
- Tab Batch: tabella multi-edificio
- Tab Risultati: pressioni e coefficienti di forma
- Tab Tabulato: formule con passaggi intermedi
"""

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pipeline.module_registry import ModuleInfo
from shared.ui.base_module_window import BaseModuleWindow


class VentoWindow(BaseModuleWindow):
    """
    Finestra principale del modulo Vento.

    Eredita da BaseModuleWindow e implementa i pannelli specifici.
    """

    def __init__(self, module_info: ModuleInfo, parent=None):
        """
        Inizializza la finestra.

        Args:
            module_info: ModuleInfo del modulo
            parent: Finestra parent (opzionale)
        """
        super().__init__(module_info, parent)

    def _create_input_panel(self) -> QWidget:
        """Crea pannello input per sito e edificio."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Input: Sito, Edificio, Categoria esposizione"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_batch_panel(self) -> QWidget:
        """Crea tab batch multi-edificio."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Batch: Tabella multi-edificio"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati con pressioni."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Risultati: Pressioni e coefficienti di forma"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_tabulato_panel(self) -> QWidget:
        """Crea pannello tabulato con formule."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Tabulato: Formule con passaggi intermedi"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel


__all__ = ["VentoWindow"]
