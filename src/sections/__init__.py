"""Bridge verso il modulo sezioni canonico (apps/sections/).

Re-esporta le classi principali per consentire al codice sotto src/
di importare da src.sections senza duplicare implementazioni.
"""

from apps.sections.geometry_model import (
    CoreData,
    EllipseData,
    SectionGeometry,
)
from apps.sections.geometry_model import (
    SectionProperties as GeometrySectionProperties,
)
from apps.sections.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    Section,
    SectionProperties,
    TSection,
    VSection,
)

__all__ = [
    "CircularHollowSection",
    "CircularSection",
    "CoreData",
    "CSection",
    "EllipseData",
    "GeometrySectionProperties",
    "ISection",
    "InvertedTSection",
    "LSection",
    "PiSection",
    "RectangularHollowSection",
    "RectangularSection",
    "Section",
    "SectionGeometry",
    "SectionProperties",
    "TSection",
    "VSection",
]
