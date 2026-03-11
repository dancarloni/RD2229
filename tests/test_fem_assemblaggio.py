"""Test M.7 — Assemblaggio, BC, soluzione e post-processing FEM beam.

Verifica le subfasi M.2–M.5:
- M.2: assemblaggio K_G sparsa
- M.3: condizioni al contorno (TipoVincolo, eliminazione/penalty)
- M.4: soluzione spsolve
- M.5: post-processing M(x), V(x), N(x), v(x)
"""

import math

import numpy as np
import pytest
import scipy.sparse as sp

from src.fem import (
    Assemblatore,
    ApplicatoreBC,
    CaricoDistribuitoUniforme,
    DiagrammaElemento,
    ElementoFEM,
    NodoFEM,
    PostProcessorFEM,
    RisultatoSoluzione,
    SolutoreFEMSparso,
    TipoVincolo,
    VincoloNodo,
)


# ---------------------------------------------------------------------------
# Helper: trave semplicemente appoggiata a 1 elemento
# ---------------------------------------------------------------------------
def _trave_appoggiata_1elem(
    L: float = 600.0, E: float = 30000.0, A: float = 100.0, I: float = 10000.0
):
    """Crea nodi, elemento e assemblatore per una trave semplicemente appoggiata (1 elem)."""
    nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
    nodo_j = NodoFEM(id=1, x=L, y=0.0)
    elem = ElementoFEM.da_nodi(0, nodo_i, nodo_j, E=E, A=A, I=I, etichetta="B1")
    asm = Assemblatore(nodi=[nodo_i, nodo_j], elementi=[elem])
    return nodo_i, nodo_j, elem, asm


# ---------------------------------------------------------------------------
# Test NodoFEM e ElementoFEM
# ---------------------------------------------------------------------------

class TestNodoFEM:
    def test_gdl_base_id_zero(self) -> None:
        n = NodoFEM(id=0, x=0.0, y=0.0)
        assert n.gdl_base == 0
        assert n.indici_gdl == (0, 1, 2)

    def test_gdl_base_id_due(self) -> None:
        n = NodoFEM(id=2, x=100.0, y=50.0)
        assert n.gdl_base == 6
        assert n.indici_gdl == (6, 7, 8)


class TestElementoFEM:
    def test_da_nodi_calcola_lunghezza(self) -> None:
        ni = NodoFEM(id=0, x=0.0, y=0.0)
        nj = NodoFEM(id=1, x=300.0, y=400.0)
        elem = ElementoFEM.da_nodi(0, ni, nj, E=30000.0, A=50.0, I=1000.0)
        assert elem.beam.L == pytest.approx(500.0)

    def test_da_nodi_calcola_angolo_45gradi(self) -> None:
        ni = NodoFEM(id=0, x=0.0, y=0.0)
        nj = NodoFEM(id=1, x=100.0, y=100.0)
        elem = ElementoFEM.da_nodi(0, ni, nj, E=30000.0, A=50.0, I=1000.0)
        assert elem.beam.angolo_rad == pytest.approx(math.pi / 4.0)

    def test_da_nodi_nodi_coincidenti_errore(self) -> None:
        ni = NodoFEM(id=0, x=100.0, y=100.0)
        nj = NodoFEM(id=1, x=100.0, y=100.0)
        with pytest.raises(ValueError, match="coincidono"):
            ElementoFEM.da_nodi(0, ni, nj, E=30000.0, A=50.0, I=1000.0)

    def test_indici_gdl_globali_ordine_corretto(self) -> None:
        ni = NodoFEM(id=0, x=0.0, y=0.0)
        nj = NodoFEM(id=1, x=100.0, y=0.0)
        elem = ElementoFEM.da_nodi(0, ni, nj, E=1.0, A=1.0, I=1.0)
        assert elem.indici_gdl_globali == [0, 1, 2, 3, 4, 5]

    def test_indici_gdl_globali_elemento_non_primo(self) -> None:
        ni = NodoFEM(id=1, x=100.0, y=0.0)
        nj = NodoFEM(id=2, x=200.0, y=0.0)
        elem = ElementoFEM.da_nodi(1, ni, nj, E=1.0, A=1.0, I=1.0)
        assert elem.indici_gdl_globali == [3, 4, 5, 6, 7, 8]


# ---------------------------------------------------------------------------
# Test Assemblatore (M.2)
# ---------------------------------------------------------------------------

class TestAssemblatore:
    def test_n_gdl_2nodi(self) -> None:
        ni = NodoFEM(id=0, x=0.0, y=0.0)
        nj = NodoFEM(id=1, x=100.0, y=0.0)
        asm = Assemblatore(nodi=[ni, nj], elementi=[])
        assert asm.n_gdl == 6

    def test_k_g_forma_corretta(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        K, F = asm.assembla()
        assert K.shape == (6, 6)
        assert F.shape == (6,)

    def test_k_g_simmetrica(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        K, _ = asm.assembla()
        diff = (K - K.T).toarray()
        np.testing.assert_allclose(diff, np.zeros((6, 6)), atol=1e-10)

    def test_k_g_e_sparsa(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        K, _ = asm.assembla()
        assert sp.issparse(K)

    def test_f_g_nullo_senza_carichi(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        _, F = asm.assembla()
        np.testing.assert_allclose(F, np.zeros(6), atol=1e-15)

    def test_f_g_con_carico_distribuito(self) -> None:
        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_j = NodoFEM(id=1, x=600.0, y=0.0)
        q = -2.0  # kg/cm (verso il basso)
        elem = ElementoFEM.da_nodi(
            0, nodo_i, nodo_j, E=30000.0, A=100.0, I=10000.0,
            carichi=[CaricoDistribuitoUniforme(intensita=q)],
        )
        asm = Assemblatore(nodi=[nodo_i, nodo_j], elementi=[elem])
        _, F = asm.assembla()
        L = 600.0
        # F_eq trasversale: qL/2 ai due nodi
        assert F[1] == pytest.approx(q * L / 2.0, rel=1e-10)
        assert F[4] == pytest.approx(q * L / 2.0, rel=1e-10)

    def test_assembla_2elementi_3nodi(self) -> None:
        n0 = NodoFEM(id=0, x=0.0, y=0.0)
        n1 = NodoFEM(id=1, x=300.0, y=0.0)
        n2 = NodoFEM(id=2, x=600.0, y=0.0)
        e0 = ElementoFEM.da_nodi(0, n0, n1, E=30000.0, A=100.0, I=10000.0)
        e1 = ElementoFEM.da_nodi(1, n1, n2, E=30000.0, A=100.0, I=10000.0)
        asm = Assemblatore(nodi=[n0, n1, n2], elementi=[e0, e1])
        K, F = asm.assembla()
        assert K.shape == (9, 9)
        assert F.shape == (9,)

    def test_k_g_non_zero_entries(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        K, _ = asm.assembla()
        assert K.nnz > 0

    def test_aggiungi_carico_nodale(self) -> None:
        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_j = NodoFEM(id=1, x=100.0, y=0.0)
        elem = ElementoFEM.da_nodi(0, nodo_i, nodo_j, E=1.0, A=1.0, I=1.0)
        asm = Assemblatore(nodi=[nodo_i, nodo_j], elementi=[elem])
        _, F = asm.assembla()
        asm.aggiungi_carico_nodale(F, id_nodo=1, forze=[5.0, -10.0, 0.0])
        assert F[3] == pytest.approx(5.0)
        assert F[4] == pytest.approx(-10.0)
        assert F[5] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Test TipoVincolo e VincoloNodo (M.3)
# ---------------------------------------------------------------------------

class TestVincoliNodo:
    def test_incastro_vincola_3gdl(self) -> None:
        v = VincoloNodo(id_nodo=0, tipo=TipoVincolo.INCASTRO)
        assert v.gdl_vincolati == [0, 1, 2]

    def test_cerniera_vincola_2gdl(self) -> None:
        v = VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA)
        assert v.gdl_vincolati == [0, 1]

    def test_carrello_v_vincola_1gdl(self) -> None:
        v = VincoloNodo(id_nodo=0, tipo=TipoVincolo.CARRELLO_V)
        assert v.gdl_vincolati == [1]

    def test_carrello_u_vincola_gdl_u(self) -> None:
        v = VincoloNodo(id_nodo=0, tipo=TipoVincolo.CARRELLO_U)
        assert v.gdl_vincolati == [0]

    def test_libero_nessun_gdl_vincolato(self) -> None:
        v = VincoloNodo(id_nodo=0, tipo=TipoVincolo.LIBERO)
        assert v.gdl_vincolati == []

    def test_gdl_base_nodo_1(self) -> None:
        v = VincoloNodo(id_nodo=1, tipo=TipoVincolo.INCASTRO)
        assert v.gdl_vincolati == [3, 4, 5]

    def test_gdl_base_nodo_2_cerniera(self) -> None:
        v = VincoloNodo(id_nodo=2, tipo=TipoVincolo.CERNIERA)
        assert v.gdl_vincolati == [6, 7]


class TestApplicatoreBC:
    def test_metodo_invalido_raise(self) -> None:
        with pytest.raises(ValueError, match="metodo"):
            ApplicatoreBC(vincoli=[], metodo="invalid")

    def test_gdl_vincolati_unione_vincoli(self) -> None:
        v0 = VincoloNodo(id_nodo=0, tipo=TipoVincolo.INCASTRO)
        v1 = VincoloNodo(id_nodo=1, tipo=TipoVincolo.CERNIERA)
        bc = ApplicatoreBC(vincoli=[v0, v1])
        assert bc.gdl_vincolati == [0, 1, 2, 3, 4]

    def test_eliminazione_riduce_dimensioni(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        K, F = asm.assembla()
        v0 = VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA)
        v1 = VincoloNodo(id_nodo=1, tipo=TipoVincolo.CERNIERA)
        bc = ApplicatoreBC(vincoli=[v0, v1])
        K_rid, F_rid, liberi, vincolati = bc.applica(K, F)
        # 6 GDL totali - 4 vincolati (2 cerniere × 2 GDL) = 2 liberi
        assert K_rid.shape == (2, 2)
        assert len(liberi) == 2
        assert len(vincolati) == 4

    def test_penalty_mantiene_dimensioni(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        K, F = asm.assembla()
        v0 = VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA)
        bc = ApplicatoreBC(vincoli=[v0], metodo="penalty")
        K_rid, F_rid, liberi, vincolati = bc.applica(K, F)
        assert K_rid.shape == (6, 6)
        assert len(liberi) == 6

    def test_penalty_impone_valore_elevato_diagonale(self) -> None:
        _, _, _, asm = _trave_appoggiata_1elem()
        K, F = asm.assembla()
        pf = 1.0e14
        v0 = VincoloNodo(id_nodo=0, tipo=TipoVincolo.INCASTRO)
        bc = ApplicatoreBC(vincoli=[v0], metodo="penalty", penalty_factor=pf)
        K_rid, _, _, _ = bc.applica(K, F)
        for i in range(3):
            assert K_rid[i, i] == pytest.approx(pf)

    def test_ricostruisci_spostamenti_inserisce_zeri_dove_vincolato(self) -> None:
        bc = ApplicatoreBC(vincoli=[VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA)])
        gdl_liberi = [2, 3, 4, 5]
        u_rid = np.array([0.01, 0.02, 0.03, 0.04])
        u = bc.ricostruisci_spostamenti(u_rid, gdl_liberi, n_totale=6)
        assert u[0] == 0.0
        assert u[1] == 0.0
        assert u[2] == pytest.approx(0.01)
        assert u[5] == pytest.approx(0.04)


# ---------------------------------------------------------------------------
# Test SolutoreFEMSparso (M.4)
# ---------------------------------------------------------------------------

class TestSolutoreFEMSparso:
    def test_matrice_singolare_raise(self) -> None:
        K = sp.csr_matrix(np.zeros((3, 3)))
        F = np.zeros(3)
        with pytest.raises((ValueError, RuntimeError)):
            SolutoreFEMSparso().risolvi(K, F, gdl_liberi=[0, 1, 2], n_gdl_totale=3)

    def test_sistema_0_gdl_liberi_raise(self) -> None:
        K = sp.csr_matrix((0, 0))
        F = np.zeros(0)
        with pytest.raises(ValueError, match="Nessun GDL libero"):
            SolutoreFEMSparso().risolvi(K, F, gdl_liberi=[], n_gdl_totale=6)

    def test_risultato_tipo_corretto(self) -> None:
        K = sp.eye(3, format="csr") * 1.0
        F = np.array([1.0, 2.0, 3.0])
        res = SolutoreFEMSparso().risolvi(K, F, gdl_liberi=[0, 1, 2], n_gdl_totale=3)
        assert isinstance(res, RisultatoSoluzione)

    def test_soluzione_sistema_diagonale(self) -> None:
        K = sp.diags([2.0, 4.0, 8.0], format="csr")
        F = np.array([4.0, 8.0, 16.0])
        res = SolutoreFEMSparso().risolvi(K, F, gdl_liberi=[0, 1, 2], n_gdl_totale=3)
        np.testing.assert_allclose(
            res.spostamenti_completi, [2.0, 2.0, 2.0], rtol=1e-10
        )

    def test_ricostruzione_spostamenti_completi(self) -> None:
        K = sp.diags([5.0, 10.0], format="csr")
        F = np.array([10.0, 30.0])
        res = SolutoreFEMSparso().risolvi(K, F, gdl_liberi=[1, 3], n_gdl_totale=6)
        assert res.spostamenti_completi[0] == 0.0  # vincolato
        assert res.spostamenti_completi[1] == pytest.approx(2.0)
        assert res.spostamenti_completi[3] == pytest.approx(3.0)

    def test_norma_residuo_piccola(self) -> None:
        K = sp.eye(4, format="csr") * 3.0
        F = np.array([6.0, 9.0, 12.0, 15.0])
        res = SolutoreFEMSparso().risolvi(K, F, gdl_liberi=[0, 1, 2, 3], n_gdl_totale=4)
        assert res.norma_residuo < 1e-9

    def test_to_dict_contiene_campi_attesi(self) -> None:
        K = sp.eye(2, format="csr")
        F = np.array([1.0, 1.0])
        res = SolutoreFEMSparso().risolvi(K, F, gdl_liberi=[0, 1], n_gdl_totale=2)
        d = res.to_dict()
        assert "n_gdl_totale" in d
        assert "norma_residuo" in d
        assert "passaggi_calcolo" in d


# ---------------------------------------------------------------------------
# Test PostProcessorFEM (M.5)
# ---------------------------------------------------------------------------

class TestPostProcessorFEM:
    def _crea_trave_risolta(
        self,
        L: float = 600.0,
        E: float = 30000.0,
        A: float = 100.0,
        I: float = 10000.0,
        q: float = -2.0,
    ):
        """Trave SA con carico uniforme — risolve il sistema completo."""
        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_j = NodoFEM(id=1, x=L, y=0.0)
        elem = ElementoFEM.da_nodi(
            0, nodo_i, nodo_j, E=E, A=A, I=I,
            carichi=[CaricoDistribuitoUniforme(intensita=q)],
        )
        asm = Assemblatore(nodi=[nodo_i, nodo_j], elementi=[elem])
        K, F = asm.assembla()
        # BC: cerniere ai due nodi (u=0, v=0 a entrambi)
        bc = ApplicatoreBC(vincoli=[
            VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA),
            VincoloNodo(id_nodo=1, tipo=TipoVincolo.CERNIERA),
        ])
        K_rid, F_rid, liberi, _ = bc.applica(K, F)
        res = SolutoreFEMSparso().risolvi(K_rid, F_rid, liberi, asm.n_gdl)
        return elem, asm, res, q, L, E, I

    def test_calcola_tutti_ritorna_lista(self) -> None:
        elem, asm, res, q, L, E, I = self._crea_trave_risolta()
        pp = PostProcessorFEM(asm.elementi, res.spostamenti_completi)
        diagrammi = pp.calcola_tutti()
        assert len(diagrammi) == 1
        assert isinstance(diagrammi[0], DiagrammaElemento)

    def test_diagramma_ha_punti(self) -> None:
        elem, asm, res, q, L, E, I = self._crea_trave_risolta()
        pp = PostProcessorFEM(asm.elementi, res.spostamenti_completi, n_punti=20)
        d = pp.calcola_tutti()[0]
        assert len(d.M_kgcm) == 20
        assert len(d.V_kg) == 20
        assert len(d.N_kg) == 20
        assert len(d.v_cm) == 20

    def test_taglio_lineare_per_carico_uniforme(self) -> None:
        """Trave SA con carico uniforme: taglio V(x) è lineare (non costante)."""
        elem, asm, res, q, L, E, I = self._crea_trave_risolta()
        pp = PostProcessorFEM(asm.elementi, res.spostamenti_completi, n_punti=11)
        d = pp.calcola_tutti()[0]
        # V(0) ≈ -qL/2 (reazione all'appoggio) e V(L) ≈ qL/2 (antisimmetrico)
        V_0 = float(d.V_kg[0])
        V_L = float(d.V_kg[-1])
        assert V_0 == pytest.approx(-q * L / 2.0, rel=1e-3)
        assert V_L == pytest.approx(q * L / 2.0, rel=1e-3)
        # La variazione è lineare: V(0) = -V(L)
        assert V_0 == pytest.approx(-V_L, rel=1e-8)

    def test_sforzo_normale_nullo_trave_orizzontale(self) -> None:
        """Trave SA orizzontale con solo carico verticale: N = 0."""
        elem, asm, res, q, L, E, I = self._crea_trave_risolta()
        pp = PostProcessorFEM(asm.elementi, res.spostamenti_completi, n_punti=10)
        d = pp.calcola_tutti()[0]
        np.testing.assert_allclose(d.N_kg, np.zeros(10), atol=1e-6)

    def test_x_glob_da_0_a_L(self) -> None:
        elem, asm, res, q, L, E, I = self._crea_trave_risolta(L=500.0)
        pp = PostProcessorFEM(asm.elementi, res.spostamenti_completi, n_punti=11)
        d = pp.calcola_tutti()[0]
        assert d.x_glob[0] == pytest.approx(0.0, abs=1e-10)
        assert d.x_glob[-1] == pytest.approx(500.0, rel=1e-10)

    def test_to_dict_serializabile(self) -> None:
        elem, asm, res, q, L, E, I = self._crea_trave_risolta()
        pp = PostProcessorFEM(asm.elementi, res.spostamenti_completi)
        d = pp.calcola_tutti()[0]
        data = d.to_dict()
        assert "M_kgcm" in data
        assert "V_kg" in data
        assert "N_kg" in data
        assert isinstance(data["passaggi_calcolo"], list)

    def test_momento_nullo_agli_appoggi_trave_sa(self) -> None:
        """Trave SA: M(0) ≈ 0 e M(L) ≈ 0 (metodo equilibrio statico nel post-processor)."""
        elem, asm, res, q, L, E, I = self._crea_trave_risolta(L=600.0, q=-2.0)
        pp = PostProcessorFEM(asm.elementi, res.spostamenti_completi, n_punti=51)
        d = pp.calcola_tutti()[0]
        M_max = float(np.max(np.abs(d.M_kgcm)))
        assert abs(float(d.M_kgcm[0])) < M_max * 0.02
        assert abs(float(d.M_kgcm[-1])) < M_max * 0.02
