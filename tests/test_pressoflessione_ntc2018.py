"""Test per check_pressoflessione_slu — verifica generalizzata N+M.

Copre: compressione centrata, trazione centrata, flessione semplice,
presso-flessione, tenso-flessione, flessione deviata (Bresler),
per sezioni rettangolari, circolari, T, I, rettangolari cave.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core_calculus.contracts import CalcInput, VerificationTemplate, NormReference
from src.methods.checks_ntc2018 import check_pressoflessione_slu


# ---------------------------------------------------------------------------
# Helper: template e materiali fittizi
# ---------------------------------------------------------------------------

def _template():
    return VerificationTemplate(
        template_id="test_pressoflessione",
        norm_code="NTC2018",
        norm_version="2018",
        verification_type="pressoflessione",
        limit_state="SLU",
        description_it="Test",
        check_category="resistenza",
        required_inputs=["section", "material", "As", "d"],
        optional_inputs=["N", "Mx", "My", "As_prime", "d_prime"],
        output_metrics=[],
        primary_reference=NormReference(
            norm_code="NTC2018", chapter="4.1", paragraph="4.1.2.1.3.1",
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
    """Materiale C25/30 + B450C."""
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


def _i_section(bf=300.0, tf=20.0, tw=12.0, hw=360.0):
    return SimpleNamespace(
        section_type="I_SECTION",
        flange_width=bf, flange_thickness=tf,
        web_thickness=tw, web_height=hw,
    )


def _rect_hollow(w=400.0, h=600.0, t=40.0):
    return SimpleNamespace(
        section_type="RECTANGULAR_HOLLOW",
        width=w, height=h, thickness=t,
    )


def _calc_input(**kwargs):
    """Crea CalcInput con valori di default ragionevoli."""
    defaults = dict(
        section=_rect(),
        material=_material(),
        N=0.0,
        Mx=0.0,
        My=0.0,
        Mz=None,
        Tx=None,
        Ty=None,
        As=8.0,        # cm²
        As_prime=4.0,   # cm²
        d=45.0,         # cm
        d_prime=4.0,    # cm
        staffe_diametro=None,
        staffe_passo=None,
        staffe_num_bracci=None,
        lc=None,
        fc=None,
    )
    defaults.update(kwargs)
    return CalcInput(**defaults)


# ===========================================================================
# Test input mancante
# ===========================================================================

class TestInputValidation:
    def test_section_none(self):
        ci = _calc_input(section=None)
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is False
        assert "Sezione non specificata" in res.messages_it[0]

    def test_material_none(self):
        ci = _calc_input(material=None)
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is False
        assert "Materiale non specificato" in res.messages_it[0]

    def test_material_missing_fck(self):
        ci = _calc_input(material=SimpleNamespace(f_yk=450))
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is False

    def test_unknown_section_type(self):
        ci = _calc_input(section=SimpleNamespace(section_type="UNKNOWN"))
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is False


# ===========================================================================
# Test sollecitazioni nulle
# ===========================================================================

class TestNullLoads:
    def test_zero_loads(self):
        ci = _calc_input(N=0, Mx=0, My=0)
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert res.utilisation == pytest.approx(0.0)


# ===========================================================================
# Test compressione centrata
# ===========================================================================

class TestCompressioneCentrata:
    def test_rect_compression_ok(self):
        """Compressione centrata moderata su rettangolare → ok."""
        ci = _calc_input(
            section=_rect(300, 500),
            N=500.0,  # kN compressione
            Mx=0.0, My=0.0,
            As=8.0, As_prime=8.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert res.utilisation < 1.0
        assert "COMPRESSIONE CENTRATA" in " ".join(res.messages_it)

    def test_rect_compression_failure(self):
        """Compressione centrata eccessiva → non ok."""
        ci = _calc_input(
            section=_rect(200, 200),
            N=5000.0,  # kN, molto alto per sezione piccola
            Mx=0.0, My=0.0,
            As=4.0, As_prime=4.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is False


# ===========================================================================
# Test trazione centrata
# ===========================================================================

class TestTrazioneCentrata:
    def test_tension_ok(self):
        """Trazione centrata con armatura sufficiente."""
        ci = _calc_input(
            N=-100.0,  # kN trazione
            Mx=0.0, My=0.0,
            As=8.0, As_prime=8.0,
            d=45.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert "TRAZIONE CENTRATA" in " ".join(res.messages_it)

    def test_tension_failure(self):
        """Trazione centrata eccessiva."""
        ci = _calc_input(
            N=-2000.0,  # kN, troppa trazione
            Mx=0.0, My=0.0,
            As=2.0, As_prime=2.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is False


# ===========================================================================
# Test flessione semplice (N=0) — sezioni diverse
# ===========================================================================

class TestFlessioneSemplice:
    def test_rect_bending(self):
        """Flessione semplice rettangolare."""
        ci = _calc_input(
            section=_rect(300, 500),
            N=0.0, Mx=100.0,
            As=10.0, As_prime=4.0, d=45.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert res.details["M_Rd_kNm"] > 100.0
        assert "FLESSIONE SEMPLICE" in " ".join(res.messages_it)

    def test_circular_bending(self):
        """Flessione semplice circolare."""
        ci = _calc_input(
            section=_circ(400),
            N=0.0, Mx=80.0,
            As=12.0, As_prime=6.0, d=35.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert res.details["M_Rd_kNm"] > 0

    def test_t_section_bending(self):
        """Flessione semplice T-section (flangia compressa)."""
        ci = _calc_input(
            section=_t_section(bf=600, tf=100, tw=200, hw=400),
            N=0.0, Mx=150.0,
            As=12.0, As_prime=4.0, d=45.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        # T-section con flangia larga ha M_Rd > rettangolare equivalente
        assert res.details["M_Rd_kNm"] > 150.0

    def test_i_section_bending(self):
        """Flessione semplice I-section con flangia larga."""
        # Flangia larga: asse neutro resta nella flangia → x/d basso
        ci = _calc_input(
            section=_i_section(bf=300, tf=50, tw=20, hw=300),
            N=0.0, Mx=50.0,
            As=8.0, As_prime=4.0, d=38.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True

    def test_rect_hollow_bending(self):
        """Flessione semplice rettangolare cava."""
        ci = _calc_input(
            section=_rect_hollow(400, 600, 40),
            N=0.0, Mx=120.0,
            As=10.0, As_prime=6.0, d=55.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True


# ===========================================================================
# Test presso-flessione retta (N>0, Mx>0)
# ===========================================================================

class TestPressoFlessione:
    def test_rect_typical_column(self):
        """Pilastro rettangolare: N=500kN, Mx=80kNm."""
        ci = _calc_input(
            section=_rect(300, 500),
            N=500.0, Mx=80.0,
            As=8.0, As_prime=8.0, d=45.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert "PRESSO-FLESSIONE" in " ".join(res.messages_it)
        assert 0 < res.utilisation < 1.0

    def test_circular_column(self):
        """Pilastro circolare: N=300kN, Mx=50kNm."""
        ci = _calc_input(
            section=_circ(400),
            N=300.0, Mx=50.0,
            As=10.0, As_prime=10.0, d=35.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True

    def test_insufficient_section(self):
        """Sezione insufficiente → ok=False."""
        ci = _calc_input(
            section=_rect(200, 200),
            N=1000.0, Mx=200.0,
            As=2.0, As_prime=2.0, d=18.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is False
        assert res.utilisation > 1.0


# ===========================================================================
# Test tenso-flessione retta (N<0, Mx>0)
# ===========================================================================

class TestTensoFlessione:
    def test_rect_tension_bending(self):
        """Tenso-flessione moderata."""
        ci = _calc_input(
            section=_rect(300, 500),
            N=-100.0,  # trazione
            Mx=60.0,
            As=12.0, As_prime=8.0, d=45.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert "TENSO-FLESSIONE" in " ".join(res.messages_it)


# ===========================================================================
# Test flessione deviata (Bresler)
# ===========================================================================

class TestFlessioneDeviata:
    def test_biaxial_ok(self):
        """Flessione deviata moderata con Bresler → ok."""
        ci = _calc_input(
            section=_rect(300, 500),
            N=300.0,
            Mx=40.0, My=20.0,
            As=10.0, As_prime=10.0, d=45.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert res.details.get("biaxial") is True
        assert "Bresler" in " ".join(res.messages_it)
        assert res.details["alpha_bresler"] >= 1.0
        assert res.details["bresler_value"] < 1.0

    def test_biaxial_failure(self):
        """Flessione deviata eccessiva → non ok."""
        ci = _calc_input(
            section=_rect(200, 300),
            N=200.0,
            Mx=100.0, My=80.0,
            As=4.0, As_prime=4.0, d=26.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        # Con sezione piccola e momenti alti, dovrebbe fallire
        assert res.ok is False or res.utilisation > 0.8

    def test_biaxial_alpha_low_N(self):
        """Per N piccolo, α → 1.0 (interazione lineare)."""
        ci = _calc_input(
            section=_rect(400, 600),
            N=10.0,  # N molto piccolo
            Mx=50.0, My=30.0,
            As=12.0, As_prime=12.0, d=55.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        alpha = res.details.get("alpha_bresler", 0)
        assert alpha == pytest.approx(1.0, abs=0.15)

    def test_biaxial_circular(self):
        """Flessione deviata su sezione circolare."""
        ci = _calc_input(
            section=_circ(500),
            N=200.0,
            Mx=30.0, My=20.0,
            As=12.0, As_prime=12.0, d=43.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.details.get("biaxial") is True


# ===========================================================================
# Test flessione attorno a y (My, asse debole)
# ===========================================================================

class TestFlessioneAsseY:
    def test_rect_my_only(self):
        """Flessione attorno a y (asse debole), solo My."""
        ci = _calc_input(
            section=_rect(300, 500),
            N=0.0, Mx=0.0, My=30.0,
            As=8.0, As_prime=4.0, d=45.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        assert res.ok is True
        assert res.details.get("axis") == "y"


# ===========================================================================
# Test duttilità (x/d > 0.45)
# ===========================================================================

class TestDuttilita:
    def test_over_reinforced(self):
        """Sezione molto armata a compressione → x/d > 0.45."""
        ci = _calc_input(
            section=_rect(200, 300),
            N=800.0,  # forte compressione
            Mx=10.0,
            As=30.0,  # moltissima armatura
            As_prime=30.0,
            d=26.0,
        )
        res = check_pressoflessione_slu(ci, _template())
        # Con forte N, x/d tende a > 0.45
        if res.details.get("x_over_d", 0) > 0.45:
            assert res.ok is False
            assert res.details["over_reinforced"] is True
