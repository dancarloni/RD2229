"""
Test per verifiche resistenza al fuoco - DM 9/3/2007, DM 16/2/2007.

Test coperti:
- Template registrati (4 template FIRE_DM2007)
- Placeholder run check per ciascun tipo (beam_rc, column_rc, slab_rc, beam_cap)
- FireVerificationConfig dataclass
- Validazione incendio in validation_engine
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core_calculus.contracts import CalcInput, VerificationTemplate
from src.core_calculus.normative_registry import get_fire_templates
from src.core_calculus.validation_engine import validate_calc_input
from src.methods.checks_fire_dm96 import (
    FireVerificationConfig,
    check_fire_resistance_beam_cap,
    check_fire_resistance_beam_rc,
    check_fire_resistance_column_rc,
    check_fire_resistance_slab_rc,
)

# ===========================================================================
# Mock objects
# ===========================================================================


@dataclass
class MockFireSection:
    """Sezione rettangolare per test incendio."""

    section_type: str = "RECTANGULAR"
    b: float = 300.0
    h: float = 500.0

    @property
    def width(self) -> float:
        return self.b

    @property
    def height(self) -> float:
        return self.h


@dataclass
class MockFireMaterial:
    """Materiale per test incendio."""

    f_ck: float = 25.0
    f_yk: float = 450.0


def _make_fire_template(template_id: str) -> VerificationTemplate:
    return VerificationTemplate(
        template_id=template_id,
        norm_code="FIRE_DM2007",
        norm_version="2007",
        limit_state="FIRE",
    )


def _make_fire_calc_input(
    fire_class: str = "R60",
    exposed_sides: int = 3,
) -> CalcInput:
    """Crea CalcInput con FireVerificationConfig."""
    return CalcInput(
        element_name="Test Fire Element",
        section=MockFireSection(),
        material=MockFireMaterial(),
        norm_code="FIRE_DM2007",
        limit_states_enabled=["FIRE"],
        extra={
            "fire_config": FireVerificationConfig(
                required_fire_resistance_class=fire_class,
                exposed_sides=exposed_sides,
                design_method="tabellare",
                protection_type="none",
            )
        },
    )


# ===========================================================================
# Test template registrati
# ===========================================================================


def test_fire_templates_registered():
    """Verifica che i 4 template incendio siano registrati."""
    templates = get_fire_templates()
    assert len(templates) == 4, f"Attesi 4 template FIRE, trovati {len(templates)}"


def test_fire_templates_ids():
    """Verifica gli ID dei template incendio."""
    templates = get_fire_templates()
    ids = {t.template_id for t in templates}
    expected = {
        "dm_fire_trave_ca",
        "dm_fire_pilastro_ca",
        "dm_fire_solaio_ca",
        "dm_fire_trave_cap",
    }
    assert ids == expected, f"Template mancanti: {expected - ids}"


def test_fire_templates_norm_code():
    """Tutti i template incendio devono avere norm_code='FIRE_DM2007'."""
    for t in get_fire_templates():
        assert t.norm_code == "FIRE_DM2007", f"{t.template_id} ha norm_code={t.norm_code}"


def test_fire_templates_limit_state():
    """Tutti i template incendio devono avere limit_state='FIRE'."""
    for t in get_fire_templates():
        assert t.limit_state == "FIRE", f"{t.template_id} ha limit_state={t.limit_state}"


# ===========================================================================
# Test FireVerificationConfig
# ===========================================================================


def test_fire_config_defaults():
    """Test valori default di FireVerificationConfig."""
    cfg = FireVerificationConfig()
    assert cfg.exposed_sides == 1
    assert cfg.protection_type == "none"
    assert cfg.protection_thickness_mm == 0.0
    assert cfg.design_method == "tabellare"
    assert cfg.user_temperature_limits == {}


def test_fire_config_custom():
    """Test costruzione con valori personalizzati."""
    cfg = FireVerificationConfig(
        required_fire_resistance_class="R90",
        exposed_sides=4,
        protection_type="intonaco",
        protection_thickness_mm=20.0,
        design_method="semplificato",
    )
    assert cfg.required_fire_resistance_class == "R90"
    assert cfg.exposed_sides == 4
    assert cfg.protection_thickness_mm == 20.0


# ===========================================================================
# Test placeholder run checks
# ===========================================================================


def test_fire_beam_rc_placeholder():
    """check_fire_resistance_beam_rc non deve crashare."""
    calc_input = _make_fire_calc_input("R60", 3)
    template = _make_fire_template("dm_fire_trave_ca")

    result = check_fire_resistance_beam_rc(calc_input, template)
    assert result.template_id == "dm_fire_trave_ca"
    assert result.limit_state == "FIRE"
    assert len(result.messages_it) > 0
    assert len(result.norm_references) > 0


def test_fire_column_rc_placeholder():
    """check_fire_resistance_column_rc non deve crashare."""
    calc_input = _make_fire_calc_input("R90", 4)
    template = _make_fire_template("dm_fire_pilastro_ca")

    result = check_fire_resistance_column_rc(calc_input, template)
    assert result.template_id == "dm_fire_pilastro_ca"
    assert result.limit_state == "FIRE"
    assert len(result.messages_it) > 0


def test_fire_slab_rc_placeholder():
    """check_fire_resistance_slab_rc non deve crashare."""
    calc_input = _make_fire_calc_input("R120", 1)
    template = _make_fire_template("dm_fire_solaio_ca")

    result = check_fire_resistance_slab_rc(calc_input, template)
    assert result.template_id == "dm_fire_solaio_ca"
    assert result.limit_state == "FIRE"
    assert len(result.messages_it) > 0


def test_fire_beam_cap_placeholder():
    """check_fire_resistance_beam_cap non deve crashare (c.a.p.)."""
    calc_input = _make_fire_calc_input("R60", 3)
    template = _make_fire_template("dm_fire_trave_cap")

    result = check_fire_resistance_beam_cap(calc_input, template)
    assert result.template_id == "dm_fire_trave_cap"
    assert result.limit_state == "FIRE"
    assert len(result.messages_it) > 0


def test_fire_beam_rc_missing_config():
    """Verifica che senza fire_config il check ritorna errore."""
    calc_input = CalcInput(
        element_name="Test No Config",
        section=MockFireSection(),
        material=MockFireMaterial(),
        norm_code="FIRE_DM2007",
        limit_states_enabled=["FIRE"],
    )
    template = _make_fire_template("dm_fire_trave_ca")

    result = check_fire_resistance_beam_rc(calc_input, template)
    assert not result.ok
    assert result.details.get("implementation_status") == "missing_config"


def test_fire_beam_rc_dict_config():
    """Verifica che fire_config come dict funzioni."""
    calc_input = CalcInput(
        element_name="Test Dict Config",
        section=MockFireSection(),
        material=MockFireMaterial(),
        norm_code="FIRE_DM2007",
        limit_states_enabled=["FIRE"],
        extra={
            "fire_config": {
                "required_fire_resistance_class": "R60",
                "exposed_sides": 3,
                "design_method": "tabellare",
            }
        },
    )
    template = _make_fire_template("dm_fire_trave_ca")

    result = check_fire_resistance_beam_rc(calc_input, template)
    assert result.limit_state == "FIRE"
    assert result.details.get("required_class") == "R60"


# ===========================================================================
# Test validazione incendio
# ===========================================================================


def test_validation_fire_missing_config():
    """Validazione deve segnalare errore se fire_config mancante."""
    calc_input = CalcInput(
        element_name="Test Validation",
        section=MockFireSection(),
        material=MockFireMaterial(),
        norm_code="FIRE_DM2007",
        limit_states_enabled=["FIRE"],
    )

    result = validate_calc_input(calc_input, "FIRE_DM2007")
    fire_issues = [i for i in result.issues if "FIRE" in i.code or "fire" in i.code.lower()]
    assert len(fire_issues) > 0, "Deve segnalare errore per fire_config mancante"


def test_validation_fire_with_config():
    """Validazione con fire_config presente non deve avere errori fire."""
    calc_input = _make_fire_calc_input("R60", 3)

    result = validate_calc_input(calc_input, "FIRE_DM2007")
    fire_errors = [
        i
        for i in result.issues
        if i.severity == "error" and ("FIRE" in i.code or "fire" in i.code.lower())
    ]
    assert len(fire_errors) == 0, f"Non dovrebbero esserci errori fire: {fire_errors}"


def test_validation_fire_invalid_exposed_sides():
    """Validazione deve segnalare errore per exposed_sides non valido."""
    calc_input = CalcInput(
        element_name="Test Invalid Sides",
        section=MockFireSection(),
        material=MockFireMaterial(),
        norm_code="FIRE_DM2007",
        limit_states_enabled=["FIRE"],
        extra={
            "fire_config": FireVerificationConfig(
                required_fire_resistance_class="R60",
                exposed_sides=5,  # Non valido!
            )
        },
    )

    result = validate_calc_input(calc_input, "FIRE_DM2007")
    side_issues = [i for i in result.issues if "EXPOSED" in i.code]
    assert len(side_issues) > 0, "Deve segnalare errore per exposed_sides=5"
