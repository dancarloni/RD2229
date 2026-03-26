"""
Modulo: Vento — Calcolo delle azioni del vento secondo NTC2018 e EN1991.

Supporta:
- NTC2018 — Azioni del vento su edifici e strutture
- EN1991 — Eurocodice 1: Azioni sul vento

Funzionalità:
- Categorizzazione edifici e siti (velocità, rugosità, topografia)
- Pressioni dinamiche di base e risultanti
- Coefficienti di forma per varie geometrie
- Effetti dinamici e vibrazioni
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="vento",
    name="Vento NTC2018",
    version="1.0.0",
    category="strutturale",
    icon="💨",
    description="Calcolo delle azioni del vento secondo NTC2018 e EN1991",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
        "EN1991",  # Eurocodice 1 — Azioni sul vento
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy"],
)


def create_engine():
    """
    Factory per il motore di calcolo azioni vento.

    Ritorna l'engine appropriato che implementa il calcolo
    delle azioni del vento per tutte le norme supportate.
    """
    from modules.vento.engine.dispatcher import VentoEngine

    return VentoEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo vento.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.vento.gui.window import VentoWindow

    return VentoWindow(MODULE_INFO, parent)


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
