"""Test moduli EC2/EC3/EC8 implementati in Fase S Sessione 2."""

import pytest

from src.methods.ec.ec2 import (
    verifica_deformazione_ec2,
    verifica_fessurazione_ec2,
    verifica_flessione_ec2,
    verifica_interazione_taglio_torsione_ec2,
    verifica_pressoflessione_ec2,
    verifica_taglio_con_armatura_ec2,
    verifica_taglio_ec2,
    verifica_torsione_ec2,
)
from src.methods.ec.ec3 import (
    classifica_sezione_ec3,
    verifica_compressione_ec3,
    verifica_flessione_ec3,
    verifica_instabilita_flessionale_ec3,
    verifica_instabilita_flessotorsionale_ec3,
    verifica_taglio_ec3,
)
from src.methods.ec.ec3_connessioni import (
    verifica_bullone_taglio_ec3,
    verifica_saldatura_cordone_ec3,
)
from src.methods.ec.ec8 import (
    calcola_armatura_confinamento_ec8,
    verifica_duttilita_disponibile_ec8,
    verifica_duttilita_ec8,
    verifica_gerarchia_nodo_ec8,
    verifica_nodo_compressione_diagonale_ec8,
    verifica_taglio_pilastro_gerarchia_ec8,
    verifica_taglio_trave_gerarchia_ec8,
)


class TestEC2:
    def test_flessione_ec2_ok(self) -> None:
        r = verifica_flessione_ec2(fck=30.0, b=30.0, d=45.0, As=12.0, c_nom=3.0, M_d=120000.0)
        assert r["esito"] is True
        assert r["M_Rd"] > r["M_d"]

    def test_flessione_ec2_non_ok(self) -> None:
        r = verifica_flessione_ec2(fck=25.0, b=20.0, d=30.0, As=3.0, c_nom=3.0, M_d=900000.0)
        assert r["esito"] is False
        assert r["rateo"] > 1.0

    def test_taglio_ec2(self) -> None:
        r = verifica_taglio_ec2(fck=30.0, b_w=25.0, d=35.0, rho_l=0.01, V_d=50000.0)
        assert "V_Rd" in r
        assert r["V_Rd"] > 0

    def test_torsione_ec2(self) -> None:
        r = verifica_torsione_ec2(fck=30.0, A_k=600.0, t_ef=4.0, T_d=200000.0)
        assert "T_Rd" in r
        assert r["T_Rd"] > 0

    def test_fessurazione_ec2(self) -> None:
        r = verifica_fessurazione_ec2(sigma_s=180.0, f_ctm=2.9, limite_wk_mm=0.3)
        assert "w_k_mm" in r
        assert r["rateo"] > 0

    def test_pressoflessione_ec2(self) -> None:
        r = verifica_pressoflessione_ec2(
            fck=30.0, b=30.0, d=45.0, As=12.0, N_d=80000.0, M_d=120000.0
        )
        assert "N_Rd" in r
        assert r["M_Rd"] > 0

    def test_taglio_con_armatura_ec2(self) -> None:
        r = verifica_taglio_con_armatura_ec2(
            fck=30.0,
            b_w=25.0,
            d=35.0,
            Asw=3.0,
            s=20.0,
            V_d=90000.0,
        )
        assert "V_Rd_s" in r
        assert r["V_Rd"] > 0

    def test_interazione_tv_ec2(self) -> None:
        r = verifica_interazione_taglio_torsione_ec2(
            V_d=60000.0, V_Rd=100000.0, T_d=80000.0, T_Rd=200000.0
        )
        assert "indice_interazione" in r
        assert r["indice_interazione"] > 0

    def test_deformazione_ec2(self) -> None:
        r = verifica_deformazione_ec2(
            M_s=120000.0, E_cm=300000.0, I_gross=500000.0, I_cr=250000.0, lunghezza_cm=500.0
        )
        assert "freccia_cm" in r
        assert r["freccia_cm"] >= 0


class TestEC3:
    def test_classificazione_ec3(self) -> None:
        r = classifica_sezione_ec3(fy=275.0, b=200.0, d=300.0, tf=12.0, tw=8.0)
        assert r["classe"] in {1, 2, 3, 4}

    def test_flessione_ec3(self) -> None:
        r = verifica_flessione_ec3(
            fy=2750.0, Wpl=1200.0, d=300.0, b=200.0, tf=12.0, tw=8.0, M_d=1500000.0
        )
        assert "M_Rd" in r
        assert r["M_Rd"] > 0

    def test_instabilita_ec3(self) -> None:
        r = verifica_instabilita_flessotorsionale_ec3(M_cr=2200000.0, M_pl_Rd=1400000.0)
        assert 0 < r["chi_lt"] <= 1.0
        assert r["M_b_Rd"] > 0

    def test_taglio_ec3(self) -> None:
        r = verifica_taglio_ec3(fy=2750.0, A_v=120.0, V_d=100000.0)
        assert "V_Rd" in r
        assert r["V_Rd"] > 0

    def test_compressione_ec3(self) -> None:
        r = verifica_compressione_ec3(fy=2750.0, A=180.0, N_d=150000.0)
        assert "N_Rd" in r
        assert r["N_Rd"] > 0

    def test_instabilita_flessionale_ec3(self) -> None:
        r = verifica_instabilita_flessionale_ec3(N_cr=3000000.0, N_pl_Rd=2000000.0)
        assert 0 < r["chi"] <= 1.0
        assert r["N_b_Rd"] > 0

    def test_connessioni_ec3(self) -> None:
        rb = verifica_bullone_taglio_ec3(A_b=2.45, f_ub=8000.0, V_ed=5000.0)
        rs = verifica_saldatura_cordone_ec3(a_mm=6.0, l_mm=120.0, f_u=430.0, F_ed=70000.0)
        assert "V_Rd" in rb
        assert "F_Rd" in rs


class TestEC8:
    def test_duttilita_ec8(self) -> None:
        r = verifica_duttilita_ec8(q=3.0, T_1=0.5, T_C=0.7, mu_phi_richiesto=8.0)
        assert "mu_phi_min" in r
        assert r["mu_phi_min"] > 0

    def test_gerarchia_nodo_ec8(self) -> None:
        r = verifica_gerarchia_nodo_ec8(somma_MRc=800.0, somma_MRb=500.0)
        assert "limite" in r
        assert r["limite"] > 0

    def test_taglio_gerarchia_ec8(self) -> None:
        r_trave = verifica_taglio_trave_gerarchia_ec8(
            M_rb_left=200000.0,
            M_rb_right=180000.0,
            L_cm=500.0,
            V_g=40.0,
            V_ed=700.0,
        )
        r_pil = verifica_taglio_pilastro_gerarchia_ec8(
            M_rc_top=250000.0,
            M_rc_bot=220000.0,
            H_cl_cm=300.0,
            V_ed=1200.0,
        )
        assert "V_cd" in r_trave
        assert "V_cd" in r_pil

    def test_nodo_compressione_diagonale_ec8(self) -> None:
        r = verifica_nodo_compressione_diagonale_ec8(
            V_jhd=300000.0, eta=0.6, f_cd=170.0, b_j=40.0, h_jc=40.0
        )
        assert "V_lim" in r
        assert r["V_lim"] > 0

    def test_duttilita_disponibile_ec8(self) -> None:
        r = verifica_duttilita_disponibile_ec8(
            eps_cu=0.0035, eps_y=0.0022, x_su_d=0.45, mu_phi_richiesto=3.0
        )
        assert "mu_phi_disponibile" in r
        assert r["mu_phi_disponibile"] > 0

    def test_armatura_confinamento_ec8(self) -> None:
        r = calcola_armatura_confinamento_ec8(
            A_c_cm2=1600.0,
            A_cc_cm2=900.0,
            f_cd=170.0,
            f_yd=3913.0,
            b0_cm=30.0,
            s_cm=12.0,
            A_sw_prov_cm2=2.2,
        )
        assert "A_sw_req_cm2" in r
        assert r["A_sw_req_cm2"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
