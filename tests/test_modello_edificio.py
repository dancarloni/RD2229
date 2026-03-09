"""Test modello geometrico edificio muratura — Fase F Blocco 1.

Test per:
- MaterialeMuratura (proprietà di calcolo fd, tau_0d)
- Apertura (coordinate)
- Parete (lunghezza, angolo, direzione)
- Piano (filtraggio pareti per direzione)
- Edificio (proprietà globali)
- ParametriSismiciEdificio (spettro elastico, FC da LC)
- ConfigPOR (parametri default)
"""

import math

import pytest

from src.methods.muratura.modello_edificio import (
    FC_DA_LC,
    Apertura,
    ConfigPOR,
    Edificio,
    LivelloConoscenza,
    MaterialeMuratura,
    ParametriSismiciEdificio,
    Parete,
    Piano,
    TipoApertura,
)

# ═══════════════════════════════════════════════════════════
#  MaterialeMuratura
# ═══════════════════════════════════════════════════════════

class TestMaterialeMuratura:

    def test_fd_calcolo(self):
        """fd = f / (γ_M × FC)."""
        mat = MaterialeMuratura(f=24.0, gamma_M=2.0, FC=1.2)
        assert pytest.approx(mat.fd, rel=1e-3) == 24.0 / (2.0 * 1.2)

    def test_fd_zero_gamma(self):
        mat = MaterialeMuratura(f=24.0, gamma_M=0.0, FC=1.0)
        assert mat.fd == 0.0

    def test_tau_0d_calcolo(self):
        """tau_0d = tau_0 / (γ_M × FC)."""
        mat = MaterialeMuratura(tau_0=0.6, gamma_M=2.0, FC=1.35)
        assert pytest.approx(mat.tau_0d, rel=1e-3) == 0.6 / (2.0 * 1.35)

    def test_fvk0d_calcolo(self):
        mat = MaterialeMuratura(fvk0=0.4, gamma_M=3.0, FC=1.0)
        assert pytest.approx(mat.fvk0d, rel=1e-3) == 0.4 / 3.0

    def test_to_dict(self):
        mat = MaterialeMuratura(nome="test", f=20.0, tau_0=0.5, E=15000, G=5000)
        d = mat.to_dict()
        assert d["nome"] == "test"
        assert d["f"] == 20.0
        assert "fd" in d
        assert "tau_0d" in d


# ═══════════════════════════════════════════════════════════
#  Apertura
# ═══════════════════════════════════════════════════════════

class TestApertura:

    def test_x_fine(self):
        ap = Apertura(x_offset=100.0, larghezza=120.0)
        assert ap.x_fine == 220.0

    def test_z_fine(self):
        ap = Apertura(z_offset=80.0, altezza=150.0)
        assert ap.z_fine == 230.0

    def test_tipo_default(self):
        ap = Apertura()
        assert ap.tipo == TipoApertura.FINESTRA

    def test_to_dict(self):
        ap = Apertura(tipo=TipoApertura.PORTA, x_offset=50, z_offset=0, larghezza=90, altezza=210)
        d = ap.to_dict()
        assert d["tipo"] == "porta"
        assert d["larghezza"] == 90.0


# ═══════════════════════════════════════════════════════════
#  Parete
# ═══════════════════════════════════════════════════════════

class TestParete:

    def test_lunghezza_orizzontale(self):
        """Parete orizzontale lungo X."""
        p = Parete(x_ini=0, y_ini=0, x_fin=500, y_fin=0)
        assert pytest.approx(p.lunghezza, rel=1e-6) == 500.0

    def test_lunghezza_verticale(self):
        """Parete verticale lungo Y."""
        p = Parete(x_ini=0, y_ini=0, x_fin=0, y_fin=400)
        assert pytest.approx(p.lunghezza, rel=1e-6) == 400.0

    def test_lunghezza_obliqua(self):
        """Parete obliqua a 45°."""
        p = Parete(x_ini=0, y_ini=0, x_fin=300, y_fin=300)
        assert pytest.approx(p.lunghezza, rel=1e-6) == 300 * math.sqrt(2)

    def test_angolo_x(self):
        p = Parete(x_ini=0, y_ini=0, x_fin=500, y_fin=0)
        assert pytest.approx(p.angolo, abs=1e-6) == 0.0

    def test_angolo_y(self):
        p = Parete(x_ini=0, y_ini=0, x_fin=0, y_fin=500)
        assert pytest.approx(p.angolo, rel=1e-6) == math.pi / 2

    def test_direzione_x(self):
        p = Parete(x_ini=0, y_ini=0, x_fin=500, y_fin=0)
        assert p.direzione_principale == "X"

    def test_direzione_y(self):
        p = Parete(x_ini=0, y_ini=0, x_fin=0, y_fin=500)
        assert p.direzione_principale == "Y"

    def test_baricentro(self):
        p = Parete(x_ini=100, y_ini=200, x_fin=500, y_fin=200)
        assert p.x_baricentro == 300.0
        assert p.y_baricentro == 200.0

    def test_aperture_ordinate(self):
        p = Parete(
            x_ini=0, y_ini=0, x_fin=800, y_fin=0,
            aperture=[
                Apertura(x_offset=400, larghezza=120),
                Apertura(x_offset=100, larghezza=120),
            ],
        )
        ordinate = p.aperture_ordinate()
        assert ordinate[0].x_offset == 100
        assert ordinate[1].x_offset == 400

    def test_to_dict(self):
        p = Parete(id_parete=1, x_ini=0, y_ini=0, x_fin=500, y_fin=0, spessore=30)
        d = p.to_dict()
        assert d["lunghezza"] == 500.0
        assert d["direzione"] == "X"


# ═══════════════════════════════════════════════════════════
#  Piano
# ═══════════════════════════════════════════════════════════

class TestPiano:

    def test_quota_sommita(self):
        piano = Piano(quota_z=300, altezza_interpiano=300)
        assert piano.quota_sommita == 600

    def test_n_pareti(self):
        piano = Piano(
            pareti=[
                Parete(x_ini=0, y_ini=0, x_fin=500, y_fin=0),
                Parete(x_ini=500, y_ini=0, x_fin=500, y_fin=400),
            ]
        )
        assert piano.n_pareti == 2

    def test_pareti_in_direzione_x(self):
        piano = Piano(
            pareti=[
                Parete(x_ini=0, y_ini=0, x_fin=500, y_fin=0),   # X
                Parete(x_ini=500, y_ini=0, x_fin=500, y_fin=400),  # Y
                Parete(x_ini=0, y_ini=400, x_fin=500, y_fin=400),  # X
            ]
        )
        pareti_x = piano.pareti_in_direzione("X")
        assert len(pareti_x) == 2

    def test_pareti_in_direzione_y(self):
        piano = Piano(
            pareti=[
                Parete(x_ini=0, y_ini=0, x_fin=500, y_fin=0),
                Parete(x_ini=0, y_ini=0, x_fin=0, y_fin=400),
            ]
        )
        assert len(piano.pareti_in_direzione("Y")) == 1


# ═══════════════════════════════════════════════════════════
#  ParametriSismiciEdificio
# ═══════════════════════════════════════════════════════════

class TestParametriSismici:

    def test_fc_da_lc1(self):
        ps = ParametriSismiciEdificio(livello_conoscenza=LivelloConoscenza.LC1)
        ps.aggiorna_FC_da_LC()
        assert ps.FC == 1.35

    def test_fc_da_lc2(self):
        ps = ParametriSismiciEdificio(livello_conoscenza=LivelloConoscenza.LC2)
        ps.aggiorna_FC_da_LC()
        assert ps.FC == 1.20

    def test_fc_da_lc3(self):
        ps = ParametriSismiciEdificio(livello_conoscenza=LivelloConoscenza.LC3)
        ps.aggiorna_FC_da_LC()
        assert ps.FC == 1.00

    def test_fc_override(self):
        ps = ParametriSismiciEdificio(FC=1.50, FC_override=True)
        ps.aggiorna_FC_da_LC()
        assert ps.FC == 1.50  # non cambiato

    def test_spettro_plateau(self):
        """Nel plateau T_B ≤ T < T_C: Se = a_g × S × η × F₀."""
        ps = ParametriSismiciEdificio(
            a_g=0.15, S=1.2, F_0=2.5,
            T_B=0.15, T_C=0.45, T_D=2.0,
        )
        Se = ps.spettro_elastico(0.3)
        assert pytest.approx(Se, rel=1e-3) == 0.15 * 1.2 * 1.0 * 2.5

    def test_spettro_ramo_discendente(self):
        """T_C ≤ T < T_D: Se = a_g × S × F₀ × (T_C/T)."""
        ps = ParametriSismiciEdificio(
            a_g=0.15, S=1.2, F_0=2.5,
            T_B=0.15, T_C=0.45, T_D=2.0,
        )
        T = 0.9
        Se = ps.spettro_elastico(T)
        atteso = 0.15 * 1.2 * 2.5 * (0.45 / 0.9)
        assert pytest.approx(Se, rel=1e-3) == atteso

    def test_spettro_ramo_costante_spostamento(self):
        """T ≥ T_D: Se = a_g × S × F₀ × (T_C × T_D / T²)."""
        ps = ParametriSismiciEdificio(
            a_g=0.15, S=1.2, F_0=2.5,
            T_B=0.15, T_C=0.45, T_D=2.0,
        )
        T = 3.0
        Se = ps.spettro_elastico(T)
        atteso = 0.15 * 1.2 * 2.5 * (0.45 * 2.0 / 9.0)
        assert pytest.approx(Se, rel=1e-3) == atteso

    def test_spettro_ramo_ascendente(self):
        """0 ≤ T < T_B."""
        ps = ParametriSismiciEdificio(
            a_g=0.15, S=1.2, F_0=2.5,
            T_B=0.15, T_C=0.45, T_D=2.0,
        )
        # T=0: Se = a_g × S (perché al T=0 si riduce a a_g×S×1)
        Se_0 = ps.spettro_elastico(0.0)
        assert pytest.approx(Se_0, rel=1e-3) == 0.15 * 1.2

    def test_spettro_progetto(self):
        ps = ParametriSismiciEdificio(
            a_g=0.15, S=1.2, F_0=2.5, q=2.0,
            T_B=0.15, T_C=0.45, T_D=2.0,
        )
        Sd = ps.spettro_progetto(0.3)
        Se = ps.spettro_elastico(0.3)
        assert pytest.approx(Sd, rel=1e-3) == Se / 2.0


# ═══════════════════════════════════════════════════════════
#  Edificio
# ═══════════════════════════════════════════════════════════

class TestEdificio:

    @pytest.fixture
    def edificio_2piani(self) -> Edificio:
        """Edificio 2 piani rettangolare 5×4 m."""
        mat = MaterialeMuratura(f=24.0, tau_0=0.6, E=15000, G=5000, gamma=0.0018)

        piano0 = Piano(
            id_piano=0, quota_z=0, altezza_interpiano=300, massa=20000,
            pareti=[
                Parete(id_parete=0, x_ini=0, y_ini=0, x_fin=500, y_fin=0, spessore=30, materiale=mat),
                Parete(id_parete=1, x_ini=500, y_ini=0, x_fin=500, y_fin=400, spessore=30, materiale=mat),
                Parete(id_parete=2, x_ini=500, y_ini=400, x_fin=0, y_fin=400, spessore=30, materiale=mat),
                Parete(id_parete=3, x_ini=0, y_ini=400, x_fin=0, y_fin=0, spessore=30, materiale=mat),
            ],
        )
        piano1 = Piano(
            id_piano=1, quota_z=300, altezza_interpiano=300, massa=15000,
            pareti=[
                Parete(id_parete=4, x_ini=0, y_ini=0, x_fin=500, y_fin=0, spessore=30, materiale=mat),
                Parete(id_parete=5, x_ini=500, y_ini=0, x_fin=500, y_fin=400, spessore=30, materiale=mat),
                Parete(id_parete=6, x_ini=500, y_ini=400, x_fin=0, y_fin=400, spessore=30, materiale=mat),
                Parete(id_parete=7, x_ini=0, y_ini=400, x_fin=0, y_fin=0, spessore=30, materiale=mat),
            ],
        )

        return Edificio(nome="test_2p", piani=[piano0, piano1])

    def test_n_piani(self, edificio_2piani):
        assert edificio_2piani.n_piani == 2

    def test_altezza_totale(self, edificio_2piani):
        assert edificio_2piani.altezza_totale == 600.0

    def test_dimensione_x(self, edificio_2piani):
        assert edificio_2piani.dimensione_x == 500.0

    def test_dimensione_y(self, edificio_2piani):
        assert edificio_2piani.dimensione_y == 400.0

    def test_massa_totale(self, edificio_2piani):
        assert edificio_2piani.massa_totale == 35000.0

    def test_piano_per_id(self, edificio_2piani):
        p = edificio_2piani.piano_per_id(1)
        assert p is not None
        assert p.quota_z == 300

    def test_piano_per_id_non_esiste(self, edificio_2piani):
        assert edificio_2piani.piano_per_id(99) is None

    def test_to_dict(self, edificio_2piani):
        d = edificio_2piani.to_dict()
        assert d["n_piani"] == 2
        assert d["altezza_totale"] == 600.0
        assert len(d["piani"]) == 2


# ═══════════════════════════════════════════════════════════
#  ConfigPOR
# ═══════════════════════════════════════════════════════════

class TestConfigPOR:

    def test_default_drift_taglio(self):
        c = ConfigPOR()
        assert c.drift_taglio == 0.005

    def test_default_drift_pflex(self):
        c = ConfigPOR()
        assert c.drift_pressoflessione == 0.010

    def test_eccentricita_default(self):
        c = ConfigPOR()
        assert c.eccentricita_accidentale == 0.05

    def test_to_dict(self):
        c = ConfigPOR()
        d = c.to_dict()
        assert "drift_taglio" in d
        assert "soglia_caduta_resistenza" in d


# ═══════════════════════════════════════════════════════════
#  FC da LC
# ═══════════════════════════════════════════════════════════

class TestFCDaLC:

    def test_lc1(self):
        assert FC_DA_LC["LC1"] == 1.35

    def test_lc2(self):
        assert FC_DA_LC["LC2"] == 1.20

    def test_lc3(self):
        assert FC_DA_LC["LC3"] == 1.00
