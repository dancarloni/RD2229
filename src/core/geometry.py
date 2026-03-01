# Shim per compatibilità test e GUI: re-esporta tutte le sezioni geometriche principali
try:
    from src.core_calculus.core.geometry import (
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
