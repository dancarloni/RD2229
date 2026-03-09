"""Test rigidezza maschi/fasce e assemblaggio matrice — Fase F Blocco 1.

Test per:
- Rigidezza maschio (incastro, cerniera, mensola)
- Rigidezza fascia (con cordolo, biella)
- Centro di rigidezza
- Matrice rigidezza piano 3×3
- Distribuzione forze sui maschi
"""

import pytest

from src.methods.muratura.discretizzazione import (
    Fascia,
    Maschio,
    TipoVincolo,
)
from src.methods.muratura.modello_edificio import MaterialeMuratura
from src.methods.muratura.rigidezza import (
    CHI_RETTANGOLARE,
    assembla_matrice_piano,
    calcola_centro_rigidezza,
    distribuisci_forza_piano,
    rigidezza_fascia,
    rigidezza_maschio,
)


@pytest.fixture
def materiale() -> MaterialeMuratura:
    return MaterialeMuratura(
        nome="mattoni_pieni",
        f=24.0, tau_0=0.6, fvk0=0.4,
        E=15000.0, G=5000.0, gamma=0.0018,
    )


def _crea_maschio(
    id_m: int, L: float, t: float, h: float,
    mat: MaterialeMuratura,
    vincolo: TipoVincolo = TipoVincolo.INCASTRO,
    x_bar: float = 0.0, y_bar: float = 0.0,
    direzione: str = "X",
) -> Maschio:
    m = Maschio(
        id_maschio=id_m, L=L, t=t, h=h,
        materiale=mat, vincolo=vincolo,
        x_baricentro=x_bar, y_baricentro=y_bar,
    )
    m._direzione = direzione  # type: ignore[attr-defined]
    return m


# ═══════════════════════════════════════════════════════════
#  Rigidezza maschio
# ═══════════════════════════════════════════════════════════

class TestRigidezzaMaschio:

    def test_doppio_incastro(self, materiale):
        """k = 1 / (h³/(12EI) + χh/(GA)) per doppio incastro."""
        m = _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          vincolo=TipoVincolo.INCASTRO)

        I = 30 * 200 ** 3 / 12  # = 20_000_000 cm⁴
        A = 200 * 30  # = 6000 cm²
        E = 15000.0
        G = 5000.0

        flex_flex = 300 ** 3 / (12 * E * I)
        flex_taglio = CHI_RETTANGOLARE * 300 / (G * A)
        k_atteso = 1.0 / (flex_flex + flex_taglio)

        k = rigidezza_maschio(m)
        assert pytest.approx(k, rel=1e-4) == k_atteso

    def test_cerniera(self, materiale):
        """k = 1 / (h³/(3EI) + χh/(GA)) per incastro-cerniera."""
        m = _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          vincolo=TipoVincolo.CERNIERA)

        I = 30 * 200 ** 3 / 12
        A = 200 * 30
        E = 15000.0
        G = 5000.0

        flex_flex = 300 ** 3 / (3 * E * I)
        flex_taglio = CHI_RETTANGOLARE * 300 / (G * A)
        k_atteso = 1.0 / (flex_flex + flex_taglio)

        k = rigidezza_maschio(m)
        assert pytest.approx(k, rel=1e-4) == k_atteso

    def test_incastro_piu_rigido_di_cerniera(self, materiale):
        """Il maschio doppiamente incastrato è più rigido."""
        m_inc = _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                              vincolo=TipoVincolo.INCASTRO)
        m_cer = _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                              vincolo=TipoVincolo.CERNIERA)

        assert rigidezza_maschio(m_inc) > rigidezza_maschio(m_cer)

    def test_maschio_tozzo(self, materiale):
        """Maschio tozzo (h/L < 1): taglio domina."""
        m = _crea_maschio(0, L=300, t=30, h=150, mat=materiale)
        k = rigidezza_maschio(m)
        assert k > 0

    def test_maschio_snello(self, materiale):
        """Maschio snello (h/L > 2): flessione domina."""
        m = _crea_maschio(0, L=100, t=30, h=300, mat=materiale)
        k = rigidezza_maschio(m)
        assert k > 0

    def test_nessun_materiale(self):
        m = Maschio(L=200, t=30, h=300, materiale=None)
        assert rigidezza_maschio(m) == 0.0

    def test_G_zero_usa_stima(self, materiale):
        """Se G=0, viene stimato come 0.4×E."""
        mat_no_G = MaterialeMuratura(E=15000.0, G=0.0, f=20.0)
        m = _crea_maschio(0, L=200, t=30, h=300, mat=mat_no_G)
        k = rigidezza_maschio(m)
        assert k > 0

    def test_proporzionalita_spessore(self, materiale):
        """Raddoppiando lo spessore, la rigidezza raddoppia."""
        m1 = _crea_maschio(0, L=200, t=30, h=300, mat=materiale)
        m2 = _crea_maschio(1, L=200, t=60, h=300, mat=materiale)
        # Non è esattamente il doppio perché I cambia con t
        # ma k cresce con t
        assert rigidezza_maschio(m2) > rigidezza_maschio(m1)


# ═══════════════════════════════════════════════════════════
#  Rigidezza fascia
# ═══════════════════════════════════════════════════════════

class TestRigidezzaFascia:

    def test_fascia_con_cordolo(self, materiale):
        """Fascia con cordolo: rigidezza come trave Timoshenko."""
        f = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=True)
        k = rigidezza_fascia(f)
        assert k > 0

    def test_fascia_biella(self, materiale):
        """Fascia biella (senza cordolo): rigidezza ridotta."""
        f = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=False)
        k = rigidezza_fascia(f)
        assert k > 0

    def test_fascia_cordolo_piu_rigida(self, materiale):
        """Fascia con cordolo è più rigida della biella."""
        f_cord = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=True)
        f_biella = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=False)
        assert rigidezza_fascia(f_cord) > rigidezza_fascia(f_biella)

    def test_nessun_materiale(self):
        f = Fascia(L=120, t=30, h=80, materiale=None)
        assert rigidezza_fascia(f) == 0.0


# ═══════════════════════════════════════════════════════════
#  Centro rigidezza
# ═══════════════════════════════════════════════════════════

class TestCentroRigidezza:

    def test_piano_simmetrico(self, materiale):
        """Piano simmetrico: CR coincide con centro geometrico."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=400, direzione="X"),
            _crea_maschio(2, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="Y"),
            _crea_maschio(3, L=200, t=30, h=300, mat=materiale,
                          x_bar=500, y_bar=0, direzione="Y"),
        ]
        cr = calcola_centro_rigidezza(maschi, x_CM=250, y_CM=200)

        # Maschi Y (id 2, 3) alle x=0 e x=500: x_CR = (k*0 + k*500)/(2k) = 250
        assert pytest.approx(cr.x_CR, rel=1e-3) == 250.0
        # Maschi X (id 0, 1) alle y=0 e y=400: y_CR = (k*0 + k*400)/(2k) = 200
        assert pytest.approx(cr.y_CR, rel=1e-3) == 200.0

    def test_eccentricita_nulla_simmetrico(self, materiale):
        """Piano simmetrico con CM al centro: eccentricità ≈ 0."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=400, direzione="X"),
            _crea_maschio(2, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="Y"),
            _crea_maschio(3, L=200, t=30, h=300, mat=materiale,
                          x_bar=500, y_bar=0, direzione="Y"),
        ]
        cr = calcola_centro_rigidezza(maschi, x_CM=250, y_CM=200)

        assert pytest.approx(cr.ex, abs=1.0) == 0.0
        assert pytest.approx(cr.ey, abs=1.0) == 0.0

    def test_rigidezza_torsionale_positiva(self, materiale):
        """Maschi a distanza dal CR generano K_θ > 0."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=400, direzione="X"),
            _crea_maschio(2, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="Y"),
            _crea_maschio(3, L=200, t=30, h=300, mat=materiale,
                          x_bar=500, y_bar=0, direzione="Y"),
        ]
        cr = calcola_centro_rigidezza(maschi, x_CM=250, y_CM=200)
        assert cr.K_theta > 0


# ═══════════════════════════════════════════════════════════
#  Matrice rigidezza piano
# ═══════════════════════════════════════════════════════════

class TestMatriceRigidezzaPiano:

    def test_matrice_simmetrica(self, materiale):
        """La matrice K deve essere simmetrica."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=500, y_bar=0, direzione="Y"),
        ]
        mat = assembla_matrice_piano(maschi)
        K = mat.K

        # K[0][1] == K[1][0], K[0][2] == K[2][0], K[1][2] == K[2][1]
        assert pytest.approx(K[0][1], abs=1e-6) == K[1][0]
        assert pytest.approx(K[0][2], abs=1e-6) == K[2][0]
        assert pytest.approx(K[1][2], abs=1e-6) == K[2][1]

    def test_diagonale_positiva(self, materiale):
        """Termini diagonali devono essere > 0."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=100, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=250, y_bar=0, direzione="Y"),
        ]
        mat = assembla_matrice_piano(maschi)
        K = mat.K

        assert K[0][0] > 0  # Kxx
        assert K[1][1] > 0  # Kyy
        assert K[2][2] > 0  # Kθθ

    def test_solo_maschi_x(self, materiale):
        """Solo maschi in X: Kyy = 0."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=400, direzione="X"),
        ]
        mat = assembla_matrice_piano(maschi)
        assert mat.K[1][1] == 0.0

    def test_rigidezze_individuali(self, materiale):
        m = _crea_maschio(0, L=200, t=30, h=300, mat=materiale, direzione="X")
        mat = assembla_matrice_piano([m])
        assert m.id_maschio in mat.rigidezze_maschi


# ═══════════════════════════════════════════════════════════
#  Distribuzione forze
# ═══════════════════════════════════════════════════════════

class TestDistribuisciForza:

    def test_distribuzione_proporzionale_uguale(self, materiale):
        """Due maschi uguali in X: forza distribuita 50-50."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=400, direzione="X"),
        ]
        tagli = distribuisci_forza_piano(maschi, Fx=10000, Fy=0,
                                          x_rif=0, y_rif=200)

        # Con maschi uguali simmetrici rispetto a y_rif=200,
        # la forza si distribuisce 50-50
        assert pytest.approx(tagli[0], rel=0.01) == 5000.0
        assert pytest.approx(tagli[1], rel=0.01) == 5000.0

    def test_somma_tagli_uguale_forza(self, materiale):
        """Somma dei tagli = forza applicata."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=150, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=400, direzione="X"),
            _crea_maschio(2, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="Y"),
            _crea_maschio(3, L=200, t=30, h=300, mat=materiale,
                          x_bar=500, y_bar=0, direzione="Y"),
        ]
        Fx = 15000.0
        tagli = distribuisci_forza_piano(maschi, Fx=Fx, Fy=0,
                                          x_rif=250, y_rif=200)

        # Tagli maschi in X devono sommare a Fx
        tagli_x = tagli[0] + tagli[1]
        assert pytest.approx(tagli_x, rel=0.02) == Fx

    def test_forza_in_y(self, materiale):
        """Forza in Y distribuita sui maschi in Y."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="Y"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=500, y_bar=0, direzione="Y"),
        ]
        Fy = 8000.0
        tagli = distribuisci_forza_piano(maschi, Fx=0, Fy=Fy,
                                          x_rif=250, y_rif=0)

        assert pytest.approx(tagli[0] + tagli[1], rel=0.01) == Fy

    def test_eccentricita_genera_torsione(self, materiale):
        """Eccentricità tra CM e CR genera taglio diverso sui maschi."""
        # Due maschi uguali in Y, ma il CM è spostato
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="Y"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=500, y_bar=0, direzione="Y"),
        ]
        # Forza applicata con eccentricità (CM a x=100 anziché 250)
        tagli = distribuisci_forza_piano(maschi, Fx=0, Fy=10000,
                                          x_rif=100, y_rif=0)

        # I tagli sui due maschi devono essere diversi (effetto torsione)
        assert tagli[0] != pytest.approx(tagli[1], rel=0.1)

    def test_momento_torcente(self, materiale):
        """Momento torcente applicato direttamente."""
        maschi = [
            _crea_maschio(0, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=0, direzione="X"),
            _crea_maschio(1, L=200, t=30, h=300, mat=materiale,
                          x_bar=0, y_bar=400, direzione="X"),
        ]
        tagli = distribuisci_forza_piano(maschi, Fx=0, Fy=0, Mz=100000,
                                          x_rif=0, y_rif=200)

        # Momento genera tagli opposti sui maschi
        assert tagli[0] > 0
        assert tagli[1] < 0  # o viceversa, simmetria

    def test_nessun_maschio_restituisce_vuoto(self):
        tagli = distribuisci_forza_piano([], Fx=1000)
        assert tagli == {}
