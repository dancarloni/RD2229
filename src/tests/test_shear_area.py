"""
test_shear_area.py

Test minimi per il modulo:
    src/calc/shear_area_registry.py

Gli obiettivi dei test:
- Verificare che il registry funzioni.
- Verificare che compute_shear_area restituisca tuple valide.
- Verificare comportamento fallback.

STUB S2: test semplici, non completi.
"""

import pytest
from src.calc.shear_area_registry import compute_shear_area


class DummyRectSection:
    """Sezione rettangolare dummy per test."""
    def __init__(self):
        self.shape_id = "rectangle"
        self.area_cm2 = 100.0
        self.kappa_x = None
        self.kappa_y = None


class DummyUnknownSection:
    """Sezione sconosciuta → fallback."""
    def __init__(self):
        self.shape_id = "unknown"
        self.area_cm2 = 50.0
        self.kappa_x = 0.8
        self.kappa_y = 0.7


def test_rectangular_shear_area():
    sec = DummyRectSection()
    Asx, Asy = compute_shear_area(sec)
    assert Asx > 0
    assert Asy > 0


def test_fallback_shear_area():
    sec = DummyUnknownSection()
    Asx, Asy = compute_shear_area(sec)
    assert Asx == pytest.approx(0.8 * 50.0)
    assert Asy == pytest.approx(0.7 * 50.0)
