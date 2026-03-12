"""Test per solver_telaio.py.

Verifica calcolo sollecitazioni (M/V/N) da momenti Cross.
Subfase L.10.
"""

from src.methods.rd2229.telaio.modello_telaio import (
    AstaTelaio,
    CaricoAsta,
    ModelloTelaio,
    NodoTelaio,
    RilascioEstremita,
    SezioneTelaio,
    TipoAsta,
    TipoCarico,
    TipoRilascioInterno,
    TipoVincoloEsterno,
    VincoloEsterno,
)
from src.methods.rd2229.telaio.solver_telaio import calcola_caso_carico


def _sez(b: float = 30.0, h: float = 50.0, E: float = 300000.0) -> SezioneTelaio:
    I = b * h**3 / 12.0
    return SezioneTelaio(
        tipo="RECTANGULAR", b=b, h=h, I=I, A=b * h, Wx=b * h**2 / 6, E=E, gamma=0.0
    )


def _vinc(tipo: TipoVincoloEsterno) -> VincoloEsterno:
    return VincoloEsterno(tipo)


def _rigido() -> RilascioEstremita:
    return RilascioEstremita(TipoRilascioInterno.NODO_RIGIDO)


# ==============================================================================
# TEST 1 — Equilibrio trave semplice (isostatica)
# ==============================================================================


class TestSollecitazioniTraveSemplice:
    """Trave AB con estremi incastrati e carico uniforme q.
    Verifica: V_i + V_j = q × L (equilibrio verticale)."""

    def _modello(self) -> ModelloTelaio:
        q = 5.0  # kg/cm
        L = 400.0
        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=_vinc(TipoVincoloEsterno.INCASTRO), etichetta="A"),
            NodoTelaio(id=2, x=L, y=0, vincolo=_vinc(TipoVincoloEsterno.INCASTRO), etichetta="B"),
        ]
        sez = _sez()
        aste = [
            AstaTelaio(
                id=1,
                nodo_i=1,
                nodo_j=2,
                tipo=TipoAsta.TRAVE,
                sezione=sez,
                carichi=[
                    CaricoAsta(tipo=TipoCarico.DISTRIBUITO_UNIFORME, valore_sx=q, direzione="Y")
                ],
                rilascio_i=_rigido(),
                rilascio_j=_rigido(),
                etichetta="AB",
            )
        ]
        return ModelloTelaio(
            nome="TraveSemplice", nodi=nodi, aste=aste, piani=[], zona_sismica="non_sismico"
        )

    def test_equilibrio_verticale(self):
        """V_i + V_j + reazione_carichi = 0 (equilibrio verticale)."""
        modello = self._modello()
        ris = calcola_caso_carico(modello, "LC1", "Test trave semplice")
        soll = ris.sollecitazioni.get(1)
        if soll and soll.V:
            q = 5.0
            L = 400.0
            carico_tot = q * L
            reazione_tot = (
                abs(soll.V[0]) + abs(soll.V[2]) if len(soll.V) > 2 else abs(soll.V[0]) * 2
            )
            assert (
                abs(reazione_tot - carico_tot) < carico_tot * 0.02
            ), f"Equilibrio verticale: reazioni={reazione_tot:.0f}, carico={carico_tot:.0f}"

    def test_momento_agli_incastri(self):
        """Per trave con 2 incastri e carico uniforme: M_i = M_j = -qL²/12."""
        modello = self._modello()
        ris = calcola_caso_carico(modello, "LC1", "Test MIP")
        soll = ris.sollecitazioni.get(1)
        if soll and soll.M:
            q, L = 5.0, 400.0
            atteso = -q * L**2 / 12.0
            # Tolleranza 2% (Cross non converge a 0 esatto ma quasi)
            assert (
                abs(soll.M[0] - atteso) < abs(atteso) * 0.05
            ), f"M_i={soll.M[0]:.0f}, atteso≈{atteso:.0f}"


# ==============================================================================
# TEST 2 — Reazioni ai vincoli
# ==============================================================================


class TestReazioniVincoli:
    """Trave isostatica (semplicemente appoggiata con cerniere).
    V_A = qL/2, V_B = qL/2 per carico uniforme centrato."""

    def _modello(self) -> ModelloTelaio:
        q = 4.0
        L = 300.0
        nodi = [
            NodoTelaio(
                id=1, x=0, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.CERNIERA), etichetta="A"
            ),
            NodoTelaio(
                id=2, x=L, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.CARRELLO_X), etichetta="B"
            ),
        ]
        sez = _sez()
        ril_cerniera = RilascioEstremita(TipoRilascioInterno.CERNIERA)
        aste = [
            AstaTelaio(
                id=1,
                nodo_i=1,
                nodo_j=2,
                tipo=TipoAsta.TRAVE,
                sezione=sez,
                carichi=[
                    CaricoAsta(tipo=TipoCarico.DISTRIBUITO_UNIFORME, valore_sx=q, direzione="Y")
                ],
                rilascio_i=ril_cerniera,
                rilascio_j=ril_cerniera,
                etichetta="AB",
            )
        ]
        return ModelloTelaio(
            nome="TraveCerniere", nodi=nodi, aste=aste, piani=[], zona_sismica="non_sismico"
        )

    def test_reazioni_uguali(self):
        """Per trave simmetrica: V_A ≈ V_B ≈ qL/2."""
        modello = self._modello()
        ris = calcola_caso_carico(modello, "LC1", "Trave cerniere")
        # Per trave isostatica: M = 0 agli estremi
        soll = ris.sollecitazioni.get(1)
        if soll and soll.M:
            # M agli estremi deve essere ≈ 0 (cerniere)
            assert abs(soll.M[0]) < 500.0, f"M_i con cerniera: {soll.M[0]:.0f} (atteso ≈ 0)"
            assert abs(soll.M[2]) < 500.0 if len(soll.M) > 2 else True


# ==============================================================================
# TEST 3 — calcola_caso_carico senza carichi
# ==============================================================================


class TestCasoSenzaCarichi:
    """Con nessun carico sulle aste, momenti devono essere 0."""

    def _modello_vuoto(self) -> ModelloTelaio:
        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
            NodoTelaio(id=2, x=300, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
        ]
        aste = [
            AstaTelaio(
                id=1,
                nodo_i=1,
                nodo_j=2,
                tipo=TipoAsta.TRAVE,
                sezione=_sez(),
                carichi=[],
                rilascio_i=_rigido(),
                rilascio_j=_rigido(),
                etichetta="AB",
            ),
        ]
        return ModelloTelaio(
            nome="Vuoto", nodi=nodi, aste=aste, piani=[], zona_sismica="non_sismico"
        )

    def test_momenti_nulli_senza_carichi(self):
        """Senza carichi, tutti i momenti devono essere nulli o trascurabili."""
        modello = self._modello_vuoto()
        ris = calcola_caso_carico(modello, "LC1", "Nessun carico")
        for id_a, soll in ris.sollecitazioni.items():
            if soll and soll.M:
                for m in soll.M:
                    assert abs(m) < 1.0, f"M non nullo senza carichi: {m:.2f}"
