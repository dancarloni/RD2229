"""
Finestra GUI principale per il modulo Strutture Esistenti.

Implementa il layout completo con:
- Tab Input: edificio, anno costruzione, norme storiche, dati indagini
- Tab Batch: valutazione batch multi-edificio
- Tab Risultati: indici di rischio, livelli di sicurezza, capacità meccaniche
- Tab Tabulato: coefficienti di confidenza, valori caratteristici, analisi dettagliata
"""

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pipeline.module_registry import ModuleInfo
from shared.ui.base_module_window import BaseModuleWindow


class EsistenziWindow(BaseModuleWindow):
    """
    Finestra principale del modulo Strutture Esistenti.

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
        """Crea pannello input edificio esistente."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Input: Edificio, Anno costruzione, Norme, Dati indagini"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_batch_panel(self) -> QWidget:
        """Crea tab batch valutazione multi-edificio."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Batch: Valutazione batch multi-edificio"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati valutazione."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Risultati: Indici di rischio, Livelli di sicurezza, Capacità"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_tabulato_panel(self) -> QWidget:
        """Crea pannello tabulato con analisi dettagliata."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("Tab Tabulato: Coefficienti confidenza, Valori caratteristici, Analisi")
        )
        layout.addStretch()

        panel.setLayout(layout)
        return panel


__all__ = ["EsistenziWindow"]
