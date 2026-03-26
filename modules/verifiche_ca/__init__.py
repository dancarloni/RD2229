"""
Modulo: Verifiche c.a. — Verifiche di resistenza e durabilità del calcestruzzo armato.

Supporta verifiche secondo:
- RD2229 (Regio Decreto 1939) — Tensioni ammissibili
- DM72, DM74, DM76 — Normative storiche
- DM92, DM96 — Normative miste
- NTC2008, NTC2018 — Normative attuali (SLU/SLE)

Tipi verifica:
- Flessione retta e deviata
- Pressoflessione
- Taglio
- Torsione
- Combinazioni T+Torsione
- SLE: Tensioni, Fessurazione, Deformabilità
- Elementi secondari
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="verifiche_ca",
    name="Verifiche c.a.",
    version="1.0.0",
    category="strutturale",
    icon="🏗️",
    description="Verifiche di resistenza e durabilità del calcestruzzo armato",
    norms_supported=[
        "RD2229",  # Tensioni ammissibili
        "DM72",  # D.M. 30/05/1972
        "DM74",  # D.M. 21/01/1974
        "DM76",  # D.M. 14/04/1976
        "DM92",  # D.M. 14/02/1992
        "DM96",  # D.M. 09/01/1996
        "NTC2008",  # Normativa Tecnica Costruzioni 2008
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy"],
)


def create_engine():
    """
    Factory per il motore di calcolo verifiche c.a.

    Ritorna l'engine appropriato che implementa le verifiche
    per tutte le norme supportate.
    """
    from modules.verifiche_ca.engine.dispatcher import VerificheCaEngine

    return VerificheCaEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo verifiche c.a.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.verifiche_ca.gui.window import VerificheCaWindow

    return VerificheCaWindow(MODULE_INFO, parent)


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
