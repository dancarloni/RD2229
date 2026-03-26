"""
Finestra GUI principale per il modulo Fuoco.

Implementa il layout completo con:
- Tab Input: elemento, materiale, tempo richiesto
- Tab Batch: tabella multi-elemento
- Tab Risultati: verifiche fuoco e curve termiche
- Tab Tabulato: formule con passaggi intermedi
"""

try:
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pipeline.module_registry import ModuleInfo
from shared.ui.base_module_window import BaseModuleWindow


class FuocoWindow(BaseModuleWindow):
    """
    Finestra principale del modulo Fuoco.

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
        """Crea pannello input elemento fuoco."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Input: Elemento, Materiale, Tempo richiesto"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_batch_panel(self) -> QWidget:
        """Crea tab batch multi-elemento."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Batch: Tabella multi-elemento"))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati verifiche fuoco."""
        panel = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tab Risultati: Verifiche fuoco e curve termiche"))
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


__all__ = ["FuocoWindow"]
