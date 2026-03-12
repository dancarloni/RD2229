"""Test modello cordolo (CA e metallico) e catene/paletti."""

import math

import pytest

from src.elements.cordolo import (
    Cordolo,
    CordoloCA,
    CordoloMetallico,
    InputCatena,
    PosizioneCordolo,
    TipoCordolo,
    TipoPiastra,
    verifica_catena,
    verifica_cordolo,
)

# ═══════════════════ Cordolo CA ═══════════════════


class TestCordoloCA:
    def test_area_armatura(self):
        ca = CordoloCA(b=30, h=25, n_barre_sup=2, n_barre_inf=2, phi_long=1.6)
        A_s_attesa = 4 * math.pi * 1.6**2 / 4  # 4Φ16 = 8.04 cm²
        assert ca.A_s_tot == pytest.approx(A_s_attesa, rel=0.01)

    def test_area_staffa(self):
        ca = CordoloCA(b=30, h=25, phi_staffe=0.8)
        A_st = 2 * math.pi * 0.8**2 / 4  # 2 bracci Φ8 = 1.005 cm²
        assert ca.A_staffa == pytest.approx(A_st, rel=0.01)

    def test_altezza_utile(self):
        ca = CordoloCA(b=30, h=25, c=3.0, phi_staffe=0.8, phi_long=1.6)
        d = 25 - 3.0 - 0.8 - 0.8  # = 20.4 cm
        assert ca.d == pytest.approx(d, rel=0.01)

    def test_minimi_ntc2018_ok(self):
        ca = CordoloCA(
            b=30,
            h=25,
            n_barre_sup=2,
            n_barre_inf=2,
            phi_long=1.6,
            phi_staffe=0.8,
            passo_staffe=20,
        )
        problemi = ca.verifica_minimi_ntc2018()
        assert len(problemi) == 0

    def test_minimi_ntc2018_h_bassa(self):
        ca = CordoloCA(b=30, h=15)
        problemi = ca.verifica_minimi_ntc2018()
        assert any("h=" in p for p in problemi)

    def test_minimi_ntc2018_armatura_insufficiente(self):
        ca = CordoloCA(
            b=30,
            h=25,
            n_barre_sup=1,
            n_barre_inf=1,
            phi_long=1.2,
        )
        problemi = ca.verifica_minimi_ntc2018()
        assert any("A_s" in p for p in problemi)

    def test_minimi_ntc2018_passo_staffe_eccessivo(self):
        ca = CordoloCA(b=30, h=25, passo_staffe=30)
        problemi = ca.verifica_minimi_ntc2018()
        assert any("passo" in p for p in problemi)


class TestVerificaCordoloCA:
    def test_flessione_verificata(self):
        ca = CordoloCA(b=30, h=25, n_barre_inf=2, phi_long=1.6)
        cordolo = Cordolo(
            tipo=TipoCordolo.CA,
            ca=ca,
            Mx=100000,
            V=2000,
        )
        res = verifica_cordolo(cordolo)
        assert res.verifica_flessione is True

    def test_flessione_non_verificata(self):
        ca = CordoloCA(b=30, h=25, n_barre_inf=2, phi_long=1.0)  # barre piccole
        cordolo = Cordolo(
            tipo=TipoCordolo.CA,
            ca=ca,
            Mx=500000,
            V=2000,
        )
        res = verifica_cordolo(cordolo)
        assert res.verifica_flessione is False

    def test_taglio_verificato(self):
        ca = CordoloCA(b=30, h=25, phi_staffe=0.8, passo_staffe=15)
        cordolo = Cordolo(
            tipo=TipoCordolo.CA,
            ca=ca,
            Mx=50000,
            V=1000,
        )
        res = verifica_cordolo(cordolo)
        assert res.verifica_taglio is True

    def test_to_dict(self):
        ca = CordoloCA(b=30, h=25)
        cordolo = Cordolo(tipo=TipoCordolo.CA, ca=ca, Mx=50000)
        res = verifica_cordolo(cordolo)
        d = res.to_dict()
        assert "verifica_globale" in d
        assert "passaggi" in d


# ═══════════════════ Cordolo metallico ═══════════════════


class TestCordoloMetallico:
    def test_m_rd(self):
        met = CordoloMetallico(
            nome_profilo="IPE 200",
            Wx=194.0,
            sigma_adm=1900.0,
        )
        assert met.M_Rd == pytest.approx(1900 * 194, rel=0.01)

    def test_v_rd(self):
        met = CordoloMetallico(
            nome_profilo="IPE 200",
            A=28.5,
            sigma_adm=1900.0,
        )
        assert met.V_Rd > 0

    def test_ancoraggio(self):
        met = CordoloMetallico(
            n_ancoraggi=4,
            phi_ancoraggio=1.6,
        )
        A_anc = 4 * math.pi * 1.6**2 / 4
        assert met.A_ancoraggio_per_m == pytest.approx(A_anc, rel=0.01)


class TestVerificaCordoloMetallico:
    def test_flessione_verificata(self):
        met = CordoloMetallico(
            nome_profilo="IPE 200",
            A=28.5,
            Wx=194.0,
            h=20.0,
            sigma_adm=1900.0,
        )
        cordolo = Cordolo(
            tipo=TipoCordolo.METALLICO_SINGOLO,
            metallico=met,
            Mx=200000,
            V=5000,
        )
        res = verifica_cordolo(cordolo)
        assert res.verifica_flessione is True
        assert res.sfruttamento_flessione < 1.0

    def test_flessione_non_verificata(self):
        met = CordoloMetallico(
            nome_profilo="IPE 100",
            A=10.3,
            Wx=34.2,
            h=10.0,
            sigma_adm=1900.0,
        )
        cordolo = Cordolo(
            tipo=TipoCordolo.METALLICO_SINGOLO,
            metallico=met,
            Mx=200000,
        )
        res = verifica_cordolo(cordolo)
        assert res.verifica_flessione is False

    def test_posizione(self):
        met = CordoloMetallico(nome_profilo="IPE 200", Wx=194.0, sigma_adm=1900.0)
        cordolo = Cordolo(
            tipo=TipoCordolo.METALLICO_SINGOLO,
            posizione=PosizioneCordolo.INTERMEDIO,
            metallico=met,
        )
        res = verifica_cordolo(cordolo)
        assert res.posizione == "intermedio"


# ═══════════════════ Catene e paletti ═══════════════════


class TestCatena:
    def test_trazione_verificata(self):
        inp = InputCatena(
            phi_catena=2.0,
            sigma_s_adm=1400.0,
            F=3000,
            tipo_piastra=TipoPiastra.QUADRATA,
            lato_piastra=20.0,
            fd_mur=10.0,
        )
        res = verifica_catena(inp)
        A = math.pi * 2.0**2 / 4
        assert res.sigma_catena == pytest.approx(3000 / A, rel=0.01)
        assert res.verifica_trazione is True

    def test_trazione_non_verificata(self):
        inp = InputCatena(
            phi_catena=1.0,  # catena piccola
            sigma_s_adm=1400.0,
            F=5000,
        )
        res = verifica_catena(inp)
        assert res.verifica_trazione is False

    def test_punzonamento_verificato(self):
        inp = InputCatena(
            phi_catena=2.0,
            F=3000,
            tipo_piastra=TipoPiastra.QUADRATA,
            lato_piastra=20.0,
            fd_mur=10.0,
        )
        res = verifica_catena(inp)
        # σ = 3000 / 400 = 7.5 < 10
        assert res.sigma_piastra == pytest.approx(3000 / 400, rel=0.01)
        assert res.verifica_punzonamento is True

    def test_punzonamento_non_verificato(self):
        inp = InputCatena(
            phi_catena=2.0,
            F=5000,
            tipo_piastra=TipoPiastra.QUADRATA,
            lato_piastra=10.0,
            fd_mur=10.0,
        )
        res = verifica_catena(inp)
        # σ = 5000 / 100 = 50 > 10
        assert res.verifica_punzonamento is False

    def test_piastra_circolare(self):
        inp = InputCatena(
            phi_catena=2.0,
            F=2000,
            tipo_piastra=TipoPiastra.CIRCOLARE,
            lato_piastra=20.0,
            fd_mur=10.0,
        )
        res = verifica_catena(inp)
        A_circ = math.pi * 20.0**2 / 4
        assert res.A_piastra == pytest.approx(A_circ, rel=0.01)

    def test_piastra_paletto(self):
        inp = InputCatena(
            phi_catena=2.0,
            F=2000,
            tipo_piastra=TipoPiastra.A_PALETTO,
            lato_piastra=15.0,
            spessore_muro=30.0,
            fd_mur=10.0,
        )
        res = verifica_catena(inp)
        # A = lato × spessore_muro = 15 × 30 = 450
        assert res.A_piastra == pytest.approx(450, rel=0.01)

    def test_verifica_globale(self):
        inp = InputCatena(
            phi_catena=2.0,
            sigma_s_adm=1400.0,
            F=3000,
            tipo_piastra=TipoPiastra.QUADRATA,
            lato_piastra=20.0,
            fd_mur=10.0,
        )
        res = verifica_catena(inp)
        assert res.verifica_globale is True

    def test_to_dict(self):
        inp = InputCatena(phi_catena=2.0, F=3000)
        res = verifica_catena(inp)
        d = res.to_dict()
        assert "verifica_globale" in d
        assert "passaggi" in d
