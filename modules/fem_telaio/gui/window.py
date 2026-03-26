"""
Finestra GUI principale per il modulo FEM/Telai.

Implementa il layout completo con:
- Tab Input: definizione modello (nodi, elementi, vincoli, carichi)
- Tab Batch: analisi batch multi-modello
- Tab Risultati: spostamenti, reazioni, sollecitazioni interne, deformata
- Tab Tabulato: diagrammi e risultati numerici dettagliati
"""

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pipeline.module_registry import ModuleInfo
from shared.ui.base_module_window import BaseModuleWindow


class FemTelaioWindow(BaseModuleWindow):
    """
    Finestra principale del modulo FEM/Telai.

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
        """Crea pannello input modello FEM."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Input: Nodi, Elementi, Vincoli, Carichi"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_batch_panel(self) -> QWidget:
        """Crea tab batch analisi multi-modello."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Batch: Analisi batch multi-modello"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati analisi FEM."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Risultati: Spostamenti, Reazioni, Sollecitazioni, Deformata"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_tabulato_panel(self) -> QWidget:
        """Crea pannello tabulato con diagrammi."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Tabulato: Diagrammi e risultati numerici dettagliati"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel


__all__ = ["FemTelaioWindow"]
