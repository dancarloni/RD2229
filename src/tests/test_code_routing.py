"""
test_code_routing.py

Test minimi per:
    src/codes/code_registry.py

Verifica che:
- il registry possa registrare una normativa
- la funzione get_code funzioni correttamente
"""

from src.codes.code_registry import register_code, get_code


def test_register_and_get_code():
    params = {"gamma_c": 1.5}
    clauses = {"general": {"title": "Test"}}

    register_code("TESTCODE", params, clauses)
    retrieved = get_code("TESTCODE")

    assert retrieved is not None
    assert retrieved["params"]["gamma_c"] == 1.5
    assert retrieved["clauses"]["general"]["title"] == "Test"
