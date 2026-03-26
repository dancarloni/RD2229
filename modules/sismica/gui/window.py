"""
Finestra GUI per modulo Sismica/Pushover.

Tab:
- Sito: parametri sismici (latitudine, longitudine, categoria suolo, topografia)
- Spettro: grafico spettro di risposta
- Pushover: curva pushover e duttilità
"""

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pipeline.module_registry import ModuleInfo
from shared.ui.base_module_window import BaseModuleWindow


class SismicaWindow(BaseModuleWindow):
    """Finestra principale del modulo Sismica/Pushover."""

    def __init__(self, module_info: ModuleInfo, parent=None):
        super().__init__(module_info, parent)

    def _create_input_panel(self) -> QWidget:
        """Crea pannello input parametri sismo."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tab Sito: Parametri sismici"))
        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def _create_batch_panel(self) -> QWidget:
        """Crea tab spettro di risposta."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tab Spettro: Grafico spettro di risposta"))
        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tab Pushover: Curva pushover"))
        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def _create_tabulato_panel(self) -> QWidget:
        """Crea pannello tabulato."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tab Tabulato: Risultati analisi"))
        layout.addStretch()
        panel.setLayout(layout)
        return panel


__all__ = ["SismicaWindow"]
