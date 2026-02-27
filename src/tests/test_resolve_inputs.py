"""
test_resolve_inputs.py

Test minimi per:
    src/elements/resolve_inputs.py

Controlliamo:
- La struttura base dell'output
- Che non sollevi errori
"""

from src.elements.resolve_inputs import resolve_verification_inputs
from src.elements.element_repo import ElementRepository
from src.materials.material_repo import MaterialRepository


def test_resolve_inputs_structure():
    repo_e = ElementRepository()
    repo_m = MaterialRepository()

    result = resolve_verification_inputs(repo_e, repo_m, {})

    assert isinstance(result, dict)
    assert "elements" in result
    assert "materials" in result
    assert "settings" in result
    assert "normative" in result
    assert "load_cases" in result
    assert "error_list" in result
