"""
Modulo: Strutture Esistenti — Valutazione della sicurezza strutturale su edifici esistenti.

Supporta:
- NTC2018, Circolare 2019 — Valutazione e miglioramento sismico di edifici esistenti
- RD2229, DM72, DM87, ecc. — Norme storiche per analisi su edifici di interesse storico

Funzionalità:
- Capacità meccaniche dedotte da prove non distruttive (carotaggi, martinetti, ecc.)
- Valore caratteristico e medio con scarse informazioni
- Coefficiente di confidenza per incertezze costruttive
- Pericolosità sismica per siti specifici (nuova zonazione NTC2018)
- Analisi pushover per valutazione vulnerabilità sismica
- Indici di rischio (SAM, SLV, SLD)
- Strategie di rinforzo (FRP, iniezioni, confinamento)
"""

from pipeline.module_registry import ModuleInfo

MODULE_INFO = ModuleInfo(
    id="esistenti",
    name="Strutture Esistenti",
    version="1.0.0",
    category="strutturale",
    icon="🏛️",
    description="Valutazione della sicurezza strutturale su edifici esistenti secondo NTC2018",
    norms_supported=[
        "NTC2018",  # Normativa Tecnica Costruzioni 2018
        "RD2229",  # Regio Decreto 1939
        "DM72",  # D.M. 30/05/1972
        "DM87",  # D.M. 1987
    ],
    standalone=True,
    requires_libs=["PySide6 | PyQt6", "numpy", "scipy"],
)


def create_engine():
    """
    Factory per il motore di valutazione strutturale edifici esistenti.

    Ritorna l'engine appropriato che implementa le valutazioni
    di sicurezza per strutture esistenti.
    """
    from modules.esistenti.engine.dispatcher import EsistenziEngine

    return EsistenziEngine()


def create_window(parent=None):
    """
    Factory per la finestra GUI del modulo strutture esistenti.

    Ritorna la finestra principale con tab Input, Batch, Risultati, Tabulato.
    """
    from modules.esistenti.gui.window import EsistenziWindow

    return EsistenziWindow(MODULE_INFO, parent)


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
