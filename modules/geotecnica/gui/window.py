"""
Finestra GUI principale per il modulo Geotecnica.

Implementa il layout completo con:
- Tab Input: fondazione, profilo geotecnico, parametri terreno
- Tab Batch: tabella multi-fondazione
- Tab Risultati: capacità portante, cedimenti, spinte
- Tab Tabulato: formule con passaggi intermedi
"""

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pipeline.module_registry import ModuleInfo
from shared.ui.base_module_window import BaseModuleWindow


class GeotecnicaWindow(BaseModuleWindow):
    """
    Finestra principale del modulo Geotecnica.

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
        """Crea pannello input fondazione e terreno."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Input: Fondazione, Profilo geotecnico, Parametri terreno"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_batch_panel(self) -> QWidget:
        """Crea tab batch multi-fondazione."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Batch: Tabella multi-fondazione"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati analisi geotecnica."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Risultati: Capacità portante, Cedimenti, Spinte"))
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


__all__ = ["GeotecnicaWindow"]
