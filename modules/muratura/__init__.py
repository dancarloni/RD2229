"""
Modulo: Muratura — Verifiche di resistenza per strutture in muratura.

Supporta:
- NTC2018 — Muri in muratura ordinaria, armata, confinata
- DM87 — Decreto Ministeriale 1987 (muratura)

Funzionalità:
- Pressoflessione fuori piano e nel piano
- Verifiche a taglio (meccanismi diagonali)
- Verifiche di spallamento
- Combinazioni di carico per muratura
- Metodi di analisi globale e per macroelementi
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="muratura",
    name="Muratura",
    version="1.0.0",
    category="strutturale",
    icon="🧱",
    description="Verifiche di resistenza per strutture in muratura secondo NTC2018 e DM87",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
        "DM87",  # Decreto Ministeriale 1987
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy"],
)


def create_engine():
    """
    Factory per il motore di calcolo verifiche muratura.

    Ritorna l'engine appropriato che implementa le verifiche
    per tutte le norme supportate.
    """
    from modules.muratura.engine.dispatcher import MuratturaEngine

    return MuratturaEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo muratura.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.muratura.gui.window import MuratturaWindow

    return MuratturaWindow(MODULE_INFO, parent)


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
