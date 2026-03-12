"""Test per section_registry, shear_area_registry e code_registry."""

from __future__ import annotations

import math
import os

# ======================================================================
# SECTION REGISTRY
# ======================================================================


class TestSectionRegistry:
    """Test per src/calc/section_registry.py."""

    def setup_method(self):
        from src.calc.section_registry import clear_registry

        clear_registry()

    def test_register_and_get(self):
        from src.calc.section_registry import get_section_metadata, register_section

        register_section("test-1", {"area_cm2": 100.0})
        meta = get_section_metadata("test-1")
        assert meta is not None
        assert meta["area_cm2"] == 100.0

    def test_register_empty_id_ignored(self):
        from src.calc.section_registry import list_sections, register_section

        register_section("", {"area_cm2": 1.0})
        assert "" not in list_sections()

    def test_list_sections(self):
        from src.calc.section_registry import list_sections, register_section

        register_section("a", {})
        register_section("b", {})
        ids = list_sections()
        assert "a" in ids
        assert "b" in ids

    def test_remove_section(self):
        from src.calc.section_registry import get_section_metadata, register_section, remove_section

        register_section("rm-me", {"x": 1})
        assert remove_section("rm-me") is True
        assert get_section_metadata("rm-me") is None
        assert remove_section("rm-me") is False

    def test_clear_registry(self):
        from src.calc.section_registry import clear_registry, list_sections, register_section

        register_section("x", {})
        clear_registry()
        assert list_sections() == []

    # --- compute functions ---

    def test_compute_rectangular(self):
        from src.calc.section_registry import compute_rectangular

        props = compute_rectangular(30.0, 50.0)
        assert props["section_type"] == "RECTANGULAR"
        assert props["area_cm2"] == 30.0 * 50.0
        expected_Ix = 30.0 * 50.0**3 / 12.0
        assert abs(props["Ix"] - round(expected_Ix, 2)) < 0.01
        expected_Iy = 50.0 * 30.0**3 / 12.0
        assert abs(props["Iy"] - round(expected_Iy, 2)) < 0.01
        assert abs(props["kappa_x"] - 5.0 / 6.0) < 1e-6
        assert abs(props["kappa_y"] - 5.0 / 6.0) < 1e-6

    def test_compute_circular(self):
        from src.calc.section_registry import compute_circular

        props = compute_circular(30.0)
        assert props["section_type"] == "CIRCULAR"
        r = 15.0
        expected_A = math.pi * r**2
        assert abs(props["area_cm2"] - round(expected_A, 2)) < 0.01
        expected_I = math.pi * r**4 / 4.0
        assert abs(props["Ix"] - round(expected_I, 2)) < 0.01
        assert props["Ix"] == props["Iy"]

    def test_compute_t_section(self):
        from src.calc.section_registry import compute_t_section

        props = compute_t_section(60.0, 10.0, 25.0, 40.0)
        assert props["section_type"] == "T_SECTION"
        A_f = 60.0 * 10.0
        A_w = 25.0 * 40.0
        assert abs(props["area_cm2"] - round(A_f + A_w, 2)) < 0.01
        assert props["height_cm"] == 50.0
        assert props["web_width_cm"] == 25.0
        assert props["web_height_cm"] == 40.0
        # kappa_x should be A_web / A_total
        expected_kappa = A_w / (A_f + A_w)
        assert abs(props["kappa_x"] - round(expected_kappa, 4)) < 1e-4

    def test_compute_i_section(self):
        from src.calc.section_registry import compute_i_section

        props = compute_i_section(20.0, 1.5, 1.0, 27.0)
        assert props["section_type"] == "I_SECTION"
        h_tot = 2 * 1.5 + 27.0
        assert props["height_cm"] == h_tot
        A_f = 20.0 * 1.5
        A_w = 1.0 * 27.0
        A = 2 * A_f + A_w
        assert abs(props["area_cm2"] - round(A, 2)) < 0.01

    def test_load_sections_from_legacy(self):
        from src.calc.section_registry import get_section_metadata, load_sections_from_legacy

        legacy_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "legacy", "sections.json"
        )
        count = load_sections_from_legacy(legacy_path)
        assert count >= 1
        # The legacy file has a section with id "daa88992-..."
        # Check that at least one section was loaded
        meta = get_section_metadata("daa88992-289b-4c02-a299-5f3ff9a49929")
        assert meta is not None
        assert meta["area_cm2"] == 600

    def test_load_sections_from_legacy_missing_file(self):
        from src.calc.section_registry import load_sections_from_legacy

        count = load_sections_from_legacy("/nonexistent/path.json")
        assert count == 0

    def test_bootstrap_default_sections(self):
        from src.calc.section_registry import bootstrap_default_sections, list_sections

        bootstrap_default_sections()
        ids = list_sections()
        assert len(ids) >= 9
        # Should contain known defaults
        assert any("Rect-30x50" in sid for sid in ids)
        assert any("Circle-D30" in sid for sid in ids)


# ======================================================================
# SHEAR AREA REGISTRY
# ======================================================================


class TestShearAreaRegistry:
    """Test per src/calc/shear_area_registry.py."""

    def test_kappa_defaults(self):
        from src.calc.shear_area_registry import (
            CIRCLE_KAPPA,
            DEFAULT_KAPPA,
            HOLLOW_CIRCLE_KAPPA,
            KAPPA_DEFAULTS,
        )

        assert abs(DEFAULT_KAPPA - 5.0 / 6.0) < 1e-10
        assert abs(CIRCLE_KAPPA - 6.0 / 7.0) < 1e-10
        assert abs(HOLLOW_CIRCLE_KAPPA - 0.5) < 1e-10
        assert KAPPA_DEFAULTS["RECTANGULAR"] == DEFAULT_KAPPA
        assert KAPPA_DEFAULTS["CIRCULAR"] == CIRCLE_KAPPA
        assert KAPPA_DEFAULTS["CIRCULAR_HOLLOW"] == HOLLOW_CIRCLE_KAPPA

    def test_get_default_kappa(self):
        from src.calc.shear_area_registry import DEFAULT_KAPPA, get_default_kappa

        assert get_default_kappa("RECTANGULAR") == DEFAULT_KAPPA
        assert get_default_kappa("UNKNOWN_TYPE") == DEFAULT_KAPPA

    def test_compute_shear_area_rectangular(self):
        from src.calc.shear_area_registry import compute_shear_area

        class FakeRect:
            shape_id = "rectangle"
            section_type = "RECTANGULAR"
            area_cm2 = 1500.0

        Asx, Asy = compute_shear_area(FakeRect())
        assert abs(Asx - 5.0 / 6.0 * 1500.0) < 0.01
        assert abs(Asy - 5.0 / 6.0 * 1500.0) < 0.01

    def test_compute_shear_area_user_override(self):
        from src.calc.shear_area_registry import compute_shear_area

        class FakeSection:
            shape_id = "rectangle"
            section_type = "RECTANGULAR"
            area_cm2 = 1000.0
            kappa_x = 0.7
            kappa_y = 0.8

        Asx, Asy = compute_shear_area(FakeSection())
        assert abs(Asx - 700.0) < 0.01
        assert abs(Asy - 800.0) < 0.01

    def test_compute_shear_area_circular(self):
        from src.calc.shear_area_registry import CIRCLE_KAPPA, compute_shear_area

        class FakeCircle:
            shape_id = "circle"
            section_type = "CIRCULAR"
            area_cm2 = 706.86

        Asx, Asy = compute_shear_area(FakeCircle())
        assert abs(Asx - CIRCLE_KAPPA * 706.86) < 0.1
        assert abs(Asy - CIRCLE_KAPPA * 706.86) < 0.1

    def test_compute_shear_area_web_based(self):
        from src.calc.shear_area_registry import compute_shear_area

        class FakeT:
            shape_id = "T_SECTION"
            section_type = "T_SECTION"
            area_cm2 = 1600.0
            web_width_cm = 25.0
            web_height_cm = 40.0

        Asx, Asy = compute_shear_area(FakeT())
        # Web-based: A_web = 25 * 40 = 1000
        assert abs(Asx - 1000.0) < 0.01
        assert abs(Asy - 1000.0) < 0.01

    def test_compute_shear_area_fallback(self):
        from src.calc.shear_area_registry import DEFAULT_KAPPA, compute_shear_area

        class FakeUnknown:
            shape_id = "some_unknown"
            section_type = "SOME_TYPE"
            area_cm2 = 500.0

        Asx, Asy = compute_shear_area(FakeUnknown())
        assert abs(Asx - DEFAULT_KAPPA * 500.0) < 0.01

    def test_compute_shear_area_kappa_defaults_for_section_type(self):
        from src.calc.shear_area_registry import HOLLOW_CIRCLE_KAPPA, compute_shear_area

        class FakeHollow:
            shape_id = "custom_hollow"
            section_type = "CIRCULAR_HOLLOW"
            area_cm2 = 400.0

        # shape_id not registered, but section_type is in SHEAR_AREA_STRATEGIES
        Asx, Asy = compute_shear_area(FakeHollow())
        assert abs(Asx - HOLLOW_CIRCLE_KAPPA * 400.0) < 0.01

    def test_all_12_section_types_have_kappa(self):
        from src.calc.shear_area_registry import KAPPA_DEFAULTS

        expected_types = [
            "RECTANGULAR",
            "CIRCULAR",
            "CIRCULAR_HOLLOW",
            "RECTANGULAR_HOLLOW",
            "T_SECTION",
            "INVERTED_T_SECTION",
            "I_SECTION",
            "PI_SECTION",
            "C_SECTION",
            "L_SECTION",
            "V_SECTION",
            "INVERTED_V_SECTION",
        ]
        for st in expected_types:
            assert st in KAPPA_DEFAULTS, f"Missing kappa default for {st}"


# ======================================================================
# CODE REGISTRY
# ======================================================================


class TestCodeRegistry:
    """Test per src/codes/code_registry.py."""

    def setup_method(self):
        from src.codes.code_registry import clear_registry

        clear_registry()

    def test_register_and_get_code(self):
        from src.codes.code_registry import get_code, register_code

        register_code("TEST", {"gamma_c": 1.5}, {"general": {"title": "Test"}})
        entry = get_code("TEST")
        assert entry is not None
        assert entry["params"]["gamma_c"] == 1.5
        assert entry["clauses"]["general"]["title"] == "Test"

    def test_register_empty_name_ignored(self):
        from src.codes.code_registry import list_codes, register_code

        register_code("", {"x": 1}, {})
        assert "" not in list_codes()

    def test_get_code_param(self):
        from src.codes.code_registry import get_code_param, register_code

        register_code("N", {"gamma_c": 1.5, "nested": {"val": 42}}, {})
        assert get_code_param("N", "gamma_c") == 1.5
        assert get_code_param("N", "nested.val") == 42
        assert get_code_param("N", "missing", 0.0) == 0.0
        assert get_code_param("NOCODE", "x", -1) == -1

    def test_get_code_clause(self):
        from src.codes.code_registry import get_code_clause, register_code

        register_code("E", {}, {"materials": {"concrete": {"limit_states": [{"id": "ULS"}]}}})
        ls = get_code_clause("E", "materials.concrete.limit_states")
        assert isinstance(ls, list)
        assert ls[0]["id"] == "ULS"
        assert get_code_clause("E", "nonexistent.path") is None
        assert get_code_clause("NOCODE", "x") is None

    def test_list_codes(self):
        from src.codes.code_registry import list_codes, register_code

        register_code("A", {}, {})
        register_code("B", {}, {})
        codes = list_codes()
        assert "A" in codes
        assert "B" in codes

    def test_clear_registry(self):
        from src.codes.code_registry import clear_registry, list_codes, register_code

        register_code("X", {}, {})
        clear_registry()
        assert list_codes() == []

    def test_bootstrap_codes(self):
        from src.codes.code_registry import bootstrap_codes, get_code, list_codes

        codes_dir = os.path.join(os.path.dirname(__file__), "..", "src", "codes")
        count = bootstrap_codes(codes_dir)
        assert count >= 2  # NTC2018 and EC2

        codes = list_codes()
        assert "NTC2018" in codes
        assert "EC2" in codes

        ntc = get_code("NTC2018")
        assert ntc is not None
        assert ntc["params"]["gamma_c"] == 1.5
        assert ntc["params"]["gamma_s"] == 1.15

        ec2 = get_code("EC2")
        assert ec2 is not None
        # EC2 clauses should have been loaded
        assert ec2["clauses"].get("general", {}).get("title") is not None

    def test_bootstrap_codes_nonexistent_dir(self):
        from src.codes.code_registry import bootstrap_codes

        count = bootstrap_codes("/nonexistent/path")
        assert count == 0

    def test_bootstrap_codes_ntc2018_expanded_params(self):
        from src.codes.code_registry import bootstrap_codes, get_code_param

        codes_dir = os.path.join(os.path.dirname(__file__), "..", "src", "codes")
        bootstrap_codes(codes_dir)

        # Verify expanded NTC2018 parameters
        assert get_code_param("NTC2018", "materials.gamma_c") == 1.5
        assert get_code_param("NTC2018", "materials.gamma_s") == 1.15
        assert get_code_param("NTC2018", "materials.alpha_cc") == 0.85
        assert get_code_param("NTC2018", "sle_limits.sigma_c_ratio_rara") == 0.60
        assert get_code_param("NTC2018", "partial_factors.gamma_G1") == 1.3
        assert get_code_param("NTC2018", "combination_coefficients.vento.psi_0") == 0.6

    def test_load_code_params_error_handling(self):
        from src.codes.code_registry import load_code_params

        result = load_code_params("test", "/nonexistent.json")
        assert result == {}

    def test_load_code_clauses_error_handling(self):
        from src.codes.code_registry import load_code_clauses

        result = load_code_clauses("test", "/nonexistent.yml")
        assert result == {}
