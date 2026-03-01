# Shim per compatibilità test e GUI: re-esporta compute_section_properties
try:
    from src.core_calculus.core.section_properties import (
        SectionProperties,
        compute_section_properties,
    )
except ImportError:
    compute_section_properties = None
    SectionProperties = None
