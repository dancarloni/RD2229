"""Test FASE J — Pressoflessione deviata multinorma.

Copre:
  - BarraArmatura estensione x (retrocompat)
  - Sezione omogenizzata biassiale (I_x_om, I_y_om, Wx, Wy)
  - Sovrapposizione elastica TA (rettangolare, T, circolare)
  - Bresler TA (alpha=1.0, alpha=4/3)
  - SLU wrapper (NTC2018, NTC2008, EC2)
  - Dominio 3D (generazione, coerenza)
  - Instabilita' biassiale (omega, amplificazione)
  - Dispatcher multinorma (routing, errori)
  - Disegno matplotlib headless
  - crea_armatura_rettangolare helper
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.codes.pressoflessione.base import (
    DominioNMy,
    PressoflessSpec,
    calcola_omogenizzata_biassiale,
    crea_armatura_rettangolare,
)
from src.codes.pressoflessione.dispatcher import (
    NORME,
    NORME_SLU,
    NORME_TA,
    calcola_pressoflessione_deviata,
)
from src.codes.pressoflessione.dominio import _m_rd_bresler, calcola_dominio_3d
from src.codes.pressoflessione.instabilita_biassiale import amplifica_momenti_biassiale
from src.codes.pressoflessione.ta_cls import (
    calcola_M_Rd_ta,
    verifica_bresler_ta,
    verifica_pressofless_ta_cls,
    verifica_sovrapposizione_elastica,
)
from src.codes.section_params.omogenizzata import BarraArmatura

# ===========================================================================
# Fixtures
# ===========================================================================


def _rect(w=30.0, h=50.0):
    return SimpleNamespace(section_type="RECTANGULAR", width=w, height=h)


def _circ(d=40.0):
    return SimpleNamespace(section_type="CIRCULAR", diameter=d)


def _t_sec(bf=40.0, tf=10.0, tw=15.0, hw=35.0):
    return SimpleNamespace(
        section_type="T_SECTION",
        flange_width=bf,
        flange_thickness=tf,
        web_thickness=tw,
        web_height=hw,
    )


def _barre_simm_rett(h=50.0, b=30.0, copri=4.0, A_inf=5.0, A_sup=5.0):
    """2 livelli simmetrici, x=0 (centrate)."""
    return [
        BarraArmatura(y=copri, A=A_sup, zona="compressa", x=0.0),
        BarraArmatura(y=h - copri, A=A_inf, zona="tesa", x=0.0),
    ]


def _spec_ta(
    section=None,
    barre=None,
    N=5000.0,
    Mx=200000.0,
    My=100000.0,
    sigma_adm=85.0,
    norma="RD2229",
    metodo="SOVRAPPOSIZIONE_ELASTICA",
    alpha=1.0,
    n=15.0,
):
    if section is None:
        section = _rect()
    if barre is None:
        barre = _barre_simm_rett()
    return PressoflessSpec(
        section=section,
        barre=barre,
        N_kg=N,
        Mx_kgcm=Mx,
        My_kgcm=My,
        sigma_c_adm_kgcm2=sigma_adm,
        n=n,
        norma=norma,
        metodo=metodo,
        alpha_bresler=alpha,
    )


# ===========================================================================
# TestBarraArmaturaExtension
# ===========================================================================


class TestBarraArmaturaExtension:
    """Retrocompat + campo x biassiale."""

    def test_default_x_zero(self):
        b = BarraArmatura(y=46.0, A=10.0)
        assert b.x == 0.0

    def test_explicit_x(self):
        b = BarraArmatura(y=46.0, A=10.0, x=5.0)
        assert b.x == 5.0

    def test_retrocompat_zona(self):
        b = BarraArmatura(y=46.0, A=10.0, zona="tesa")
        assert b.zona == "tesa"
        assert b.x == 0.0

    def test_negative_x(self):
        b = BarraArmatura(y=46.0, A=10.0, x=-8.0)
        assert b.x == -8.0

    def test_biaxial_pair(self):
        b1 = BarraArmatura(y=46.0, A=5.0, x=-10.0)
        b2 = BarraArmatura(y=46.0, A=5.0, x=10.0)
        assert b1.x + b2.x == 0.0


# ===========================================================================
# TestCreaArmaturaRettangolare
# ===========================================================================


class TestCreaArmaturaRettangolare:
    def test_4_barre_inf(self):
        barre = crea_armatura_rettangolare(30, 50, 4, 4, 16)
        assert len(barre) == 4
        assert all(b.zona == "tesa" for b in barre)
        # y = h - copriferro = 46
        assert all(abs(b.y - 46.0) < 0.01 for b in barre)
        # x distribuite da -11 a +11
        xs = sorted(b.x for b in barre)
        assert abs(xs[0] - (-11.0)) < 0.01
        assert abs(xs[-1] - 11.0) < 0.01

    def test_inf_sup(self):
        barre = crea_armatura_rettangolare(30, 50, 4, 3, 16, 2, 14)
        n_tese = sum(1 for b in barre if b.zona == "tesa")
        n_comp = sum(1 for b in barre if b.zona == "compressa")
        assert n_tese == 3
        assert n_comp == 2

    def test_single_bar(self):
        barre = crea_armatura_rettangolare(30, 50, 4, 1, 20)
        assert len(barre) == 1
        assert barre[0].x == 0.0

    def test_area_correct(self):
        barre = crea_armatura_rettangolare(30, 50, 4, 2, 20)
        A_expected = math.pi * 2.0**2 / 4.0  # diam 20mm = 2cm
        assert abs(barre[0].A - A_expected) < 1e-6


# ===========================================================================
# TestOmogenizzataBiassiale
# ===========================================================================


class TestOmogenizzataBiassiale:
    def test_rect_no_barre(self):
        """Sezione lorda rettangolare senza barre."""
        props = calcola_omogenizzata_biassiale(_rect(30, 50), [], 15)
        assert props["esito"] == "OK"
        A = 30 * 50
        assert abs(props["A_om_cm2"] - A) < 1.0
        assert abs(props["y_G_om_cm"] - 25.0) < 0.5
        # I_x = b*h^3/12 = 30*50^3/12 = 312500
        assert abs(props["I_x_om_cm4"] - 312500) < 500
        # I_y = h*b^3/12 = 50*30^3/12 = 112500
        assert abs(props["I_y_om_cm4"] - 112500) < 500

    def test_rect_with_symm_barre(self):
        """Con barre simmetriche, x_G deve restare ~0."""
        barre = _barre_simm_rett()
        props = calcola_omogenizzata_biassiale(_rect(), barre, 15)
        assert props["esito"] == "OK"
        assert abs(props["x_G_om_cm"]) < 0.1
        # A_om > A_c
        assert props["A_om_cm2"] > 30 * 50

    def test_rect_I_y_increases_with_x(self):
        """Barre con x != 0 aumentano I_y."""
        barre_center = [BarraArmatura(y=46, A=10, x=0.0)]
        barre_edge = [BarraArmatura(y=46, A=10, x=10.0)]
        props_c = calcola_omogenizzata_biassiale(_rect(), barre_center, 15)
        props_e = calcola_omogenizzata_biassiale(_rect(), barre_edge, 15)
        assert props_e["I_y_om_cm4"] > props_c["I_y_om_cm4"]

    def test_Wx_Wy_positive(self):
        props = calcola_omogenizzata_biassiale(_rect(), _barre_simm_rett(), 15)
        assert props["Wx_sup_cm3"] > 0
        assert props["Wx_inf_cm3"] > 0
        assert props["Wy_sx_cm3"] > 0
        assert props["Wy_dx_cm3"] > 0

    def test_symmetric_Wy(self):
        """Per sezione + barre simmetriche: Wy_sx == Wy_dx."""
        props = calcola_omogenizzata_biassiale(_rect(), _barre_simm_rett(), 15)
        assert abs(props["Wy_sx_cm3"] - props["Wy_dx_cm3"]) < 1.0

    def test_I_xy_zero_symmetric(self):
        """I_xy = 0 per sezione e armature simmetriche."""
        barre = [
            BarraArmatura(y=4, A=5, x=-10),
            BarraArmatura(y=4, A=5, x=10),
            BarraArmatura(y=46, A=5, x=-10),
            BarraArmatura(y=46, A=5, x=10),
        ]
        props = calcola_omogenizzata_biassiale(_rect(), barre, 15)
        assert abs(props["I_xy_om_cm4"]) < 1.0

    def test_circular_section(self):
        """Circolare: I_x ~ I_y (entrambi pi*d^4/64)."""
        props = calcola_omogenizzata_biassiale(_circ(40), [], 15)
        assert props["esito"] == "OK"
        # Per circolare senza barre: I_x ~ I_y
        ratio = props["I_x_om_cm4"] / props["I_y_om_cm4"]
        assert 0.9 < ratio < 1.1

    def test_t_section(self):
        """T-section: I_y > per direzione con ala."""
        props = calcola_omogenizzata_biassiale(_t_sec(), [], 15)
        assert props["esito"] == "OK"
        # Il baricentro e' spostato verso l'ala
        assert props["y_G_om_cm"] < 22.5  # < meta' altezza


# ===========================================================================
# TestSovrapposizioneElastica
# ===========================================================================


class TestSovrapposizioneElastica:
    def test_basic_rect(self):
        """Verifica base: sigma = N/A + Mx*y/Ix + My*x/Iy."""
        spec = _spec_ta(N=5000, Mx=200000, My=100000, sigma_adm=85)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.metodo == "SOVRAPPOSIZIONE_ELASTICA"
        assert res.norma == "RD2229"
        assert res.sigma_c_max_kgcm2 > 0
        assert res.utilisation > 0

    def test_pure_N(self):
        """Solo sforzo normale: sigma = N/A."""
        spec = _spec_ta(N=1000, Mx=0, My=0, sigma_adm=85)
        res = verifica_sovrapposizione_elastica(spec)
        # sigma ~ 1000 / A_om
        assert res.sigma_c_max_kgcm2 < 1.0  # ben sotto il limite
        assert res.esito == "OK"

    def test_pure_Mx(self):
        """Solo momento Mx."""
        spec = _spec_ta(N=0, Mx=100000, My=0, sigma_adm=85)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.sigma_c_max_kgcm2 > 0
        assert res.details["sigma_My_kgcm2"] == 0.0

    def test_over_limit(self):
        """Superamento limite -> NON_OK."""
        spec = _spec_ta(N=50000, Mx=500000, My=300000, sigma_adm=30)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.esito == "NON_OK"
        assert res.utilisation > 1.0

    def test_passaggi_calcolo(self):
        """Verifica presenza passaggi di calcolo."""
        spec = _spec_ta()
        res = verifica_sovrapposizione_elastica(spec)
        assert len(res.passaggi_calcolo) >= 5

    def test_norm_references(self):
        spec = _spec_ta(norma="DM96")
        res = verifica_sovrapposizione_elastica(spec)
        assert any("DM" in r for r in res.norm_references)


# ===========================================================================
# TestSovrapposizioneElasticaDuckTyped
# ===========================================================================


class TestSovrapposizioneElasticaDuckTyped:
    def test_t_section(self):
        sec = _t_sec()
        barre = [BarraArmatura(y=42, A=8, x=0)]
        spec = _spec_ta(section=sec, barre=barre, N=3000, Mx=100000, My=50000)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.esito in ("OK", "NON_OK")
        assert res.sigma_c_max_kgcm2 > 0

    def test_circular(self):
        sec = _circ(40)
        barre = [BarraArmatura(y=36, A=6, x=0)]
        spec = _spec_ta(section=sec, barre=barre, N=2000, Mx=80000, My=40000)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.esito in ("OK", "NON_OK")

    def test_rect_no_barre(self):
        """Sezione lorda (nessuna barra)."""
        spec = _spec_ta(barre=[], N=2000, Mx=100000, My=0)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.esito in ("OK", "NON_OK")

    def test_rect_hollow(self):
        sec = SimpleNamespace(
            section_type="RECTANGULAR_HOLLOW",
            width=40,
            height=60,
            thickness=5,
        )
        spec = _spec_ta(section=sec, barre=[], N=2000, Mx=100000, My=50000)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.esito in ("OK", "NON_OK")

    def test_circular_hollow(self):
        sec = SimpleNamespace(
            section_type="CIRCULAR_HOLLOW",
            outer_diameter=50,
            thickness=5,
        )
        spec = _spec_ta(section=sec, barre=[], N=2000, Mx=100000, My=50000)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.esito in ("OK", "NON_OK")


# ===========================================================================
# TestBreslerTA
# ===========================================================================


class TestBreslerTA:
    def test_alpha_1(self):
        """Bresler con alpha=1 (conservativo)."""
        spec = _spec_ta(metodo="BRESLER_TA", alpha=1.0, N=5000, Mx=100000, My=50000)
        res = verifica_bresler_ta(spec)
        assert res.metodo == "BRESLER_TA"
        assert res.bresler_value is not None
        assert res.M_Rdx_kgcm > 0
        assert res.M_Rdy_kgcm > 0

    def test_alpha_giangreco(self):
        """Bresler con alpha=4/3 (Giangreco) — meno conservativo."""
        spec1 = _spec_ta(metodo="BRESLER_TA", alpha=1.0, N=5000, Mx=100000, My=50000)
        spec2 = _spec_ta(metodo="BRESLER_TA", alpha=4.0 / 3.0, N=5000, Mx=100000, My=50000)
        res1 = verifica_bresler_ta(spec1)
        res2 = verifica_bresler_ta(spec2)
        # alpha=4/3 e' meno conservativo: bresler_value minore
        assert res2.bresler_value < res1.bresler_value

    def test_M_Rdx_formula(self):
        """M_Rd = (sigma_adm - N/A_om) * W."""
        spec = _spec_ta(metodo="BRESLER_TA", N=5000, sigma_adm=85)
        props = calcola_omogenizzata_biassiale(spec.section, spec.barre, spec.n)
        A_om = props["A_om_cm2"]
        Wx = min(props["Wx_sup_cm3"], props["Wx_inf_cm3"])
        M_Rd_expected = calcola_M_Rd_ta(A_om, Wx, 5000, 85)
        res = verifica_bresler_ta(spec)
        assert abs(res.M_Rdx_kgcm - round(M_Rd_expected, 4)) < 1.0

    def test_N_saturates_section(self):
        """N troppo alto esaurisce la sezione: M_Rd = 0."""
        # sigma_adm = 85, A_om ~ 1640 -> N_max ~ 139400
        spec = _spec_ta(metodo="BRESLER_TA", N=150000, Mx=1000, My=1000, sigma_adm=85)
        res = verifica_bresler_ta(spec)
        assert res.bresler_value == 999.0

    def test_bresler_ok(self):
        """Caso favorevole: bresler <= 1."""
        spec = _spec_ta(metodo="BRESLER_TA", alpha=1.0, N=2000, Mx=50000, My=20000, sigma_adm=85)
        res = verifica_bresler_ta(spec)
        assert res.esito == "OK"
        assert res.bresler_value <= 1.0

    def test_routing_ta(self):
        """verifica_pressofless_ta_cls routing su metodo."""
        spec_e = _spec_ta(metodo="SOVRAPPOSIZIONE_ELASTICA")
        spec_b = _spec_ta(metodo="BRESLER_TA")
        res_e = verifica_pressofless_ta_cls(spec_e)
        res_b = verifica_pressofless_ta_cls(spec_b)
        assert res_e.metodo == "SOVRAPPOSIZIONE_ELASTICA"
        assert res_b.metodo == "BRESLER_TA"


# ===========================================================================
# TestCalcolaM_Rd_ta
# ===========================================================================


class TestCalcolaM_Rd_ta:
    def test_positive(self):
        M = calcola_M_Rd_ta(1500, 12500, 5000, 85)
        # sigma_res = 85 - 5000/1500 = 85 - 3.33 = 81.67
        # M_Rd = 81.67 * 12500 = 1020833
        assert abs(M - 81.67 * 12500) < 500

    def test_zero_N(self):
        M = calcola_M_Rd_ta(1500, 12500, 0, 85)
        assert abs(M - 85 * 12500) < 1.0

    def test_N_exceeds_capacity(self):
        # N/A > sigma_adm
        M = calcola_M_Rd_ta(1000, 12500, 90000, 85)
        assert M == 0.0

    def test_zero_area(self):
        assert calcola_M_Rd_ta(0, 12500, 5000, 85) == 0.0


# ===========================================================================
# TestDispatcher
# ===========================================================================


class TestDispatcher:
    def test_routing_ta_norms(self):
        for norma in NORME_TA:
            spec = _spec_ta(norma=norma)
            res = calcola_pressoflessione_deviata(spec)
            assert res.norma == norma

    def test_routing_slu_norms(self):
        """SLU norms require f_ck and f_yk."""
        for norma in NORME_SLU:
            spec = PressoflessSpec(
                section=_rect(),
                barre=_barre_simm_rett(),
                N_kg=5000,
                Mx_kgcm=200000,
                My_kgcm=100000,
                sigma_c_adm_kgcm2=85,
                norma=norma,
                f_ck_MPa=25,
                f_yk_MPa=450,
            )
            res = calcola_pressoflessione_deviata(spec)
            assert res.norma == norma

    def test_unknown_norm_raises(self):
        spec = _spec_ta(norma="UNKNOWN_NORM")
        with pytest.raises(ValueError, match="non supportata"):
            calcola_pressoflessione_deviata(spec)

    def test_all_norms_covered(self):
        assert NORME == NORME_TA | NORME_SLU
        assert len(NORME) == 6

    def test_result_contract(self):
        """Tutti i result hanno i campi del contratto."""
        spec = _spec_ta()
        res = calcola_pressoflessione_deviata(spec)
        assert hasattr(res, "esito")
        assert hasattr(res, "utilisation")
        assert hasattr(res, "metodo")
        assert hasattr(res, "norma")
        assert hasattr(res, "passaggi_calcolo")
        assert hasattr(res, "details")

    def test_instab_flag_off(self):
        """Con amplifica_instabilita=False, nessun omega nel result."""
        spec = _spec_ta()
        res = calcola_pressoflessione_deviata(spec)
        assert res.omega_x is None
        assert res.omega_y is None


# ===========================================================================
# TestSLUWrapper
# ===========================================================================


class TestSLUWrapper:
    def test_missing_fck_fyk(self):
        """Senza f_ck/f_yk: errore."""
        spec = PressoflessSpec(
            section=_rect(),
            barre=_barre_simm_rett(),
            N_kg=5000,
            Mx_kgcm=200000,
            My_kgcm=100000,
            sigma_c_adm_kgcm2=85,
            norma="NTC2018",
        )
        res = calcola_pressoflessione_deviata(spec)
        assert res.esito == "ERRORE"

    def test_ntc2018(self):
        spec = PressoflessSpec(
            section=_rect(),
            barre=_barre_simm_rett(),
            N_kg=5000,
            Mx_kgcm=100000,
            My_kgcm=50000,
            sigma_c_adm_kgcm2=85,
            norma="NTC2018",
            f_ck_MPa=25,
            f_yk_MPa=450,
        )
        res = calcola_pressoflessione_deviata(spec)
        assert res.norma == "NTC2018"
        assert res.metodo == "BRESLER_SLU"

    def test_ec2(self):
        spec = PressoflessSpec(
            section=_rect(),
            barre=_barre_simm_rett(),
            N_kg=5000,
            Mx_kgcm=100000,
            My_kgcm=50000,
            sigma_c_adm_kgcm2=85,
            norma="EC2",
            f_ck_MPa=25,
            f_yk_MPa=450,
        )
        res = calcola_pressoflessione_deviata(spec)
        assert res.norma == "EC2"

    def test_ntc2008(self):
        spec = PressoflessSpec(
            section=_rect(),
            barre=_barre_simm_rett(),
            N_kg=5000,
            Mx_kgcm=100000,
            My_kgcm=50000,
            sigma_c_adm_kgcm2=85,
            norma="NTC2008",
            f_ck_MPa=25,
            f_yk_MPa=450,
        )
        res = calcola_pressoflessione_deviata(spec)
        assert res.norma == "NTC2008"


# ===========================================================================
# TestInstabilitaBiassiale
# ===========================================================================


class TestInstabilitaBiassiale:
    def test_basic_amplification(self):
        sec = _rect(30, 50)
        barre = _barre_simm_rett()
        w_x, w_y, Mx_amp, My_amp, det = amplifica_momenti_biassiale(
            N_kg=10000,
            Mx_kgcm=100000,
            My_kgcm=50000,
            section=sec,
            barre=barre,
            n=15,
            l0_x_cm=300,
            l0_y_cm=300,
            sigma_c_adm=85,
            E_c_kgcm2=250000,
        )
        assert w_x >= 1.0
        assert w_y >= 1.0
        assert Mx_amp >= 100000
        assert My_amp >= 50000

    def test_omega_values(self):
        """omega cresce con snellezza."""
        sec = _rect(30, 50)
        barre = _barre_simm_rett()
        _, _, _, _, det_short = amplifica_momenti_biassiale(
            10000,
            100000,
            50000,
            sec,
            barre,
            15,
            l0_x_cm=100,
            l0_y_cm=100,
            sigma_c_adm=85,
        )
        _, _, _, _, det_long = amplifica_momenti_biassiale(
            10000,
            100000,
            50000,
            sec,
            barre,
            15,
            l0_x_cm=500,
            l0_y_cm=500,
            sigma_c_adm=85,
        )
        assert det_long["omega_x"] >= det_short["omega_x"]
        assert det_long["omega_y"] >= det_short["omega_y"]

    def test_details_keys(self):
        sec = _rect()
        barre = _barre_simm_rett()
        _, _, _, _, det = amplifica_momenti_biassiale(
            5000,
            100000,
            50000,
            sec,
            barre,
            15,
            l0_x_cm=300,
            l0_y_cm=300,
            sigma_c_adm=85,
        )
        assert "lambda_x" in det
        assert "lambda_y" in det
        assert "Pcr_x_kg" in det
        assert "alpha_Mx" in det

    def test_dispatcher_with_instab(self):
        """Dispatcher amplifica momenti se flag attivo."""
        spec = PressoflessSpec(
            section=_rect(),
            barre=_barre_simm_rett(),
            N_kg=10000,
            Mx_kgcm=100000,
            My_kgcm=50000,
            sigma_c_adm_kgcm2=85,
            norma="RD2229",
            amplifica_instabilita=True,
            l0_x_cm=300,
            l0_y_cm=300,
        )
        res = calcola_pressoflessione_deviata(spec)
        assert res.omega_x is not None
        assert res.omega_y is not None
        assert res.Mx_amplificato_kgcm >= 100000
        assert res.My_amplificato_kgcm >= 50000

    def test_no_amplif_without_l0(self):
        """Senza l0, amplificazione non si attiva."""
        spec = PressoflessSpec(
            section=_rect(),
            barre=_barre_simm_rett(),
            N_kg=10000,
            Mx_kgcm=100000,
            My_kgcm=50000,
            sigma_c_adm_kgcm2=85,
            norma="RD2229",
            amplifica_instabilita=True,
            l0_x_cm=None,
            l0_y_cm=None,
        )
        res = calcola_pressoflessione_deviata(spec)
        assert res.omega_x is None


# ===========================================================================
# TestDominio
# ===========================================================================


class TestDominio:
    def test_basic_generation(self):
        spec = _spec_ta(N=0, Mx=0, My=0)
        dom = calcola_dominio_3d(spec, n_N=8, n_theta=12)
        assert isinstance(dom, DominioNMy)
        assert len(dom.N_levels_kg) == 8
        assert len(dom.theta_rad) == 12
        assert len(dom.Mx_Rd_kgcm) == 8
        assert len(dom.Mx_Rd_kgcm[0]) == 12

    def test_domain_decreases_with_N(self):
        """M_Rd diminuisce all'aumentare di N."""
        spec = _spec_ta()
        dom = calcola_dominio_3d(spec, n_N=10, n_theta=4)
        # theta=0 -> puro Mx
        Mx_at_N0 = abs(dom.Mx_Rd_kgcm[0][0])
        Mx_at_Nmax = abs(dom.Mx_Rd_kgcm[-1][0])
        assert Mx_at_N0 > Mx_at_Nmax

    def test_symmetry_theta(self):
        """Per sezione simmetrica: Mx_Rd(theta) = Mx_Rd(-theta) in modulo."""
        spec = _spec_ta()
        dom = calcola_dominio_3d(spec, n_N=4, n_theta=36)
        # theta[0]=0, theta[-1] prossimo a 2*pi; confronta theta[1] con theta[-1]
        Mx_1 = dom.Mx_Rd_kgcm[0][1]
        Mx_n = dom.Mx_Rd_kgcm[0][-1]
        # Simmetria: |Mx_Rd| a theta e 2*pi-theta dovrebbero essere uguali
        assert abs(abs(Mx_1) - abs(Mx_n)) < 1.0

    def test_m_rd_bresler_pure_axis(self):
        """_m_rd_bresler a theta=0 -> M_Rdx, theta=pi/2 -> M_Rdy."""
        M = _m_rd_bresler(1000, 500, 0, 1.0)
        assert abs(M - 1000) < 0.01
        M2 = _m_rd_bresler(1000, 500, math.pi / 2, 1.0)
        assert abs(M2 - 500) < 0.01

    def test_m_rd_bresler_alpha_effect(self):
        """alpha > 1 allarga il dominio (M_Rd maggiore a 45 deg)."""
        M1 = _m_rd_bresler(1000, 1000, math.pi / 4, 1.0)
        M2 = _m_rd_bresler(1000, 1000, math.pi / 4, 2.0)
        assert M2 > M1

    def test_empty_domain_on_error(self):
        """Sezione con area nulla -> dominio vuoto."""
        sec = SimpleNamespace(section_type="RECTANGULAR", width=0, height=0)
        spec = _spec_ta(section=sec, barre=[])
        dom = calcola_dominio_3d(spec, n_N=4, n_theta=4)
        assert dom.N_levels_kg == []


# ===========================================================================
# TestDisegno (matplotlib headless)
# ===========================================================================


class TestDisegno:
    @pytest.fixture(autouse=True)
    def _use_agg(self):
        import matplotlib

        matplotlib.use("Agg")

    def test_disegna_3d(self):
        from src.codes.pressoflessione.dominio import disegna_dominio_3d

        spec = _spec_ta()
        dom = calcola_dominio_3d(spec, n_N=6, n_theta=12)
        fig = disegna_dominio_3d(dom)
        assert fig is not None
        import matplotlib.pyplot as plt

        plt.close(fig)

    def test_disegna_2d_mxmy(self):
        from src.codes.pressoflessione.dominio import disegna_dominio_2d_mxmy

        spec = _spec_ta()
        dom = calcola_dominio_3d(spec, n_N=6, n_theta=12)
        fig = disegna_dominio_2d_mxmy(dom, N_fisso_kg=0)
        assert fig is not None
        import matplotlib.pyplot as plt

        plt.close(fig)

    def test_disegna_2d_nm(self):
        from src.codes.pressoflessione.dominio import disegna_dominio_2d_nm

        spec = _spec_ta()
        dom = calcola_dominio_3d(spec, n_N=6, n_theta=12)
        fig = disegna_dominio_2d_nm(dom, theta_fisso_rad=0)
        assert fig is not None
        import matplotlib.pyplot as plt

        plt.close(fig)

    def test_disegna_empty_domain(self):
        from src.codes.pressoflessione.dominio import disegna_dominio_2d_mxmy

        dom = DominioNMy([], [], [], [], "TA_ELASTICO", "RD2229")
        fig = disegna_dominio_2d_mxmy(dom)
        assert fig is not None
        import matplotlib.pyplot as plt

        plt.close(fig)


# ===========================================================================
# TestAllSectionTypesTA
# ===========================================================================


class TestAllSectionTypesTA:
    """Verifica TA per vari tipi sezione duck-typed."""

    @pytest.mark.parametrize(
        "sec,name",
        [
            (_rect(30, 50), "rect"),
            (_circ(40), "circ"),
            (_t_sec(), "T"),
            (
                SimpleNamespace(
                    section_type="RECTANGULAR_HOLLOW", width=40, height=60, thickness=5
                ),
                "rect_hollow",
            ),
            (
                SimpleNamespace(section_type="CIRCULAR_HOLLOW", outer_diameter=50, thickness=5),
                "circ_hollow",
            ),
        ],
    )
    def test_section_type(self, sec, name):
        barre = [BarraArmatura(y=4, A=5, x=0)]
        spec = _spec_ta(section=sec, barre=barre, N=3000, Mx=80000, My=40000)
        res = verifica_sovrapposizione_elastica(spec)
        assert res.esito in ("OK", "NON_OK"), f"Failed for {name}"
        assert res.sigma_c_max_kgcm2 > 0, f"sigma_c=0 for {name}"


# ===========================================================================
# TestValoriRiferimento (hand-calculated)
# ===========================================================================


class TestValoriRiferimento:
    def test_rect_30x50_hand_calc(self):
        """Confronto con calcolo a mano: 30x50, 10cm2 totali, n=15."""
        # A_c = 1500, As_tot = 10, A_om = 1500 + 14*10 = 1640
        # Approssimazione con sezione lorda per Wx, Wy
        barre = _barre_simm_rett(h=50, b=30, copri=4, A_inf=5, A_sup=5)
        spec = _spec_ta(
            section=_rect(30, 50),
            barre=barre,
            N=5000,
            Mx=200000,
            My=100000,
            sigma_adm=85,
        )
        res = verifica_sovrapposizione_elastica(spec)
        # sigma_N ~ 5000/1640 ~ 3.05
        assert 2.5 < res.details["sigma_N_kgcm2"] < 3.5
        # sigma_c_max dovrebbe essere ~ 30-35 (con sezione omogenizzata)
        assert res.sigma_c_max_kgcm2 > 15

    def test_calcola_M_Rd_ta_hand(self):
        """M_Rd = (85 - 5000/1640) * 12500 ~ (85 - 3.05) * 12500 ~ 1024375."""
        M = calcola_M_Rd_ta(1640, 12500, 5000, 85)
        expected = (85 - 5000 / 1640) * 12500
        assert abs(M - expected) < 1.0
