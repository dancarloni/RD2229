"""
Modulo: Fuoco — Analisi e verifiche della resistenza al fuoco.

Supporta:
- NTC2018 — Resistenza al fuoco in strutture c.a., acciaio, legno
- ISO834 — Curva di incendio standard

Funzionalità:
- Verifiche di resistenza al fuoco per elementi strutturali
- Curve di incendio (ISO834, naturale, parametrica)
- Metodi tabellari e analitici
- Isolamento termico e riduzione delle proprietà materiali
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="fuoco",
    name="Fuoco ISO 834",
    version="1.0.0",
    category="strutturale",
    icon="🔥",
    description="Analisi e verifiche della resistenza al fuoco secondo NTC2018 e ISO834",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
        "ISO834",  # Curva di incendio standard
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy"],
)


def create_engine():
    """
    Factory per il motore di calcolo resistenza fuoco.

    Ritorna l'engine appropriato che implementa le verifiche
    per tutte le norme supportate.
    """
    from modules.fuoco.engine.dispatcher import FuocoEngine

    return FuocoEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo fuoco.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.fuoco.gui.window import FuocoWindow

    return FuocoWindow(MODULE_INFO, parent)


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
