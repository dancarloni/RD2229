"""Test module for configuration loaders.

Tests for calculation_codes_loader and historical_materials_loader modules.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.calculation_codes_loader import (
    CalculationCodeLoader,
    get_safety_coefficients,
    get_strain_limits,
    get_stress_limits,
    list_available_codes,
    load_code,
)
from config.historical_materials_loader import (
    HistoricalMaterialsLoader,
    get_concrete_classes,
    get_concrete_properties,
    get_steel_properties,
    get_steel_types,
    list_available_sources,
    load_material_source,
)


class TestCalculationCodeLoader:
    """Test cases for CalculationCodeLoader."""

    def test_list_available_codes(self):
        """Test listing available calculation codes."""
        codes = list_available_codes()
        assert isinstance(codes, list)
        assert "TA" in codes
        assert "SLU" in codes
        assert "SLE" in codes

    def test_load_ta_code(self):
        """Test loading TA (Tensioni Ammissibili) configuration."""
        config = load_code("TA")
        assert config["code_name"] == "TA"
        assert "description" in config
        assert "safety_coefficients" in config
        assert "stress_limits" in config
        assert "verification_types" in config

    def test_load_slu_code(self):
        """Test loading SLU (Stato Limite Ultimo) configuration."""
        config = load_code("SLU")
        assert config["code_name"] == "SLU"
        assert "strain_limits" in config
        assert "constitutive_models" in config

    def test_load_sle_code(self):
        """Test loading SLE (Stato Limite Esercizio) configuration."""
        config = load_code("SLE")
        assert config["code_name"] == "SLE"
        assert "crack_limits" in config
        assert "stress_limits" in config

    def test_get_safety_coefficients_ta(self):
        """Test getting safety coefficients for TA."""
        coeffs = get_safety_coefficients("TA")
        assert "gamma_c" in coeffs
        assert "gamma_s" in coeffs
        # TA uses gamma = 1.0 (already in allowable stress)
        assert coeffs["gamma_c"]["value"] == 1.0
        assert coeffs["gamma_s"]["value"] == 1.0

    def test_get_safety_coefficients_slu(self):
        """Test getting safety coefficients for SLU."""
        coeffs = get_safety_coefficients("SLU")
        assert "gamma_c" in coeffs
        assert "gamma_s" in coeffs
        # SLU uses actual safety factors
        assert coeffs["gamma_c"]["value"] == 1.5
        assert coeffs["gamma_s"]["value"] == 1.15

    def test_get_stress_limits_ta(self):
        """Test getting stress limits for TA."""
        limits = get_stress_limits("TA")
        assert "concrete" in limits
        assert "shear" in limits
        assert limits["concrete"]["sigma_c_max_factor"] == 0.5
        assert limits["shear"]["tau_c0"]["value"] == 0.06
        assert limits["shear"]["tau_c1"]["value"] == 0.14

    def test_get_strain_limits_slu(self):
        """Test getting strain limits for SLU."""
        limits = get_strain_limits("SLU")
        assert "concrete" in limits
        assert "steel" in limits
        assert limits["concrete"]["eps_c2"]["value"] == 0.002
        assert limits["concrete"]["eps_cu"]["value"] == 0.0035

    def test_loader_caching(self):
        """Test that configurations are cached."""
        loader = CalculationCodeLoader()
        config1 = loader.load_code("TA")
        config2 = loader.load_code("TA")
        # Should return the same object from cache
        assert config1 is config2

    def test_invalid_code_raises_error(self):
        """Test that loading invalid code raises FileNotFoundError."""
        loader = CalculationCodeLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_code("INVALID_CODE")


class TestHistoricalMaterialsLoader:
    """Test cases for HistoricalMaterialsLoader."""

    def test_list_available_sources(self):
        """Test listing available material sources."""
        sources = list_available_sources()
        assert isinstance(sources, list)
        assert "RD2229" in sources
        assert "DM92" in sources
        assert "NTC2008" in sources
        assert "NTC2018" in sources

    def test_load_rd2229(self):
        """Test loading RD2229 historical materials."""
        config = load_material_source("RD2229")
        assert config["code_name"] == "RD2229"
        assert config["period"] == "1939-1972"
        assert config["unit_system"] == "tecnico"
        assert "concrete_classes" in config
        assert "steel_types" in config
        assert "cement_types" in config

    def test_load_ntc2018(self):
        """Test loading NTC2018 materials."""
        config = load_material_source("NTC2018")
        assert config["code_name"] == "NTC2018"
        assert config["period"] == "2018-presente"
        assert config["unit_system"] == "SI"

    def test_get_concrete_classes_rd2229(self):
        """Test getting concrete classes for RD2229."""
        classes = get_concrete_classes("RD2229")
        assert "R120" in classes
        assert "R160" in classes
        assert "R225" in classes
        assert "R300" in classes

    def test_get_concrete_properties_rd2229(self):
        """Test getting specific concrete properties for RD2229."""
        props = get_concrete_properties("RD2229", "R160")
        assert props is not None
        assert props["sigma_c28"] == 160  # kg/cm²
        assert props["sigma_c_adm"] == 80  # kg/cm²
        assert props["tau_c0"] == 9.6
        assert props["tau_c1"] == 22.4
        assert props["Ec"] == 250000
        assert props["n"] == 8.4

    def test_get_steel_types_rd2229(self):
        """Test getting steel types for RD2229."""
        types = get_steel_types("RD2229")
        assert "dolce" in types
        assert "semiduro" in types
        assert "duro" in types
        assert "FeB32k" in types
        assert "FeB38k" in types
        assert "FeB44k" in types
        assert "AQ42" in types
        assert "AQ50" in types

    def test_get_steel_properties_rd2229(self):
        """Test getting specific steel properties for RD2229."""
        props = get_steel_properties("RD2229", "FeB38k")
        assert props is not None
        assert props["sigma_sn"] == 3800  # kg/cm²
        assert props["sigma_s_adm"] == 1900  # kg/cm²
        assert props["Es"] == 2100000
        assert props["bond"] == "aderenza_migliorata"

    def test_get_steel_types_ntc2018(self):
        """Test getting steel types for NTC2018."""
        types = get_steel_types("NTC2018")
        assert "B450C" in types
        assert "B450A" in types

    def test_get_concrete_classes_ntc2018(self):
        """Test getting concrete classes for NTC2018."""
        classes = get_concrete_classes("NTC2018")
        assert "C20_25" in classes
        assert "C25_30" in classes
        assert "C30_37" in classes
        # Check properties structure
        c25 = classes["C25_30"]
        assert c25["fck"] == 25  # MPa
        assert c25["fcm"] == 33
        assert c25["Ecm"] == 31000

    def test_cement_types_rd2229(self):
        """Test cement types in RD2229."""
        loader = HistoricalMaterialsLoader()
        cement_types = loader.get_cement_types("RD2229")
        assert "normale" in cement_types
        assert "presa_lenta" in cement_types
        assert "alta_resistenza" in cement_types
        assert "alluminoso" in cement_types

        # Check strength factors
        assert cement_types["normale"]["strength_factor"] == 1.0
        assert cement_types["presa_lenta"]["strength_factor"] == 0.85
        assert cement_types["alluminoso"]["strength_factor"] == 1.3

    def test_conversion_factors(self):
        """Test unit conversion factors."""
        loader = HistoricalMaterialsLoader()
        factors_rd2229 = loader.get_conversion_factors("RD2229")
        assert "kg_cm2_to_MPa" in factors_rd2229
        assert "MPa_to_kg_cm2" in factors_rd2229
        assert abs(factors_rd2229["kg_cm2_to_MPa"] - 0.0980665) < 1e-6
        assert abs(factors_rd2229["MPa_to_kg_cm2"] - 10.197) < 1e-3

    def test_loader_caching(self):
        """Test that material source configurations are cached."""
        loader = HistoricalMaterialsLoader()
        config1 = loader.load_material_source("RD2229")
        config2 = loader.load_material_source("RD2229")
        # Should return the same object from cache
        assert config1 is config2

    def test_invalid_source_raises_error(self):
        """Test that loading invalid source raises FileNotFoundError."""
        loader = HistoricalMaterialsLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_material_source("INVALID_SOURCE")


class TestVerificationInputOutput:
    """Test cases for VerificationInput and VerificationOutput dataclasses."""

    def test_verification_input_new_fields(self):
        """Test that VerificationInput has new fields."""
        from verification_table import VerificationInput

        v_input = VerificationInput()

        # Check new fields exist with default values
        assert hasattr(v_input, "Mx")
        assert v_input.Mx == 0.0

        assert hasattr(v_input, "My")
        assert v_input.My == 0.0

        assert hasattr(v_input, "Mz")
        assert v_input.Mz == 0.0

        assert hasattr(v_input, "Tx")
        assert v_input.Tx == 0.0

        assert hasattr(v_input, "Ty")
        assert v_input.Ty == 0.0

        assert hasattr(v_input, "At")
        assert v_input.At == 0.0

    def test_verification_input_legacy_compatibility(self):
        """Test backward compatibility with legacy M and T fields."""
        from verification_table import VerificationInput

        v_input = VerificationInput()

        # Test M property (should map to Mx)
        v_input.M = 100.0
        assert v_input.Mx == 100.0
        assert v_input.M == 100.0

        # Test T property (should map to Ty)
        v_input.T = 50.0
        assert v_input.Ty == 50.0
        assert v_input.T == 50.0

    def test_verification_output_new_fields(self):
        """Test that VerificationOutput has new fields."""
        from verification_table import VerificationOutput

        v_output = VerificationOutput(sigma_c_max=10.0, sigma_c_min=0.0, sigma_s_max=200.0, asse_neutro=15.0)

        # Check new fields exist with default values
        assert hasattr(v_output, "asse_neutro_x")
        assert v_output.asse_neutro_x == 0.0

        assert hasattr(v_output, "asse_neutro_y")
        assert v_output.asse_neutro_y == 0.0

        assert hasattr(v_output, "inclinazione_asse_neutro")
        assert v_output.inclinazione_asse_neutro == 0.0

        assert hasattr(v_output, "tipo_verifica")
        assert v_output.tipo_verifica == ""

        assert hasattr(v_output, "sigma_c")
        assert v_output.sigma_c == 0.0

        assert hasattr(v_output, "sigma_s_tesi")
        assert v_output.sigma_s_tesi == 0.0

        assert hasattr(v_output, "sigma_s_compressi")
        assert v_output.sigma_s_compressi == 0.0

        # Check default messaggi initialization
        assert v_output.messaggi == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
