"""
Modulo: Sismica — Analisi sismica e progettazione antisismica.

Supporta:
- Spettri di risposta NTC2018
- Analisi pushover semplificata
- Fattori di struttura
- Combinazioni sismiche
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="sismica",
    name="Sismica/Pushover",
    version="1.0.0",
    category="azioni",
    icon="🌊",
    description="Analisi sismica e progettazione antisismica",
    norms_supported=[
        "NTC2008",  # Normativa Tecnica Costruzioni 2008
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy"],
)


def create_engine():
    """Factory per il motore di calcolo sismica."""
    from modules.sismica.engine.dispatcher import SismicaEngine

    return SismicaEngine()


def create_window(parent=None):
    """Factory per la finestra GUI del modulo sismica."""
    from modules.sismica.gui.window import SismicaWindow

    return SismicaWindow(MODULE_INFO, parent)


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
