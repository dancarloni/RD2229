"""Test M.7 — Validazione FEM telaio: trave appoggiata, sbalzo, portale.

Confronta i risultati FEM con soluzioni analitiche note (Pozzati, testi classici).
Tolleranza: < 1% su grandezze globali chiave.
"""

import numpy as np
import pytest

from src.fem import (
    ApplicatoreBC,
    Assemblatore,
    CaricoDistribuitoUniforme,
    DiagrammaElemento,
    ElementoFEM,
    NodoFEM,
    PostProcessorFEM,
    SolutoreFEMSparso,
    TipoVincolo,
    VincoloNodo,
)


def _risolvi_sistema(
    nodi: list[NodoFEM],
    elementi: list[ElementoFEM],
    vincoli: list[VincoloNodo],
    carichi_nodali: dict[int, list[float]] | None = None,
    n_punti: int = 50,
) -> tuple[list[DiagrammaElemento], np.ndarray]:
    """Pipeline completa: assembla → applica BC → risolvi → post-processa."""
    asm = Assemblatore(nodi=nodi, elementi=elementi)
    K, F = asm.assembla()

    if carichi_nodali:
        for id_nodo, forze in carichi_nodali.items():
            asm.aggiungi_carico_nodale(F, id_nodo=id_nodo, forze=forze)

    bc = ApplicatoreBC(vincoli=vincoli)
    K_rid, F_rid, liberi, _ = bc.applica(K, F)
    res = SolutoreFEMSparso().risolvi(K_rid, F_rid, liberi, asm.n_gdl)

    pp = PostProcessorFEM(elementi, res.spostamenti_completi, n_punti=n_punti)
    diagrammi = pp.calcola_tutti()
    return diagrammi, res.spostamenti_completi


def _trave_sa_multielemento(
    L: float,
    E: float,
    A: float,
    I: float,
    q: float,
    n_elem: int = 8,
):
    """Trave SA con n elementi uniformi e carico distribuito uniforme."""
    L_e = L / n_elem
    nodi = [NodoFEM(id=i, x=i * L_e, y=0.0) for i in range(n_elem + 1)]
    elementi = [
        ElementoFEM.da_nodi(
            i,
            nodi[i],
            nodi[i + 1],
            E=E,
            A=A,
            I=I,
            carichi=[CaricoDistribuitoUniforme(intensita=q)],
        )
        for i in range(n_elem)
    ]
    vincoli = [
        VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA),
        VincoloNodo(id_nodo=n_elem, tipo=TipoVincolo.CERNIERA),
    ]
    asm = Assemblatore(nodi=nodi, elementi=elementi)
    K, F = asm.assembla()
    bc = ApplicatoreBC(vincoli=vincoli)
    K_rid, F_rid, liberi, _ = bc.applica(K, F)
    res = SolutoreFEMSparso().risolvi(K_rid, F_rid, liberi, asm.n_gdl)
    pp = PostProcessorFEM(elementi, res.spostamenti_completi, n_punti=51)
    return pp.calcola_tutti(), res.spostamenti_completi, nodi


# ---------------------------------------------------------------------------
# 1. Trave semplicemente appoggiata con carico distribuito uniforme
# ---------------------------------------------------------------------------


class TestTraveSA:
    """Confronto con soluzione analitica Pozzati.

    L=600 cm, E=30000 kg/cm², I=10000 cm⁴, q=-2 kg/cm
    M_max = -qL²/8 = 90000 kg·cm (al centro, positivo per q<0)
    v_max = 5qL⁴/(384EI) = -11.25 cm (freccia massima al centro)
    """

    L = 600.0
    E = 30000.0
    A = 100.0
    I = 10000.0
    q = -2.0  # kg/cm (verso il basso)

    @pytest.fixture
    def setup_multielemento(self):
        return _trave_sa_multielemento(self.L, self.E, self.A, self.I, self.q, n_elem=8)

    def test_freccia_massima_formula_analitica(self, setup_multielemento) -> None:
        """v_max = 5qL⁴/(384EI) — trave SA con carico uniforme (8 elementi)."""
        diagrammi, u, nodi = setup_multielemento
        # Trova il nodo centrale (indice 4 su 8 elementi = nodo 4)
        n_nodi = len(nodi)
        nodo_centro = n_nodi // 2
        gdl_v_centro = nodo_centro * 3 + 1  # GDL v del nodo centrale
        v_max_fem = float(u[gdl_v_centro])
        v_max_analitico = 5.0 * self.q * self.L**4 / (384.0 * self.E * self.I)
        assert v_max_fem == pytest.approx(v_max_analitico, rel=1e-3)

    def test_spostamento_nullo_agli_appoggi(self, setup_multielemento) -> None:
        diagrammi, u, nodi = setup_multielemento
        assert float(u[1]) == pytest.approx(0.0, abs=1e-8)  # v nodo 0
        assert float(u[-2]) == pytest.approx(0.0, abs=1e-8)  # v ultimo nodo

    def test_momento_massimo_al_centro(self) -> None:
        """M_max = qL²/8 al centro (metodo equilibrio nel post-processor)."""
        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_j = NodoFEM(id=1, x=self.L, y=0.0)
        elem = ElementoFEM.da_nodi(
            0,
            nodo_i,
            nodo_j,
            E=self.E,
            A=self.A,
            I=self.I,
            carichi=[CaricoDistribuitoUniforme(intensita=self.q)],
        )
        vincoli = [
            VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA),
            VincoloNodo(id_nodo=1, tipo=TipoVincolo.CERNIERA),
        ]
        diagrammi, u = _risolvi_sistema([nodo_i, nodo_j], [elem], vincoli, n_punti=101)
        d = diagrammi[0]
        M_max_fem = float(np.max(d.M_kgcm))
        M_max_analitico = -self.q * self.L**2 / 8.0
        assert M_max_fem == pytest.approx(M_max_analitico, rel=1e-3)

    def test_rotazioni_agli_appoggi_uguali_e_opposte(self, setup_multielemento) -> None:
        """Per trave SA simmetrica, θ(0) = -θ(L)."""
        diagrammi, u, nodi = setup_multielemento
        theta_i = float(u[2])  # GDL θ nodo 0
        theta_j = float(u[-1])  # GDL θ ultimo nodo
        assert theta_i == pytest.approx(-theta_j, rel=1e-6)


# ---------------------------------------------------------------------------
# 2. Trave a sbalzo (incastro-libera) con carico concentrato in punta
# ---------------------------------------------------------------------------


class TestTraveSbalzo:
    """Trave a sbalzo con forza concentrata all'estremità libera.

    L=300 cm, E=21000 kg/cm², I=8000 cm⁴, P=-100 kg
    v_max = PL³/(3EI) = -17.857 cm
    θ_max = PL²/(2EI) = -0.08929 rad
    """

    L = 300.0
    E = 21000.0
    A = 50.0
    I = 8000.0
    P = -100.0  # kg, verso il basso

    @pytest.fixture
    def setup(self):
        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_j = NodoFEM(id=1, x=self.L, y=0.0)
        elem = ElementoFEM.da_nodi(0, nodo_i, nodo_j, E=self.E, A=self.A, I=self.I)
        vincoli = [VincoloNodo(id_nodo=0, tipo=TipoVincolo.INCASTRO)]
        carichi_nodali = {1: [0.0, self.P, 0.0]}
        return _risolvi_sistema([nodo_i, nodo_j], [elem], vincoli, carichi_nodali, n_punti=51)

    def test_freccia_estremita_libera(self, setup) -> None:
        """v(L) = PL³/(3EI) — esatto per 1 elemento con carico nodale."""
        diagrammi, u = setup
        v_fem = float(u[4])  # GDL v nodo 1
        v_analitico = self.P * self.L**3 / (3.0 * self.E * self.I)
        assert v_fem == pytest.approx(v_analitico, rel=1e-3)

    def test_rotazione_estremita_libera(self, setup) -> None:
        """θ(L) = PL²/(2EI) — esatto per 1 elemento con carico nodale."""
        diagrammi, u = setup
        theta_fem = float(u[5])  # GDL θ nodo 1
        theta_analitico = self.P * self.L**2 / (2.0 * self.E * self.I)
        assert theta_fem == pytest.approx(theta_analitico, rel=1e-3)

    def test_spostamento_nullo_allincastro(self, setup) -> None:
        diagrammi, u = setup
        assert float(u[0]) == pytest.approx(0.0, abs=1e-10)
        assert float(u[1]) == pytest.approx(0.0, abs=1e-10)
        assert float(u[2]) == pytest.approx(0.0, abs=1e-10)

    def test_taglio_costante_uguale_a_P(self, setup) -> None:
        """Trave a sbalzo con P in punta, senza carichi distribuiti: taglio costante = P."""
        diagrammi, u = setup
        d = diagrammi[0]
        # V è costante (nessun carico distribuito → q_arr = 0, V = F_left_v costante)
        V_medio = float(np.mean(d.V_kg))
        assert abs(V_medio) == pytest.approx(abs(self.P), rel=1e-3)


# ---------------------------------------------------------------------------
# 3. Trave SA con carico concentrato a metà campata
# ---------------------------------------------------------------------------


class TestTraveSAConcentrato:
    """Trave SA con forza concentrata al centro.

    L=400 cm, E=30000 kg/cm², I=5000 cm⁴, P=-200 kg
    Con 2 elementi e il carico concentrato applicato come forza nodale al centro:
    v_max = PL³/(48EI) = -17.778 cm (esatto: carico al nodo intermedio)
    M_max = |P|*L/4 = 20000 kg·cm (esatto via equilibrio)
    """

    L = 400.0
    E = 30000.0
    A = 80.0
    I = 5000.0
    P = -200.0

    @pytest.fixture
    def setup(self):
        # 2 elementi: il nodo centrale è a x=L/2; la forza P è applicata al nodo 1
        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_m = NodoFEM(id=1, x=self.L / 2.0, y=0.0)
        nodo_j = NodoFEM(id=2, x=self.L, y=0.0)
        e0 = ElementoFEM.da_nodi(0, nodo_i, nodo_m, E=self.E, A=self.A, I=self.I)
        e1 = ElementoFEM.da_nodi(1, nodo_m, nodo_j, E=self.E, A=self.A, I=self.I)
        vincoli = [
            VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA),
            VincoloNodo(id_nodo=2, tipo=TipoVincolo.CERNIERA),
        ]
        carichi_nodali = {1: [0.0, self.P, 0.0]}
        return _risolvi_sistema(
            [nodo_i, nodo_m, nodo_j], [e0, e1], vincoli, carichi_nodali, n_punti=51
        )

    def test_freccia_massima_al_centro(self, setup) -> None:
        """v_max = PL³/(48EI) — esatto al nodo centrale (GDL v nodo 1)."""
        diagrammi, u = setup
        v_fem = float(u[4])  # GDL v nodo 1 (= v_max al centro)
        v_max_analitico = self.P * self.L**3 / (48.0 * self.E * self.I)
        assert v_fem == pytest.approx(v_max_analitico, rel=1e-3)

    def test_momento_massimo_al_centro(self, setup) -> None:
        """M_max = |P|*L/4 al centro per forza concentrata."""
        diagrammi, u = setup
        # Primo elemento: M a fine elemento (x = L/2) = PL/4
        M_fine_e0 = float(diagrammi[0].M_kgcm[-1])
        M_max_analitico = -self.P * self.L / 4.0
        assert M_fine_e0 == pytest.approx(M_max_analitico, rel=1e-3)


# ---------------------------------------------------------------------------
# 4. Portale a un piano
# ---------------------------------------------------------------------------


class TestPortaleUnPiano:
    """Portale rettangolare: 2 pilastri + 1 traverso con carico verticale.

    Geometria:
        Nodo 0: (0, 0)    — incastro
        Nodo 1: (L, 0)    — incastro
        Nodo 2: (0, H)    — libero (testa pilastro sx)
        Nodo 3: (L, H)    — libero (testa pilastro dx)
    Elementi:
        0: pilastro sinistro  0→2
        1: traverso           2→3  (con carico uniforme)
        2: pilastro destro    1→3
    """

    L = 500.0  # cm
    H = 300.0  # cm
    E = 30000.0
    A_pil = 100.0
    I_pil = 5000.0
    A_trav = 100.0
    I_trav = 10000.0
    q = -1.0  # kg/cm

    @pytest.fixture
    def setup(self):
        n0 = NodoFEM(id=0, x=0.0, y=0.0)
        n1 = NodoFEM(id=1, x=self.L, y=0.0)
        n2 = NodoFEM(id=2, x=0.0, y=self.H)
        n3 = NodoFEM(id=3, x=self.L, y=self.H)
        e_pil_sx = ElementoFEM.da_nodi(
            0, n0, n2, E=self.E, A=self.A_pil, I=self.I_pil, etichetta="pilastro_sx"
        )
        e_trav = ElementoFEM.da_nodi(
            1,
            n2,
            n3,
            E=self.E,
            A=self.A_trav,
            I=self.I_trav,
            etichetta="traverso",
            carichi=[CaricoDistribuitoUniforme(intensita=self.q)],
        )
        e_pil_dx = ElementoFEM.da_nodi(
            2, n1, n3, E=self.E, A=self.A_pil, I=self.I_pil, etichetta="pilastro_dx"
        )
        vincoli = [
            VincoloNodo(id_nodo=0, tipo=TipoVincolo.INCASTRO),
            VincoloNodo(id_nodo=1, tipo=TipoVincolo.INCASTRO),
        ]
        return _risolvi_sistema([n0, n1, n2, n3], [e_pil_sx, e_trav, e_pil_dx], vincoli, n_punti=21)

    def test_assenza_spostamenti_agli_incastri(self, setup) -> None:
        diagrammi, u = setup
        np.testing.assert_allclose(u[0:3], np.zeros(3), atol=1e-10)
        np.testing.assert_allclose(u[3:6], np.zeros(3), atol=1e-10)

    def test_abbassamento_traverso(self, setup) -> None:
        """Il traverso si abbassa sotto il carico verticale."""
        diagrammi, u = setup
        d_trav = diagrammi[1]
        v_min = float(np.min(d_trav.v_cm))
        assert v_min < 0.0

    def test_spostamento_orizzontale_antisimmetrico(self, setup) -> None:
        """Per portale simmetrico con carico verticale uniforme, u2 = -u3 (antisimmetria)."""
        diagrammi, u = setup
        u_nodo_2 = float(u[6])  # u nodo 2
        u_nodo_3 = float(u[9])  # u nodo 3
        # Per struttura simmetrica + carico simmetrico: u2 = -u3 (spostamenti opposti)
        assert u_nodo_2 == pytest.approx(-u_nodo_3, rel=1e-4)

    def test_3_diagrammi_ritornati(self, setup) -> None:
        diagrammi, _ = setup
        assert len(diagrammi) == 3

    def test_momento_negativo_agli_incastri_base(self, setup) -> None:
        """I momenti di incastro alla base dei pilastri sono non nulli."""
        diagrammi, u = setup
        # La base del pilastro sinistro è il nodo i (nodo 0, incastro)
        d_pil_sx = diagrammi[0]
        # Il momento all'incastro è diverso da zero (portale con carico verticale)
        M_base = float(d_pil_sx.M_kgcm[0])
        assert abs(M_base) > 0.0


# ---------------------------------------------------------------------------
# 5. Trave continua 2 campate (3 nodi, 2 elementi)
# ---------------------------------------------------------------------------


class TestTraveContinua2Campate:
    """Trave continua su 3 appoggi (cerniera + 2 carrelli) con carico uniforme.

    L1 = L2 = L = 400 cm, q = -1.5 kg/cm
    Soluzione analitica (trave continua 2 campate uguali):
    M_appoggio_centrale = qL²/8 = -30000 kg·cm (negativo per q<0)
    """

    L = 400.0
    E = 30000.0
    A = 100.0
    I = 8000.0
    q = -1.5

    @pytest.fixture
    def setup(self):
        n0 = NodoFEM(id=0, x=0.0, y=0.0)
        n1 = NodoFEM(id=1, x=self.L, y=0.0)
        n2 = NodoFEM(id=2, x=2.0 * self.L, y=0.0)
        e0 = ElementoFEM.da_nodi(
            0,
            n0,
            n1,
            E=self.E,
            A=self.A,
            I=self.I,
            carichi=[CaricoDistribuitoUniforme(intensita=self.q)],
        )
        e1 = ElementoFEM.da_nodi(
            1,
            n1,
            n2,
            E=self.E,
            A=self.A,
            I=self.I,
            carichi=[CaricoDistribuitoUniforme(intensita=self.q)],
        )
        # BC: cerniera sx (u=0, v=0), carrello centrale (v=0), carrello dx (v=0)
        # Per evitare modo rigido assiale: cerniera anche a destra
        vincoli = [
            VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA),
            VincoloNodo(id_nodo=1, tipo=TipoVincolo.CARRELLO_V),
            VincoloNodo(id_nodo=2, tipo=TipoVincolo.CERNIERA),
        ]
        return _risolvi_sistema([n0, n1, n2], [e0, e1], vincoli, n_punti=51)

    def test_spostamenti_nulli_agli_appoggi(self, setup) -> None:
        diagrammi, u = setup
        assert float(u[1]) == pytest.approx(0.0, abs=1e-8)  # v nodo 0
        assert float(u[4]) == pytest.approx(0.0, abs=1e-8)  # v nodo 1
        assert float(u[7]) == pytest.approx(0.0, abs=1e-8)  # v nodo 2

    def test_momento_allappoggio_centrale(self, setup) -> None:
        """M all'appoggio centrale = qL²/8 (trave continua 2 campate uguali)."""
        diagrammi, u = setup
        d0 = diagrammi[0]
        # Il momento a fine primo elemento (x=L) = momento all'appoggio centrale
        M_appoggio_dx = float(d0.M_kgcm[-1])
        M_analitico = self.q * self.L**2 / 8.0  # negativo per q<0
        assert M_appoggio_dx == pytest.approx(M_analitico, rel=0.05)

    def test_rotazione_nulla_allappoggio_centrale(self, setup) -> None:
        """Per 2 campate simmetriche con carico simmetrico: θ=0 al nodo centrale."""
        diagrammi, u = setup
        theta_nodo1 = float(u[5])  # θ nodo 1 (appoggio centrale)
        assert abs(theta_nodo1) < 1e-8

    def test_2_diagrammi_ritornati(self, setup) -> None:
        diagrammi, _ = setup
        assert len(diagrammi) == 2


# ---------------------------------------------------------------------------
# 6. Test metodo penalty equivalente a eliminazione
# ---------------------------------------------------------------------------


class TestPenaltyVsEliminazione:
    """Verifica che il metodo penalty dia risultati equivalenti all'eliminazione."""

    def test_spostamenti_equivalenti(self) -> None:
        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_j = NodoFEM(id=1, x=500.0, y=0.0)
        elem = ElementoFEM.da_nodi(
            0,
            nodo_i,
            nodo_j,
            E=30000.0,
            A=100.0,
            I=10000.0,
            carichi=[CaricoDistribuitoUniforme(intensita=-2.0)],
        )
        nodi = [nodo_i, nodo_j]
        vincoli = [
            VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA),
            VincoloNodo(id_nodo=1, tipo=TipoVincolo.CERNIERA),
        ]
        asm = Assemblatore(nodi=nodi, elementi=[elem])
        K, F = asm.assembla()

        bc_elim = ApplicatoreBC(vincoli=vincoli, metodo="eliminazione")
        K_e, F_e, lib_e, _ = bc_elim.applica(K, F)
        res_e = SolutoreFEMSparso().risolvi(K_e, F_e, lib_e, asm.n_gdl)

        bc_pen = ApplicatoreBC(vincoli=vincoli, metodo="penalty", penalty_factor=1e14)
        K_p, F_p, lib_p, _ = bc_pen.applica(K.copy(), F.copy())
        res_p = SolutoreFEMSparso().risolvi(K_p, F_p, lib_p, asm.n_gdl)

        np.testing.assert_allclose(
            res_e.spostamenti_completi,
            res_p.spostamenti_completi,
            rtol=1e-4,
            atol=1e-8,
        )
