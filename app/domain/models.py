from __future__ import annotations

from dataclasses import dataclass, InitVar
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class VerificationInput:
    element_name: str = ""
    section_id: str = ""
    verification_method: str = "TA"
    material_concrete: str = ""
    material_steel: str = ""
    n_homog: float = 15.0
    N: float = 0.0
    Mx: float = 0.0
    My: float = 0.0
    Mz: float = 0.0
    Tx: float = 0.0
    Ty: float = 0.0
    As_sup: float = 0.0
    As_inf: float = 0.0
    At: float = 0.0
    d_sup: float = 0.0
    d_inf: float = 0.0
    stirrup_step: float = 0.0
    stirrup_diameter: float = 0.0
    stirrup_material: str = ""
    notes: str = ""
    # Legacy Init vars to accept old keywords M and T in constructor
    M: InitVar[Optional[float]] = None
    T: InitVar[Optional[float]] = None

    def __post_init__(self, M: Optional[float], T: Optional[float]) -> None:
        # Map legacy init kwargs to new internal fields for backward compatibility
        if M is not None:
            try:
                self.Mx = M
            except Exception:
                self.__dict__["Mx"] = M
        if T is not None:
            try:
                self.Ty = T
            except Exception:
                self.__dict__["Ty"] = T

        # Ensure numeric fields exist as instance attributes (avoid unexpected property objects)
        for field_name in ("Mx", "My", "Mz", "Tx", "Ty", "At", "As_sup", "As_inf"):
            val = self.__dict__.get(field_name, None)
            if not isinstance(val, (int, float)):
                try:
                    candidate = getattr(self, field_name)
                    if isinstance(candidate, (int, float)):
                        self.__dict__[field_name] = candidate
                    else:
                        self.__dict__[field_name] = 0.0
                except Exception:
                    self.__dict__[field_name] = 0.0

    # Legacy field support for backward compatibility via properties
    @property
    def M(self) -> float:
        return self.Mx

    @M.setter
    def M(self, value: float):
        self.Mx = value

    @property
    def T(self) -> float:
        return self.Ty

    @T.setter
    def T(self, value: float):
        self.Ty = value


@dataclass
class VerificationOutput:
    sigma_c_max: float
    sigma_c_min: float
    sigma_s_max: float
    asse_neutro: float
    asse_neutro_x: float = 0.0
    asse_neutro_y: float = 0.0
    inclinazione_asse_neutro: float = 0.0
    tipo_verifica: str = ""
    sigma_c: float = 0.0
    sigma_s_tesi: float = 0.0
    sigma_s_compressi: float = 0.0
    deformazioni: str = ""
    coeff_sicurezza: float = 1.0
    esito: str = ""
    messaggi: List[str] = None

    def __post_init__(self):
        if self.messaggi is None:
            self.messaggi = []
