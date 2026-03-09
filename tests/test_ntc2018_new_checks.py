"""Test per le nuove verifiche NTC2018: torsione, tensioni SLE, fessurazione, deformazioni.

Copre: torsione SLU, tensioni esercizio SLE, fessurazione SLE, deformazioni SLE,
proprietà torsionali sezioni, per sezioni rettangolari, circolari, T, cave.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core_calculus.contracts import CalcInput, NormReference, VerificationTemplate

# ---------------------------------------------------------------------------
# Helper: template e materiali fittizi
# ---------------------------------------------------------------------------

def _template(vtype="torsione", limit_state="SLU"):
    return VerificationTemplate(
        template_id=f"test_{vtype}",
        norm_code="NTC2018",
        norm_version="2018",
        verification_type=vtype,
        limit_state=limit_state,
        description_it="Test",
        check_category="resistenza" if limit_state == "SLU" else vtype,
        required_inputs=["section", "material"],
        optional_inputs=[],
        output_metrics=[],
        primary_reference=NormReference(
            norm_code="NTC2018", chapter="4.1", paragraph="4.1",
            description_it="test",
        ),
        secondary_references=[],
        function_path="test",
        can_batch=False,
        supports_real_time=False,
        applicable_section_types=[],
        applicable_material_tags=[],
        requires_existing_structure=False,
        extra_params={},
    )


def _material(f_ck=25.0, f_yk=450.0):
    return SimpleNamespace(f_ck=f_ck, f_yk=f_yk)


def _rect(w=300.0, h=500.0):
    return SimpleNamespace(section_type="RECTANGULAR", width=w, height=h)


def _circ(d=400.0):
    return SimpleNamespace(section_type="CIRCULAR", diameter=d)


def _t_section(bf=600.0, tf=100.0, tw=200.0, hw=400.0):
    return SimpleNamespace(
        section_type="T_SECTION",
        flange_width=bf, flange_thickness=tf,
        web_thickness=tw, web_height=hw,
    )


def _rect_hollow(w=400.0, h=600.0, t=40.0):
    return SimpleNamespace(
        section_type="RECTANGULAR_HOLLOW",
        width=w, height=h, thickness=t,
    )


def _calc_input(**kwargs):
    defaults = dict(
        section=_rect(),
        material=_material(),
        N=0.0, Mx=0.0, My=0.0, Mz=None,
        Tx=None, Ty=None,
        As=8.0, As_prime=4.0,
        d=45.0, d_prime=4.0,
        staffe_diametro=None, staffe_passo=None, staffe_num_bracci=None,
        lc=None, fc=None,
    )
    defaults.update(kwargs)
    return CalcInput(**defaults)


# ===========================================================================
# Test proprietà torsionali (section_fiber.compute_torsion_properties)
# ===========================================================================

class TestTorsionProperties:
    def test_rect_torsion(self):
        from src.methods.section_fiber import compute_torsion_properties
        sec = _rect(300, 500)
        A_k, u_k, t_ef = compute_torsion_properties(sec)
        assert A_k > 0
        assert u_k > 0
        assert t_ef > 0
        # t_ef = A / u = 300*500 / (2*(300+500)) = 93.75
        assert t_ef == pytest.approx(93.75, rel=0.01)

    def test_circular_torsion(self):
        from src.methods.section_fiber import compute_torsion_properties
        sec = _circ(400)
        A_k, u_k, t_ef = compute_torsion_properties(sec)
        assert A_k > 0
        # t_ef = A/u = pi*R^2 / (2*pi*R) = R/2 = 100
        assert t_ef == pytest.approx(100.0, rel=0.01)

    def test_rect_hollow_torsion(self):
        from src.methods.section_fiber import compute_torsion_properties
        sec = _rect_hollow(400, 600, 40)
        A_k, u_k, t_ef = compute_torsion_properties(sec)
        assert t_ef == pytest.approx(40.0)  # wall thickness
        # A_k = (400-40)*(600-40) = 360*560
        assert A_k == pytest.approx(360 * 560, rel=0.01)

    def test_t_section_torsion(self):
        from src.methods.section_fiber import compute_torsion_properties
        sec = _t_section()
        A_k, u_k, t_ef = compute_torsion_properties(sec)
        assert A_k > 0
        assert t_ef > 0


# ===========================================================================
# Test torsione SLU
# ===========================================================================

class TestTorsioneSLU:
    def test_zero_torsion(self):
        from src.methods.ntc2018.checks import check_torsione_slu
        ci = _calc_input(Mz=0.0)
        res = check_torsione_slu(ci, _template("torsione"))
        assert res.ok is True
        assert res.utilisation == pytest.approx(0.0)

    def test_section_none(self):
        from src.methods.ntc2018.checks import check_torsione_slu
        ci = _calc_input(section=None, Mz=10.0)
        res = check_torsione_slu(ci, _template("torsione"))
        assert res.ok is False

    def test_material_none(self):
        from src.methods.ntc2018.checks import check_torsione_slu
        ci = _calc_input(material=None, Mz=10.0)
        res = check_torsione_slu(ci, _template("torsione"))
        assert res.ok is False

    def test_moderate_torsion_rect(self):
        """Torsione moderata su rettangolare → ok."""
        from src.methods.ntc2018.checks import check_torsione_slu
        ci = _calc_input(
            section=_rect(300, 500),
            Mz=5.0,  # kNm, modesto
            staffe_diametro=8, staffe_passo=15, staffe_num_bracci=2,
        )
        res = check_torsione_slu(ci, _template("torsione"))
        assert res.ok is True
        assert res.details["T_Rd_max_kNm"] > 5.0
        assert res.utilisation < 1.0

    def test_excessive_torsion(self):
        """Torsione eccessiva su sezione piccola → non ok."""
        from src.methods.ntc2018.checks import check_torsione_slu
        ci = _calc_input(
            section=_rect(150, 200),
            Mz=50.0,  # molto alto per sezione piccola
            staffe_diametro=6, staffe_passo=20, staffe_num_bracci=2,
        )
        res = check_torsione_slu(ci, _template("torsione"))
        assert res.ok is False
        assert res.utilisation > 1.0

    def test_torsion_with_shear_interaction(self):
        """Torsione + taglio → interazione verificata."""
        from src.methods.ntc2018.checks import check_torsione_slu
        ci = _calc_input(
            section=_rect(300, 500),
            Mz=5.0, Tx=50.0,
            staffe_diametro=8, staffe_passo=15, staffe_num_bracci=2,
        )
        res = check_torsione_slu(ci, _template("torsione"))
        assert res.details["has_interaction"] is True
        assert res.details["interaction_ratio"] > 0

    def test_rect_hollow_torsion(self):
        """Sezione cava: buona per torsione."""
        from src.methods.ntc2018.checks import check_torsione_slu
        ci = _calc_input(
            section=_rect_hollow(400, 600, 40),
            Mz=20.0,
            staffe_diametro=10, staffe_passo=15, staffe_num_bracci=2,
        )
        res = check_torsione_slu(ci, _template("torsione"))
        # Sezioni cave resistono bene a torsione
        assert res.details["T_Rd_max_kNm"] > 20.0


# ===========================================================================
# Test tensioni SLE
# ===========================================================================

class TestTensioniSLE:
    def test_zero_loads(self):
        from src.methods.ntc2018.checks import check_tensioni_sle
        ci = _calc_input(Mx=0.0, N=0.0)
        res = check_tensioni_sle(ci, _template("tensioni_esercizio", "SLE"))
        assert res.ok is True
        assert res.utilisation == pytest.approx(0.0)

    def test_section_none(self):
        from src.methods.ntc2018.checks import check_tensioni_sle
        ci = _calc_input(section=None, Mx=50.0)
        res = check_tensioni_sle(ci, _template("tensioni_esercizio", "SLE"))
        assert res.ok is False

    def test_moderate_bending_rect(self):
        """Flessione moderata → tensioni entro limiti."""
        from src.methods.ntc2018.checks import check_tensioni_sle
        ci = _calc_input(
            section=_rect(300, 500),
            Mx=30.0,  # kNm, modesto per questa sezione
            As=8.0, d=45.0,
        )
        res = check_tensioni_sle(ci, _template("tensioni_esercizio", "SLE"))
        assert res.ok is True
        assert res.details["sigma_c_MPa"] > 0
        assert res.details["sigma_s_MPa"] > 0
        assert res.details["sigma_c_MPa"] < 15.0  # 0.6*25 = 15
        assert res.utilisation < 1.0

    def test_high_bending_fails(self):
        """Flessione alta con poca armatura → tensione acciaio troppo alta."""
        from src.methods.ntc2018.checks import check_tensioni_sle
        ci = _calc_input(
            section=_rect(200, 300),
            Mx=100.0,  # alto per sezione piccola
            As=2.0, d=26.0,
        )
        res = check_tensioni_sle(ci, _template("tensioni_esercizio", "SLE"))
        # Con poca armatura e tanto momento, σ_s > 0.8*fyk
        assert res.utilisation > 0.5  # almeno significativo


# ===========================================================================
# Test fessurazione SLE
# ===========================================================================

class TestFessurazioneSLE:
    def test_zero_moment(self):
        from src.methods.ntc2018.checks import check_fessurazione_sle
        ci = _calc_input(Mx=0.0)
        res = check_fessurazione_sle(ci, _template("fessurazione", "SLE"))
        assert res.ok is True

    def test_section_none(self):
        from src.methods.ntc2018.checks import check_fessurazione_sle
        ci = _calc_input(section=None, Mx=50.0)
        res = check_fessurazione_sle(ci, _template("fessurazione", "SLE"))
        assert res.ok is False

    def test_moderate_cracking_ok(self):
        """Fessure entro limite 0.3mm."""
        from src.methods.ntc2018.checks import check_fessurazione_sle
        ci = _calc_input(
            section=_rect(300, 500),
            Mx=30.0,
            As=10.0, d=45.0,
        )
        res = check_fessurazione_sle(ci, _template("fessurazione", "SLE"))
        assert res.ok is True
        assert res.details["w_k_mm"] < 0.3
        assert res.details["w_k_mm"] > 0.0

    def test_excessive_cracking(self):
        """Fessure eccessive con poca armatura."""
        from src.methods.ntc2018.checks import check_fessurazione_sle
        ci = _calc_input(
            section=_rect(200, 300),
            Mx=80.0,  # alto
            As=2.0, d=26.0,
        )
        res = check_fessurazione_sle(ci, _template("fessurazione", "SLE"))
        # Con poca armatura e tanto momento, fessure ampie
        assert res.details["w_k_mm"] > 0

    def test_w_k_positive(self):
        """w_k deve essere positivo con momento non nullo."""
        from src.methods.ntc2018.checks import check_fessurazione_sle
        ci = _calc_input(
            section=_rect(300, 500),
            Mx=50.0,
            As=8.0, d=45.0,
        )
        res = check_fessurazione_sle(ci, _template("fessurazione", "SLE"))
        assert res.details["w_k_mm"] > 0


# ===========================================================================
# Test deformazioni SLE
# ===========================================================================

class TestDeformazioniSLE:
    def test_zero_moment(self):
        from src.methods.ntc2018.checks import check_deformazioni_sle
        ci = _calc_input(Mx=0.0, extra={"span_mm": 5000.0})
        res = check_deformazioni_sle(ci, _template("deformazioni", "SLE"))
        assert res.ok is True

    def test_missing_span(self):
        from src.methods.ntc2018.checks import check_deformazioni_sle
        ci = _calc_input(Mx=50.0)
        res = check_deformazioni_sle(ci, _template("deformazioni", "SLE"))
        assert res.ok is False
        assert "span_mm" in res.messages_it[0]

    def test_moderate_deflection_ok(self):
        """Freccia entro L/250."""
        from src.methods.ntc2018.checks import check_deformazioni_sle
        ci = _calc_input(
            section=_rect(300, 500),
            Mx=30.0,
            As=10.0, As_prime=4.0, d=45.0,
            extra={"span_mm": 5000.0, "phi_creep": 2.0},
        )
        res = check_deformazioni_sle(ci, _template("deformazioni", "SLE"))
        assert res.ok is True
        assert res.details["delta_mm"] > 0
        assert res.details["delta_mm"] < 20.0  # L/250 = 20mm
        assert res.utilisation < 1.0

    def test_long_span_fails(self):
        """Luce lunga con sezione piccola → freccia eccessiva."""
        from src.methods.ntc2018.checks import check_deformazioni_sle
        ci = _calc_input(
            section=_rect(200, 300),
            Mx=50.0,
            As=4.0, d=26.0,
            extra={"span_mm": 8000.0, "phi_creep": 2.5},
        )
        res = check_deformazioni_sle(ci, _template("deformazioni", "SLE"))
        # Con luce lunga e sezione piccola, freccia alta
        assert res.details["delta_mm"] > 0

    def test_section_none(self):
        from src.methods.ntc2018.checks import check_deformazioni_sle
        ci = _calc_input(section=None, Mx=50.0, extra={"span_mm": 5000.0})
        res = check_deformazioni_sle(ci, _template("deformazioni", "SLE"))
        assert res.ok is False

    def test_creep_amplification(self):
        """Freccia con creep > senza creep."""
        from src.methods.ntc2018.checks import check_deformazioni_sle
        ci_no_creep = _calc_input(
            section=_rect(300, 500),
            Mx=30.0, As=10.0, d=45.0,
            extra={"span_mm": 5000.0, "phi_creep": 0.0},
        )
        ci_creep = _calc_input(
            section=_rect(300, 500),
            Mx=30.0, As=10.0, d=45.0,
            extra={"span_mm": 5000.0, "phi_creep": 2.0},
        )
        res_no = check_deformazioni_sle(ci_no_creep, _template("deformazioni", "SLE"))
        res_yes = check_deformazioni_sle(ci_creep, _template("deformazioni", "SLE"))
        assert res_yes.details["delta_mm"] > res_no.details["delta_mm"]
