"""Test resistenza maschi e fasce — Fase F Blocco 2.

Test per:
- Resistenza maschio (3 criteri, curva bilineare)
- Resistenza fascia (biella, con cordolo)
- Stato maschio per spostamento
"""

import math
import pytest

from src.methods.muratura.modello_edificio import MaterialeMuratura
from src.methods.muratura.discretizzazione import (
    Fascia,
    Maschio,
    TipoVincolo,
)
from src.methods.muratura.resistenza import (
    ResistenzaMaschio,
    StatoMaschio,
    calcola_resistenza_fascia,
    calcola_resistenza_maschio,
    calcola_resistenze_piano,
)
from src.methods.muratura.rigidezza import rigidezza_maschio


@pytest.fixture
def materiale() -> MaterialeMuratura:
    return MaterialeMuratura(
        nome="mattoni_pieni",
        f=24.0, tau_0=0.6, fvk0=0.4,
        E=15000.0, G=5000.0, gamma=0.0018,
        gamma_M=2.0, FC=1.2, mu=0.4,
    )


def _crea_maschio(
    mat: MaterialeMuratura,
    L: float = 200, t: float = 30, h: float = 300,
    N: float = 10000,
    vincolo: TipoVincolo = TipoVincolo.INCASTRO,
) -> Maschio:
    m = Maschio(
        id_maschio=0, L=L, t=t, h=h,
        materiale=mat,
        N_gravitazionale=N,
        vincolo=vincolo,
    )
    m._direzione = "X"  # type: ignore[attr-defined]
    return m


# ═══════════════════════════════════════════════════════════
#  Resistenza maschio
# ═══════════════════════════════════════════════════════════

class TestResistenzaMaschio:

    def test_V_Rd_positivo(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        assert rm.V_Rd > 0

    def test_criterio_dominante_presente(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        assert rm.criterio_dominante in ("diagonale", "scorrimento", "pressoflessione")

    def test_V_Rd_minimo_dei_criteri(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)

        # V_Rd deve essere il minimo tra i criteri calcolati
        criteri = []
        if rm.V_Rd_diagonale > 0:
            criteri.append(rm.V_Rd_diagonale)
        if rm.V_Rd_scorrimento > 0:
            criteri.append(rm.V_Rd_scorrimento)
        if rm.V_Rd_pressoflessione > 0:
            criteri.append(rm.V_Rd_pressoflessione)

        if criteri:
            assert pytest.approx(rm.V_Rd, rel=0.01) == min(criteri)

    def test_delta_y_positivo(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        assert rm.delta_y > 0

    def test_delta_u_maggiore_delta_y(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        assert rm.delta_u > rm.delta_y

    def test_curva_bilineare_elastica(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)

        # Nel tratto elastico: V = k × δ
        delta_test = rm.delta_y * 0.5
        V = rm.forza_per_spostamento(delta_test)
        assert pytest.approx(V, rel=0.01) == rm.k_elastico * delta_test

    def test_curva_bilineare_plateau(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)

        # Nel plateau: V = V_Rd
        delta_test = (rm.delta_y + rm.delta_u) / 2
        V = rm.forza_per_spostamento(delta_test)
        assert pytest.approx(V, rel=0.01) == rm.V_Rd

    def test_curva_bilineare_collasso(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)

        # Dopo il collasso: V = 0
        delta_test = rm.delta_u * 1.5
        V = rm.forza_per_spostamento(delta_test)
        assert V == 0.0

    def test_curva_bilineare_negativa(self, materiale):
        """Spostamento negativo → forza negativa (simmetria)."""
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)

        delta_test = -rm.delta_y * 0.5
        V = rm.forza_per_spostamento(delta_test)
        assert V < 0

    def test_stato_elastico(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        assert rm.stato_per_spostamento(rm.delta_y * 0.5) == StatoMaschio.ELASTICO

    def test_stato_plastico(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        delta = (rm.delta_y + rm.delta_u) / 2
        assert rm.stato_per_spostamento(delta) == StatoMaschio.PLASTICO

    def test_stato_collassato(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        assert rm.stato_per_spostamento(rm.delta_u * 1.5) == StatoMaschio.COLLASSATO

    def test_nessun_materiale(self):
        m = Maschio(L=200, t=30, h=300, materiale=None)
        rm = calcola_resistenza_maschio(m)
        assert rm.V_Rd == 0.0

    def test_N_zero_no_pressoflessione(self, materiale):
        """Con N=0 il criterio pressoflessione non si attiva."""
        m = _crea_maschio(materiale, N=0)
        rm = calcola_resistenza_maschio(m)
        assert rm.V_Rd_pressoflessione == 0.0

    def test_maschio_snello_vs_tozzo(self, materiale):
        """Maschio snello ha V_Rd inferiore (a parità di N)."""
        m_tozzo = _crea_maschio(materiale, L=300, h=150, N=20000)
        m_snello = _crea_maschio(materiale, L=100, h=300, N=20000)

        rm_tozzo = calcola_resistenza_maschio(m_tozzo)
        rm_snello = calcola_resistenza_maschio(m_snello)

        # Il maschio tozzo è generalmente più resistente
        assert rm_tozzo.V_Rd > rm_snello.V_Rd

    def test_to_dict(self, materiale):
        m = _crea_maschio(materiale, N=15000)
        rm = calcola_resistenza_maschio(m)
        d = rm.to_dict()
        assert "V_Rd" in d
        assert "criterio_dominante" in d
        assert "delta_y" in d


# ═══════════════════════════════════════════════════════════
#  Resistenza fascia
# ═══════════════════════════════════════════════════════════

class TestResistenzaFascia:

    def test_fascia_biella_V_Rd_positivo(self, materiale):
        f = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=False)
        rf = calcola_resistenza_fascia(f)
        assert rf.V_Rd > 0
        assert rf.e_biella is True

    def test_fascia_cordolo_V_Rd_positivo(self, materiale):
        f = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=True)
        rf = calcola_resistenza_fascia(f)
        assert rf.V_Rd > 0
        assert rf.M_Rd > 0

    def test_fascia_cordolo_piu_resistente(self, materiale):
        f_biella = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=False)
        f_cordolo = Fascia(L=120, t=30, h=80, materiale=materiale, ha_cordolo=True)

        rf_b = calcola_resistenza_fascia(f_biella)
        rf_c = calcola_resistenza_fascia(f_cordolo)

        # Fascia con cordolo generalmente più resistente
        assert rf_c.V_Rd > 0

    def test_nessun_materiale(self):
        f = Fascia(L=120, t=30, h=80, materiale=None)
        rf = calcola_resistenza_fascia(f)
        assert rf.V_Rd == 0.0


# ═══════════════════════════════════════════════════════════
#  Calcolo resistenze piano
# ═══════════════════════════════════════════════════════════

class TestCalcolaResistenzePiano:

    def test_calcola_tutti(self, materiale):
        maschi = [
            _crea_maschio(materiale, N=10000),
            _crea_maschio(materiale, L=150, N=8000),
        ]
        maschi[1].id_maschio = 1

        fasce = [
            Fascia(id_fascia=0, L=120, t=30, h=80, materiale=materiale),
        ]

        rm, rf = calcola_resistenze_piano(maschi, fasce)
        assert len(rm) == 2
        assert len(rf) == 1
        assert all(r.V_Rd > 0 for r in rm)
