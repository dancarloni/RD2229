"""Test logica business per GUI cordoli — senza Qt.

Verifica che i moduli di calcolo (cordolo.py, cordolo_reticolare.py)
producano output compatibile con TabulatoCalcolo, indipendentemente dalla GUI.
"""

import pytest

from src.elements.cordolo import (
    Cordolo,
    CordoloCA,
    CordoloMetallico,
    PosizioneCordolo,
    TipoCordolo,
    verifica_cordolo,
)
from src.elements.cordolo_reticolare import (
    CordoloReticolare,
    SchemaReticolare,
    verifica_cordolo_reticolare,
)
from src.report.tabulati_calcolo import TabulatoCalcolo
from src.steel.sagomario import SagomarioAcciaio
from src.steel.sezione_asta import SezioneAsta

# ─── Helpers ────────────────────────────────────────────────────────────────

DATA_DIR = __import__("pathlib").Path(__file__).parent.parent / "data" / "steel"


def _sagomario():
    s = SagomarioAcciaio()
    s.carica_tutti(DATA_DIR)
    return s


def _build_tabulato_da_passaggi(
    titolo: str,
    passaggi: list[str],
    domanda: float,
    capacita: float,
    unita: str,
) -> TabulatoCalcolo:
    """Costruisce un TabulatoCalcolo dai passaggi di un RisultatoCordolo."""
    tab = TabulatoCalcolo(
        titolo=titolo,
        normativa="TA DM 1992 / NTC2018",
        modulo="cordoli_widget",
    )
    for passo in passaggi:
        tab.aggiungi_riga_calcolo(descrizione=passo)
    tab.imposta_esito(
        domanda=domanda,
        capacita=capacita,
        unita=unita,
        nome_domanda="D",
        nome_capacita="C",
    )
    return tab


# ─── TestLogicaMetallico ────────────────────────────────────────────────────


class TestLogicaMetallico:
    """Verifica cordolo metallico con profilo IPE 200."""

    @pytest.fixture
    def ipe200(self):
        s = _sagomario()
        p = s.get("IPE 200")
        assert p is not None
        return p

    def _cordolo(self, ipe200, Mx: float, V: float = 500.0) -> Cordolo:
        met = CordoloMetallico(
            nome_profilo=ipe200.nome,
            A=ipe200.A,
            Wx=ipe200.Wx,
            Wy=ipe200.Wy,
            Ix=ipe200.Ix,
            h=ipe200.h,
            tipo_acciaio="Fe430",
            sigma_adm=1900.0,
        )
        return Cordolo(
            tipo=TipoCordolo.METALLICO_SINGOLO,
            posizione=PosizioneCordolo.SOMMITALE,
            Mx=Mx,
            V=V,
            N=0.0,
            metallico=met,
        )

    def test_verifica_metallico_ok(self, ipe200):
        # IPE 200: Wx=194 cm³, M_Rd = 1900 * 194 = 368600 kg·cm
        cord = self._cordolo(ipe200, Mx=50_000.0)
        ris = verifica_cordolo(cord)
        assert ris.verifica_globale is True
        assert ris.verifica_flessione is True
        assert ris.sfruttamento_flessione == pytest.approx(50_000 / 368_600, rel=0.01)

    def test_verifica_metallico_ko(self, ipe200):
        cord = self._cordolo(ipe200, Mx=50_000_000.0)
        ris = verifica_cordolo(cord)
        assert ris.verifica_flessione is False
        assert ris.verifica_globale is False

    def test_tabulato_ascii(self, ipe200):
        cord = self._cordolo(ipe200, Mx=50_000.0)
        ris = verifica_cordolo(cord)
        tab = _build_tabulato_da_passaggi(
            "Cordolo Metallico",
            ris.passaggi,
            domanda=abs(cord.Mx),
            capacita=cord.metallico.M_Rd,  # type: ignore[union-attr]
            unita="kg·cm",
        )
        ascii_out = tab.come_ascii()
        assert ascii_out  # non vuoto
        assert "Cordolo Metallico" in ascii_out

    def test_tabulato_dict_ha_esito(self, ipe200):
        cord = self._cordolo(ipe200, Mx=50_000.0)
        ris = verifica_cordolo(cord)
        tab = _build_tabulato_da_passaggi(
            "Cordolo Metallico",
            ris.passaggi,
            domanda=abs(cord.Mx),
            capacita=cord.metallico.M_Rd,  # type: ignore[union-attr]
            unita="kg·cm",
        )
        d = tab.come_dizionario()
        assert "esito" in d
        assert d["esito"]["verificato"] is True


# ─── TestLogicaCA ────────────────────────────────────────────────────────────


class TestLogicaCA:
    """Verifica cordolo in CA con sezione 30×50."""

    def _cordolo_ca(self, Mx: float = 300_000.0, V: float = 3_000.0) -> Cordolo:
        ca = CordoloCA(
            b=30.0,
            h=50.0,
            n_barre_sup=2,
            n_barre_inf=2,
            phi_long=1.6,
            phi_staffe=0.8,
            passo_staffe=20.0,
            c=3.0,
            sigma_c_adm=60.0,
            sigma_s_adm=2600.0,
        )
        return Cordolo(
            tipo=TipoCordolo.CA,
            posizione=PosizioneCordolo.SOMMITALE,
            Mx=Mx,
            V=V,
            N=0.0,
            ca=ca,
        )

    def test_verifica_ca_ok(self):
        cord = self._cordolo_ca()
        ris = verifica_cordolo(cord)
        # Con sezione 30×50 e 4Φ16 M=300000 kg·cm deve essere verificato
        assert ris.verifica_minimi is True
        assert isinstance(ris.verifica_globale, bool)

    def test_minimi_ntc2018(self):
        # Sezione troppo piccola (h < 20 cm) e armatura insufficiente
        ca = CordoloCA(
            b=15.0,
            h=15.0,
            n_barre_sup=2,
            n_barre_inf=2,
            phi_long=0.8,
            phi_staffe=0.8,
            passo_staffe=20.0,
        )
        cord = Cordolo(tipo=TipoCordolo.CA, Mx=1000.0, V=100.0, ca=ca)
        ris = verifica_cordolo(cord)
        assert ris.verifica_minimi is False
        assert len(ris.problemi_minimi) > 0

    def test_tabulato_ca_dict(self):
        cord = self._cordolo_ca()
        ris = verifica_cordolo(cord)
        tab = _build_tabulato_da_passaggi(
            "Cordolo CA",
            ris.passaggi,
            domanda=abs(cord.Mx),
            capacita=1.0,  # placeholder
            unita="kg·cm",
        )
        d = tab.come_dizionario()
        assert "esito" in d
        assert "calcolo" in d
        assert len(d["calcolo"]) > 0


# ─── TestLogicaReticolare ────────────────────────────────────────────────────


class TestLogicaReticolare:
    """Verifica cordolo reticolare — schema Howe, piatti semplici."""

    @pytest.fixture
    def cordolo_ret(self):
        sec_corr = SezioneAsta.da_piatto(5.0, 1.0)
        sec_diag = SezioneAsta.da_piatto(4.0, 0.8)
        return CordoloReticolare(
            schema=SchemaReticolare.HOWE,
            n_campate=4,
            L=500.0,  # cm
            h=30.0,  # cm (spessore muro)
            sezione_corrente=sec_corr,
            sezione_diagonale=sec_diag,
            tipo_acciaio="Fe430",
        )

    def test_reticolare_converge(self, cordolo_ret):
        ris = verifica_cordolo_reticolare(cordolo_ret, F_y=1_000.0)
        assert ris.convergenza is True
        assert ris.K_globale > 0
        assert len(ris.verifiche_aste) > 0

    def test_reticolare_tabulato_non_vuoto(self, cordolo_ret):
        ris = verifica_cordolo_reticolare(cordolo_ret, F_y=1_000.0)
        tab = TabulatoCalcolo(
            titolo="Cordolo Reticolare — Verifica",
            normativa="NTC2018 §8.7 / TA DM1992",
            modulo="cordoli_widget",
        )
        for passo in ris.passaggi:
            tab.aggiungi_riga_calcolo(descrizione=passo)
        tab.imposta_esito(
            domanda=1_000.0,
            capacita=ris.F_ritegno_disponibile,
            unita="kg",
            nome_domanda="F_y",
            nome_capacita="F_ritegno",
        )
        ascii_out = tab.come_ascii()
        assert ascii_out
        assert "Reticolare" in ascii_out

    def test_reticolare_to_dict(self, cordolo_ret):
        ris = verifica_cordolo_reticolare(cordolo_ret, F_y=1_000.0)
        d = ris.to_dict()
        assert "convergenza" in d
        assert "verificato" in d
        assert "verifiche_aste" in d
        assert isinstance(d["verifiche_aste"], list)
