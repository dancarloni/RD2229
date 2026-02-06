from __future__ import annotations
from typing import Optional
import logging

from app.domain.models import VerificationInput, VerificationOutput
from app.verification.engine_adapter import compute_with_engine
from app.verification.methods_ta import compute_ta_verification
from app.verification.methods_slu import compute_slu_verification
from app.verification.methods_sle import compute_sle_verification

logger = logging.getLogger(__name__)


def compute_verification_result(
    _input: VerificationInput,
    section_repository: Optional[object] = None,
    material_repository: Optional[object] = None,
) -> VerificationOutput:
    method = (_input.verification_method or "").upper().strip()

    if method in ("TA", "SLU", "SLE"):
        engine_result = compute_with_engine(_input, section_repository, material_repository)
        if engine_result is not None:
            return engine_result

    if method == "TA":
        return compute_ta_verification(_input, section_repository, material_repository)
    elif method == "SLU":
        return compute_slu_verification(_input, section_repository, material_repository)
    elif method == "SLE":
        return compute_sle_verification(_input, section_repository, material_repository)
    elif method in ("SANT", "PLACEHOLDER"):
        from app.verification.methods_ta import compute_ta_verification as _placeholder

        return _placeholder(_input, section_repository, material_repository)

    return VerificationOutput(
        sigma_c_max=0.0,
        sigma_c_min=0.0,
        sigma_s_max=0.0,
        asse_neutro=0.0,
        deformazioni="",
        coeff_sicurezza=0.0,
        esito="ERRORE",
        messaggi=[
            "Metodo di verifica non specificato o sconosciuto: '{}'".format(method),
            "Selezionare un metodo dalla colonna 'Metodo verifica': TA, SLU, SLE, SANT",
        ],
    )
