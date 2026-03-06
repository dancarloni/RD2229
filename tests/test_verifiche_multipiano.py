"""Test per verifiche_multipiano.py — compressione multipiano con eccentricità."""

import pytest

from src.methods.muratura.carichi_verticali import CaricoMaschio
from src.methods.muratura.combinazioni_muratura import GestoreCombinazioni
from src.methods.muratura.discretizzazione import Maschio
from src.methods.muratura.modello_edificio import MaterialeMuratura
from src.methods.muratura.verifiche_multipiano import (
    Eccentricita,
    RigaVerificaMaschio,
    RigaVerificaPiano,
    TabellaVerificheMultipiano,
    calcola_eccentricita,
    verifica_multipiano,
)


# ═══════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def materiale():
    return MaterialeMuratura(
        nome="Mattoni pieni", f=32.0, tau_0=0.76,
        E=15000, G=5000, gamma=0.0018,
        gamma_M=2.0, FC=1.20,
    )


@pytest.fixture
def maschio_base(materiale):
    return Maschio(
        id_maschio=0, id_parete=1, id_piano=0,
        L=100, t=30, h=300,
        x_ini_locale=0, x_fin_locale=100,
        materiale=materiale,
    )


# ═══════════════════════════════════════════════════════════
#  Eccentricità
# ═══════════════════════════════════════════════════════════

class TestEccentricita:

    def test_default(self):
        e = Eccentricita()
        assert e.e_totale == pytest.approx(0.0)

    def test_somma_componenti(self):
        e = Eccentricita(e_geom=1.0, e_carico=0.5, e_accidentale=2.0, e_vento=0.3)
        assert e.e_totale == pytest.approx(3.8)

    def test_to_dict(self):
        e = Eccentricita(e_accidentale=2.0)
        d = e.to_dict()
        assert d["e_accidentale"] == 2.0
        assert "e_totale" in d


class TestCalcolaEccentricita:

    def test_accidentale_minima_2cm(self, maschio_base):
        """NTC2018: e_a ≥ 2 cm."""
        ecc = calcola_eccentricita(maschio_base, rho=1.0)
        # h_eff = 300, h_eff/200 = 1.5 < 2 → e_a = 2
        assert ecc.e_accidentale == pytest.approx(2.0)

    def test_accidentale_da_snellezza(self, materiale):
        """Parete alta: e_a = h_eff/200 > 2."""
        m = Maschio(id_maschio=0, L=100, t=30, h=600, materiale=materiale)
        ecc = calcola_eccentricita(m, rho=1.0)
        # h_eff = 600, h_eff/200 = 3.0 > 2 → e_a = 3.0
        assert ecc.e_accidentale == pytest.approx(3.0)

    def test_e_carico(self, maschio_base):
        ecc = calcola_eccentricita(maschio_base, e_carico=1.5)
        assert ecc.e_carico == pytest.approx(1.5)

    def test_e_vento(self, maschio_base):
        ecc = calcola_eccentricita(maschio_base, M_fuori_piano=5000, N=10000)
        assert ecc.e_vento == pytest.approx(0.5)

    def test_e_vento_N_zero(self, maschio_base):
        """Se N = 0, e_vento = 0 (no eccentricità)."""
        ecc = calcola_eccentricita(maschio_base, M_fuori_piano=5000, N=0)
        assert ecc.e_vento == pytest.approx(0.0)

    def test_rho_riduce_accidentale(self, maschio_base):
        """rho < 1 riduce h_eff → può cambiare e_accidentale."""
        ecc = calcola_eccentricita(maschio_base, rho=0.75)
        # h_eff = 0.75 × 300 = 225, h_eff/200 = 1.125 < 2 → e_a = 2
        assert ecc.e_accidentale == pytest.approx(2.0)


# ═══════════════════════════════════════════════════════════
#  RigaVerificaMaschio
# ═══════════════════════════════════════════════════════════

class TestRigaVerificaMaschio:

    def test_to_dict(self):
        r = RigaVerificaMaschio(
            id_maschio=1, id_piano=0, N_Ed=10000,
            N_Rd=15000, DC=0.667, verificato=True,
        )
        d = r.to_dict()
        assert d["D/C"] == pytest.approx(0.667, abs=0.001)
        assert d["verificato"] is True


# ═══════════════════════════════════════════════════════════
#  RigaVerificaPiano
# ═══════════════════════════════════════════════════════════

class TestRigaVerificaPiano:

    def test_to_dict(self):
        r = RigaVerificaPiano(id_piano=0, quota=0, n_maschi=3, DC_max=0.8)
        d = r.to_dict()
        assert d["D/C_max"] == pytest.approx(0.8)


# ═══════════════════════════════════════════════════════════
#  TabellaVerificheMultipiano
# ═══════════════════════════════════════════════════════════

class TestTabellaVerifiche:

    def test_vuota(self):
        t = TabellaVerificheMultipiano()
        assert t.verificato is True
        assert t.DC_max == 0.0

    def test_con_righe(self):
        t = TabellaVerificheMultipiano(
            righe_maschi=[
                RigaVerificaMaschio(DC=0.5, verificato=True),
                RigaVerificaMaschio(DC=1.2, verificato=False),
            ],
        )
        assert t.verificato is False
        assert t.DC_max == pytest.approx(1.2)

    def test_formato_testo(self):
        t = TabellaVerificheMultipiano(
            righe_maschi=[
                RigaVerificaMaschio(
                    id_maschio=1, id_piano=0, L=100, t=30,
                    N_Ed=10000, sigma_0=3.33, lam=10,
                    phi=0.97, N_Rd=15000, DC=0.667, verificato=True,
                ),
            ],
            righe_piani=[
                RigaVerificaPiano(id_piano=0, quota=0, n_maschi=1, DC_max=0.667),
            ],
        )
        testo = t.formato_testo()
        assert "COMPRESSIONE MULTIPIANO" in testo
        assert "OK" in testo
        assert "RIEPILOGO PER PIANO" in testo
        assert "DETTAGLIO PER MASCHIO" in testo


# ═══════════════════════════════════════════════════════════
#  verifica_multipiano
# ═══════════════════════════════════════════════════════════

class TestVerificaMultipiano:

    def test_singolo_piano_verificato(self, materiale):
        m = Maschio(
            id_maschio=0, id_parete=1, id_piano=0,
            L=100, t=30, h=300,
            materiale=materiale,
        )
        cm = CaricoMaschio(
            id_maschio=0,
            peso_proprio=1620,
            N_solaio_G1=3000,
            N_solaio_G2=1000,
            N_solaio_Q=500,
        )
        g = GestoreCombinazioni()
        ris = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {0: cm}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
        )
        assert len(ris.righe_maschi) == 1
        assert len(ris.righe_piani) == 1
        r = ris.righe_maschi[0]
        # fd = 32/(2×1.2) = 13.33 kg/cm²
        # A = 3000, Φ ≈ 0.97 (λ=10, e/t piccolo)
        # N_Rd = 0.97 × 13.33 × 3000 ≈ 38792
        # N_Ed (SLU sfav) = 1.3×(1620+3000) + 1.5×1000 + 1.5×0.7×500
        # = 6006 + 1500 + 525 = 8031
        assert r.N_Ed > 0
        assert r.N_Rd > r.N_Ed
        assert r.verificato is True
        assert r.DC < 1.0

    def test_maschio_sovraccaricato(self, materiale):
        """Maschio piccolo con carico enorme → non verificato."""
        m = Maschio(
            id_maschio=0, id_parete=1, id_piano=0,
            L=30, t=15, h=300,  # maschio molto piccolo
            materiale=materiale,
        )
        cm = CaricoMaschio(
            id_maschio=0,
            peso_proprio=300,
            N_solaio_G1=50000,  # carico enorme
            N_solaio_G2=20000,
            N_solaio_Q=10000,
        )
        g = GestoreCombinazioni()
        ris = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {0: cm}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
        )
        assert ris.righe_maschi[0].verificato is False
        assert ris.righe_maschi[0].DC > 1.0

    def test_due_piani(self, materiale):
        """Due piani: piano basso ha D/C maggiore."""
        maschi = {
            0: [Maschio(id_maschio=0, id_parete=1, id_piano=0,
                        L=100, t=30, h=300, materiale=materiale)],
            1: [Maschio(id_maschio=10, id_parete=1, id_piano=1,
                        L=100, t=30, h=300, materiale=materiale)],
        }
        carichi = {
            0: {0: CaricoMaschio(id_maschio=0, peso_proprio=1620,
                                  N_solaio_G1=5000, N_superiore=8000)},
            1: {10: CaricoMaschio(id_maschio=10, peso_proprio=1620,
                                   N_solaio_G1=5000)},
        }
        g = GestoreCombinazioni()
        ris = verifica_multipiano(
            maschi_per_piano=maschi,
            carichi_per_piano=carichi,
            piani_ordinati=[0, 1],
            quote_piani={0: 0, 1: 300},
            gestore_combinazioni=g,
        )
        assert len(ris.righe_piani) == 2
        dc_p0 = ris.righe_maschi[0].DC
        dc_p1 = ris.righe_maschi[1].DC
        assert dc_p0 > dc_p1

    def test_snellezza_fuori_limite(self, materiale):
        """Maschio snello (λ > 20) → non verificato."""
        m = Maschio(
            id_maschio=0, id_parete=1, id_piano=0,
            L=100, t=12, h=300,  # λ = 300/12 = 25 > 20
            materiale=materiale,
        )
        cm = CaricoMaschio(id_maschio=0, peso_proprio=500, N_solaio_G1=1000)
        g = GestoreCombinazioni()
        ris = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {0: cm}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
            lambda_max=20.0,
        )
        assert ris.righe_maschi[0].lam == pytest.approx(25.0)
        assert ris.righe_maschi[0].verificato is False

    def test_eccentricita_vento(self, materiale):
        """Momento fuori piano → eccentricità aumenta e/t → Φ ridotto."""
        m = Maschio(
            id_maschio=0, id_parete=1, id_piano=0,
            L=100, t=30, h=300,
            materiale=materiale,
        )
        cm = CaricoMaschio(id_maschio=0, peso_proprio=1620, N_solaio_G1=5000)
        g = GestoreCombinazioni()

        # Senza vento
        ris_no = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {0: cm}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
        )

        # Con momento fuori piano grande
        ris_si = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {0: cm}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
            M_fuoripiano_per_maschio={0: 50000},
        )

        assert ris_si.righe_maschi[0].e_t > ris_no.righe_maschi[0].e_t
        assert ris_si.righe_maschi[0].phi <= ris_no.righe_maschi[0].phi

    def test_passaggi_non_vuoti(self, materiale):
        m = Maschio(id_maschio=0, id_parete=1, id_piano=0,
                    L=100, t=30, h=300, materiale=materiale)
        cm = CaricoMaschio(id_maschio=0, peso_proprio=1000)
        g = GestoreCombinazioni()
        ris = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {0: cm}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
        )
        assert len(ris.passaggi) > 1

    def test_senza_carichi(self, materiale):
        """Maschio senza carichi → usa N_gravitazionale."""
        m = Maschio(id_maschio=0, id_parete=1, id_piano=0,
                    L=100, t=30, h=300, materiale=materiale,
                    N_gravitazionale=5000)
        g = GestoreCombinazioni()
        ris = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
        )
        assert ris.righe_maschi[0].N_Ed > 0

    def test_to_dict(self, materiale):
        m = Maschio(id_maschio=0, id_parete=1, id_piano=0,
                    L=100, t=30, h=300, materiale=materiale)
        cm = CaricoMaschio(id_maschio=0, peso_proprio=1000)
        g = GestoreCombinazioni()
        ris = verifica_multipiano(
            maschi_per_piano={0: [m]},
            carichi_per_piano={0: {0: cm}},
            piani_ordinati=[0],
            quote_piani={0: 0},
            gestore_combinazioni=g,
        )
        d = ris.to_dict()
        assert "verificato" in d
        assert "DC_max" in d
        assert "maschi" in d
        assert "piani" in d
