"""Test per combinazioni_rd2229.py — inviluppo sollecitazioni.

Subfase L.10.
"""

from src.methods.rd2229.telaio.combinazioni_rd2229 import (
    calcola_tutte_le_combinazioni,
    combinazioni_attive,
)
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


def _sez(b: float = 30.0, h: float = 50.0, E: float = 300000.0) -> SezioneTelaio:
    I = b * h**3 / 12.0
    return SezioneTelaio(tipo="RECT", b=b, h=h, I=I, A=b * h, Wx=b * h**2 / 6, E=E, gamma=0.0)


def _rigido() -> RilascioEstremita:
    return RilascioEstremita(TipoRilascioInterno.NODO_RIGIDO)


# ==============================================================================
# TEST 1 — Combinazioni attive per zona
# ==============================================================================


class TestCombinazioniAttive:
    """combinazioni_attive() restituisce list[str] con gli ID delle combinazioni."""

    def test_non_sismico(self):
        ids = combinazioni_attive("non_sismico")
        assert "LC1" in ids
        assert "LC2" in ids
        assert "LC3" not in ids
        assert "LC4" not in ids
        assert "LC5" not in ids

    def test_zona_bassa(self):
        ids = combinazioni_attive("bassa")
        assert "LC3" in ids
        assert "LC4" in ids
        assert "LC5" not in ids  # sussultorio solo media/alta

    def test_zona_media(self):
        ids = combinazioni_attive("media")
        assert "LC3" in ids
        assert "LC4" in ids
        assert "LC5" in ids
        assert "LC6" in ids

    def test_zona_alta(self):
        ids = combinazioni_attive("alta")
        assert "LC5" in ids and "LC6" in ids

    def test_tutte_includono_LC1_LC2(self):
        for zona in ("non_sismico", "bassa", "media", "alta"):
            ids = combinazioni_attive(zona)
            assert "LC1" in ids and "LC2" in ids


# ==============================================================================
# TEST 2 — Inviluppo: M_max ≥ M_min per ogni sezione
# ==============================================================================


class TestInviluppo:
    def _modello_semplice(self, zona: str = "bassa") -> ModelloTelaio:
        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
            NodoTelaio(
                id=2,
                x=300,
                y=300,
                vincolo=VincoloEsterno(TipoVincoloEsterno.LIBERO),
                piano=1,
                etichetta="B",
            ),
            NodoTelaio(id=3, x=600, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
        ]
        sez = _sez()
        aste = [
            AstaTelaio(
                id=1,
                nodo_i=1,
                nodo_j=2,
                tipo=TipoAsta.PILASTRO,
                sezione=sez,
                carichi=[],
                rilascio_i=_rigido(),
                rilascio_j=_rigido(),
                etichetta="AB",
            ),
            AstaTelaio(
                id=2,
                nodo_i=2,
                nodo_j=3,
                tipo=TipoAsta.PILASTRO,
                sezione=sez,
                carichi=[],
                rilascio_i=_rigido(),
                rilascio_j=_rigido(),
                etichetta="BC",
            ),
        ]
        piani = [PianoTelaio(id_piano=1, quota=300.0)]
        return ModelloTelaio(
            nome="TestInviluppo", nodi=nodi, aste=aste, piani=piani, zona_sismica=zona
        )

    def test_inviluppo_ha_tutte_le_aste(self):
        modello = self._modello_semplice()
        ris = calcola_tutte_le_combinazioni(modello)
        for id_asta in [a.id for a in modello.aste]:
            assert id_asta in ris.inviluppo, f"Asta {id_asta} mancante nell'inviluppo"

    def test_inviluppo_M_max_ge_M_min(self):
        """M_max deve essere ≥ M_min per ogni sezione."""
        modello = self._modello_semplice()
        ris = calcola_tutte_le_combinazioni(modello)
        for id_asta, inv in ris.inviluppo.items():
            assert (
                inv.M_max_i >= inv.M_min_i - 1e-6
            ), f"Asta {id_asta} sez i: M_max_i={inv.M_max_i:.0f} < M_min_i={inv.M_min_i:.0f}"
            assert (
                inv.M_max_m >= inv.M_min_m - 1e-6
            ), f"Asta {id_asta} sez mid: M_max_m={inv.M_max_m:.0f} < M_min_m={inv.M_min_m:.0f}"
            assert (
                inv.M_max_j >= inv.M_min_j - 1e-6
            ), f"Asta {id_asta} sez j: M_max_j={inv.M_max_j:.0f} < M_min_j={inv.M_min_j:.0f}"


# ==============================================================================
# TEST 3 — Coppia (M_gov, N_gov) deve provenire dallo stesso caso
# ==============================================================================


class TestCoppiaGovernante:
    def _portale(self, zona: str = "media") -> ModelloTelaio:
        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
            NodoTelaio(
                id=2, x=0, y=400, vincolo=VincoloEsterno(TipoVincoloEsterno.LIBERO), piano=1
            ),
            NodoTelaio(
                id=3, x=500, y=400, vincolo=VincoloEsterno(TipoVincoloEsterno.LIBERO), piano=1
            ),
            NodoTelaio(id=4, x=500, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
        ]
        sez = _sez()
        aste = [
            AstaTelaio(
                id=1,
                nodo_i=1,
                nodo_j=2,
                tipo=TipoAsta.PILASTRO,
                sezione=sez,
                carichi=[],
                rilascio_i=_rigido(),
                rilascio_j=_rigido(),
            ),
            AstaTelaio(
                id=2,
                nodo_i=2,
                nodo_j=3,
                tipo=TipoAsta.TRAVE,
                sezione=sez,
                carichi=[CaricoAsta(TipoCarico.DISTRIBUITO_UNIFORME, valore_sx=3.0)],
                rilascio_i=_rigido(),
                rilascio_j=_rigido(),
            ),
            AstaTelaio(
                id=3,
                nodo_i=4,
                nodo_j=3,
                tipo=TipoAsta.PILASTRO,
                sezione=sez,
                carichi=[],
                rilascio_i=_rigido(),
                rilascio_j=_rigido(),
            ),
        ]
        piani = [PianoTelaio(id_piano=1, quota=400.0)]
        return ModelloTelaio(nome="CoppiaGov", nodi=nodi, aste=aste, piani=piani, zona_sismica=zona)

    def test_M_gov_e_N_gov_sono_float(self):
        """M_gov_i, N_gov_i ecc. sono float (non None)."""
        modello = self._portale()
        ris = calcola_tutte_le_combinazioni(modello)

        for id_asta, inv in ris.inviluppo.items():
            # Accediamo tramite il metodo M_gov() che ritorna (M, N, combo)
            for sezione in range(3):
                M, N, combo = inv.M_gov(sezione)
                assert isinstance(M, float), f"Asta {id_asta} sez {sezione}: M_gov non float"
                assert isinstance(N, float), f"Asta {id_asta} sez {sezione}: N_gov non float"

    def test_combo_gov_e_stringa(self):
        """combo_gov è una stringa (id caso o vuoto)."""
        modello = self._portale()
        ris = calcola_tutte_le_combinazioni(modello)
        for id_asta, inv in ris.inviluppo.items():
            assert isinstance(inv.combo_gov_i, str)
            assert isinstance(inv.combo_gov_m, str)
            assert isinstance(inv.combo_gov_j, str)
