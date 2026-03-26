"""
Modulo: Geotecnica — Analisi e verifiche geotecniche (fondazioni, spinte, cedimenti).

Supporta:
- NTC2018 — Verifiche SLU/SLE per fondazioni, scavi, spinte
- EC7 — Eurocodice 7: Progettazione geotecnica

Funzionalità:
- Capacità portante fondazioni (Terzaghi, Hansen, etc.)
- Spinte del terreno (Coulomb, Rankine, logaritmica)
- Cedimenti immediati e di consolidazione
- Stabilità di scavi e pendii
- Prove geotecniche (SPT, CPT conversioni)
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="geotecnica",
    name="Geotecnica",
    version="1.0.0",
    category="strutturale",
    icon="⛰️",
    description="Analisi e verifiche geotecniche secondo NTC2018 e EC7",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
        "EC7",  # Eurocodice 7: Progettazione geotecnica
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy", "scipy"],
)


def create_engine():
    """
    Factory per il motore di calcolo geotecnico.

    Ritorna l'engine appropriato che implementa le verifiche
    per tutte le norme supportate.
    """
    from modules.geotecnica.engine.dispatcher import GeotecnicaEngine

    return GeotecnicaEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo geotecnica.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.geotecnica.gui.window import GeotecnicaWindow

    return GeotecnicaWindow(MODULE_INFO, parent)


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
