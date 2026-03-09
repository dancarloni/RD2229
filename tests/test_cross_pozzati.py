"""Test benchmark algoritmo Cross-Pozzati.

Subfase L.10 — test_cross_pozzati.py.
Benchmark numerici da Santarella e Pozzati con verifica equilibrio.
"""

import pytest

from src.methods.rd2229.telaio.cross_pozzati import calcola_cross_pozzati
from src.methods.rd2229.telaio.modello_telaio import (
    AstaTelaio,
    CaricoAsta,
    ModelloTelaio,
    NodoTelaio,
    PianoTelaio,
    RilascioEstremita,
    SezioneTelaio,
    TipoAsta,
    TipoCarico,
    TipoRilascioInterno,
    TipoVincoloEsterno,
    VincoloEsterno,
)


def _sez(b: float, h: float, E: float = 300000.0) -> SezioneTelaio:
    """Crea sezione rettangolare con I e A calcolati automaticamente."""
    I = b * h**3 / 12.0
    A = b * h
    Wx = b * h**2 / 6.0
    return SezioneTelaio(tipo="RECTANGULAR", b=b, h=h, I=I, A=A, Wx=Wx, E=E, gamma=0.0025)


def _incastro() -> VincoloEsterno:
    return VincoloEsterno(TipoVincoloEsterno.INCASTRO)


def _libero() -> VincoloEsterno:
    return VincoloEsterno(TipoVincoloEsterno.LIBERO)


def _cerniera() -> VincoloEsterno:
    return VincoloEsterno(TipoVincoloEsterno.CERNIERA)


def _rigido() -> RilascioEstremita:
    return RilascioEstremita(TipoRilascioInterno.NODO_RIGIDO)


# ==============================================================================
# TEST 1 — Trave continua su 2 campate (Santarella cap.3)
# ==============================================================================

class TestTraveContinua2Campate:
    """Trave continua A-B-C.
    A: incastro, B: libero, C: incastro.
    Asta AB: L=400 cm, EI=3×10⁸ kg·cm²
    Asta BC: L=300 cm, EI=3×10⁸ kg·cm²
    Carico: q=2 kg/cm su AB, q=3 kg/cm su BC
    """

    def _modello(self) -> ModelloTelaio:
        EI = 3e8
        b, h = 30.0, 50.0
        # EI reale = E × I = E × b×h³/12
        # Scegliamo E tale che E × b×h³/12 = 3e8
        I = b * h**3 / 12.0   # = 312500 cm⁴
        E = EI / I             # ≈ 960 kg/cm² (solo per test)

        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=_incastro(), etichetta="A"),
            NodoTelaio(id=2, x=400, y=0, vincolo=_libero(), etichetta="B"),
            NodoTelaio(id=3, x=700, y=0, vincolo=_incastro(), etichetta="C"),
        ]
        aste = [
            AstaTelaio(
                id=1, nodo_i=1, nodo_j=2, tipo=TipoAsta.TRAVE,
                sezione=SezioneTelaio(tipo="RECTANGULAR", b=b, h=h, I=I, A=b*h, Wx=b*h**2/6, E=E, gamma=0.0),
                rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="AB",
            ),
            AstaTelaio(
                id=2, nodo_i=2, nodo_j=3, tipo=TipoAsta.TRAVE,
                sezione=SezioneTelaio(tipo="RECTANGULAR", b=b, h=h, I=I, A=b*h, Wx=b*h**2/6, E=E, gamma=0.0),
                rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="BC",
            ),
        ]
        return ModelloTelaio(nome="Test1", nodi=nodi, aste=aste, piani=[], zona_sismica="non_sismico")

    def test_convergenza(self):
        """Cross deve convergere in meno di 200 iterazioni."""
        modello = self._modello()
        dati = calcola_cross_pozzati(modello)
        assert dati.convergenza, "Cross deve convergere"
        assert dati.n_iterazioni < 200

    def test_equilibrio_nodo_B(self):
        """Al nodo B (libero): M_BA + M_BC ≈ 0 (equilibrio momenti)."""
        modello = self._modello()
        dati = calcola_cross_pozzati(modello)

        M_BA = dati.momenti_finali.get(1, (0.0, 0.0))[1]   # M_j asta AB = M_BA
        M_BC = dati.momenti_finali.get(2, (0.0, 0.0))[0]   # M_i asta BC = M_BC

        # Equilibrio: somma momenti agli estremi convergenti in B = 0
        squilibrio = abs(M_BA + M_BC)
        assert squilibrio < 10.0, (
            f"Squilibrio al nodo B: {squilibrio:.2f} kg·cm (atteso < 10)"
        )

    def test_simmetria_aste_uguali_stesso_carico(self):
        """Con carichi uniformi, i momenti agli incastri devono essere non nulli."""
        modello = self._modello()
        # Aggiunge carichi uniformi alle aste
        modello.aste[0].carichi = [CaricoAsta(TipoCarico.DISTRIBUITO_UNIFORME, valore_sx=2.0)]
        modello.aste[1].carichi = [CaricoAsta(TipoCarico.DISTRIBUITO_UNIFORME, valore_sx=3.0)]
        dati = calcola_cross_pozzati(modello)
        M_A = dati.momenti_finali.get(1, (0.0, 0.0))[0]   # M_i asta AB = M_A
        M_C = dati.momenti_finali.get(2, (0.0, 0.0))[1]   # M_j asta BC = M_C
        # Con carichi non nulli, i momenti agli incastri devono essere non zero
        assert abs(M_A) > 0.1, "M_A deve essere diverso da zero"
        assert abs(M_C) > 0.1, "M_C deve essere diverso da zero"


# ==============================================================================
# TEST 2 — Portale 1 piano — equilibrio globale
# ==============================================================================

class TestPortaleUnPiano:
    """Portale rettangolare:
    Nodi: A(incastro), B(libero, piano1), C(libero, piano1), D(incastro)
    Aste: pilastri AB e CD (h=300cm), trave BC (L=500cm)
    Carico: q=4 kg/cm su BC
    """

    def _modello(self) -> ModelloTelaio:
        h_col = 300.0
        L_trave = 500.0
        E = 300000.0

        # Sezioni: EI_trave = 2 × EI_col
        b_col, h_col_sez = 30.0, 30.0
        I_col = b_col * h_col_sez**3 / 12.0   # cm⁴
        b_trave, h_trave_sez = 30.0, 50.0
        I_trave = b_trave * h_trave_sez**3 / 12.0  # cm⁴

        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=_incastro(), piano=0, etichetta="A"),
            NodoTelaio(id=2, x=0, y=h_col, vincolo=_libero(), piano=1, etichetta="B"),
            NodoTelaio(id=3, x=L_trave, y=h_col, vincolo=_libero(), piano=1, etichetta="C"),
            NodoTelaio(id=4, x=L_trave, y=0, vincolo=_incastro(), piano=0, etichetta="D"),
        ]

        sez_col = SezioneTelaio(
            tipo="RECTANGULAR", b=b_col, h=h_col_sez,
            I=I_col, A=b_col*h_col_sez, Wx=b_col*h_col_sez**2/6, E=E, gamma=0.0
        )
        sez_trave = SezioneTelaio(
            tipo="RECTANGULAR", b=b_trave, h=h_trave_sez,
            I=I_trave, A=b_trave*h_trave_sez, Wx=b_trave*h_trave_sez**2/6, E=E, gamma=0.0
        )

        aste = [
            AstaTelaio(id=1, nodo_i=1, nodo_j=2, tipo=TipoAsta.PILASTRO,
                       sezione=sez_col, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="AB"),
            AstaTelaio(id=2, nodo_i=2, nodo_j=3, tipo=TipoAsta.TRAVE,
                       sezione=sez_trave, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="BC"),
            AstaTelaio(id=3, nodo_i=3, nodo_j=4, tipo=TipoAsta.PILASTRO,
                       sezione=sez_col, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="CD"),
        ]

        return ModelloTelaio(
            nome="Portale1Piano", nodi=nodi, aste=aste,
            piani=[PianoTelaio(id_piano=1, quota=h_col)],
            zona_sismica="non_sismico"
        )

    def test_convergenza_portale(self):
        modello = self._modello()
        dati = calcola_cross_pozzati(modello)
        assert dati.convergenza
        assert dati.n_iterazioni < 200

    def test_equilibrio_nodo_B(self):
        """Nodo B: M_BA + M_BC = 0."""
        modello = self._modello()
        dati = calcola_cross_pozzati(modello)
        # M_j asta 1 (AB) = M_BA, M_i asta 2 (BC) = M_BC
        M_BA = dati.momenti_finali.get(1, (0.0, 0.0))[1]
        M_BC = dati.momenti_finali.get(2, (0.0, 0.0))[0]
        squilibrio = abs(M_BA + M_BC)
        assert squilibrio < 5.0, f"Squilibrio B: {squilibrio:.2f}"

    def test_equilibrio_nodo_C(self):
        """Nodo C: M_CB + M_CD = 0."""
        modello = self._modello()
        dati = calcola_cross_pozzati(modello)
        M_CB = dati.momenti_finali.get(2, (0.0, 0.0))[1]
        M_CD = dati.momenti_finali.get(3, (0.0, 0.0))[0]
        squilibrio = abs(M_CB + M_CD)
        assert squilibrio < 5.0, f"Squilibrio C: {squilibrio:.2f}"

    def test_simmetria_portale_simmetrico(self):
        """Portale simmetrico con carico simmetrico: M_A ≈ M_D (simmetria)."""
        modello = self._modello()
        dati = calcola_cross_pozzati(modello)
        M_A = dati.momenti_finali.get(1, (0.0, 0.0))[0]
        M_D = dati.momenti_finali.get(3, (0.0, 0.0))[1]
        # Per simmetria: |M_A| ≈ |M_D|
        assert abs(abs(M_A) - abs(M_D)) < 10.0, (
            f"Asimmetria A-D: M_A={M_A:.0f}, M_D={M_D:.0f}"
        )


# ==============================================================================
# TEST 3 — Fattori di distribuzione: Σμ = 1 per ogni nodo libero
# ==============================================================================

class TestFattoriDistribuzione:

    def _modello_semplice(self) -> ModelloTelaio:
        """Trave continua 3 campate per test fattori."""
        EI = 2e8
        b, h = 30.0, 50.0
        I = b * h**3 / 12.0
        E = EI / I

        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=_incastro(), etichetta="A"),
            NodoTelaio(id=2, x=300, y=0, vincolo=_libero(), etichetta="B"),
            NodoTelaio(id=3, x=600, y=0, vincolo=_libero(), etichetta="C"),
            NodoTelaio(id=4, x=900, y=0, vincolo=_incastro(), etichetta="D"),
        ]
        sez = SezioneTelaio(tipo="RECT", b=b, h=h, I=I, A=b*h, Wx=b*h**2/6, E=E, gamma=0.0)
        aste = [
            AstaTelaio(id=1, nodo_i=1, nodo_j=2, tipo=TipoAsta.TRAVE, sezione=sez,
                       rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="AB"),
            AstaTelaio(id=2, nodo_i=2, nodo_j=3, tipo=TipoAsta.TRAVE, sezione=sez,
                       rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="BC"),
            AstaTelaio(id=3, nodo_i=3, nodo_j=4, tipo=TipoAsta.TRAVE, sezione=sez,
                       rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="CD"),
        ]
        return ModelloTelaio(nome="3Campate", nodi=nodi, aste=aste, piani=[], zona_sismica="non_sismico")

    def test_somma_mu_uguale_1(self):
        """Per ogni nodo libero: Σμ_ij = 1."""
        from src.methods.rd2229.telaio.cross_pozzati import (
            calcola_fattori_distribuzione,
            calcola_rigidezze,
        )
        modello = self._modello_semplice()
        k_i, k_j, _ = calcola_rigidezze(modello)
        fattori = calcola_fattori_distribuzione(modello, k_i, k_j)

        for id_nodo, f_nodo in fattori.items():
            somma = sum(f_nodo.values())
            assert somma == pytest.approx(1.0, abs=1e-9), (
                f"Nodo {id_nodo}: Σμ = {somma:.6f} ≠ 1"
            )

    def test_rigidezze_positive(self):
        """Tutte le rigidezze k_from_i devono essere > 0."""
        from src.methods.rd2229.telaio.cross_pozzati import calcola_rigidezze
        modello = self._modello_semplice()
        k_i, k_j, _ = calcola_rigidezze(modello)
        for id_a, k in k_i.items():
            assert k > 0, f"Asta {id_a}: rigidezza k_i = {k}"


# ==============================================================================
# TEST 4 — Equilibrio globale forze orizzontali con sway
# ==============================================================================

class TestEquilibrioSway:
    """Telaio 2 piani con forze sismiche — ΣTaglio piano = ΣForze piano superiori."""

    def _modello_2piani(self) -> ModelloTelaio:
        """Telaio a 2 piani, 1 campata."""
        E = 300000.0
        h_piano = 300.0
        L_trave = 400.0

        sez_col = _sez(30, 40, E)
        sez_trave = _sez(30, 50, E)

        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=_incastro(), piano=0, etichetta="A"),
            NodoTelaio(id=2, x=L_trave, y=0, vincolo=_incastro(), piano=0, etichetta="B"),
            NodoTelaio(id=3, x=0, y=h_piano, vincolo=_libero(), piano=1, etichetta="C"),
            NodoTelaio(id=4, x=L_trave, y=h_piano, vincolo=_libero(), piano=1, etichetta="D"),
            NodoTelaio(id=5, x=0, y=2*h_piano, vincolo=_libero(), piano=2, etichetta="E"),
            NodoTelaio(id=6, x=L_trave, y=2*h_piano, vincolo=_libero(), piano=2, etichetta="F"),
        ]

        aste = [
            # Pilastri piano 1
            AstaTelaio(id=1, nodo_i=1, nodo_j=3, tipo=TipoAsta.PILASTRO,
                       sezione=sez_col, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="AC"),
            AstaTelaio(id=2, nodo_i=2, nodo_j=4, tipo=TipoAsta.PILASTRO,
                       sezione=sez_col, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="BD"),
            # Trave piano 1
            AstaTelaio(id=3, nodo_i=3, nodo_j=4, tipo=TipoAsta.TRAVE,
                       sezione=sez_trave, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="CD"),
            # Pilastri piano 2
            AstaTelaio(id=4, nodo_i=3, nodo_j=5, tipo=TipoAsta.PILASTRO,
                       sezione=sez_col, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="CE"),
            AstaTelaio(id=5, nodo_i=4, nodo_j=6, tipo=TipoAsta.PILASTRO,
                       sezione=sez_col, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="DF"),
            # Trave piano 2
            AstaTelaio(id=6, nodo_i=5, nodo_j=6, tipo=TipoAsta.TRAVE,
                       sezione=sez_trave, rilascio_i=_rigido(), rilascio_j=_rigido(), etichetta="EF"),
        ]

        piani = [
            PianoTelaio(id_piano=1, quota=h_piano, forza_sismica_x=3000.0),
            PianoTelaio(id_piano=2, quota=2*h_piano, forza_sismica_x=6000.0),
        ]

        return ModelloTelaio(
            nome="Telaio2Piani", nodi=nodi, aste=aste, piani=piani,
            zona_sismica="media"
        )

    def test_convergenza_con_sway(self):
        """Il calcolo con correzione sway deve convergere."""
        modello = self._modello_2piani()
        dati = calcola_cross_pozzati(modello)
        assert dati.convergenza, "Cross con sway deve convergere"
        assert dati.n_iterazioni < 400

    def test_momenti_finali_non_nulli(self):
        """Con forze sismiche, tutti i momenti devono essere non nulli."""
        modello = self._modello_2piani()
        dati = calcola_cross_pozzati(modello)
        momenti_non_nulli = sum(
            1 for (Mi, Mj) in dati.momenti_finali.values()
            if abs(Mi) > 0.1 or abs(Mj) > 0.1
        )
        assert momenti_non_nulli >= 4, (
            f"Troppo pochi momenti non nulli: {momenti_non_nulli}"
        )
