"""
Modulo: FEM/Telai — Analisi strutturale FEM e calcolo telai piani/spaziali.

Supporta:
- NTC2018 — Analisi elastica lineare, non lineare geometrica (P-Δ)

Funzionalità:
- Assemblaggio matrice rigidezza globale
- Soluzione sistemi lineari (sparse, iterativi)
- Calcolo spostamenti, reazioni, sollecitazioni interne
- Analisi modale (autovalori, autovettori)
- Analisi instabilità (autovalori di carico critico)
- Esportazione risultati (grafico deformata, diagrammi sollecitazioni)
- Interfaccia con risolutori FEM standard (OpenSees, Ansys APDL)
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="fem_telaio",
    name="FEM/Telai",
    version="1.0.0",
    category="utility",
    icon="🔗",
    description="Analisi strutturale FEM e calcolo telai piani/spaziali secondo NTC2018",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy", "scipy"],
)


def create_engine():
    """
    Factory per il motore FEM/telai.

    Ritorna l'engine appropriato che implementa l'analisi
    strutturale con metodo degli elementi finiti.
    """
    from modules.fem_telaio.engine.dispatcher import FemTelaioEngine

    return FemTelaioEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo FEM/Telai.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.fem_telaio.gui.window import FemTelaioWindow

    return FemTelaioWindow(MODULE_INFO, parent)


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
