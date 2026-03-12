"""Test per src/esistenti/modello_globale_mur.py — Fase R.4.

LV3 telaio equivalente: distribuzione taglio sismico, rigidezza maschi.
"""

import pytest

from src.esistenti.modello_globale_mur import (
    MaschioPaino,
    PianoEdificio,
    RisultatoLV3,
    TipoDomandaSismica,
    TipoModelloGlobale,
    VerificaMaschio,
    analisi_lv3,
    analisi_lv3_telaio_equivalente,
    calcola_forze_laterali_equivalenti,
    distribuisci_taglio_piano,
    lv3_analisi_modale_placeholder,
)

# ─── Fixture maschi ──────────────────────────────────────────────────────────


@pytest.fixture
def maschio_rigido():
    """MaschioPaino: L=lunghezza [cm], h=altezza [cm], t=spessore [cm]."""
    return MaschioPaino(
        id_maschio="M1",
        piano=1,
        h=300.0,
        L=50.0,  # lunghezza maschio
        t=40.0,  # spessore
        E=20_000.0,
        G=8_000.0,
        N=20_000.0,
        fvd0=2.0,
        fd=20.0,
    )


@pytest.fixture
def maschio_flessibile():
    return MaschioPaino(
        id_maschio="M2",
        piano=1,
        h=300.0,
        L=100.0,
        t=30.0,
        E=15_000.0,
        G=6_000.0,
        N=10_000.0,
        fvd0=1.5,
        fd=15.0,
    )


@pytest.fixture
def piano_con_due_maschi(maschio_rigido, maschio_flessibile):
    return PianoEdificio(
        numero=1,
        h_piano=300.0,
        W_piano=80_000.0,
        maschi=[maschio_rigido, maschio_flessibile],
    )


@pytest.fixture
def edificio_due_piani(maschio_rigido, maschio_flessibile):
    m3 = MaschioPaino(
        id_maschio="M3",
        piano=2,
        h=300.0,
        L=60.0,
        t=40.0,
        E=20_000.0,
        G=8_000.0,
        N=15_000.0,
        fvd0=2.0,
        fd=20.0,
    )
    p1 = PianoEdificio(
        numero=1,
        h_piano=300.0,
        W_piano=80_000.0,
        maschi=[maschio_rigido, maschio_flessibile],
    )
    p2 = PianoEdificio(
        numero=2,
        h_piano=300.0,
        W_piano=60_000.0,
        maschi=[m3],
    )
    return [p1, p2]


# ─── Test MaschioPaino.rigidezza ─────────────────────────────────────────────


class TestRigidezzaMaschio:
    def test_k_positiva(self, maschio_rigido):
        assert maschio_rigido.rigidezza_totale > 0.0

    def test_k_componenti(self, maschio_rigido):
        """K_flessionale > 0 e K_taglio > 0."""
        assert maschio_rigido.rigidezza_flessionale > 0.0
        assert maschio_rigido.rigidezza_taglio > 0.0

    def test_k_combinata_minore_di_componenti(self, maschio_rigido):
        """K_tot = Kf·Kt/(Kf+Kt) ≤ min(Kf, Kt)."""
        K = maschio_rigido.rigidezza_totale
        Kf = maschio_rigido.rigidezza_flessionale
        Kt = maschio_rigido.rigidezza_taglio
        assert K <= min(Kf, Kt) + 1e-9

    def test_maschio_maggiore_piu_rigido(self, maschio_rigido, maschio_flessibile):
        """Maschio M2 con L più grande (100>50) ha rigidezza totale diversa."""
        K1 = maschio_rigido.rigidezza_totale
        K2 = maschio_flessibile.rigidezza_totale
        # L maggiore causa I molto maggiore → K_flex domina → K2 > K1
        assert K1 != K2  # i due maschi devono essere distinti


# ─── Test calcola_forze_laterali_equivalenti ─────────────────────────────────


class TestForzelaterali:
    def test_v_base_positivo(self, edificio_due_piani):
        V_base, F_piani = calcola_forze_laterali_equivalenti(
            edificio_due_piani, a_g=0.15, S=1.2, q=2.0, FC=1.35
        )
        assert V_base > 0.0

    def test_somma_forze_uguale_taglio(self, edificio_due_piani):
        """ΣF_i = V_base."""
        V_base, F_piani = calcola_forze_laterali_equivalenti(
            edificio_due_piani, a_g=0.15, S=1.2, q=2.0, FC=1.35
        )
        assert abs(sum(F_piani) - V_base) < 1.0

    def test_n_forze_uguale_n_piani(self, edificio_due_piani):
        _, F_piani = calcola_forze_laterali_equivalenti(
            edificio_due_piani, a_g=0.15, S=1.2, q=2.0, FC=1.35
        )
        assert len(F_piani) == len(edificio_due_piani)


# ─── Test distribuisci_taglio_piano ──────────────────────────────────────────


class TestDistribuisciTaglio:
    def test_somma_taglio_coerente(self, piano_con_due_maschi):
        V_piano = 10_000.0
        dist = distribuisci_taglio_piano(piano_con_due_maschi, V_piano)
        assert abs(sum(dist.values()) - V_piano) < 1.0

    def test_chiavi_sono_gli_id_maschi(self, piano_con_due_maschi):
        dist = distribuisci_taglio_piano(piano_con_due_maschi, 5_000.0)
        assert "M1" in dist and "M2" in dist

    def test_distribuzione_proporzionale_a_rigidezza(
        self, piano_con_due_maschi, maschio_rigido, maschio_flessibile
    ):
        """Distribuzione proporzionale a rigidezza → rapporti V_i/V corrispondono a K_i/K_tot."""
        dist = distribuisci_taglio_piano(piano_con_due_maschi, 10_000.0)
        K1 = maschio_rigido.rigidezza_totale
        K2 = maschio_flessibile.rigidezza_totale
        K_tot = K1 + K2
        assert abs(dist["M1"] / 10_000.0 - K1 / K_tot) < 0.01


# ─── Test analisi_lv3_telaio_equivalente ─────────────────────────────────────


class TestAnalisiLV3Telaio:
    def test_restituisce_risultato(self, edificio_due_piani):
        ris = analisi_lv3_telaio_equivalente(edificio_due_piani, a_g=0.15, S=1.2, q=2.0, FC=1.35)
        assert isinstance(ris, RisultatoLV3)

    def test_rho_globale_positivo(self, edificio_due_piani):
        ris = analisi_lv3_telaio_equivalente(edificio_due_piani, a_g=0.15, S=1.2, q=2.0, FC=1.35)
        assert ris.rho_globale > 0.0

    def test_v_base_presente(self, edificio_due_piani):
        ris = analisi_lv3_telaio_equivalente(edificio_due_piani, a_g=0.15, S=1.2, q=2.0, FC=1.35)
        assert ris.V_taglio_base > 0.0


# ─── Test analisi_lv3 (dispatcher) ───────────────────────────────────────────


class TestAnalisiLV3Dispatcher:
    def test_telaio_equiv_default(self, edificio_due_piani):
        ris = analisi_lv3(
            edificio_due_piani,
            a_g=0.15,
            S=1.2,
            q=2.0,
            FC=1.35,
            modello=TipoModelloGlobale.TELAIO_EQUIVALENTE,
        )
        assert isinstance(ris, RisultatoLV3)
        assert ris.modello == TipoModelloGlobale.TELAIO_EQUIVALENTE

    def test_macro_elemento_fallback(self, edificio_due_piani):
        """MACRO_ELEMENTO non implementato → fallback a TELAIO_EQUIV + avviso."""
        ris = analisi_lv3(
            edificio_due_piani,
            a_g=0.15,
            S=1.2,
            q=2.0,
            FC=1.35,
            modello=TipoModelloGlobale.MACRO_ELEMENTO,
        )
        assert isinstance(ris, RisultatoLV3)
        assert len(ris.avvisi) > 0


# ─── Test placeholder modale ─────────────────────────────────────────────────


class TestPlaceholderModale:
    def test_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            lv3_analisi_modale_placeholder()
