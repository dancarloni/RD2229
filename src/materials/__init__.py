"""Package materiali strutturali.

Fornisce modello dati, repository con persistenza, e validazione
per calcestruzzo, acciaio, e muratura.
"""

from .material_model import (
    Material,
    ParametroDerivato,
    crea_acciaio_ntc2018,
    crea_calcestruzzo_ntc2018,
    crea_muratura_ntc2018,
)
from .material_repo import MaterialRepository
from .validation import MaterialValidationError, validate_material

__all__ = [
    "Material",
    "MaterialRepository",
    "MaterialValidationError",
    "ParametroDerivato",
    "crea_acciaio_ntc2018",
    "crea_calcestruzzo_ntc2018",
    "crea_muratura_ntc2018",
    "validate_material",
]
