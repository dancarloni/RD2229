"""
Finestra GUI principale per il modulo Combinazioni.

Implementa il layout completo con:
- Tab Input: casi di carico, fattori parziali, coefficienti combinazione
- Tab Batch: generazione batch combinazioni
- Tab Risultati: tabella combinazioni SLU, SLE, CAR
- Tab Tabulato: formule di combinazione e regole normative
"""

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pipeline.module_registry import ModuleInfo
from shared.ui.base_module_window import BaseModuleWindow


class CombinazioniWindow(BaseModuleWindow):
    """
    Finestra principale del modulo Combinazioni.

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
        """Crea pannello input casi di carico."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Input: Casi di carico, Fattori parziali, Coefficienti"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_batch_panel(self) -> QWidget:
        """Crea tab batch generazione combinazioni."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Batch: Generazione batch combinazioni"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati combinazioni."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Risultati: Combinazioni SLU, SLE, CAR"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_tabulato_panel(self) -> QWidget:
        """Crea pannello tabulato con regole normative."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Tabulato: Formule di combinazione e regole normative"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel


__all__ = ["CombinazioniWindow"]
