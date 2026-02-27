"""
test_elements_repo.py

Test minimi per il repository degli elementi.
"""

from src.elements.element_model import Element
from src.elements.element_repo import ElementRepository


def test_add_and_get_element():
    repo = ElementRepository()
    e = Element(element_id="E1", type="beam", length_cm=300.0)
    repo.add_element(e)

    got = repo.get("E1")
    assert got is not None
    assert got.type == "beam"
