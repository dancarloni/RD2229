"""Test FRP CNR-DT 200 (S.6)."""

import pytest

from src.rinforzi.frp_cnr_dt200 import (
    FRP_MATERIALI_DEFAULT,
    calcola_fattori_riduzione_frp,
    verifica_confinamento_frp,
    verifica_delaminazione_frp,
    verifica_rinforzo_flessione_frp,
    verifica_rinforzo_taglio_frp,
)


class TestFRP:
    def test_materiali_default(self) -> None:
        assert "CFRP" in FRP_MATERIALI_DEFAULT
        assert "GFRP" in FRP_MATERIALI_DEFAULT
        assert "AFRP" in FRP_MATERIALI_DEFAULT

    def test_rinforzo_flessione_frp(self) -> None:
        r = verifica_rinforzo_flessione_frp(
            tipo_frp="CFRP",
            A_f_cm2=2.5,
            z_cm=40.0,
            eps_fd=0.007,
            M_d=220000.0,
            M_rd_base=180000.0,
        )
        assert "delta_M_Rd" in r
        assert r["M_Rd"] > r["M_rd_base"]

    def test_delaminazione_frp(self) -> None:
        r = verifica_delaminazione_frp(tau_b=1.5, f_ctm=2.9)
        assert "f_bd" in r
        assert r["f_bd"] > 0

    def test_rinforzo_taglio_frp(self) -> None:
        r = verifica_rinforzo_taglio_frp(
            A_fv_cm2=4.0,
            f_fd=1600.0,
            s_cm=20.0,
            d_cm=45.0,
            V_d=120000.0,
            V_rd_base=90000.0,
            wrapping_totale=False,
        )
        assert "delta_V_Rd" in r
        assert r["V_Rd"] > r["V_rd_base"]

    def test_confinamento_frp(self) -> None:
        r = verifica_confinamento_frp(f_c=250.0, f_l=25.0)
        assert r["f_cc"] > r["f_c"]
        assert r["incremento"] > 1.0

    def test_fattori_riduzione_frp(self) -> None:
        r = calcola_fattori_riduzione_frp(tipo_frp="CFRP", classe_esposizione="esterna")
        assert r["gamma_f"] > 1.0
        assert 0 < r["eta_a"] < 1.0
        assert r["fattore_globale"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
