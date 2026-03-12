"""Test per carichi_verticali.py — distribuzione carichi per aree di influenza."""

import pytest

from src.methods.muratura.carichi_verticali import (
    CaricoMaschio,
    CaricoSolaio,
    _area_influenza_maschio,
    calcola_N_multipiano,
    distribuisci_carichi_solaio,
)
from src.methods.muratura.discretizzazione import Maschio
from src.methods.muratura.modello_edificio import MaterialeMuratura

# ═══════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def materiale():
    return MaterialeMuratura(
        nome="Mattoni pieni",
        f=32.0,
        tau_0=0.76,
        E=15000,
        G=5000,
        gamma=0.0018,  # 1800 kg/m³
        gamma_M=2.0,
        FC=1.20,
    )


@pytest.fixture
def maschi_3(materiale):
    """3 maschi sulla stessa parete (id_parete=1)."""
    return [
        Maschio(
            id_maschio=0,
            id_parete=1,
            id_piano=0,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
        ),
        Maschio(
            id_maschio=1,
            id_parete=1,
            id_piano=0,
            L=80,
            t=30,
            h=300,
            x_ini_locale=200,
            x_fin_locale=280,
            materiale=materiale,
        ),
        Maschio(
            id_maschio=2,
            id_parete=1,
            id_piano=0,
            L=120,
            t=30,
            h=300,
            x_ini_locale=380,
            x_fin_locale=500,
            materiale=materiale,
        ),
    ]


# ═══════════════════════════════════════════════════════════
#  CaricoSolaio
# ═══════════════════════════════════════════════════════════


class TestCaricoSolaio:
    def test_luce_influenza(self):
        cs = CaricoSolaio(luce_sx=400, luce_dx=300)
        assert cs.luce_influenza == pytest.approx(350)

    def test_q_lineare_G1(self):
        cs = CaricoSolaio(G1=0.04, luce_sx=400, luce_dx=400)
        # luce_influenza = 400, q_lin = 0.04 × 400 = 16 kg/cm
        assert cs.q_lineare_G1 == pytest.approx(16.0)

    def test_q_lineare_totale(self):
        cs = CaricoSolaio(G1=0.03, G2=0.01, Q=0.02, luce_sx=200, luce_dx=200)
        # luce = 200, q_tot = (0.03+0.01+0.02) × 200 = 12 kg/cm
        assert cs.q_lineare_totale == pytest.approx(12.0)

    def test_luce_asimmetrica(self):
        cs = CaricoSolaio(luce_sx=500, luce_dx=100)
        assert cs.luce_influenza == pytest.approx(300)

    def test_to_dict(self):
        cs = CaricoSolaio(id_parete=1, G1=0.04, luce_sx=400, luce_dx=400)
        d = cs.to_dict()
        assert d["id_parete"] == 1
        assert "q_lineare_totale" in d


# ═══════════════════════════════════════════════════════════
#  CaricoMaschio
# ═══════════════════════════════════════════════════════════


class TestCaricoMaschio:
    def test_N_G1_include_peso_proprio(self):
        cm = CaricoMaschio(peso_proprio=500, N_solaio_G1=1000, N_superiore=2000)
        assert cm.N_G1 == pytest.approx(3500)

    def test_N_caratteristico(self):
        cm = CaricoMaschio(
            peso_proprio=500,
            N_solaio_G1=1000,
            N_solaio_G2=300,
            N_solaio_Q=200,
            N_superiore=0,
        )
        assert cm.N_caratteristico == pytest.approx(2000)

    def test_to_dict(self):
        cm = CaricoMaschio(id_maschio=5, peso_proprio=100)
        d = cm.to_dict()
        assert d["id_maschio"] == 5
        assert d["N_G1"] == 100


# ═══════════════════════════════════════════════════════════
#  Area di influenza
# ═══════════════════════════════════════════════════════════


class TestAreaInfluenza:
    def test_maschio_unico(self, materiale):
        m = Maschio(
            id_maschio=0,
            id_parete=1,
            L=200,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=200,
            materiale=materiale,
        )
        larghezza = _area_influenza_maschio(m, [m])
        assert larghezza == pytest.approx(200)

    def test_maschi_3_centrale(self, maschi_3):
        """Maschio centrale: dal punto medio sx al punto medio dx."""
        m1 = maschi_3[1]  # x=[200,280]
        larghezza = _area_influenza_maschio(m1, maschi_3)
        # sx: punto medio tra fine M0 (100) e inizio M1 (200) = 150
        # dx: punto medio tra fine M1 (280) e inizio M2 (380) = 330
        # larghezza = 330 - 150 = 180
        assert larghezza == pytest.approx(180)

    def test_maschi_3_primo(self, maschi_3):
        """Primo maschio: dall'inizio al punto medio con il successivo."""
        m0 = maschi_3[0]  # x=[0,100]
        larghezza = _area_influenza_maschio(m0, maschi_3)
        # sx: x_ini = 0
        # dx: punto medio (100+200)/2 = 150
        # larghezza = 150
        assert larghezza == pytest.approx(150)

    def test_maschi_3_ultimo(self, maschi_3):
        """Ultimo maschio: dal punto medio con precedente alla fine."""
        m2 = maschi_3[2]  # x=[380,500]
        larghezza = _area_influenza_maschio(m2, maschi_3)
        # sx: punto medio (280+380)/2 = 330
        # dx: x_fin = 500
        # larghezza = 170
        assert larghezza == pytest.approx(170)

    def test_maschi_due_pareti_diverse(self, materiale):
        """Maschi su pareti diverse non si influenzano."""
        m1 = Maschio(
            id_maschio=0,
            id_parete=1,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
        )
        m2 = Maschio(
            id_maschio=1,
            id_parete=2,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
        )
        larghezza = _area_influenza_maschio(m1, [m1, m2])
        assert larghezza == pytest.approx(100)


# ═══════════════════════════════════════════════════════════
#  Distribuzione carichi
# ═══════════════════════════════════════════════════════════


class TestDistribuzioneCarichi:
    def test_peso_proprio_maschio(self, materiale):
        m = Maschio(
            id_maschio=0,
            id_parete=1,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
        )
        ris = distribuisci_carichi_solaio([m], [])
        cm = ris[0]
        # Wp = 100 × 30 × 300 × 0.0018 = 1620 kg
        assert cm.peso_proprio == pytest.approx(1620)

    def test_carico_solaio_distribuito(self, maschi_3):
        cs = CaricoSolaio(id_parete=1, G1=0.04, G2=0.01, Q=0.02, luce_sx=400, luce_dx=400)
        ris = distribuisci_carichi_solaio(maschi_3, [cs])
        # luce_influenza = 400
        # q_lin_G1 = 0.04 × 400 = 16 kg/cm
        # M0 (larghezza 150): G1 = 16 × 150 = 2400
        assert ris[0].N_solaio_G1 == pytest.approx(16 * 150)
        assert ris[0].N_solaio_G2 == pytest.approx(0.01 * 400 * 150)
        assert ris[0].N_solaio_Q == pytest.approx(0.02 * 400 * 150)

    def test_nessun_carico_solaio(self, maschi_3):
        ris = distribuisci_carichi_solaio(maschi_3, [])
        for cm in ris.values():
            assert cm.N_solaio_G1 == 0
            assert cm.N_solaio_G2 == 0
            assert cm.N_solaio_Q == 0
            assert cm.peso_proprio > 0


# ═══════════════════════════════════════════════════════════
#  Accumulo multipiano
# ═══════════════════════════════════════════════════════════


class TestAccumuloMultipiano:
    def test_due_piani(self, materiale):
        """Due piani identici: piano 0 riceve N dal piano 1."""
        m_p0 = Maschio(
            id_maschio=0,
            id_parete=1,
            id_piano=0,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
        )
        m_p1 = Maschio(
            id_maschio=10,
            id_parete=1,
            id_piano=1,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
        )

        carichi = {
            0: [CaricoSolaio(id_parete=1, G1=0.04, luce_sx=400, luce_dx=400)],
            1: [CaricoSolaio(id_parete=1, G1=0.04, luce_sx=400, luce_dx=400)],
        }

        ris, passaggi = calcola_N_multipiano(
            maschi_per_piano={0: [m_p0], 1: [m_p1]},
            carichi_per_piano=carichi,
            piani_ordinati=[0, 1],
        )

        # Piano 1 (alto): peso proprio + solaio
        cm_p1 = ris[1][10]
        N_p1 = cm_p1.N_caratteristico
        assert N_p1 > 0

        # Piano 0 (basso): peso proprio + solaio + N_superiore da piano 1
        cm_p0 = ris[0][0]
        assert cm_p0.N_superiore == pytest.approx(N_p1)
        assert cm_p0.N_caratteristico > N_p1

    def test_override_N(self, materiale):
        """Maschio con N_override non viene modificato."""
        m = Maschio(
            id_maschio=0,
            id_parete=1,
            id_piano=0,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
            N_gravitazionale=99999,
            N_override=True,
        )
        ris, passaggi = calcola_N_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: [CaricoSolaio(id_parete=1, G1=0.1, luce_sx=400, luce_dx=400)]},
            piani_ordinati=[0],
        )
        assert m.N_gravitazionale == pytest.approx(99999)

    def test_passaggi_non_vuoti(self, materiale):
        m = Maschio(
            id_maschio=0,
            id_parete=1,
            id_piano=0,
            L=100,
            t=30,
            h=300,
            x_ini_locale=0,
            x_fin_locale=100,
            materiale=materiale,
        )
        _, passaggi = calcola_N_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: []},
            piani_ordinati=[0],
        )
        assert len(passaggi) > 1

    def test_tre_piani_accumulo_crescente(self, materiale):
        """3 piani: N cresce scendendo."""
        maschi = {}
        carichi = {}
        for p in range(3):
            maschi[p] = [
                Maschio(
                    id_maschio=p * 10,
                    id_parete=1,
                    id_piano=p,
                    L=100,
                    t=30,
                    h=300,
                    x_ini_locale=0,
                    x_fin_locale=100,
                    materiale=materiale,
                )
            ]
            carichi[p] = [CaricoSolaio(id_parete=1, G1=0.03, luce_sx=300, luce_dx=300)]

        ris, _ = calcola_N_multipiano(maschi, carichi, [0, 1, 2])

        N_p2 = ris[2][20].N_caratteristico
        N_p1 = ris[1][10].N_caratteristico
        N_p0 = ris[0][0].N_caratteristico

        assert N_p0 > N_p1 > N_p2
