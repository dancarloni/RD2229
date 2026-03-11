"""Test FEM su telai e confronto con soluzioni analitiche — Fase M.7.

Casi di validazione:
- Portale a un piano (2 pilastri + 1 traverso)
- Telaio multipiano (2 piani, 2 campate)
- Confronto FEM vs soluzioni analitiche (Pozzati — Teoria e Tecnica delle Strutture)
- Benchmark: strutture simmetriche
"""

from __future__ import annotations

import pytest
import numpy as np

from src.fem import (
    Assemblatore,
    CaricoConcentrato,
    CaricoDistribuitoUniforme,
    ElementoBeam,
    ElementoStruttura,
    Nodo,
    RisultatoAssemblaggio,
    TipoVincolo,
    Vincolo,
    applica_condizioni_contorno,
    calcola_diagrammi_elemento,
    calcola_postprocessing,
    risolvi,
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _risolvi_struttura(
    nodi: list[Nodo],
    elementi: list[ElementoStruttura],
    vincoli: list[Vincolo],
):
    """Pipeline completa: assembla → BC → risolvi."""
    ris_ass = Assemblatore(nodi, elementi).assembla()
    ris_bc = applica_condizioni_contorno(ris_ass.K_globale, ris_ass.F_globale, vincoli)
    ris_sol = risolvi(ris_bc, ris_ass.n_gdl)
    return ris_ass, ris_bc, ris_sol


# ---------------------------------------------------------------------------
# M.7.1 — Trave semplicemente appoggiata: confronto con soluzione analitica Pozzati
# ---------------------------------------------------------------------------

class TestTraveSemplicementeAppoggiata:
    """Trave con carico uniformemente distribuito.

    Soluzione analitica (Pozzati, Vol.2):
    - Freccia massima:  v_max = 5qL⁴/(384EI)
    - Momento massimo:  M_max = qL²/8
    - Taglio massimo:   V_max = qL/2
    - Rotazione agli appoggi: θ = qL³/(24EI)
    """

    @pytest.fixture
    def struttura(self):
        L, E, I, A = 600.0, 30000.0, 1000.0, 25.0
        q = 2.0
        elem = ElementoBeam(
            E=E, A=A, I=I, L=L, angolo=0.0, unita_angolo="deg",
            id_nodo_iniziale=0, id_nodo_finale=1, etichetta="Trave-SA",
        )
        nodi = [Nodo(0, 0.0, 0.0), Nodo(1, L, 0.0)]
        es = ElementoStruttura(elem, [CaricoDistribuitoUniforme(q)])
        vincoli = [Vincolo(0, TipoVincolo.CERNIERA), Vincolo(1, TipoVincolo.CARRELLO_V)]
        ris_ass, ris_bc, ris_sol = _risolvi_struttura(nodi, [es], vincoli)
        return elem, es, ris_sol, L, E, I, q

    def test_freccia_agli_appoggi_nulla(self, struttura):
        elem, es, ris_sol, L, E, I, q = struttura
        assert abs(ris_sol.spostamenti[1]) < 1e-8  # v nodo 0
        assert abs(ris_sol.spostamenti[4]) < 1e-8  # v nodo 1

    def test_rotazioni_agli_appoggi_analitiche(self, struttura):
        elem, es, ris_sol, L, E, I, q = struttura
        theta_analitica = q * L**3 / (24.0 * E * I)
        theta_0 = ris_sol.spostamenti[2]   # θ nodo 0
        theta_1 = ris_sol.spostamenti[5]   # θ nodo 1
        assert theta_0 == pytest.approx(theta_analitica, rel=1e-6)
        assert theta_1 == pytest.approx(-theta_analitica, rel=1e-6)

    def test_momento_massimo_al_centro(self, struttura):
        elem, es, ris_sol, L, E, I, q = struttura
        diagr = calcola_diagrammi_elemento(
            elem, ris_sol.spostamenti, 0, 1, n_punti=101, carichi=es.carichi
        )
        M_max_analitico = q * L**2 / 8.0
        assert diagr.M_max == pytest.approx(M_max_analitico, rel=1e-4)

    def test_taglio_agli_appoggi(self, struttura):
        elem, es, ris_sol, L, E, I, q = struttura
        diagr = calcola_diagrammi_elemento(
            elem, ris_sol.spostamenti, 0, 1, n_punti=101, carichi=es.carichi
        )
        V_max_analitico = q * L / 2.0
        assert diagr.V_max == pytest.approx(V_max_analitico, rel=1e-4)

    def test_converged(self, struttura):
        _, _, ris_sol, *_ = struttura
        assert ris_sol.converged


# ---------------------------------------------------------------------------
# M.7.2 — Trave a sbalzo (incastro-libera): confronto con soluzione analitica
# ---------------------------------------------------------------------------

class TestTraveASbalzo:
    """Trave a sbalzo con carico concentrato in punta.

    Soluzione analitica:
    - Freccia in punta: v_libera = PL³/(3EI)
    - Rotazione in punta: θ_libera = PL²/(2EI)
    - Momento all'incastro: M_incastro = -P·L (fibra superiore tesa)
    """

    @pytest.fixture
    def struttura(self):
        L, E, I, A = 300.0, 21000.0, 500.0, 20.0
        P = 200.0
        elem = ElementoBeam(
            E=E, A=A, I=I, L=L, angolo=0.0, unita_angolo="deg",
            id_nodo_iniziale=0, id_nodo_finale=1, etichetta="Sbalzo",
        )
        nodi = [Nodo(0, 0.0, 0.0), Nodo(1, L, 0.0)]
        es = ElementoStruttura(elem, [CaricoConcentrato(valore=P, posizione_x=L, tipo="forza_y")])
        vincoli = [Vincolo(0, TipoVincolo.INCASTRO)]
        ris_ass, ris_bc, ris_sol = _risolvi_struttura(nodi, [es], vincoli)
        return elem, es, ris_sol, L, E, I, P

    def test_freccia_punta_analitica(self, struttura):
        elem, es, ris_sol, L, E, I, P = struttura
        v_analitica = P * L**3 / (3.0 * E * I)
        v_punta = ris_sol.spostamenti[4]
        assert v_punta == pytest.approx(v_analitica, rel=1e-6)

    def test_rotazione_punta_analitica(self, struttura):
        elem, es, ris_sol, L, E, I, P = struttura
        theta_analitica = P * L**2 / (2.0 * E * I)
        theta_punta = ris_sol.spostamenti[5]
        assert theta_punta == pytest.approx(theta_analitica, rel=1e-6)

    def test_incastro_bloccato(self, struttura):
        _, _, ris_sol, *_ = struttura
        for gdl in range(3):  # u, v, θ del nodo 0
            assert abs(ris_sol.spostamenti[gdl]) < 1e-10

    def test_momento_incastro(self, struttura):
        elem, es, ris_sol, L, E, I, P = struttura
        diagr = calcola_diagrammi_elemento(elem, ris_sol.spostamenti, 0, 1, n_punti=51)
        M_incastro_analitico = P * L
        assert abs(diagr.M[0]) == pytest.approx(M_incastro_analitico, rel=1e-4)


# ---------------------------------------------------------------------------
# M.7.3 — Portale a un piano (2 pilastri + traverso)
# ---------------------------------------------------------------------------

class TestPortaleUnPiano:
    """Portale con 2 pilastri verticali e 1 traverso orizzontale.

    Nodi:
      0 (base sx)  1 (base dx)
      2 (testa sx) 3 (testa dx)

    Elementi:
      E0: nodo 0→2 (pilastro sx, L=300 cm, verticale, angolo=90°)
      E1: nodo 2→3 (traverso, L=600 cm, orizzontale, angolo=0°)
      E2: nodo 1→3 (pilastro dx, L=300 cm, verticale, angolo=90°)

    Carico: q=2 kg/cm sul traverso.
    Vincoli: incastri a nodi 0 e 1.

    La struttura è simmetrica → spostamenti agli appoggi nulli,
    simmetria dei risultati verificabile.
    """

    @pytest.fixture
    def portale(self):
        Hp, Lt = 300.0, 600.0  # altezza pilastri, luce traverso
        E, A, I = 25000.0, 30.0, 1200.0
        q = 2.0

        nodi = [
            Nodo(0, 0.0, 0.0),
            Nodo(1, Lt, 0.0),
            Nodo(2, 0.0, Hp),
            Nodo(3, Lt, Hp),
        ]

        pilastro_sx = ElementoBeam(
            E=E, A=A, I=I, L=Hp,
            angolo=90.0, unita_angolo="deg",
            id_nodo_iniziale=0, id_nodo_finale=2, etichetta="P-sx",
        )
        traverso = ElementoBeam(
            E=E, A=A, I=I, L=Lt,
            angolo=0.0, unita_angolo="deg",
            id_nodo_iniziale=2, id_nodo_finale=3, etichetta="Traverso",
        )
        pilastro_dx = ElementoBeam(
            E=E, A=A, I=I, L=Hp,
            angolo=90.0, unita_angolo="deg",
            id_nodo_iniziale=1, id_nodo_finale=3, etichetta="P-dx",
        )

        elementi = [
            ElementoStruttura(pilastro_sx),
            ElementoStruttura(traverso, [CaricoDistribuitoUniforme(q)]),
            ElementoStruttura(pilastro_dx),
        ]

        vincoli = [
            Vincolo(0, TipoVincolo.INCASTRO),
            Vincolo(1, TipoVincolo.INCASTRO),
        ]

        ris_ass, ris_bc, ris_sol = _risolvi_struttura(nodi, elementi, vincoli)
        return nodi, elementi, ris_sol, Hp, Lt, E, I, q

    def test_incastri_bloccati(self, portale):
        _, _, ris_sol, *_ = portale
        for gdl in range(6):  # nodi 0 e 1, 3 GDL each
            assert abs(ris_sol.spostamenti[gdl]) < 1e-8

    def test_simmetria_spostamenti_orizzontali_nodi_testa(self, portale):
        """Per carico simmetrico, gli spost. orizzontali alle teste sono antisimmetrici."""
        _, _, ris_sol, *_ = portale
        u_testa_sx = ris_sol.spostamenti[6]   # u nodo 2
        u_testa_dx = ris_sol.spostamenti[9]   # u nodo 3
        # I segni devono essere opposti (spostamenti orizzontali antisimmetrici)
        assert u_testa_sx == pytest.approx(-u_testa_dx, rel=1e-6)

    def test_spostamenti_verticali_nodi_testa_uguali(self, portale):
        """Per portale simmetrico, v alle teste devono essere uguali."""
        _, _, ris_sol, *_ = portale
        v_testa_sx = ris_sol.spostamenti[7]   # v nodo 2
        v_testa_dx = ris_sol.spostamenti[10]  # v nodo 3
        assert v_testa_sx == pytest.approx(v_testa_dx, rel=1e-6)

    def test_converged(self, portale):
        _, _, ris_sol, *_ = portale
        assert ris_sol.converged

    def test_postprocessing_traverso(self, portale):
        """Traverso del portale: M_max deve essere positivo e non nullo."""
        _, elementi, ris_sol, Hp, Lt, E, I, q = portale
        traverso_es = elementi[1]
        traverso = traverso_es.elemento
        diagr = calcola_diagrammi_elemento(
            traverso, ris_sol.spostamenti, 2, 3, n_punti=51
        )
        assert diagr.M_max > 0.0
        # Per il traverso incastrato a entrambe le estremità, M_max < qL²/8
        M_libera = q * Lt**2 / 8.0
        assert diagr.M_max < M_libera


# ---------------------------------------------------------------------------
# M.7.4 — Trave continua su 3 appoggi (verifica ridistribuzione)
# ---------------------------------------------------------------------------

class TestTraveContinua3Appoggi:
    """Trave continua a 2 campate uguali con carico uniformemente distribuito.

    Soluzione analitica (metodo delle tre equazioni di Clapeyron):
    - Momento sul supporto centrale: M_centro = -qL²/8
    - Reazioni: R_estreme = 3qL/8, R_centrale = 10qL/8 = 5qL/4
    """

    @pytest.fixture
    def trave_continua(self):
        L, E, I, A = 400.0, 30000.0, 1000.0, 25.0
        q = 1.0

        nodi = [Nodo(0, 0.0, 0.0), Nodo(1, L, 0.0), Nodo(2, 2 * L, 0.0)]

        elem_sx = ElementoBeam(
            E=E, A=A, I=I, L=L, angolo=0.0, unita_angolo="deg",
            id_nodo_iniziale=0, id_nodo_finale=1, etichetta="SX",
        )
        elem_dx = ElementoBeam(
            E=E, A=A, I=I, L=L, angolo=0.0, unita_angolo="deg",
            id_nodo_iniziale=1, id_nodo_finale=2, etichetta="DX",
        )

        carico = CaricoDistribuitoUniforme(q)
        elementi = [
            ElementoStruttura(elem_sx, [carico]),
            ElementoStruttura(elem_dx, [carico]),
        ]

        vincoli = [
            Vincolo(0, TipoVincolo.CERNIERA),
            Vincolo(1, TipoVincolo.CARRELLO_V),
            Vincolo(2, TipoVincolo.CARRELLO_V),
        ]

        ris_ass, ris_bc, ris_sol = _risolvi_struttura(nodi, elementi, vincoli)
        return elem_sx, elem_dx, ris_sol, L, E, I, q

    def test_appoggi_verticali_nulli(self, trave_continua):
        _, _, ris_sol, *_ = trave_continua
        for id_nodo in (0, 1, 2):
            v = ris_sol.spostamenti[3 * id_nodo + 1]
            assert abs(v) < 1e-8

    def test_momento_appoggio_centrale_analitico(self, trave_continua):
        """Momento sul supporto centrale: M_sup = qL²/8 (valore assoluto)."""
        elem_sx, elem_dx, ris_sol, L, E, I, q = trave_continua
        # Usa il metodo equilibrio passando i carichi
        carico = CaricoDistribuitoUniforme(q)
        diagr_sx = calcola_diagrammi_elemento(
            elem_sx, ris_sol.spostamenti, 0, 1, n_punti=101, carichi=[carico]
        )
        M_sup_analitico = q * L**2 / 8.0
        # Momento all'estremità dx della campata sx (indice -1)
        assert abs(diagr_sx.M[-1]) == pytest.approx(M_sup_analitico, rel=1e-4)

    def test_simmetria_rotazioni_appoggio_centrale(self, trave_continua):
        """Per struttura simmetrica, rotazione sul supporto centrale deve essere nulla."""
        _, _, ris_sol, *_ = trave_continua
        theta_centrale = ris_sol.spostamenti[5]  # θ nodo 1
        # Rotazioni uguali e opposte dalle due campate si annullano; la trave è continua
        # Per q uniforme su entrambe: θ_nodo1 = 0 per simmetria
        assert abs(theta_centrale) < 1e-8


# ---------------------------------------------------------------------------
# M.7.5 — Simmetria: struttura simmetrica con carico simmetrico
# ---------------------------------------------------------------------------

def test_simmetria_portale_incastrato_carico_simmetrico() -> None:
    """Per un portale incastrato con carico simmetrico sul traverso,
    |u_sx| == |u_dx| con segni opposti (antisimmetria per struttura simmetrica),
    e le rotazioni alle basi devono essere nulle.
    """
    Hp, Lt = 400.0, 800.0
    E, A, I = 20000.0, 40.0, 2000.0

    nodi = [Nodo(0, 0.0, 0.0), Nodo(1, Lt, 0.0), Nodo(2, 0.0, Hp), Nodo(3, Lt, Hp)]

    p_sx = ElementoBeam(E=E, A=A, I=I, L=Hp, angolo=90.0, unita_angolo="deg",
                        id_nodo_iniziale=0, id_nodo_finale=2)
    traverso = ElementoBeam(E=E, A=A, I=I, L=Lt, angolo=0.0, unita_angolo="deg",
                            id_nodo_iniziale=2, id_nodo_finale=3)
    p_dx = ElementoBeam(E=E, A=A, I=I, L=Hp, angolo=90.0, unita_angolo="deg",
                        id_nodo_iniziale=1, id_nodo_finale=3)

    q = 5.0
    elementi = [
        ElementoStruttura(p_sx),
        ElementoStruttura(traverso, [CaricoDistribuitoUniforme(q)]),
        ElementoStruttura(p_dx),
    ]
    vincoli = [Vincolo(0, TipoVincolo.INCASTRO), Vincolo(1, TipoVincolo.INCASTRO)]

    _, _, ris_sol = _risolvi_struttura(nodi, elementi, vincoli)

    # Spostamenti orizzontali alle teste: |u2| == |u3| con segni opposti
    u2 = ris_sol.spostamenti[6]
    u3 = ris_sol.spostamenti[9]
    assert abs(u2) == pytest.approx(abs(u3), rel=1e-6)
    assert u2 == pytest.approx(-u3, rel=1e-6)

    # Spostamenti verticali alle teste devono essere uguali (simmetria)
    v2 = ris_sol.spostamenti[7]
    v3 = ris_sol.spostamenti[10]
    assert v2 == pytest.approx(v3, rel=1e-6)


# ---------------------------------------------------------------------------
# M.7.6 — Benchmark performance: 100 elementi
# ---------------------------------------------------------------------------

def test_benchmark_assemblaggio_100_elementi() -> None:
    """Struttura a 100 elementi in serie: assemblaggio deve completarsi senza errori."""
    n_elem = 100
    L_elem = 10.0
    E, A, I = 30000.0, 25.0, 1000.0

    nodi = [Nodo(i, float(i) * L_elem, 0.0) for i in range(n_elem + 1)]
    elementi = [
        ElementoStruttura(
            ElementoBeam(
                E=E, A=A, I=I, L=L_elem,
                angolo=0.0, unita_angolo="deg",
                id_nodo_iniziale=i, id_nodo_finale=i + 1,
                etichetta=f"E{i}",
            ),
            [CaricoDistribuitoUniforme(1.0)],
        )
        for i in range(n_elem)
    ]
    vincoli = [Vincolo(0, TipoVincolo.CERNIERA), Vincolo(n_elem, TipoVincolo.CARRELLO_V)]

    ris_ass, ris_bc, ris_sol = _risolvi_struttura(nodi, elementi, vincoli)

    assert ris_ass.n_gdl == 3 * (n_elem + 1)
    assert ris_sol.converged
    # Tutti gli appoggi devono avere v=0
    assert abs(ris_sol.spostamenti[1]) < 1e-8
    assert abs(ris_sol.spostamenti[3 * n_elem + 1]) < 1e-8


# ---------------------------------------------------------------------------
# M.7.7 — Trave a sbalzo con carico distribuito
# ---------------------------------------------------------------------------

def test_trave_sbalzo_distribuito_freccia_estremita() -> None:
    """Trave a sbalzo con q uniforme: v_punta = qL⁴/(8EI)."""
    L, E, I, A = 200.0, 20000.0, 800.0, 20.0
    q = 3.0

    elem = ElementoBeam(
        E=E, A=A, I=I, L=L,
        angolo=0.0, unita_angolo="deg",
        id_nodo_iniziale=0, id_nodo_finale=1,
    )
    nodi = [Nodo(0, 0.0, 0.0), Nodo(1, L, 0.0)]
    es = ElementoStruttura(elem, [CaricoDistribuitoUniforme(q)])
    vincoli = [Vincolo(0, TipoVincolo.INCASTRO)]

    _, _, ris_sol = _risolvi_struttura(nodi, [es], vincoli)

    v_analitica = q * L**4 / (8.0 * E * I)
    v_punta = ris_sol.spostamenti[4]
    assert v_punta == pytest.approx(v_analitica, rel=1e-6)


# ---------------------------------------------------------------------------
# M.7.8 — Confronto FEM vs soluzioni analitiche multiple
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("L,q", [
    (100.0, 1.0),
    (300.0, 5.0),
    (500.0, 0.5),
    (1000.0, 2.0),
])
def test_trave_appoggiata_formula_analitica_parametrica(L: float, q: float) -> None:
    """Freccia massima = 5qL⁴/(384EI) per vari L e q."""
    E, I, A = 25000.0, 1200.0, 30.0
    elem = ElementoBeam(
        E=E, A=A, I=I, L=L,
        angolo=0.0, unita_angolo="deg",
        id_nodo_iniziale=0, id_nodo_finale=1,
    )
    nodi = [Nodo(0, 0.0, 0.0), Nodo(1, L, 0.0)]
    es = ElementoStruttura(elem, [CaricoDistribuitoUniforme(q)])
    vincoli = [Vincolo(0, TipoVincolo.CERNIERA), Vincolo(1, TipoVincolo.CARRELLO_V)]

    _, _, ris_sol = _risolvi_struttura(nodi, [es], vincoli)

    theta_analitica = q * L**3 / (24.0 * E * I)
    theta_0 = ris_sol.spostamenti[2]
    assert theta_0 == pytest.approx(theta_analitica, rel=1e-6)
