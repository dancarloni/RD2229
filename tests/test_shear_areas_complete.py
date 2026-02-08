"""Test per le aree a taglio e i fattori di correzione shear.

Verifica che tutti i 12 tipi di sezione abbiano handler per le aree a taglio
e che i fattori kappa siano correttamente assegnati e utilizzati.
"""

import math
import sys
from dataclasses import dataclass, field

import pytest

sys.path.insert(0, ".")

from sections_app.services.area_calculations import (
    _area_c_section,
    _area_circular,
    _area_circular_hollow,
    _area_i_section,
    _area_inverted_t_section,
    _area_inverted_v_section,
    _area_l_section,
    _area_pi_section,
    _area_rectangular,
    _area_rectangular_hollow,
    _area_t_section,
    _area_v_section,
    compute_shear_areas,
)
from sections_app.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    InvertedVSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    TSection,
    VSection,
    DEFAULT_SHEAR_KAPPAS,
)
from sections_app.shear_factors import DEFAULT_SHEAR_FACTORS, get_default_shear_factor


# Mock section for testing compute_shear_areas
@dataclass
class MockSection:
    section_type: str
    dimensions: dict[str, float] = field(default_factory=dict)
    properties: object = None


class TestNewShearAreaHandlers:
    """Test the newly added shear area handler functions."""

    def test_inverted_t_same_as_t(self):
        """INVERTED_T_SECTION should produce same shear areas as T_SECTION."""
        dims = {
            "flange_width": 20,
            "flange_thickness": 3,
            "web_thickness": 2,
            "web_height": 17,
        }
        ay_t, az_t = _area_t_section(dims)
        ay_it, az_it = _area_inverted_t_section(dims)
        assert ay_it == ay_t
        assert az_it == az_t

    def test_pi_section_double_web(self):
        """PI_SECTION should have A_z based on two webs."""
        dims = {
            "flange_width": 30,
            "flange_thickness": 3,
            "web_thickness": 2,
            "web_height": 20,
        }
        ay, az = _area_pi_section(dims)
        # A_z = 2 * web_thickness * web_height = 2*2*20 = 80
        assert az == pytest.approx(80.0)
        # A_y = 2 * web_thickness * web_height + flange_width * flange_thickness
        assert ay == pytest.approx(2 * 2 * 20 + 30 * 3)

    def test_v_section_uses_total_area(self):
        """V_SECTION falls back to total area."""
        dims = {"width": 20, "height": 15, "thickness": 2}
        ay, az = _area_v_section(dims)
        half_w = 10
        length = math.sqrt(half_w**2 + 15**2)
        expected = 2 * length * 2
        assert ay == pytest.approx(expected)
        assert az == pytest.approx(expected)

    def test_inverted_v_same_as_v(self):
        """INVERTED_V_SECTION produces same as V_SECTION."""
        dims = {"width": 20, "height": 15, "thickness": 2}
        ay_v, az_v = _area_v_section(dims)
        ay_iv, az_iv = _area_inverted_v_section(dims)
        assert ay_iv == ay_v
        assert az_iv == az_v

    def test_l_section_directional(self):
        """L_SECTION should have different A_y and A_z."""
        dims = {"width": 100, "height": 80, "t_horizontal": 10, "t_vertical": 10}
        ay, az = _area_l_section(dims)
        # A_y = t_vertical * height = 10 * 80 = 800
        assert ay == pytest.approx(800.0)
        # A_z = width * t_horizontal = 100 * 10 = 1000
        assert az == pytest.approx(1000.0)


class TestComputeShearAreasAllTypes:
    """Verify compute_shear_areas works for all 12 section types."""

    @pytest.mark.parametrize(
        "section_type,dims",
        [
            ("RECTANGULAR", {"width": 30, "height": 50}),
            ("CIRCULAR", {"diameter": 20}),
            ("CIRCULAR_HOLLOW", {"outer_diameter": 30, "thickness": 3}),
            ("RECTANGULAR_HOLLOW", {"width": 30, "height": 50, "thickness": 3}),
            ("T_SECTION", {"flange_width": 20, "flange_thickness": 3, "web_thickness": 2, "web_height": 17}),
            ("I_SECTION", {"flange_width": 20, "flange_thickness": 3, "web_thickness": 2, "web_height": 14}),
            ("L_SECTION", {"width": 100, "height": 80, "t_horizontal": 10, "t_vertical": 10}),
            ("C_SECTION", {"width": 20, "height": 40, "thickness": 3}),
            ("INVERTED_T_SECTION", {"flange_width": 20, "flange_thickness": 3, "web_thickness": 2, "web_height": 17}),
            ("PI_SECTION", {"flange_width": 30, "flange_thickness": 3, "web_thickness": 2, "web_height": 20}),
            ("V_SECTION", {"width": 20, "height": 15, "thickness": 2}),
            ("INVERTED_V_SECTION", {"width": 20, "height": 15, "thickness": 2}),
        ],
    )
    def test_all_types_return_positive(self, section_type, dims):
        sec = MockSection(section_type=section_type, dimensions=dims)
        ay, az = compute_shear_areas(sec)
        assert ay > 0, f"{section_type}: A_y should be > 0"
        assert az > 0, f"{section_type}: A_z should be > 0"


class TestShearFactorsComplete:
    """Verify all section types have shear factors defined."""

    @pytest.mark.parametrize(
        "section_type",
        [
            "RECTANGULAR",
            "CIRCULAR",
            "CIRCULAR_HOLLOW",
            "RECTANGULAR_HOLLOW",
            "T_SECTION",
            "I_SECTION",
            "L_SECTION",
            "C_SECTION",
            "INVERTED_T_SECTION",
            "PI_SECTION",
            "V_SECTION",
            "INVERTED_V_SECTION",
        ],
    )
    def test_shear_factor_defined(self, section_type):
        """Each section type should have a non-zero default shear factor."""
        factor = get_default_shear_factor(section_type)
        assert factor > 0, f"{section_type}: shear factor should be > 0"

    @pytest.mark.parametrize(
        "section_type",
        [
            "RECTANGULAR",
            "CIRCULAR",
            "CIRCULAR_HOLLOW",
            "RECTANGULAR_HOLLOW",
            "T_SECTION",
            "I_SECTION",
            "L_SECTION",
            "C_SECTION",
            "INVERTED_T_SECTION",
            "PI_SECTION",
            "V_SECTION",
            "INVERTED_V_SECTION",
        ],
    )
    def test_kappa_pair_defined(self, section_type):
        """Each section type should have kappa (y, z) pair in DEFAULT_SHEAR_KAPPAS."""
        assert section_type in DEFAULT_SHEAR_KAPPAS, (
            f"{section_type} missing from DEFAULT_SHEAR_KAPPAS"
        )
        ky, kz = DEFAULT_SHEAR_KAPPAS[section_type]
        assert ky > 0
        assert kz > 0


class TestKappaAppliedToSection:
    """Verify that kappa values are applied when computing section properties."""

    def test_default_kappa_applied(self):
        """When no user kappa is set, defaults should be applied."""
        sec = RectangularSection("r", 30, 50)
        sec.compute_properties()
        assert sec.shear_factor_y is not None
        assert sec.shear_factor_z is not None
        assert sec.shear_factor_y == pytest.approx(5.0 / 6.0)
        assert sec.shear_factor_z == pytest.approx(5.0 / 6.0)

    def test_user_kappa_preserved(self):
        """User-specified kappa should be used instead of defaults."""
        sec = RectangularSection("r", 30, 50)
        sec.shear_factor_y = 0.7
        sec.shear_factor_z = 0.8
        sec.compute_properties()
        assert sec.shear_factor_y == pytest.approx(0.7)
        assert sec.shear_factor_z == pytest.approx(0.8)

    def test_shear_areas_computed(self):
        """Shear areas A_y and A_z should be computed after compute_properties."""
        sec = RectangularSection("r", 30, 50)
        sec.compute_properties()
        p = sec.properties
        assert p.shear_area_y is not None and p.shear_area_y > 0
        assert p.shear_area_z is not None and p.shear_area_z > 0
