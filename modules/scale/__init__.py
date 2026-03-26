"""
Modulo: Scale — Progettazione e verifiche di scale (rampe e pianerottoli).

Supporta:
- NTC2018 — Scale in c.a., acciaio, legno, muratura
- EC3 — Eurocodice 3: Progettazione costruzioni in acciaio

Funzionalità:
- Dimensionamento rampe e pianerottoli
- Verifiche di resistenza (SLU) per diversi materiali
- Verifiche di esercizio (SLE): deformabilità, comfort
- Carico lineare equivalente per modellazione FEM
- Analisi stabilità strutturale (instabilità laterale, vibrazioni)
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="scale",
    name="Scale",
    version="1.0.0",
    category="strutturale",
    icon="🪜",
    description="Progettazione e verifiche di scale secondo NTC2018 e EC3",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
        "EC3",  # Eurocodice 3: Progettazione costruzioni in acciaio
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy"],
)


def create_engine():
    """
    Factory per il motore di calcolo scale.

    Ritorna l'engine appropriato che implementa il dimensionamento
    e le verifiche per tutte le norme supportate.
    """
    from modules.scale.engine.dispatcher import ScaleEngine

    return ScaleEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo scale.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.scale.gui.window import ScaleWindow

    return ScaleWindow(MODULE_INFO, parent)


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
