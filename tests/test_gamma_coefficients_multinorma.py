"""Controlli di coerenza coefficienti gamma multi-norma.

Obiettivo:
- garantire allineamento tra cataloghi materiali, metodi di verifica e registry.
- intercettare regressioni su gamma_c/gamma_s nelle norme principali.
"""

from __future__ import annotations

from src.core_calculus.normative_registry import get_dm96_templates, get_ntc2018_templates
from src.materials.material_repo import MaterialRepository
from src.methods.dm92.checks import GAMMA_C_DM92, GAMMA_S_DM92


def test_dm92_constants_are_project_aligned() -> None:
    """DM92 nel progetto usa gamma_c=1.6 e gamma_s=1.15."""
    assert GAMMA_C_DM92 == 1.6
    assert GAMMA_S_DM92 == 1.15


def test_catalog_gamma_values_by_norm() -> None:
    """I cataloghi devono mantenere i gamma attesi per le norme principali."""
    repo = MaterialRepository()
    repo.carica_tutti_cataloghi()

    expected_gamma_c = {
        "RD2229": 1.0,
        "DM72": 1.0,
        "DM92": 1.6,
        "DM96": 1.6,
        "NTC2008": 1.5,
        "NTC2018": 1.5,
        "OPCM3274": 1.6,
    }

    expected_gamma_s = {
        "RD2229": 1.0,
        "DM72": 1.0,
        "DM92": 1.15,
        "DM96": 1.15,
        "NTC2008": 1.15,
        "NTC2018": 1.15,
        "OPCM3274": 1.15,
    }

    for norma, gamma_c in expected_gamma_c.items():
        concretes = [m for m in repo.list_by_norma(norma) if m.famiglia == "calcestruzzo"]
        assert concretes, f"Nessun calcestruzzo trovato per norma {norma}"
        assert all(m.gamma_c == gamma_c for m in concretes)

    for norma, gamma_s in expected_gamma_s.items():
        steels = [m for m in repo.list_by_norma(norma) if m.famiglia == "acciaio"]
        assert steels, f"Nessun acciaio trovato per norma {norma}"
        assert all(m.gamma_s == gamma_s for m in steels)


def test_dm96_registry_templates_expose_expected_gamma() -> None:
    """Le verifiche SLU DM96 nel registry devono esporre gamma_c=1.6/gamma_s=1.15."""
    dm96_templates = get_dm96_templates()
    slu_templates = [t for t in dm96_templates if t.limit_state == "SLU"]

    assert slu_templates, "Nessun template SLU DM96 trovato"

    # Controllo solo i template che dichiarano esplicitamente gamma in extra_params.
    with_gamma = [
        t for t in slu_templates if "gamma_c" in t.extra_params or "gamma_s" in t.extra_params
    ]
    assert with_gamma, "Nessun template SLU DM96 con gamma espliciti"

    for template in with_gamma:
        gamma_c = template.extra_params.get("gamma_c", 1.6)
        gamma_s = template.extra_params.get("gamma_s", 1.15)
        assert gamma_c == 1.6, f"{template.template_id}: gamma_c={gamma_c}"
        assert gamma_s == 1.15, f"{template.template_id}: gamma_s={gamma_s}"


def test_ntc2018_registry_slu_templates_gamma_baseline() -> None:
    """I template NTC2018 con gamma espliciti devono rimanere sul baseline 1.5/1.15."""
    ntc_templates = get_ntc2018_templates()
    slu_templates = [t for t in ntc_templates if t.limit_state == "SLU"]
    with_gamma = [
        t for t in slu_templates if "gamma_c" in t.extra_params or "gamma_s" in t.extra_params
    ]

    for template in with_gamma:
        gamma_c = template.extra_params.get("gamma_c", 1.5)
        gamma_s = template.extra_params.get("gamma_s", 1.15)
        assert gamma_c == 1.5, f"{template.template_id}: gamma_c={gamma_c}"
        assert gamma_s == 1.15, f"{template.template_id}: gamma_s={gamma_s}"
