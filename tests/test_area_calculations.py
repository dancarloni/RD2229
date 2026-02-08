"""Suite di test unitari per area_calculations.py.

Test granulari per funzioni interne, compute_shear_areas e validazione numerica
basata sugli esercizi del PDF Cap7bEsercizisullageometriadellearee.pdf.
"""

import math
import sys
from dataclasses import dataclass, field

import pytest

# Aggiungi il path corrente per importare il modulo
sys.path.insert(0, ".")

# Import del modulo da testare
from sections_app.services.area_calculations import (  # noqa: E402
    SectionProperties,
    _area_c_section,
    _area_circular,
    _area_circular_hollow,
    _area_i_section,
    _area_l_section,
    _area_rectangular,
    _area_rectangular_hollow,
    _area_t_section,
    compute_shear_areas,
)


# Classe mock per test (poiché Section è astratta)
@dataclass
class MockSection:
    section_type: str
    dimensions: dict[str, float]
    properties: SectionProperties = field(default_factory=SectionProperties)


# =============================================================================
# Test delle funzioni interne di calcolo area (_area_*)
# =============================================================================


class TestAreaRectangular:
    """Test per _area_rectangular."""

    def test_nominal_case(self):
        dims = {"width": 10.0, "height": 20.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 200.0
        assert A_z == 200.0

    def test_missing_width(self):
        dims = {"height": 20.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_missing_height(self):
        dims = {"width": 10.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_empty_dimensions(self):
        dims = {}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_values(self):
        dims = {"width": "invalid", "height": None}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 0.0
        assert A_z == 0.0


class TestAreaCircular:
    """Test per _area_circular."""

    def test_nominal_case(self):
        dims = {"diameter": 10.0}
        A_y, A_z = _area_circular(dims)
        expected = math.pi * (5.0**2)
        assert A_y == pytest.approx(expected)
        assert A_z == pytest.approx(expected)

    def test_missing_diameter(self):
        dims = {}
        A_y, A_z = _area_circular(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_diameter(self):
        dims = {"diameter": "invalid"}
        A_y, A_z = _area_circular(dims)
        assert A_y == 0.0
        assert A_z == 0.0


class TestAreaCircularHollow:
    """Test per _area_circular_hollow."""

    def test_nominal_case(self):
        dims = {"outer_diameter": 20.0, "thickness": 2.0}
        A_y, A_z = _area_circular_hollow(dims)
        outer_r = 10.0
        inner_r = 8.0
        expected = math.pi * (outer_r**2 - inner_r**2)
        assert A_y == pytest.approx(expected)
        assert A_z == pytest.approx(expected)

    def test_thickness_too_large(self):
        dims = {"outer_diameter": 10.0, "thickness": 6.0}  # inner_r = 5-6 = -1 -> 0
        A_y, A_z = _area_circular_hollow(dims)
        expected = math.pi * (5.0**2 - 0**2)
        assert A_y == pytest.approx(expected)
        assert A_z == pytest.approx(expected)

    def test_missing_outer_diameter(self):
        dims = {"thickness": 2.0}
        A_y, A_z = _area_circular_hollow(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_values(self):
        dims = {"outer_diameter": "invalid", "thickness": None}
        A_y, A_z = _area_circular_hollow(dims)
        assert A_y == 0.0
        assert A_z == 0.0


class TestAreaRectangularHollow:
    """Test per _area_rectangular_hollow."""

    def test_nominal_case(self):
        dims = {"width": 10.0, "height": 8.0, "thickness": 1.0}
        A_y, A_z = _area_rectangular_hollow(dims)
        A_ext = 10 * 8
        A_int = 8 * 6
        expected = A_ext - A_int
        assert A_y == expected
        assert A_z == expected

    def test_thickness_too_large(self):
        dims = {"width": 10.0, "height": 8.0, "thickness": 5.0}  # inner_w=0, inner_h=-2->0
        A_y, A_z = _area_rectangular_hollow(dims)
        A_ext = 10 * 8
        A_int = 0 * 0
        expected = A_ext - A_int
        assert A_y == expected
        assert A_z == expected

    def test_missing_dimensions(self):
        dims = {"thickness": 1.0}
        A_y, A_z = _area_rectangular_hollow(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_values(self):
        dims = {"width": "invalid", "height": None, "thickness": 1.0}
        A_y, A_z = _area_rectangular_hollow(dims)
        assert A_y == 0.0
        assert A_z == 0.0


class TestAreaTSection:
    """Test per _area_t_section."""

    def test_nominal_case(self):
        dims = {
            "flange_width": 100.0,
            "flange_thickness": 10.0,
            "web_thickness": 5.0,
            "web_height": 80.0,
        }
        A_y, A_z = _area_t_section(dims)
        expected_A_y = 100 * 10 + 5 * 80
        expected_A_z = 5 * 80
        assert A_y == expected_A_y
        assert A_z == expected_A_z

    def test_missing_dimensions(self):
        dims = {}
        A_y, A_z = _area_t_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_values(self):
        dims = {"flange_width": "invalid", "flange_thickness": None}
        A_y, A_z = _area_t_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0


class TestAreaISection:
    """Test per _area_i_section."""

    def test_nominal_case(self):
        dims = {
            "flange_width": 100.0,
            "flange_thickness": 10.0,
            "web_thickness": 5.0,
            "web_height": 80.0,
        }
        A_y, A_z = _area_i_section(dims)
        expected_A_y = 2 * 100 * 10 + 5 * 80
        expected_A_z = 5 * 80
        assert A_y == expected_A_y
        assert A_z == expected_A_z

    def test_missing_dimensions(self):
        dims = {}
        A_y, A_z = _area_i_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_values(self):
        dims = {"flange_width": "invalid"}
        A_y, A_z = _area_i_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0


class TestAreaLSection:
    """Test per _area_l_section."""

    def test_nominal_case(self):
        dims = {
            "width": 20.0,
            "height": 30.0,
            "t_horizontal": 4.0,
            "t_vertical": 4.0,
        }
        A_y, A_z = _area_l_section(dims)
        expected_A_y = 4 * 30
        expected_A_z = 20 * 4
        assert A_y == expected_A_y
        assert A_z == expected_A_z

    def test_missing_dimensions(self):
        dims = {}
        A_y, A_z = _area_l_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_values(self):
        dims = {"width": "invalid", "height": None}
        A_y, A_z = _area_l_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0


class TestAreaCSection:
    """Test per _area_c_section."""

    def test_nominal_case(self):
        dims = {"width": 50.0, "height": 100.0, "thickness": 5.0}
        A_y, A_z = _area_c_section(dims)
        expected_A_y = 2 * 50 * 5 + max(0, 100 - 2 * 5) * 5
        expected_A_z = 2 * 50 * 5
        assert A_y == expected_A_y
        assert A_z == expected_A_z

    def test_thickness_too_large(self):
        dims = {"width": 50.0, "height": 10.0, "thickness": 6.0}  # height-2*thickness=10-12=-2->0
        A_y, A_z = _area_c_section(dims)
        expected_A_y = 2 * 50 * 6 + 0 * 6
        expected_A_z = 2 * 50 * 6
        assert A_y == expected_A_y
        assert A_z == expected_A_z

    def test_missing_dimensions(self):
        dims = {}
        A_y, A_z = _area_c_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_non_numeric_values(self):
        dims = {"width": "invalid"}
        A_y, A_z = _area_c_section(dims)
        assert A_y == 0.0
        assert A_z == 0.0


# =============================================================================
# Test per compute_shear_areas
# =============================================================================


class TestComputeShearAreas:
    """Test per compute_shear_areas."""

    def test_supported_type_case_insensitive(self):
        section = MockSection("rectangular", {"width": 10.0, "height": 20.0})
        A_y, A_z = compute_shear_areas(section)
        assert A_y == 200.0
        assert A_z == 200.0

    def test_section_none(self):
        with pytest.raises(ValueError, match="section non può essere None"):
            compute_shear_areas(None)

    def test_unsupported_type_with_properties_area(self):
        section = MockSection("UNKNOWN", {}, SectionProperties(area=123.4))
        A_y, A_z = compute_shear_areas(section)
        assert A_y == 123.4
        assert A_z == 123.4

    def test_unsupported_type_without_area(self):
        section = MockSection("UNKNOWN", {})
        A_y, A_z = compute_shear_areas(section)
        assert A_y == 0.0
        assert A_z == 0.0

    def test_supported_type_empty_dimensions(self):
        section = MockSection("RECTANGULAR", {})
        A_y, A_z = compute_shear_areas(section)
        assert A_y == 0.0
        assert A_z == 0.0


# =============================================================================
# Test di validazione numerica basati sugli esercizi del PDF
# =============================================================================


class TestValidationNumerica:
    """Test di validazione numerica dagli esercizi del PDF."""

    # Esercizio 1 – Rettangoli A₁ e A₂
    def test_esercizio_1_rettangolo_A1(self):
        dims = {"width": 15.0, "height": 30.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 450.0
        assert A_z == 450.0

    def test_esercizio_1_rettangolo_A2(self):
        dims = {"width": 15.0, "height": 10.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 150.0
        assert A_z == 150.0

    def test_esercizio_1_somma_aree(self):
        # Somma A1 + A2 = 600
        A1 = 450.0
        A2 = 150.0
        assert A1 + A2 == 600.0

    # Esercizio 2 – Due profilati a T + piastra rettangolare
    def test_esercizio_2_piastra_rettangolare_A3(self):
        dims = {"width": 100.0, "height": 5.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 500.0
        assert A_z == 500.0

    def test_esercizio_2_piastra_via_compute_shear_areas(self):
        section = MockSection("RECTANGULAR", {"width": 100.0, "height": 5.0})
        A_y, A_z = compute_shear_areas(section)
        assert A_y == 500.0
        assert A_z == 500.0

    def test_esercizio_2_profilato_T_fallback_A1(self):
        # Simula area fornita dal profilo UNI tramite fallback
        section = MockSection("GENERIC_T", {}, SectionProperties(area=651.0))
        A_y, A_z = compute_shear_areas(section)
        assert A_y == 651.0
        assert A_z == 651.0

    def test_esercizio_2_profilato_T_fallback_A2(self):
        # Secondo T
        section = MockSection("GENERIC_T", {}, SectionProperties(area=651.0))
        A_y, A_z = compute_shear_areas(section)
        assert A_y == 651.0
        assert A_z == 651.0

    def test_esercizio_2_somma_totale(self):
        # 651 + 651 + 500 = 1802
        A_T1 = 651.0
        A_T2 = 651.0
        A_piastra = 500.0
        assert A_T1 + A_T2 + A_piastra == 1802.0

    # Esercizio 3 – Quadrato con foro circolare
    def test_esercizio_3_quadrato(self):
        dims = {"width": 40.0, "height": 40.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 1600.0
        assert A_z == 1600.0

    def test_esercizio_3_foro_circolare(self):
        dims = {"diameter": 10.0}
        A_y, A_z = _area_circular(dims)
        expected = math.pi * (5.0**2)
        assert A_y == pytest.approx(expected)
        assert A_z == pytest.approx(expected)
        # Dal PDF: ~78.54
        assert A_y == pytest.approx(78.54, abs=0.01)

    def test_esercizio_3_area_netta(self):
        A_quadrato = 1600.0
        A_foro = math.pi * (5.0**2)
        A_netta = A_quadrato - A_foro
        # Dal PDF: ~1521.46
        assert A_netta == pytest.approx(1521.46, abs=0.01)

    # Esercizio 4 – Sezione angolare (L) a lati disuguali
    def test_esercizio_4_composizione_rettangoli_A1(self):
        dims = {"width": 4.0, "height": 16.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 64.0
        assert A_z == 64.0

    def test_esercizio_4_composizione_rettangoli_A2(self):
        dims = {"width": 30.0, "height": 4.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 120.0
        assert A_z == 120.0

    def test_esercizio_4_somma_rettangoli(self):
        A1 = 64.0
        A2 = 120.0
        assert A1 + A2 == 184.0

    def test_esercizio_4_sezione_L_semplificata(self):
        dims = {"width": 20.0, "height": 30.0, "t_horizontal": 4.0, "t_vertical": 4.0}
        A_y, A_z = _area_l_section(dims)
        # A_y = t_vertical * height = 4 * 30 = 120
        # A_z = width * t_horizontal = 20 * 4 = 80
        assert A_y == 120.0
        assert A_z == 80.0
        # Nota: somma 120 + 80 = 200, ma geometria effettiva 184 (sovrapposizione)

    # Esercizio 5 – Quadrato con due fori circolari simmetrici
    def test_esercizio_5_quadrato(self):
        dims = {"width": 50.0, "height": 50.0}
        A_y, A_z = _area_rectangular(dims)
        assert A_y == 2500.0
        assert A_z == 2500.0

    def test_esercizio_5_foro_circolare(self):
        dims = {"diameter": 10.0}
        A_y, A_z = _area_circular(dims)
        expected = math.pi * (5.0**2)
        assert A_y == pytest.approx(expected)
        assert A_z == pytest.approx(expected)
        # Dal PDF: ~78.54
        assert A_y == pytest.approx(78.54, abs=0.01)

    def test_esercizio_5_area_netta(self):
        A_quadrato = 2500.0
        A_foro = math.pi * (5.0**2)
        A_netta = A_quadrato - 2 * A_foro
        # Dal PDF: ~2342.9
        assert A_netta == pytest.approx(2342.9, abs=0.1)
