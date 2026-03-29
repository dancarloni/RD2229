"""Core pipeline and results for RD2229.

Shim: re-exports geometry for test compatibility (core.geometry → core_calculus.core.geometry).

Esporta anche l'adapter centralizzato per le conversioni di unità di misura.
Importare le funzioni di conversione da:
    from src.core.adapter_unita_misura import mpa_to_kg_cm2, kg_cm2_to_mpa, ...
"""

# Re-esporta tutte le classi geometriche principali per compatibilità test/GUI
try:
    from core_calculus.core.geometry import (
        CircularHollowSection,
        CircularSection,
        InvertedTSection,
        ISection,
        LSection,
        PiSection,
        RectangularHollowSection,
        RectangularSection,
        SectionGeometry,
        TSection,
    )
except ImportError:
    SectionGeometry = None
    RectangularSection = None
    CircularSection = None
    TSection = None
    LSection = None
    ISection = None
    InvertedTSection = None
    PiSection = None
    RectangularHollowSection = None
    CircularHollowSection = None
