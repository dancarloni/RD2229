"""Test discretizzazione pareti in maschi e fasce — Fase F Blocco 1.

Test per:
- Discretizzazione parete senza aperture → un solo maschio
- Discretizzazione parete con 1, 2, 3 aperture
- Fasce superiori e inferiori
- Identificazione maschi adiacenti alle fasce
- Discretizzazione piano completo
- Calcolo N gravitazionale
- Determinazione vincoli maschi
"""

import pytest

from src.methods.muratura.discretizzazione import (
    Fascia,
    Maschio,
    TipoVincolo,
    calcola_N_gravitazionale,
    determina_vincoli_maschi,
    discretizza_parete,
    discretizza_piano,
)
from src.methods.muratura.modello_edificio import (
    Apertura,
    MaterialeMuratura,
    Parete,
    Piano,
    TipoApertura,
)

# ═══════════════════════════════════════════════════════════
#  Fixture comune
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def materiale_base() -> MaterialeMuratura:
    return MaterialeMuratura(
        nome="mattoni_pieni",
        f=24.0, tau_0=0.6, fvk0=0.4,
        E=15000, G=5000, gamma=0.0018,
        gamma_M=2.0, FC=1.2,
    )


# ═══════════════════════════════════════════════════════════
#  Parete senza aperture
# ═══════════════════════════════════════════════════════════

class TestPareteSenzaAperture:

    def test_maschio_unico(self, materiale_base):
        """Parete senza aperture → 1 maschio con L = lunghezza parete."""
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
            spessore=30, materiale=materiale_base,
        )
        maschi, fasce, passaggi = discretizza_parete(parete, altezza_interpiano=300)

        assert len(maschi) == 1
        assert len(fasce) == 0
        assert maschi[0].L == 500.0
        assert maschi[0].t == 30.0
        assert maschi[0].h == 300.0

    def test_maschio_unico_direzione(self, materiale_base):
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
            spessore=30, materiale=materiale_base,
        )
        maschi, _, _ = discretizza_parete(parete, altezza_interpiano=300)
        # Il maschio dovrebbe avere la direzione della parete
        assert hasattr(maschi[0], '_direzione')
        assert maschi[0]._direzione == "X"

    def test_parete_in_y(self, materiale_base):
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=0, y_fin=400,
            spessore=30, materiale=materiale_base,
        )
        maschi, _, _ = discretizza_parete(parete, altezza_interpiano=300)
        assert len(maschi) == 1
        assert maschi[0]._direzione == "Y"
        assert pytest.approx(maschi[0].L, rel=1e-3) == 400.0


# ═══════════════════════════════════════════════════════════
#  Parete con 1 apertura
# ═══════════════════════════════════════════════════════════

class TestPareteConUnaApertura:

    def test_due_maschi(self, materiale_base):
        """Parete 500 cm con finestra al centro → 2 maschi."""
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
            spessore=30, materiale=materiale_base,
            aperture=[
                Apertura(tipo=TipoApertura.FINESTRA, x_offset=150, z_offset=100,
                         larghezza=120, altezza=120),
            ],
        )
        maschi, fasce, passaggi = discretizza_parete(parete, altezza_interpiano=300)

        # 2 maschi: [0÷150] e [270÷500]
        assert len(maschi) == 2
        assert maschi[0].L == 150.0
        assert maschi[1].L == 230.0

    def test_fasce_superiore_inferiore(self, materiale_base):
        """Finestra con z_offset=100, altezza=120 → fascia sup e inf."""
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
            spessore=30, materiale=materiale_base,
            aperture=[
                Apertura(x_offset=150, z_offset=100, larghezza=120, altezza=120),
            ],
        )
        maschi, fasce, passaggi = discretizza_parete(parete, altezza_interpiano=300)

        # Fascia superiore: h = 300 - 100 - 120 = 80 cm
        # Fascia inferiore: h = 100 cm
        assert len(fasce) == 2

        fasce_sup = [f for f in fasce if f.posizione == "superiore"]
        fasce_inf = [f for f in fasce if f.posizione == "inferiore"]

        assert len(fasce_sup) == 1
        assert len(fasce_inf) == 1
        assert fasce_sup[0].h == 80.0
        assert fasce_inf[0].h == 100.0
        assert fasce_sup[0].L == 120.0  # larghezza apertura

    def test_porta_no_fascia_inferiore(self, materiale_base):
        """Porta (z_offset=0) → nessuna fascia inferiore."""
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
            spessore=30, materiale=materiale_base,
            aperture=[
                Apertura(tipo=TipoApertura.PORTA, x_offset=150, z_offset=0,
                         larghezza=100, altezza=210),
            ],
        )
        maschi, fasce, passaggi = discretizza_parete(parete, altezza_interpiano=300)

        # Solo fascia superiore: h = 300 - 0 - 210 = 90 cm
        fasce_inf = [f for f in fasce if f.posizione == "inferiore"]
        fasce_sup = [f for f in fasce if f.posizione == "superiore"]
        assert len(fasce_inf) == 0
        assert len(fasce_sup) == 1
        assert fasce_sup[0].h == 90.0


# ═══════════════════════════════════════════════════════════
#  Parete con 2 aperture
# ═══════════════════════════════════════════════════════════

class TestPareteConDueAperture:

    def test_tre_maschi(self, materiale_base):
        """Parete 800 cm con 2 finestre → 3 maschi."""
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=800, y_fin=0,
            spessore=30, materiale=materiale_base,
            aperture=[
                Apertura(x_offset=100, z_offset=80, larghezza=120, altezza=120),
                Apertura(x_offset=450, z_offset=80, larghezza=120, altezza=120),
            ],
        )
        maschi, fasce, _ = discretizza_parete(parete, altezza_interpiano=300)

        # Maschi: [0÷100], [220÷450], [570÷800]
        assert len(maschi) == 3
        assert maschi[0].L == 100.0
        assert maschi[1].L == 230.0
        assert maschi[2].L == 230.0

    def test_quattro_fasce(self, materiale_base):
        """2 aperture con z_offset > 0 → 4 fasce (2 sup + 2 inf)."""
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=800, y_fin=0,
            spessore=30, materiale=materiale_base,
            aperture=[
                Apertura(x_offset=100, z_offset=80, larghezza=120, altezza=120),
                Apertura(x_offset=450, z_offset=80, larghezza=120, altezza=120),
            ],
        )
        _, fasce, _ = discretizza_parete(parete, altezza_interpiano=300)

        assert len(fasce) == 4  # 2 sup + 2 inf

    def test_maschi_adiacenti_fasce(self, materiale_base):
        """Verifica che le fasce collegano i maschi corretti."""
        parete = Parete(
            id_parete=0, x_ini=0, y_ini=0, x_fin=800, y_fin=0,
            spessore=30, materiale=materiale_base,
            aperture=[
                Apertura(x_offset=100, z_offset=80, larghezza=120, altezza=120),
                Apertura(x_offset=450, z_offset=80, larghezza=120, altezza=120),
            ],
        )
        maschi, fasce, _ = discretizza_parete(parete, altezza_interpiano=300)

        # Prima apertura: maschio sx=0, maschio dx=1
        fascia_1 = [f for f in fasce if abs(f.x_baricentro - (100 + 60)) < 5][0]
        assert fascia_1.id_maschio_sx == 0
        assert fascia_1.id_maschio_dx == 1


# ═══════════════════════════════════════════════════════════
#  Discretizzazione piano
# ═══════════════════════════════════════════════════════════

class TestDiscretizzaPiano:

    def test_piano_4_pareti(self, materiale_base):
        """Piano rettangolare 5×4 m, senza aperture → 4 maschi."""
        piano = Piano(
            id_piano=0, quota_z=0, altezza_interpiano=300,
            pareti=[
                Parete(id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
                       spessore=30, materiale=materiale_base),
                Parete(id_parete=1, x_ini=500, y_ini=0, x_fin=500, y_fin=400,
                       spessore=30, materiale=materiale_base),
                Parete(id_parete=2, x_ini=500, y_ini=400, x_fin=0, y_fin=400,
                       spessore=30, materiale=materiale_base),
                Parete(id_parete=3, x_ini=0, y_ini=400, x_fin=0, y_fin=0,
                       spessore=30, materiale=materiale_base),
            ],
        )
        risultato = discretizza_piano(piano)
        assert risultato.n_maschi == 4
        assert risultato.n_fasce == 0

    def test_piano_con_aperture(self, materiale_base):
        """Piano con 1 finestra su 1 parete → 2 maschi su quella parete + 3 piene."""
        piano = Piano(
            id_piano=0, quota_z=0, altezza_interpiano=300,
            pareti=[
                Parete(id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
                       spessore=30, materiale=materiale_base,
                       aperture=[
                           Apertura(x_offset=150, z_offset=80, larghezza=120, altezza=120),
                       ]),
                Parete(id_parete=1, x_ini=500, y_ini=0, x_fin=500, y_fin=400,
                       spessore=30, materiale=materiale_base),
                Parete(id_parete=2, x_ini=500, y_ini=400, x_fin=0, y_fin=400,
                       spessore=30, materiale=materiale_base),
                Parete(id_parete=3, x_ini=0, y_ini=400, x_fin=0, y_fin=0,
                       spessore=30, materiale=materiale_base),
            ],
        )
        risultato = discretizza_piano(piano)
        # Parete 0: 2 maschi + fasce, parete 1-3: 1 maschio ciascuna
        assert risultato.n_maschi == 5
        assert risultato.n_fasce > 0

    def test_numerazione_progressiva(self, materiale_base):
        """Id maschi progressivi anche con più pareti."""
        piano = Piano(
            id_piano=0, quota_z=0, altezza_interpiano=300,
            pareti=[
                Parete(id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
                       spessore=30, materiale=materiale_base),
                Parete(id_parete=1, x_ini=500, y_ini=0, x_fin=500, y_fin=400,
                       spessore=30, materiale=materiale_base),
            ],
        )
        risultato = discretizza_piano(piano)
        ids = [m.id_maschio for m in risultato.maschi]
        assert ids == [0, 1]

    def test_to_dict(self, materiale_base):
        piano = Piano(
            id_piano=0, quota_z=0, altezza_interpiano=300,
            pareti=[
                Parete(id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0,
                       spessore=30, materiale=materiale_base),
            ],
        )
        risultato = discretizza_piano(piano)
        d = risultato.to_dict()
        assert "n_maschi" in d
        assert "maschi" in d


# ═══════════════════════════════════════════════════════════
#  Maschio proprietà
# ═══════════════════════════════════════════════════════════

class TestMaschioProprietà:

    def test_area(self):
        m = Maschio(L=200, t=30, h=300)
        assert m.area == 6000.0

    def test_momento_inerzia(self):
        m = Maschio(L=200, t=30, h=300)
        I_atteso = 30 * 200 ** 3 / 12
        assert pytest.approx(m.I_x, rel=1e-6) == I_atteso

    def test_spostamento_limite_taglio(self):
        m = Maschio(L=200, t=30, h=300, drift_taglio=0.005)
        assert m.spostamento_limite_taglio == 1.5  # 0.005 × 300

    def test_spostamento_limite_pflex(self):
        m = Maschio(L=200, t=30, h=300, drift_pressoflessione=0.010)
        assert m.spostamento_limite_pflex == 3.0  # 0.010 × 300


# ═══════════════════════════════════════════════════════════
#  Fascia proprietà
# ═══════════════════════════════════════════════════════════

class TestFasciaProprietà:

    def test_e_biella_senza_cordolo(self):
        f = Fascia(ha_cordolo=False)
        assert f.e_biella is True

    def test_non_biella_con_cordolo(self):
        f = Fascia(ha_cordolo=True)
        assert f.e_biella is False

    def test_area(self):
        f = Fascia(L=120, t=30, h=80)
        assert f.area == 3600.0


# ═══════════════════════════════════════════════════════════
#  Vincoli maschi
# ═══════════════════════════════════════════════════════════

class TestDeterminaVincoli:

    def test_nessuna_fascia_mensola(self, materiale_base):
        """Maschio senza fasce collegate → mensola."""
        maschi = [Maschio(id_maschio=0, L=200, t=30, h=300)]
        fasce: list[Fascia] = []

        passaggi = determina_vincoli_maschi(maschi, fasce)
        assert maschi[0].vincolo == TipoVincolo.MENSOLA

    def test_fascia_biella_cerniera(self, materiale_base):
        """Maschio con fasce biella → cerniera."""
        maschi = [
            Maschio(id_maschio=0, L=200, t=30, h=300),
            Maschio(id_maschio=1, L=200, t=30, h=300),
        ]
        fasce = [
            Fascia(id_fascia=0, L=120, t=30, h=80,
                   id_maschio_sx=0, id_maschio_dx=1, ha_cordolo=False),
        ]

        determina_vincoli_maschi(maschi, fasce)
        assert maschi[0].vincolo == TipoVincolo.CERNIERA
        assert maschi[1].vincolo == TipoVincolo.CERNIERA

    def test_fascia_con_cordolo_incastro(self, materiale_base):
        """Maschio con fascia con cordolo → incastro."""
        maschi = [
            Maschio(id_maschio=0, L=200, t=30, h=300),
            Maschio(id_maschio=1, L=200, t=30, h=300),
        ]
        fasce = [
            Fascia(id_fascia=0, L=120, t=30, h=80,
                   id_maschio_sx=0, id_maschio_dx=1, ha_cordolo=True),
        ]

        determina_vincoli_maschi(maschi, fasce)
        assert maschi[0].vincolo == TipoVincolo.INCASTRO
        assert maschi[1].vincolo == TipoVincolo.INCASTRO

    def test_override_rispettato(self, materiale_base):
        """Override manuale vincolo non deve cambiare."""
        maschi = [
            Maschio(id_maschio=0, L=200, t=30, h=300,
                    vincolo=TipoVincolo.CERNIERA, vincolo_override=True),
        ]
        fasce: list[Fascia] = []

        determina_vincoli_maschi(maschi, fasce)
        assert maschi[0].vincolo == TipoVincolo.CERNIERA


# ═══════════════════════════════════════════════════════════
#  N gravitazionale
# ═══════════════════════════════════════════════════════════

class TestCalcolaNGravitazionale:

    def test_peso_proprio_singolo_piano(self, materiale_base):
        """Maschio singolo piano: N = peso proprio + quota solaio."""
        m = Maschio(
            id_maschio=0, id_parete=0, id_piano=0,
            L=200, t=30, h=300,
            materiale=materiale_base,
        )

        maschi_per_piano = {0: [m]}
        masse_piani = {0: 10000.0}
        piani_ordinati = [0]

        passaggi = calcola_N_gravitazionale(maschi_per_piano, masse_piani, piani_ordinati)

        # Peso proprio: 200 × 30 × 300 × 0.0018 = 3240 kg
        # Quota solaio: 10000 (unico maschio, prende tutto)
        atteso = 200 * 30 * 300 * 0.0018 + 10000
        assert pytest.approx(m.N_gravitazionale, rel=1e-3) == atteso

    def test_n_override_rispettato(self, materiale_base):
        """Override N non deve essere ricalcolato."""
        m = Maschio(
            id_maschio=0, id_parete=0, id_piano=0,
            L=200, t=30, h=300,
            materiale=materiale_base,
            N_gravitazionale=50000.0,
            N_override=True,
        )

        maschi_per_piano = {0: [m]}
        masse_piani = {0: 10000.0}
        piani_ordinati = [0]

        calcola_N_gravitazionale(maschi_per_piano, masse_piani, piani_ordinati)
        assert m.N_gravitazionale == 50000.0
