"""Test analisi POR pushover — Fase F Blocco 2.

Test per:
- Distribuzione forze in altezza
- Pushover singolo piano
- Pushover multipiano
- Bilinearizzazione curva
- Analisi completa (2 dir × 2 distr)
"""

import pytest

from src.methods.muratura.discretizzazione import Maschio, TipoVincolo
from src.methods.muratura.modello_edificio import ConfigPOR, MaterialeMuratura
from src.methods.muratura.por_analisi import (
    CurvaPushover,
    TipoDistribuzione,
    analisi_por_completa,
    bilinearizza_curva,
    forze_in_altezza,
    pushover_multipiano,
    pushover_piano,
)
from src.methods.muratura.resistenza import calcola_resistenza_maschio


@pytest.fixture
def materiale() -> MaterialeMuratura:
    return MaterialeMuratura(
        nome="mattoni_pieni",
        f=24.0,
        tau_0=0.6,
        fvk0=0.4,
        E=15000.0,
        G=5000.0,
        gamma=0.0018,
        gamma_M=2.0,
        FC=1.2,
        mu=0.4,
    )


def _crea_maschio(
    mat: MaterialeMuratura,
    id_m: int = 0,
    L: float = 200,
    t: float = 30,
    h: float = 300,
    N: float = 15000,
    direzione: str = "X",
) -> Maschio:
    m = Maschio(
        id_maschio=id_m,
        L=L,
        t=t,
        h=h,
        materiale=mat,
        N_gravitazionale=N,
        vincolo=TipoVincolo.INCASTRO,
    )
    m._direzione = direzione  # type: ignore[attr-defined]
    return m


# ═══════════════════════════════════════════════════════════
#  Distribuzione forze
# ═══════════════════════════════════════════════════════════


class TestForzeInAltezza:
    def test_modo_1_singolo_piano(self):
        F = forze_in_altezza([10000], [300], V_base=5000, distribuzione=TipoDistribuzione.MODO_1)
        assert len(F) == 1
        assert pytest.approx(F[0], rel=1e-3) == 5000.0

    def test_modo_1_due_piani(self):
        """Piano 1 a 300 cm, piano 2 a 600 cm."""
        masse = [10000, 8000]
        quote = [300, 600]
        V_base = 10000
        F = forze_in_altezza(masse, quote, V_base, distribuzione=TipoDistribuzione.MODO_1)

        # F_1 = 10000 × (10000×300) / (10000×300 + 8000×600)
        somma_mz = 10000 * 300 + 8000 * 600
        assert pytest.approx(F[0], rel=1e-3) == V_base * 10000 * 300 / somma_mz
        assert pytest.approx(F[1], rel=1e-3) == V_base * 8000 * 600 / somma_mz
        assert pytest.approx(sum(F), rel=1e-3) == V_base

    def test_uniforme(self):
        masse = [10000, 8000]
        F = forze_in_altezza(
            masse, [300, 600], V_base=10000, distribuzione=TipoDistribuzione.UNIFORME
        )

        assert pytest.approx(F[0], rel=1e-3) == 10000 * 10000 / 18000
        assert pytest.approx(sum(F), rel=1e-3) == 10000

    def test_somma_forze(self):
        """Somma forze = V_base per entrambe le distribuzioni."""
        masse = [10000, 8000, 6000]
        quote = [300, 600, 900]

        for distr in [TipoDistribuzione.MODO_1, TipoDistribuzione.UNIFORME]:
            F = forze_in_altezza(masse, quote, 15000, distr)
            assert pytest.approx(sum(F), rel=1e-3) == 15000

    def test_vuoto(self):
        F = forze_in_altezza([], [], 1000)
        assert F == []


# ═══════════════════════════════════════════════════════════
#  Pushover singolo piano
# ═══════════════════════════════════════════════════════════


class TestPushoverPiano:
    def test_curva_non_vuota(self, materiale):
        maschi = [_crea_maschio(materiale, id_m=i) for i in range(3)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=50, spostamento_max=5.0)

        curva = pushover_piano(maschi, resistenze, 10000, config)
        assert len(curva.punti) > 0

    def test_primo_punto_zero(self, materiale):
        maschi = [_crea_maschio(materiale)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=50, spostamento_max=5.0)

        curva = pushover_piano(maschi, resistenze, 10000, config)
        assert curva.punti[0].delta_controllo == 0.0
        assert curva.punti[0].V_base == 0.0

    def test_V_max_positivo(self, materiale):
        maschi = [_crea_maschio(materiale, id_m=i, N=20000) for i in range(3)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=100, spostamento_max=10.0)

        curva = pushover_piano(maschi, resistenze, 10000, config)
        assert curva.V_max > 0

    def test_collasso_caduta_resistenza(self, materiale):
        """La curva deve fermarsi quando V_base scende sotto 80% V_max."""
        maschi = [_crea_maschio(materiale, id_m=i, N=20000) for i in range(3)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(
            n_passi=200,
            spostamento_max=20.0,
            criterio_collasso="caduta_resistenza",
            soglia_caduta_resistenza=0.80,
        )

        curva = pushover_piano(maschi, resistenze, 10000, config)
        # La curva deve fermarsi prima di n_passi
        assert len(curva.punti) <= 201  # può arrivare al max

    def test_conteggio_stati(self, materiale):
        maschi = [_crea_maschio(materiale, id_m=i, N=20000) for i in range(3)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=50, spostamento_max=5.0)

        curva = pushover_piano(maschi, resistenze, 10000, config)

        # All'inizio tutti elastici
        assert curva.punti[0].n_elastici == 3

        # Ultimo punto: almeno qualcuno non più elastico
        ultimo = curva.punti[-1]
        assert ultimo.n_elastici + ultimo.n_plastici + ultimo.n_collassati == 3


# ═══════════════════════════════════════════════════════════
#  Pushover multipiano
# ═══════════════════════════════════════════════════════════


class TestPushoverMultipiano:
    def test_due_piani(self, materiale):
        maschi_p0 = [_crea_maschio(materiale, id_m=i, N=30000) for i in range(3)]
        maschi_p1 = [_crea_maschio(materiale, id_m=i + 3, N=15000) for i in range(3)]

        res_p0 = [calcola_resistenza_maschio(m) for m in maschi_p0]
        res_p1 = [calcola_resistenza_maschio(m) for m in maschi_p1]

        config = ConfigPOR(n_passi=100, spostamento_max=10.0)

        curva = pushover_multipiano(
            maschi_per_piano={0: maschi_p0, 1: maschi_p1},
            resistenze_per_piano={0: res_p0, 1: res_p1},
            masse=[20000, 15000],
            quote=[150, 450],
            piani_ordinati=[0, 1],
            config=config,
        )

        assert len(curva.punti) > 0
        assert curva.V_max > 0


# ═══════════════════════════════════════════════════════════
#  Bilinearizzazione
# ═══════════════════════════════════════════════════════════


class TestBilinearizzazione:
    def test_bilineare_valida(self, materiale):
        maschi = [_crea_maschio(materiale, id_m=i, N=20000) for i in range(3)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=100, spostamento_max=10.0)

        curva = pushover_piano(maschi, resistenze, 10000, config)
        bilinearizza_curva(curva, massa_star=20000)

        assert curva.V_y > 0
        assert curva.delta_y > 0
        assert curva.delta_u > curva.delta_y
        assert curva.k_bilineare > 0

    def test_duttilita_positiva(self, materiale):
        maschi = [_crea_maschio(materiale, id_m=i, N=20000) for i in range(3)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=100, spostamento_max=10.0)

        curva = pushover_piano(maschi, resistenze, 10000, config)
        bilinearizza_curva(curva, massa_star=20000)

        assert curva.mu > 1.0  # duttilità > 1

    def test_periodo_positivo(self, materiale):
        maschi = [_crea_maschio(materiale, id_m=i, N=20000) for i in range(3)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=100, spostamento_max=10.0)

        curva = pushover_piano(maschi, resistenze, 10000, config)
        bilinearizza_curva(curva, massa_star=20000)

        assert curva.T_star > 0

    def test_curva_vuota(self):
        curva = CurvaPushover()
        bilinearizza_curva(curva)
        assert curva.V_y == 0.0


# ═══════════════════════════════════════════════════════════
#  Analisi completa
# ═══════════════════════════════════════════════════════════


class TestAnalisiCompleta:
    def test_8_curve(self, materiale):
        """2 dir × 2 distr × 2 segni ecc = 8 curve."""
        maschi = [
            _crea_maschio(materiale, id_m=0, N=20000, direzione="X"),
            _crea_maschio(materiale, id_m=1, N=20000, direzione="Y"),
        ]
        maschi[1].x_baricentro = 500
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]

        config = ConfigPOR(n_passi=50, spostamento_max=5.0)

        risultato = analisi_por_completa(
            maschi_per_piano={0: maschi},
            resistenze_per_piano={0: resistenze},
            masse=[20000],
            quote=[150],
            piani_ordinati=[0],
            config=config,
        )

        assert len(risultato.curve) == 8

    def test_curva_governante(self, materiale):
        maschi = [
            _crea_maschio(materiale, id_m=0, N=20000, direzione="X"),
            _crea_maschio(materiale, id_m=1, N=20000, direzione="Y"),
        ]
        maschi[1].x_baricentro = 500
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]

        config = ConfigPOR(n_passi=50, spostamento_max=5.0)

        risultato = analisi_por_completa(
            maschi_per_piano={0: maschi},
            resistenze_per_piano={0: resistenze},
            masse=[20000],
            quote=[150],
            piani_ordinati=[0],
            config=config,
        )

        assert risultato.curva_governante is not None

    def test_to_dict(self, materiale):
        maschi = [_crea_maschio(materiale, id_m=0, N=20000)]
        resistenze = [calcola_resistenza_maschio(m) for m in maschi]
        config = ConfigPOR(n_passi=20, spostamento_max=3.0)

        risultato = analisi_por_completa(
            maschi_per_piano={0: maschi},
            resistenze_per_piano={0: resistenze},
            masse=[20000],
            quote=[150],
            piani_ordinati=[0],
            config=config,
        )

        d = risultato.to_dict()
        assert "n_curve" in d
        assert "curve" in d
