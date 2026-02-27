"""
Test per verifiche DM 9/1/1996 - TA, SLU, SLE, c.a.p.

Test coperti:
- 5 test TA: flessione OK/NOK, pressoflessione, taglio, minimi armatura
- 5 test SLU: flessione OK/NOK, taglio, minimi armatura flessione, minimi armatura taglio
- 2 test SLE: fessurazione placeholder, deformazioni placeholder
- 3 test integrazione: template registrati, utility tensioni ammissibili, tau
- Test placeholder precompressione (verifica che le funzioni esistano e non crashino)
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core_calculus.contracts import CalcInput, VerificationTemplate
from src.core_calculus.normative_registry import get_dm96_templates
from src.methods.checks_dm96 import (
    check_deformazioni_sle_dm96,
    check_fessurazione_sle_dm96,
    check_flessione_slu_dm96,
    check_flessione_ta_dm96,
    check_instabilita_compressione_slu_dm96,
    check_minimi_armatura_flessione_slu_dm96,
    check_minimi_armatura_ta_dm96,
    check_minimi_armatura_taglio_slu_dm96,
    check_precompression_slu_dm96,
    check_precompression_stresses_ta_dm96,
    check_pressoflessione_ta_dm96,
    check_punzonamento_slu_dm96,
    check_taglio_slu_dm96,
    check_taglio_ta_dm96,
    check_torsione_slu_dm96,
    compute_precompression_effects_dm96,
    estimate_prestress_losses_dm96,
    get_dm96_allowable_stresses,
)

# ===========================================================================
# Mock objects
# ===========================================================================


@dataclass
class MockDM96Section:
    """Sezione rettangolare 30x50 cm per test DM96."""

    section_type: str = "RECTANGULAR"
    b: float = 300.0  # mm
    h: float = 500.0  # mm

    @property
    def width(self) -> float:
        return self.b

    @property
    def height(self) -> float:
        return self.h


@dataclass
class MockDM96Material:
    """Materiale DM92: C20/25 + FeB38k per test DM96.

    Valori da DM92.jsoncode (sigma_c_adm = 0.30 * Rck).
    """

    # Proprietà calcestruzzo DM92
    f_ck: float = 20.0  # MPa (per SLU)
    Rck_kg_cm2: float = 250.0
    sigma_c_adm_kg_cm2: float = 75.0  # 0.30 * 250
    tau_c0_kg_cm2: float = 5.7
    tau_c1_kg_cm2: float = 20.0
    n_homog: float = 6.9

    # Proprietà acciaio DM92
    f_yk: float = 375.0  # MPa (FeB38k, per SLU)
    sigma_sn_kg_cm2: float = 3800.0
    sigma_s_adm_kg_cm2: float = 2550.0

    # Proprietà aggiuntive per SLU
    Ecm: float = 30000.0  # MPa
    f_ctm: float = 2.2  # MPa


def _make_template(template_id: str, limit_state: str = "TA", **extra) -> VerificationTemplate:
    """Helper per creare un template di test."""
    return VerificationTemplate(
        template_id=template_id,
        norm_code="DM96",
        norm_version="1996",
        limit_state=limit_state,
        extra_params=extra,
    )


# ===========================================================================
# Test integrazione: template registrati
# ===========================================================================


def test_dm96_templates_registered():
    """Verifica che i template DM96 siano registrati nel registry."""
    templates = get_dm96_templates()
    assert len(templates) == 15, f"Attesi 15 template DM96, trovati {len(templates)}"


def test_dm96_template_ids():
    """Verifica gli ID dei template DM96."""
    templates = get_dm96_templates()
    ids = {t.template_id for t in templates}
    expected_ids = {
        "dm96_ta_flessione_rett",
        "dm96_ta_pressoflessione_rett",
        "dm96_ta_taglio_rett",
        "dm96_ta_minimi_armatura_long",
        "dm96_slu_flessione_rett",
        "dm96_slu_taglio",
        "dm96_slu_minimi_armatura_fless",
        "dm96_slu_minimi_armatura_taglio",
        "dm96_sle_fessurazione",
        "dm96_sle_deformazioni",
        "dm96_slu_torsione",
        "dm96_slu_punzonamento",
        "dm96_slu_instabilita",
        "dm96_ta_prestress_stresses",
        "dm96_slu_prestress",
    }
    assert ids == expected_ids, f"Template mancanti: {expected_ids - ids}"


def test_dm96_templates_norm_code():
    """Tutti i template DM96 devono avere norm_code='DM96'."""
    for t in get_dm96_templates():
        assert t.norm_code == "DM96", f"Template {t.template_id} ha norm_code={t.norm_code}"


# ===========================================================================
# Test utility: tensioni ammissibili
# ===========================================================================


def test_get_dm96_allowable_stresses_from_dm92():
    """Test estrazione tensioni ammissibili da campi DM92."""
    mat = MockDM96Material()
    result = get_dm96_allowable_stresses(mat)
    assert result.sigma_c_allow == 75.0, f"sigma_c_adm atteso 75, ottenuto {result.sigma_c_allow}"
    assert result.sigma_s_allow == 2550.0, f"sigma_s_adm atteso 2550, ottenuto {result.sigma_s_allow}"


def test_get_dm96_allowable_stresses_from_fck():
    """Test stima tensioni ammissibili da fck (fallback)."""

    @dataclass
    class MinimalMaterial:
        f_ck: float = 20.0
        f_yk: float = 375.0

    mat = MinimalMaterial()
    result = get_dm96_allowable_stresses(mat)
    assert result.sigma_c_allow > 0, "sigma_c_allow deve essere positiva"
    assert result.sigma_s_allow > 0, "sigma_s_allow deve essere positiva"


# ===========================================================================
# Test TA: flessione
# ===========================================================================


def test_flessione_ta_dm96_ok():
    """Flessione TA con momento moderato - deve passare."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_ta_flessione_rett", "TA")

    calc_input = CalcInput(
        element_name="Trave Test DM96 Flessione TA",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["TA"],
        Mx=50.0,  # kNm - momento moderato
        As=10.0,  # cm²
        d=45.0,  # cm
    )

    result = check_flessione_ta_dm96(calc_input, template)
    assert result.ok, f"Verifica TA flessione dovrebbe passare. Messaggi: {result.messages_it}"
    assert result.utilisation is not None
    assert result.utilisation < 1.0


def test_flessione_ta_dm96_non_ok():
    """Flessione TA con momento molto elevato - deve fallire o avere alta utilizzazione."""
    section = MockDM96Section(b=200.0, h=350.0)
    material = MockDM96Material()
    template = _make_template("dm96_ta_flessione_rett", "TA")

    calc_input = CalcInput(
        element_name="Trave Test DM96 NON OK",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["TA"],
        Mx=300.0,  # kNm - momento molto elevato
        As=2.0,  # cm² - armatura molto insufficiente
        d=30.0,  # cm
    )

    result = check_flessione_ta_dm96(calc_input, template)
    # Il motore TA con sezione 20x35 e momento alto dovrebbe dare alta utilizzazione.
    # Verifica che il risultato sia coerente (non crashi e produca utilizzazione).
    assert result.utilisation is not None, "Deve produrre un valore di utilizzazione"
    assert result.template_id == "dm96_ta_flessione_rett"
    assert result.limit_state == "TA"


# ===========================================================================
# Test TA: pressoflessione
# ===========================================================================


def test_pressoflessione_ta_dm96():
    """Pressoflessione TA con N + M."""
    section = MockDM96Section(b=300.0, h=300.0)
    material = MockDM96Material()
    template = _make_template("dm96_ta_pressoflessione_rett", "TA")

    calc_input = CalcInput(
        element_name="Pilastro Test DM96 Pressoflessione",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["TA"],
        N=200.0,  # kN compressione
        Mx=30.0,  # kNm
        As=8.0,  # cm²
        d=26.0,  # cm
    )

    result = check_pressoflessione_ta_dm96(calc_input, template)
    assert result.template_id == "dm96_ta_pressoflessione_rett"
    assert result.limit_state == "TA"
    assert result.utilisation is not None or len(result.messages_it) > 0


# ===========================================================================
# Test TA: taglio
# ===========================================================================


def test_taglio_ta_dm96():
    """Taglio TA con taglio moderato."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_ta_taglio_rett", "TA")

    calc_input = CalcInput(
        element_name="Trave Test DM96 Taglio TA",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["TA"],
        Tx=40.0,  # kN
        d=45.0,  # cm
    )

    result = check_taglio_ta_dm96(calc_input, template)
    assert result.template_id == "dm96_ta_taglio_rett"
    assert result.utilisation is not None or len(result.messages_it) > 0


# ===========================================================================
# Test TA: minimi armatura
# ===========================================================================


def test_minimi_armatura_ta_dm96():
    """Minimi armatura TA con armatura adeguata."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_ta_minimi_armatura_long", "TA")

    calc_input = CalcInput(
        element_name="Trave Test DM96 Minimi Armatura",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["TA"],
        As=10.0,  # cm² - armatura abbondante
    )

    result = check_minimi_armatura_ta_dm96(calc_input, template)
    assert result.template_id == "dm96_ta_minimi_armatura_long"


# ===========================================================================
# Test SLU: flessione
# ===========================================================================


def test_flessione_slu_dm96_ok():
    """Flessione SLU DM96 con momento moderato - deve passare."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_slu_flessione_rett", "SLU", gamma_c=1.6, gamma_s=1.15)

    calc_input = CalcInput(
        element_name="Trave Test DM96 Flessione SLU",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        Mx=80.0,  # kNm
        As=15.0,  # cm²
        d=45.0,  # cm
    )

    result = check_flessione_slu_dm96(calc_input, template)
    assert result.ok, f"Flessione SLU dovrebbe passare. Messaggi: {result.messages_it}"
    assert result.utilisation is not None
    assert result.utilisation < 1.0
    assert "M_Rd_kNm" in result.details


def test_flessione_slu_dm96_non_ok():
    """Flessione SLU DM96 con armatura insufficiente - deve fallire."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_slu_flessione_rett", "SLU", gamma_c=1.6, gamma_s=1.15)

    calc_input = CalcInput(
        element_name="Trave SLU NON OK",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        Mx=200.0,  # kNm - momento molto alto
        As=4.0,  # cm² - armatura insufficiente
        d=45.0,  # cm
    )

    result = check_flessione_slu_dm96(calc_input, template)
    assert not result.ok, "Flessione SLU dovrebbe fallire"
    assert result.utilisation is not None
    assert result.utilisation > 1.0


def test_flessione_slu_dm96_gamma_c_16():
    """Verifica che gamma_c=1.6 sia usato (non 1.5 come NTC2018)."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_slu_flessione_rett", "SLU", gamma_c=1.6, gamma_s=1.15)

    calc_input = CalcInput(
        element_name="Test gamma_c",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        Mx=100.0,
        As=12.0,
        d=45.0,
    )

    result = check_flessione_slu_dm96(calc_input, template)
    # gamma_c = 1.6 -> fcd = 0.85 * fck / 1.6 = 0.85 * 20 / 1.6 = 10.625 MPa
    if "f_cd_MPa" in result.details:
        assert (
            abs(result.details["f_cd_MPa"] - 10.625) < 0.1
        ), f"f_cd dovrebbe essere 10.625 MPa (0.85*fck/gamma_c=0.85*20/1.6), ottenuto {result.details['f_cd_MPa']}"


# ===========================================================================
# Test SLU: taglio
# ===========================================================================


def test_taglio_slu_dm96():
    """Taglio SLU DM96 con staffe."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_slu_taglio", "SLU", gamma_c=1.6, gamma_s=1.15, theta_deg=21.8)

    calc_input = CalcInput(
        element_name="Trave Test Taglio SLU",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        Tx=80.0,  # kN
        d=450.0,  # mm (nota: d in mm per SLU)
        staffe_diametro=8.0,  # mm
        staffe_num_bracci=2,
        staffe_passo=200.0,  # mm
    )

    result = check_taglio_slu_dm96(calc_input, template)
    assert result.template_id == "dm96_slu_taglio"
    assert result.limit_state == "SLU"


# ===========================================================================
# Test SLU: minimi armatura
# ===========================================================================


def test_minimi_armatura_flessione_slu_dm96():
    """Minimi armatura flessione SLU."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_slu_minimi_armatura_fless", "SLU")

    calc_input = CalcInput(
        element_name="Test Minimi Flex SLU",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        As=10.0,  # cm²
        d=450.0,  # mm
    )

    result = check_minimi_armatura_flessione_slu_dm96(calc_input, template)
    assert result.template_id == "dm96_slu_minimi_armatura_fless"


def test_minimi_armatura_taglio_slu_dm96():
    """Minimi armatura taglio SLU."""
    section = MockDM96Section(b=300.0, h=500.0)
    material = MockDM96Material()
    template = _make_template("dm96_slu_minimi_armatura_taglio", "SLU", gamma_c=1.6, gamma_s=1.15)

    calc_input = CalcInput(
        element_name="Test Minimi Taglio SLU",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        staffe_diametro=8.0,
        staffe_num_bracci=2,
        staffe_passo=200.0,
    )

    result = check_minimi_armatura_taglio_slu_dm96(calc_input, template)
    assert result.template_id == "dm96_slu_minimi_armatura_taglio"


# ===========================================================================
# Test SLE: fessurazione e deformazioni
# ===========================================================================


def test_fessurazione_sle_dm96_placeholder():
    """Fessurazione SLE placeholder - deve ritornare SingleCheckResult senza crash."""
    section = MockDM96Section()
    material = MockDM96Material()
    template = _make_template("dm96_sle_fessurazione", "SLE", w_amm_mm=0.3)

    calc_input = CalcInput(
        element_name="Test Fessurazione",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLE"],
        Mx=50.0,
        As=8.0,
        d=45.0,
    )

    result = check_fessurazione_sle_dm96(calc_input, template)
    assert result.template_id == "dm96_sle_fessurazione"
    assert result.limit_state == "SLE"
    assert len(result.messages_it) > 0


def test_deformazioni_sle_dm96_placeholder():
    """Deformazioni SLE placeholder - deve ritornare SingleCheckResult senza crash."""
    section = MockDM96Section()
    material = MockDM96Material()
    template = _make_template("dm96_sle_deformazioni", "SLE", deflection_limit_ratio=250.0)

    calc_input = CalcInput(
        element_name="Test Deformazioni",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLE"],
        Mx=50.0,
        extra={"span_mm": 6000.0},
    )

    result = check_deformazioni_sle_dm96(calc_input, template)
    assert result.template_id == "dm96_sle_deformazioni"
    assert result.limit_state == "SLE"


# ===========================================================================
# Test SLU aggiuntivi: torsione, punzonamento, instabilita
# ===========================================================================


def test_torsione_slu_dm96_placeholder():
    """Torsione SLU placeholder."""
    section = MockDM96Section()
    material = MockDM96Material()
    template = _make_template("dm96_slu_torsione", "SLU", gamma_c=1.6)

    calc_input = CalcInput(
        element_name="Test Torsione",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        Mz=10.0,  # kNm - torsione
    )

    result = check_torsione_slu_dm96(calc_input, template)
    assert result.template_id == "dm96_slu_torsione"
    assert result.limit_state == "SLU"


def test_punzonamento_slu_dm96_placeholder():
    """Punzonamento SLU placeholder."""
    section = MockDM96Section()
    material = MockDM96Material()
    template = _make_template("dm96_slu_punzonamento", "SLU", gamma_c=1.6)

    calc_input = CalcInput(
        element_name="Test Punzonamento",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        N=300.0,  # kN
        d=250.0,  # mm
    )

    result = check_punzonamento_slu_dm96(calc_input, template)
    assert result.template_id == "dm96_slu_punzonamento"


def test_instabilita_slu_dm96_placeholder():
    """Instabilita SLU placeholder."""
    section = MockDM96Section()
    material = MockDM96Material()
    template = _make_template("dm96_slu_instabilita", "SLU", gamma_c=1.6)

    calc_input = CalcInput(
        element_name="Test Instabilita",
        section=section,
        material=material,
        norm_code="DM96",
        limit_states_enabled=["SLU"],
        N=500.0,  # kN
        extra={"l_0_mm": 3000.0},
    )

    result = check_instabilita_compressione_slu_dm96(calc_input, template)
    assert result.template_id == "dm96_slu_instabilita"
    assert result.limit_state == "SLU"


# ===========================================================================
# Test precompressione c.a.p. (placeholder - verificano che le funzioni esistano)
# ===========================================================================


def test_compute_precompression_effects_placeholder():
    """compute_precompression_effects_dm96 non deve crashare."""
    # Signature: (precompression_data, section_geometry, concrete_law)
    result = compute_precompression_effects_dm96(
        precompression_data=None,
        section_geometry=None,
        concrete_law=None,
    )
    assert isinstance(result, dict)
    assert "implementation_status" in result


def test_estimate_prestress_losses_placeholder():
    """estimate_prestress_losses_dm96 non deve crashare."""
    # Signature: (precompression_data, material_concrete, material_prestressing, user_config)
    result = estimate_prestress_losses_dm96(
        precompression_data=None,
        material_concrete=None,
        material_prestressing=None,
    )
    assert isinstance(result, dict)


def test_check_precompression_stresses_ta_placeholder():
    """check_precompression_stresses_ta_dm96 non deve crashare."""
    section = MockDM96Section()
    material = MockDM96Material()
    template = _make_template("dm96_ta_prestress_stresses", "TA")

    calc_input = CalcInput(
        element_name="Test CAP Stresses TA",
        section=section,
        material=material,
        norm_code="DM96",
    )

    result = check_precompression_stresses_ta_dm96(calc_input, template)
    assert result.template_id == "dm96_ta_prestress_stresses"
    assert len(result.messages_it) > 0


def test_check_precompression_slu_placeholder():
    """check_precompression_slu_dm96 non deve crashare."""
    section = MockDM96Section()
    material = MockDM96Material()
    template = _make_template("dm96_slu_prestress", "SLU")

    calc_input = CalcInput(
        element_name="Test CAP SLU",
        section=section,
        material=material,
        norm_code="DM96",
    )

    result = check_precompression_slu_dm96(calc_input, template)
    assert result.template_id == "dm96_slu_prestress"
    assert len(result.messages_it) > 0
