"""
Modulo: Combinazioni — Generazione automatica di combinazioni di carico.

Supporta:
- NTC2018 — Combinazioni SLU, SLE, CAR (costruzione, assistenza, riparazione)
- NTC2008 — Combinazioni legacy 2008

Funzionalità:
- Generazione combinazioni fondamentali SLU
- Combinazioni di servizio SLE (rara, frequente, quasi-permanente)
- Combinazioni CAR per situazioni costruttive temporanee
- Coefficienti parziali e di combinazione configurabili
- Esportazione verso formati standard (Excel, JSON)
- Inviluppi per analisi strutturale
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="combinazioni",
    name="Combinazioni",
    version="1.0.0",
    category="utility",
    icon="⚖️",
    description="Generazione automatica di combinazioni di carico secondo NTC2018 e NTC2008",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
        "NTC2008",  # Normativa Tecnica Costruzioni 2008
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy"],
)


def create_engine():
    """
    Factory per il motore di combinazioni.

    Ritorna l'engine appropriato che implementa la generazione
    di combinazioni per tutte le norme supportate.
    """
    from modules.combinazioni.engine.dispatcher import CombinazioniEngine

    return CombinazioniEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo combinazioni.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.combinazioni.gui.window import CombinazioniWindow

    return CombinazioniWindow(MODULE_INFO, parent)


def register():
    """Registra questo modulo nel ModuleRegistry."""
    from pipeline.module_registry import ModuleRegistry

    ModuleRegistry.register(MODULE_INFO, create_engine, create_window)


__all__ = [
    "MODULE_INFO",
    "create_engine",
    "create_window",
    "register",
]
