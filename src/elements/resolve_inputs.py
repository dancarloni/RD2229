"""Risoluzione input per la pipeline di verifica.

Raccoglie dati da element_repo, material_repo e configurazione utente,
producendo una struttura pronta per action_repo e report renderers.
"""

from __future__ import annotations

import logging
from typing import Any

from ..materials.material_repo import MaterialRepository
from .element_repo import ElementRepository

logger = logging.getLogger(__name__)


def resolve_verification_inputs(
    element_repo: ElementRepository,
    material_repo: MaterialRepository,
    user_config: dict[str, Any],
) -> dict[str, Any]:
    """Risolve gli input e costruisce la struttura per le verifiche.

    Args:
        element_repo: repository elementi (già popolato).
        material_repo: repository materiali (già popolato).
        user_config: configurazione utente (norm_code, checks, settings, ecc.).

    Returns:
        Dizionario con: project_name, norm_code, elements, materials,
        normative, settings, error_list.
    """
    errors: list[str] = []

    norm_code = user_config.get("norm_code", "NTC2018")
    project_name = user_config.get("project_name", "Progetto")

    # Raccogli tutti gli elementi con dati di verifica
    elements_data: list[dict[str, Any]] = []
    for el in element_repo.list_all():
        el_dict = el.to_verification_dict()

        if el.material is None:
            errors.append(f"Elemento '{el.element_id}': materiale non assegnato.")
        else:
            el_dict["material_id"] = el.material.material_id

        elements_data.append(el_dict)

    if not elements_data:
        errors.append("Nessun elemento nel repository.")

    # Costruisci contesto normativo dal materiale di default o config
    normative: dict[str, Any] = {"norm_code": norm_code}

    # Parametri materiale dal primo elemento con materiale assegnato
    mat_params: dict[str, float] = {}
    for el in element_repo.list_all():
        if el.material is not None:
            m = el.material
            for key in ("f_ck", "f_cd", "f_yd", "f_yk", "E_cm", "E_s",
                        "f_ctm", "sigma_c_adm", "sigma_s_adm",
                        "tau_c1_adm", "n_omogenizzazione", "gamma_c", "gamma_s"):
                val = m.get_param(key)
                if val is not None:
                    mat_params[key] = float(val)
            break

    # Override da user_config
    mat_params.update(user_config.get("material_overrides", {}))
    normative["material"] = mat_params

    # Settings
    settings: dict[str, Any] = {
        "w_lim_mm": user_config.get("w_lim_mm", 0.3),
    }
    settings.update(user_config.get("settings", {}))

    # Checks richiesti
    checks = user_config.get("checks", [])

    # Materiali serializzati
    materials_data = []
    for mat in material_repo.list_all():
        materials_data.append(mat.to_dict())

    return {
        "project_name": project_name,
        "norm_code": norm_code,
        "elements": elements_data,
        "materials": materials_data,
        "normative": normative,
        "settings": settings,
        "checks": checks,
        "error_list": errors,
    }
