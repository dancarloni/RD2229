"""Core pipeline and results for RD2229.

Shim: re-exports geometry for test compatibility (core.geometry → core_calculus.core.geometry).
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
