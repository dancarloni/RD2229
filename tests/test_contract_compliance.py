"""Test del protocollo I/O standard CalcInput/CalcOutput.

Verifica:
- Validazione CalcInput (f_ck < 0 → errore)
- Serializzazione CalcOutput (to_dict, to_latex)
- Normalizzazione round-trip (kg/cm² → MPa → kg/cm²)
- Adapter dict legacy → SingleCheckResult
- Aggregazione risultati da template
- Denormalizzazione per output utente
"""

from __future__ import annotations

import json
import math

import pytest

from src.core_calculus.contracts import (
    CalcInput,
    CalcOutput,
    ElementRole,
    NormReference,
    SingleCheckResult,
    ValidationIssue,
    ValidationResult,
    VerificationTemplate,
)
from src.core_calculus.normalization import (
    denormalize_for_output,
    dict_to_single_check_result,
    normalize_material_to_mpa,
    normalize_to_mpa,
)
from src.core_calculus.validation_engine import validate_calc_input


# ==============================================================================
# FIXTURE HELPERS
# ==============================================================================


class MockMaterial:
    """Materiale mock per i test."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockSection:
    """Sezione mock per i test."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def _make_calc_input(**overrides) -> CalcInput:
    """Crea un CalcInput valido con valori di default sensati."""
    defaults = dict(
        element_name="Trave T1",
        section=MockSection(width=30, height=50, section_type="rectangular"),
        material=MockMaterial(f_ck=25.0, f_yk=450.0),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        N=0.0,
        Mx=100.0,
        As=5.0,
        d=45.0,
    )
    defaults.update(overrides)
    return CalcInput(**defaults)


def _make_single_check_result(**overrides) -> SingleCheckResult:
    """Crea un SingleCheckResult di esempio."""
    defaults = dict(
        template_id="ntc2018_slu_flessione",
        ok=True,
        utilisation=0.75,
        passaggi_calcolo=[
            "Passo 1: Calcolo altezza utile d = 45 cm",
            "Passo 2: M_Rd = As * f_yd * (d - 0.4*x) = 133.5 kN·m",
            "Passo 3: Rapporto M_Ed/M_Rd = 100/133.5 = 0.749",
        ],
        formule_usate=["NTC2018 §4.1.2.1.3.1"],
        stress_max=18.75,
        stress_limit=25.0,
        norm_references=[
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.3.1",
                description_it="Resistenza a flessione sezioni rettangolari",
            )
        ],
        messages_it=["Verifica soddisfatta"],
    )
    defaults.update(overrides)
    return SingleCheckResult(**defaults)


# ==============================================================================
# TEST CalcInput
# ==============================================================================


class TestCalcInput:
    """Test per CalcInput: creazione, campi, timestamp."""

    def test_creation_defaults(self):
        """CalcInput creato con defaults ha timestamp auto-impostato."""
        ci = CalcInput()
        assert ci.timestamp != ""
        assert ci.element_name == ""
        assert ci.norm_code == ""

    def test_creation_full(self):
        """CalcInput con tutti i campi principali."""
        ci = _make_calc_input()
        assert ci.element_name == "Trave T1"
        assert ci.norm_code == "NTC2018"
        assert ci.Mx == 100.0
        assert ci.As == 5.0
        assert ci.d == 45.0

    def test_combinazione_field(self):
        """Campo combinazione presente e impostabile."""
        ci = _make_calc_input(combinazione="sismica")
        assert ci.combinazione == "sismica"

    def test_environment_class_field(self):
        """Campo environment_class presente."""
        ci = _make_calc_input(environment_class="XC2")
        assert ci.environment_class == "XC2"

    def test_durability_field(self):
        """Campo durability presente e dict."""
        ci = _make_calc_input(durability={"copriferro": 40, "acciaio": "B500B"})
        assert ci.durability["copriferro"] == 40

    def test_user_notes_field(self):
        """Campo user_notes presente."""
        ci = _make_calc_input(user_notes="Nota di prova")
        assert ci.user_notes == "Nota di prova"

    def test_timestamp_preserved_if_given(self):
        """Se timestamp fornito, non viene sovrascritto."""
        ci = CalcInput(timestamp="2026-01-01T00:00:00")
        assert ci.timestamp == "2026-01-01T00:00:00"


# ==============================================================================
# TEST CalcInput VALIDATION
# ==============================================================================


class TestCalcInputValidation:
    """Test validazione CalcInput tramite validation_engine."""

    def test_fck_negative_error(self):
        """f_ck negativo genera errore di validazione."""
        ci = _make_calc_input(material=MockMaterial(f_ck=-10.0, f_yk=450.0))
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "INVALID_F_CK" in error_codes

    def test_fyk_negative_error(self):
        """f_yk negativo genera errore di validazione."""
        ci = _make_calc_input(material=MockMaterial(f_ck=25.0, f_yk=-500.0))
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "INVALID_F_YK" in error_codes

    def test_d_negative_error(self):
        """Altezza utile d negativa genera errore."""
        ci = _make_calc_input(d=-5.0)
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "INVALID_D" in error_codes

    def test_d_prime_ge_d_error(self):
        """d' >= d genera errore."""
        ci = _make_calc_input(d=45.0, d_prime=50.0)
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "D_PRIME_GE_D" in error_codes

    def test_as_negative_error(self):
        """Area armatura negativa genera errore."""
        ci = _make_calc_input(As=-2.0)
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "NEGATIVE_AS" in error_codes

    def test_missing_section_error(self):
        """Sezione mancante genera errore."""
        ci = _make_calc_input(section=None)
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "MISSING_SECTION" in error_codes

    def test_missing_material_error(self):
        """Materiale mancante genera errore."""
        ci = _make_calc_input(material=None)
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "MISSING_MATERIAL" in error_codes

    def test_valid_input_no_errors(self):
        """Input valido non genera errori."""
        ci = _make_calc_input()
        result = validate_calc_input(ci, "NTC2018")
        assert not result.has_errors

    def test_fc_out_of_range(self):
        """FC fuori range [1.0, 1.5] genera errore."""
        ci = _make_calc_input(lc="LC1", fc=2.0)
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "FC_OUT_OF_RANGE" in error_codes

    def test_lc_invalid_error(self):
        """LC non valido genera errore."""
        ci = _make_calc_input(lc="LC4")
        result = validate_calc_input(ci, "NTC2018")
        assert result.has_errors
        error_codes = [i.code for i in result.issues if i.severity == "error"]
        assert "INVALID_LC" in error_codes


# ==============================================================================
# TEST SingleCheckResult
# ==============================================================================


class TestSingleCheckResult:
    """Test per SingleCheckResult: campi, serializzazione."""

    def test_creation(self):
        """SingleCheckResult creato correttamente."""
        scr = _make_single_check_result()
        assert scr.ok is True
        assert scr.utilisation == 0.75
        assert len(scr.passaggi_calcolo) == 3
        assert len(scr.formule_usate) == 1
        assert scr.stress_max == 18.75
        assert scr.stress_limit == 25.0

    def test_to_dict(self):
        """to_dict produce dizionario JSON-serializzabile."""
        scr = _make_single_check_result()
        d = scr.to_dict()
        assert isinstance(d, dict)
        assert d["ok"] is True
        assert d["utilisation"] == 0.75
        assert d["stress_max"] == 18.75
        assert "passaggi_calcolo" in d
        # Deve essere JSON-serializzabile
        json_str = json.dumps(d, ensure_ascii=False)
        assert "NTC2018" in json_str

    def test_default_empty_passaggi(self):
        """Default: passaggi_calcolo e formule_usate sono liste vuote."""
        scr = SingleCheckResult(template_id="test", ok=True)
        assert scr.passaggi_calcolo == []
        assert scr.formule_usate == []
        assert scr.stress_max is None


# ==============================================================================
# TEST CalcOutput
# ==============================================================================


class TestCalcOutput:
    """Test per CalcOutput: aggregazione, serializzazione."""

    def test_creation_defaults(self):
        """CalcOutput con defaults."""
        co = CalcOutput()
        assert co.ok is False
        assert co.rapporto_verifica == 0.0
        assert co.passaggi_calcolo == []
        assert co.timestamp != ""

    def test_aggregate_from_templates(self):
        """aggregate_from_templates raccoglie dati dai template."""
        scr1 = _make_single_check_result(
            template_id="check_flessione",
            utilisation=0.75,
            passaggi_calcolo=["Passo A1", "Passo A2"],
            formule_usate=["NTC2018 §4.1.2"],
            stress_max=18.75,
            stress_limit=25.0,
        )
        scr2 = _make_single_check_result(
            template_id="check_taglio",
            utilisation=0.90,
            passaggi_calcolo=["Passo B1"],
            formule_usate=["NTC2018 §4.1.2.1.3.2", "NTC2018 §4.1.2"],
            stress_max=22.5,
            stress_limit=25.0,
        )

        co = CalcOutput(
            element_name="T1",
            norm_code="NTC2018",
            ok=True,
            per_template_results={
                "check_flessione": scr1,
                "check_taglio": scr2,
            },
        )
        co.aggregate_from_templates()

        assert co.rapporto_verifica == 0.90
        assert len(co.passaggi_calcolo) > 0
        # Deve avere intestazioni template
        assert any("check_flessione" in p for p in co.passaggi_calcolo)
        assert any("check_taglio" in p for p in co.passaggi_calcolo)
        # Formule deduplicate
        assert "NTC2018 §4.1.2" in co.formule_usate
        assert "NTC2018 §4.1.2.1.3.2" in co.formule_usate
        # Stress dal template controllante (taglio, util=0.90)
        assert co.stress_max == 22.5
        assert co.stress_limit == 25.0

    def test_to_dict(self):
        """to_dict produce dizionario JSON-serializzabile completo."""
        scr = _make_single_check_result()
        co = CalcOutput(
            element_name="T1",
            norm_code="NTC2018",
            ok=True,
            per_template_results={"check_1": scr},
            rapporto_verifica=0.75,
            stress_max=18.75,
            stress_limit=25.0,
            passaggi_calcolo=["Passo 1"],
            formule_usate=["NTC2018 §4.1.2"],
            warnings=["Copriferro minimo non verificato"],
        )

        d = co.to_dict()
        assert isinstance(d, dict)
        assert d["ok"] is True
        assert d["rapporto_verifica"] == 0.75
        assert d["stress_max"] == 18.75
        assert "verifiche" in d
        assert "check_1" in d["verifiche"]
        assert d["warnings"] == ["Copriferro minimo non verificato"]

        # JSON serializzabile
        json_str = json.dumps(d, ensure_ascii=False, indent=2)
        assert "NTC2018" in json_str

    def test_to_dict_with_validation(self):
        """to_dict include validazione se presente."""
        co = CalcOutput(
            element_name="T1",
            norm_code="NTC2018",
            validation_result=ValidationResult(
                issues=[
                    ValidationIssue(
                        severity="warning",
                        field="As",
                        code="LOW_AS",
                        message_it="Armatura minima",
                    )
                ]
            ),
        )
        d = co.to_dict()
        assert "validazione" in d
        assert d["validazione"]["has_warnings"] is True

    def test_to_latex(self):
        """to_latex genera LaTeX valido con escape caratteri speciali."""
        co = CalcOutput(
            element_name="Trave T1 & T2",
            norm_code="NTC2018",
            ok=True,
            rapporto_verifica=0.75,
            stress_max=18.75,
            stress_limit=25.0,
            passaggi_calcolo=["Passo 1: M_Rd > M_Ed"],
            formule_usate=["NTC2018 §4.1.2"],
            warnings=["Copriferro 100%"],
        )
        latex = co.to_latex()

        # Deve contenere strutture LaTeX
        assert r"\subsection" in latex
        assert r"\begin{tabular}" in latex
        assert r"\end{tabular}" in latex
        # Caratteri speciali escaped
        assert r"\&" in latex  # & → \&
        assert r"\%" in latex  # % → \%
        # Valori numerici
        assert "0.750" in latex
        assert "18.75" in latex

    def test_to_latex_non_verificato(self):
        """to_latex mostra NON VERIFICATO se ok=False."""
        co = CalcOutput(ok=False, element_name="P1")
        latex = co.to_latex()
        assert "NON VERIFICATO" in latex


# ==============================================================================
# TEST NORMALIZZAZIONE
# ==============================================================================


class TestNormalization:
    """Test per normalization.py: conversione unità materiali."""

    def test_normalize_material_fck_kgcm2(self):
        """f_ck > 200 viene convertito da kg/cm² a MPa."""
        mat = MockMaterial(f_ck=250.0, f_yk=450.0)
        mat_norm = normalize_material_to_mpa(mat)
        # 250 kg/cm² = 250 * 0.0980665 ≈ 24.52 MPa
        assert mat_norm.f_ck < 200.0  # Convertito a MPa
        assert abs(mat_norm.f_ck - 24.5166) < 0.01
        # f_yk < 1000, resta invariato
        assert mat_norm.f_yk == 450.0

    def test_normalize_material_fyk_kgcm2(self):
        """f_yk > 1000 viene convertito da kg/cm² a MPa."""
        mat = MockMaterial(f_ck=25.0, f_yk=4400.0)
        mat_norm = normalize_material_to_mpa(mat)
        # 4400 kg/cm² = 4400 * 0.0980665 ≈ 431.49 MPa
        assert mat_norm.f_yk < 1000.0
        assert abs(mat_norm.f_yk - 431.4926) < 0.01
        # f_ck < 200, resta invariato
        assert mat_norm.f_ck == 25.0

    def test_normalize_material_already_mpa(self):
        """Materiale già in MPa resta invariato."""
        mat = MockMaterial(f_ck=25.0, f_yk=450.0)
        mat_norm = normalize_material_to_mpa(mat)
        assert mat_norm.f_ck == 25.0
        assert mat_norm.f_yk == 450.0

    def test_normalize_material_dict(self):
        """Normalizzazione materiale in formato dict."""
        # E = 2_100_000 kg/cm² (acciaio) → > 10000 → auto-detect kg/cm²
        mat = {"f_ck": 300.0, "f_yk": 4400.0, "E": 2_100_000.0}
        mat_norm = normalize_material_to_mpa(mat)
        assert isinstance(mat_norm, dict)
        assert mat_norm["f_ck"] < 200.0
        assert mat_norm["f_yk"] < 1000.0
        # 2_100_000 kg/cm² ≈ 205940 MPa (acciaio)
        assert mat_norm["E"] < 2_100_000.0
        # Annotazioni unità originali
        assert mat_norm["_f_ck_original_unit"] == "kg/cm²"
        assert mat_norm["_f_yk_original_unit"] == "kg/cm²"
        assert mat_norm["_E_original_unit"] == "kg/cm²"

    def test_normalize_material_none(self):
        """Materiale None resta None."""
        assert normalize_material_to_mpa(None) is None

    def test_normalize_to_mpa_calc_input(self):
        """normalize_to_mpa restituisce nuova istanza CalcInput."""
        ci = _make_calc_input(
            material=MockMaterial(f_ck=300.0, f_yk=4400.0),
        )
        ci_norm = normalize_to_mpa(ci)

        # Nuova istanza
        assert ci_norm is not ci
        # Materiale normalizzato
        assert ci_norm.material.f_ck < 200.0
        assert ci_norm.material.f_yk < 1000.0
        # Originale invariato
        assert ci.material.f_ck == 300.0
        assert ci.material.f_yk == 4400.0

    def test_normalize_to_mpa_type_error(self):
        """normalize_to_mpa con tipo errato solleva TypeError."""
        with pytest.raises(TypeError, match="CalcInput"):
            normalize_to_mpa({"not": "a CalcInput"})

    def test_normalization_roundtrip(self):
        """Round-trip: kg/cm² → MPa → kg/cm² preserva precisione."""
        from src.core.adapter_unita_misura import kg_cm2_to_mpa, mpa_to_kg_cm2

        valori_test = [60.0, 100.0, 225.0, 300.0, 2100.0, 4400.0]
        for v_orig in valori_test:
            v_mpa = kg_cm2_to_mpa(v_orig)
            v_back = mpa_to_kg_cm2(v_mpa)
            assert abs(v_back - v_orig) < 0.1, (
                f"Round-trip fallito: {v_orig} → {v_mpa} → {v_back}"
            )


# ==============================================================================
# TEST DENORMALIZZAZIONE OUTPUT
# ==============================================================================


class TestDenormalization:
    """Test per denormalize_for_output."""

    def _make_output(self, **kwargs) -> CalcOutput:
        defaults = dict(
            element_name="T1",
            norm_code="NTC2018",
            ok=True,
            rapporto_verifica=0.75,
            stress_max=25.0,  # MPa
            stress_limit=33.3,  # MPa
            deformation=5.2,  # mm
            passaggi_calcolo=["Passo 1"],
            formule_usate=["NTC2018 §4.1.2"],
            warnings=[],
            errors=[],
        )
        defaults.update(kwargs)
        return CalcOutput(**defaults)

    def test_denormalize_mpa(self):
        """Output in MPa: valori invariati."""
        co = self._make_output()
        d = denormalize_for_output(co, "MPa")
        assert d["stress_max"] == 25.0
        assert d["stress_limit"] == 33.3
        assert d["unita_tensione"] == "MPa"

    def test_denormalize_kgcm2(self):
        """Output in kg/cm²: valori convertiti."""
        co = self._make_output(stress_max=25.0, stress_limit=33.3)
        d = denormalize_for_output(co, "kg/cm²")
        # 25 MPa ≈ 254.93 kg/cm²
        assert d["stress_max"] > 200.0
        assert d["unita_tensione"] == "kg/cm²"
        assert abs(d["stress_max"] - 254.929) < 0.5

    def test_denormalize_kpa(self):
        """Output in kPa: valori moltiplicati per 1000."""
        co = self._make_output(stress_max=25.0)
        d = denormalize_for_output(co, "kPa")
        assert d["stress_max"] == 25000.0
        assert d["unita_tensione"] == "kPa"

    def test_denormalize_invalid_unit(self):
        """Unità non supportata solleva ValueError."""
        co = self._make_output()
        with pytest.raises(ValueError, match="non supportata"):
            denormalize_for_output(co, "psi")

    def test_denormalize_preserves_invariants(self):
        """Rapporto verifica e deformazione sono invarianti."""
        co = self._make_output()
        d = denormalize_for_output(co, "kg/cm²")
        assert d["rapporto_verifica"] == 0.75
        assert d["deformation"] == 5.2
        assert d["ok"] is True

    def test_denormalize_none_stress(self):
        """Tensioni None restano None."""
        co = self._make_output(stress_max=None, stress_limit=None)
        d = denormalize_for_output(co, "kg/cm²")
        assert d["stress_max"] is None
        assert d["stress_limit"] is None


# ==============================================================================
# TEST ADAPTER LEGACY
# ==============================================================================


class TestDictToSingleCheckResult:
    """Test per adapter dict legacy → SingleCheckResult."""

    def test_adapter_esito_ok(self):
        """Adapter mappa 'esito' → ok."""
        result = dict_to_single_check_result(
            {"esito": True, "rateo": 0.85},
            template_id="dm92_flessione",
        )
        assert result.ok is True
        assert result.utilisation == 0.85
        assert result.template_id == "dm92_flessione"

    def test_adapter_verificato(self):
        """Adapter mappa 'verificato' → ok."""
        result = dict_to_single_check_result({"verificato": True})
        assert result.ok is True

    def test_adapter_passaggi(self):
        """Adapter mappa 'passaggi_calcolo' e 'formule_usate'."""
        result = dict_to_single_check_result({
            "esito": True,
            "rateo": 0.5,
            "passaggi_calcolo": ["P1", "P2"],
            "formule_usate": ["DM92 §5.2.1"],
            "sigma_max": 15.0,
            "sigma_amm": 25.0,
        })
        assert result.passaggi_calcolo == ["P1", "P2"]
        assert result.formule_usate == ["DM92 §5.2.1"]
        assert result.stress_max == 15.0
        assert result.stress_limit == 25.0

    def test_adapter_details_preserved(self):
        """Campi extra finiscono in details."""
        result = dict_to_single_check_result({
            "esito": True,
            "rateo": 0.5,
            "x_asse_neutro": 12.5,
            "epsilon_cls": 0.0035,
        })
        assert result.details["x_asse_neutro"] == 12.5
        assert result.details["epsilon_cls"] == 0.0035


# ==============================================================================
# TEST INTEGRAZIONE: PIPELINE COMPLETA
# ==============================================================================


class TestIntegrationPipeline:
    """Test di integrazione: flusso completo input → normalizzazione → output."""

    def test_dm96_pipeline_kgcm2_to_mpa_and_back(self):
        """Pipeline DM96: catalogo kg/cm² → normalizza MPa → verifica → denormalizza."""
        # 1. Materiale da catalogo in kg/cm² (simulazione)
        mat = MockMaterial(
            f_ck=300.0,   # kg/cm² (>200 → auto-detect)
            f_yk=4400.0,  # kg/cm² (>1000 → auto-detect)
            sigma_c_adm=90.0,  # kg/cm² (storico)
        )
        sect = MockSection(width=30, height=50, section_type="rectangular")

        ci = CalcInput(
            element_name="Trave DM96",
            section=sect,
            material=mat,
            norm_code="DM96",
            limit_states_enabled=["TA", "SLU"],
            Mx=80.0,
            As=5.0,
            d=45.0,
        )

        # 2. Normalizzazione
        ci_norm = normalize_to_mpa(ci)
        assert ci_norm.material.f_ck < 200.0  # Ora in MPa
        assert ci_norm.material.f_yk < 1000.0  # Ora in MPa

        # 3. Simulazione verifica (creazione risultato)
        scr = SingleCheckResult(
            template_id="dm96_ta_flessione",
            ok=True,
            utilisation=0.72,
            passaggi_calcolo=[
                f"f_ck = {ci_norm.material.f_ck:.2f} MPa (normalizzato da catalogo)",
                f"f_yk = {ci_norm.material.f_yk:.2f} MPa (normalizzato da catalogo)",
                "σ_cls,calc = 18.0 MPa < σ_amm = 25.0 MPa → OK",
            ],
            formule_usate=["DM92 §5.2.1", "DM96 §2.3"],
            stress_max=18.0,
            stress_limit=25.0,
        )

        co = CalcOutput(
            element_name="Trave DM96",
            norm_code="DM96",
            ok=True,
            per_template_results={"dm96_ta_flessione": scr},
        )
        co.aggregate_from_templates()

        # 4. Verifica aggregazione
        assert co.rapporto_verifica == 0.72
        assert len(co.passaggi_calcolo) > 0
        assert co.stress_max == 18.0

        # 5. Denormalizzazione per output in kg/cm²
        output = denormalize_for_output(co, "kg/cm²")
        assert output["unita_tensione"] == "kg/cm²"
        # 18.0 MPa ≈ 183.5 kg/cm²
        assert output["stress_max"] > 100.0
        assert output["rapporto_verifica"] == 0.72

    def test_rapporto_verifica_le_1_means_ok(self):
        """Rapporto verifica ≤ 1.0 → elemento verificato."""
        scr_ok = _make_single_check_result(utilisation=0.95, ok=True)
        co = CalcOutput(
            ok=True,
            per_template_results={"check": scr_ok},
        )
        co.aggregate_from_templates()
        assert co.rapporto_verifica <= 1.0
        assert co.ok is True

    def test_rapporto_verifica_gt_1_means_fail(self):
        """Rapporto verifica > 1.0 → elemento non verificato."""
        scr_fail = _make_single_check_result(utilisation=1.15, ok=False)
        co = CalcOutput(
            ok=False,
            per_template_results={"check": scr_fail},
        )
        co.aggregate_from_templates()
        assert co.rapporto_verifica > 1.0

    def test_passaggi_calcolo_coherent(self):
        """I passaggi di calcolo aggregati sono coerenti e tracciabili."""
        scr = _make_single_check_result(
            passaggi_calcolo=[
                "1. Dati: b=30cm, d=45cm, As=5.0cm²",
                "2. f_cd = 25.0/1.5 = 16.67 MPa",
                "3. M_Rd = 5.0 * 391.3 * (45 - 0.4*12) = 76100 kgcm = 76.1 kNm",
                "4. M_Ed/M_Rd = 80/76.1 = 1.05 > 1.0 → NON VERIFICATO",
            ]
        )
        co = CalcOutput(
            per_template_results={"check": scr},
        )
        co.aggregate_from_templates()

        # Tutti i passaggi presenti
        full_text = " ".join(co.passaggi_calcolo)
        assert "b=30cm" in full_text
        assert "M_Rd" in full_text
        assert "NON VERIFICATO" in full_text

    def test_to_dict_then_json_roundtrip(self):
        """CalcOutput.to_dict() → JSON → dict: nessuna perdita dati."""
        scr = _make_single_check_result()
        co = CalcOutput(
            element_name="T1",
            norm_code="NTC2018",
            ok=True,
            per_template_results={"check": scr},
            rapporto_verifica=0.75,
            stress_max=18.75,
            stress_limit=25.0,
            passaggi_calcolo=["Passo 1"],
            formule_usate=["NTC2018 §4.1.2"],
        )

        d = co.to_dict()
        json_str = json.dumps(d, ensure_ascii=False, indent=2)
        d_back = json.loads(json_str)

        assert d_back["ok"] is True
        assert d_back["rapporto_verifica"] == 0.75
        assert d_back["stress_max"] == 18.75
        assert d_back["verifiche"]["check"]["ok"] is True
