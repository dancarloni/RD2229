"""Test modulo ingv_hazard — lettura CSV griglia INGV e interpolazione.

Copre:
  - _trova_tr_bracket: logica di bracket (senza CSV)
  - _interpola_log_lineare_tr: interpolazione log-lineare (senza CSV)
  - get_hazard_params_csv: lettura da griglia reale (~10.751 punti)
  - profilo_spettrale_completo: curva spettrale completa (senza CSV)

Coordinate di test:
  Norcia     lat=42.8,  lon=13.1   — alta sismicita'
  Calabria   lat=38.0,  lon=15.5   — alta sismicita'
  Sardegna   lat=40.7,  lon=8.6    — bassa sismicita'

Il CSV contiene ag in [m/s^2]; il modulo converte automaticamente in [g].
I test verificano coerenza fisica (range plausibili) e monotonia con TR.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from src.codes.ntc2018.ingv_hazard import (
    _TR_DISPONIBILI,
    _interpola_log_lineare_tr,
    _invalida_cache_csv,
    _trova_tr_bracket,
    _valida_coordinate,
    get_hazard_params_csv,
)
from src.codes.ntc2018.spectrum import (
    CategoriaSuolo,
    CategoriaTopografica,
    profilo_spettrale_completo,
    spettro_da_hazard_row,
)

CSV_PATH = Path(__file__).parent.parent / "data" / "seismic" / "griglia_ingv.csv"
CSV_DISPONIBILE = CSV_PATH.exists()

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def pulisci_cache():
    """Pulisce la cache CSV prima di ogni test per evitare interferenze."""
    _invalida_cache_csv()
    yield
    _invalida_cache_csv()


# ---------------------------------------------------------------------------
# _trova_tr_bracket
# ---------------------------------------------------------------------------


class TestTrovaTrBracket:
    def test_tr_esatto_nella_griglia(self):
        for tr in _TR_DISPONIBILI:
            tr1, tr2 = _trova_tr_bracket(tr)
            assert tr1 == tr2 == tr

    def test_tr_tra_due_valori(self):
        tr1, tr2 = _trova_tr_bracket(300)
        assert tr1 == 201
        assert tr2 == 475

    def test_tr_tra_50_e_72(self):
        tr1, tr2 = _trova_tr_bracket(60)
        assert tr1 == 50
        assert tr2 == 72

    def test_tr_sotto_minimo_clamp(self):
        tr1, tr2 = _trova_tr_bracket(10)
        assert tr1 == tr2 == _TR_DISPONIBILI[0]

    def test_tr_sopra_massimo_clamp(self):
        tr1, tr2 = _trova_tr_bracket(5000)
        assert tr1 == tr2 == _TR_DISPONIBILI[-1]

    def test_tr_495_tra_475_e_975(self):
        tr1, tr2 = _trova_tr_bracket(495)
        assert tr1 == 475
        assert tr2 == 975


# ---------------------------------------------------------------------------
# _interpola_log_lineare_tr
# ---------------------------------------------------------------------------


class TestInterpolaLogLineareTR:
    def test_tr_esattamente_tr1_ritorna_valori_tr1(self):
        # alpha=0 -> risultato = valori TR1
        ag, f0, tc = _interpola_log_lineare_tr(475, 475, 975, 0.168, 2.40, 0.33, 0.25, 2.35, 0.36)
        assert abs(ag - 0.168) < 1e-9
        assert abs(f0 - 2.40) < 1e-9
        assert abs(tc - 0.33) < 1e-9

    def test_tr_esattamente_tr2_ritorna_valori_tr2(self):
        # alpha=1 -> risultato = valori TR2
        ag, f0, tc = _interpola_log_lineare_tr(975, 475, 975, 0.168, 2.40, 0.33, 0.25, 2.35, 0.36)
        assert abs(ag - 0.25) < 1e-9

    def test_monotonia_ag_crescente_con_tr(self):
        # ag deve crescere con TR (piu' lungo ritorno = piu' alta intensita')
        ag300, _, _ = _interpola_log_lineare_tr(300, 201, 475, 0.12, 2.4, 0.30, 0.20, 2.4, 0.33)
        assert 0.12 < ag300 < 0.20

    def test_interpolazione_log_lineare_simetria(self):
        # TR=sqrt(tr1*tr2) => alpha=0.5 => ag = sqrt(ag1*ag2)
        tr1, tr2 = 100, 1000
        tr_mid = int(round(math.sqrt(tr1 * tr2)))  # ~316
        ag1, ag2 = 0.10, 0.40
        ag_mid, _, _ = _interpola_log_lineare_tr(
            int(math.sqrt(tr1 * tr2)), tr1, tr2, ag1, 2.4, 0.3, ag2, 2.4, 0.3
        )
        assert abs(ag_mid - math.sqrt(ag1 * ag2)) < 0.01


# ---------------------------------------------------------------------------
# _valida_coordinate
# ---------------------------------------------------------------------------


class TestValidaCoordinate:
    def test_coordinate_valide_italia(self):
        _valida_coordinate(41.9, 12.5)  # Roma

    def test_latitudine_fuori_range(self):
        with pytest.raises(ValueError, match="Latitudine"):
            _valida_coordinate(50.0, 12.0)

    def test_longitudine_fuori_range(self):
        with pytest.raises(ValueError, match="Longitudine"):
            _valida_coordinate(41.9, 3.0)

    def test_bordi_accettati(self):
        _valida_coordinate(35.0, 6.0)
        _valida_coordinate(48.0, 19.0)


# ---------------------------------------------------------------------------
# get_hazard_params_csv — test con CSV reale
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not CSV_DISPONIBILE, reason="CSV griglia INGV non disponibile")
class TestGetHazardParamsCsv:
    """Test con la griglia reale (data/seismic/griglia_ingv.csv)."""

    def test_norcia_tr475_range_fisici(self):
        """Norcia (alta sismicita'): ag_g > 0.20g a TR=475."""
        row = get_hazard_params_csv(42.8, 13.1, 475, CSV_PATH)
        assert row.ag_g > 0.20, f"ag_g={row.ag_g:.4f}g troppo basso per Norcia"
        assert 2.0 < row.f0 < 3.5, f"F0={row.f0:.3f} fuori range"
        assert 0.1 < row.tc_star_s < 0.7, f"TC*={row.tc_star_s:.3f}s fuori range"

    def test_sardegna_tr475_bassa_sismicita(self):
        """Sardegna (bassa sismicita'): ag_g < 0.10g a TR=475."""
        row = get_hazard_params_csv(40.7, 8.6, 475, CSV_PATH)
        assert row.ag_g < 0.10, f"ag_g={row.ag_g:.4f}g troppo alto per Sardegna"
        assert row.ag_g > 0.0

    def test_calabria_tr475_alta_sismicita(self):
        """Calabria (alta sismicita'): ag_g > 0.20g a TR=475."""
        row = get_hazard_params_csv(38.0, 15.5, 475, CSV_PATH)
        assert row.ag_g > 0.20

    def test_monotonia_ag_cresce_con_tr(self):
        """ag deve aumentare al crescere del TR."""
        lat, lon = 42.8, 13.1  # Norcia
        valori = [get_hazard_params_csv(lat, lon, tr, CSV_PATH).ag_g for tr in [50, 201, 475, 975]]
        for i in range(len(valori) - 1):
            assert (
                valori[i] < valori[i + 1]
            ), f"ag non cresce: TR=... ag={valori[i]:.4f} > {valori[i+1]:.4f}"

    def test_tr_475_nella_griglia(self):
        """TR=475 e' nella griglia: nessuna interpolazione TR."""
        row = get_hazard_params_csv(41.9, 12.5, 475, CSV_PATH)
        assert row.tr_years == 475.0
        assert row.ag_g > 0.0

    def test_tr_300_interpolato(self):
        """TR=300 non e' nella griglia: interpolato tra 201 e 475."""
        lat, lon = 42.8, 13.1
        row200 = get_hazard_params_csv(lat, lon, 201, CSV_PATH)
        row300 = get_hazard_params_csv(lat, lon, 300, CSV_PATH)
        row475 = get_hazard_params_csv(lat, lon, 475, CSV_PATH)
        assert row200.ag_g < row300.ag_g < row475.ag_g

    def test_label_formato_corretto(self):
        row = get_hazard_params_csv(41.9, 12.5, 475, CSV_PATH)
        assert "TR=475" in row.limit_state_label

    def test_coordinate_fuori_italia_errore(self):
        with pytest.raises(ValueError):
            get_hazard_params_csv(50.0, 12.0, 475, CSV_PATH)

    def test_csv_non_esistente_errore(self):
        with pytest.raises(FileNotFoundError):
            get_hazard_params_csv(41.9, 12.5, 475, Path("/nonexistente/griglia.csv"))

    def test_f0_range_plausibile(self):
        """F0 tipicamente tra 2.2 e 3.0 per l'Italia."""
        row = get_hazard_params_csv(42.0, 14.0, 475, CSV_PATH)
        assert 2.0 <= row.f0 <= 3.5

    def test_tc_star_range_plausibile(self):
        """TC* tipicamente tra 0.2 e 0.5s per l'Italia."""
        row = get_hazard_params_csv(42.0, 14.0, 475, CSV_PATH)
        assert 0.1 <= row.tc_star_s <= 0.8

    def test_integrazione_spettro_da_hazard_row(self):
        """Verifica che l'output di get_hazard_params_csv sia compatibile con spettro_da_hazard_row."""
        row = get_hazard_params_csv(42.8, 13.1, 475, CSV_PATH)
        risultato = spettro_da_hazard_row(row, CategoriaSuolo.B, CategoriaTopografica.T1)
        assert risultato["SS"] >= 1.0
        assert risultato["TB"] < risultato["TC"] < risultato["TD"]
        se_tb = risultato["Se_func"](risultato["TB"])
        assert se_tb > 0.0


# ---------------------------------------------------------------------------
# profilo_spettrale_completo
# ---------------------------------------------------------------------------


class TestProfiloSpettraleCompleto:
    """Test per profilo_spettrale_completo() in spectrum.py."""

    # Parametri Roma cat B, SLV
    _AG = 0.168
    _F0 = 2.398
    _SS = 1.073
    _ST = 1.0
    _TB = 0.150
    _TC = 0.450
    _TD = 2.272

    def _profilo(self, T_max=4.0, n=100):
        return profilo_spettrale_completo(
            self._AG,
            self._F0,
            self._SS,
            self._ST,
            self._TB,
            self._TC,
            self._TD,
            xi=5.0,
            T_max=T_max,
            n_punti=n,
        )

    def test_ritorna_lista_tuple(self):
        punti = self._profilo()
        assert isinstance(punti, list)
        assert all(isinstance(p, tuple) and len(p) == 2 for p in punti)

    def test_t_ordinato_crescente(self):
        punti = self._profilo()
        ts = [p[0] for p in punti]
        assert ts == sorted(ts)

    def test_primo_punto_t_zero(self):
        punti = self._profilo()
        assert punti[0][0] == 0.0

    def test_ultimo_punto_t_max(self):
        punti = self._profilo(T_max=4.0)
        assert abs(punti[-1][0] - 4.0) < 1e-6

    def test_punti_speciali_presenti(self):
        """TB, TC, TD devono essere punti esatti nel profilo."""
        punti = self._profilo()
        ts = {round(p[0], 6) for p in punti}
        assert round(self._TB, 6) in ts, f"TB={self._TB} non nel profilo"
        assert round(self._TC, 6) in ts, f"TC={self._TC} non nel profilo"
        assert round(self._TD, 6) in ts, f"TD={self._TD} non nel profilo"

    def test_plateau_tb_tc(self):
        """Tra TB e TC, Se e' costante (plateau)."""
        punti = self._profilo()
        se_tb = next(se for t, se in punti if abs(t - self._TB) < 1e-6)
        se_tc = next(se for t, se in punti if abs(t - self._TC) < 1e-6)
        assert abs(se_tb - se_tc) / se_tb < 0.01, "Il plateau TB-TC non e' piatto"

    def test_ramo_discendente_tc_td(self):
        """Tra TC e TD, Se decresce (1/T)."""
        punti_zona = [(t, se) for t, se in self._profilo() if self._TC <= t <= self._TD]
        ses = [se for _, se in punti_zona]
        assert ses == sorted(ses, reverse=True), "Se non decresce tra TC e TD"

    def test_ramo_discendente_oltre_td(self):
        """Oltre TD, Se decresce (1/T^2) — quindi piu' veloce del ramo TC-TD."""
        punti = self._profilo(T_max=6.0)
        ses_td_4 = [se for t, se in punti if self._TD <= t <= 4.0]
        assert ses_td_4 == sorted(ses_td_4, reverse=True)

    def test_n_punti_minimo(self):
        punti = self._profilo(n=20)
        assert len(punti) >= 5  # almeno T=0, TB, TC, TD, T_max

    def test_se_positivo_ovunque(self):
        punti = self._profilo()
        assert all(se > 0 for _, se in punti)

    def test_t_max_default_almeno_4s(self):
        """T_max default deve essere almeno 4 secondi."""
        punti = self._profilo(T_max=None)
        assert punti[-1][0] >= 4.0

    def test_compatibilita_con_spettro_elastico(self):
        """Valori del profilo devono coincidere con spettro_elastico per T campione."""
        from src.codes.ntc2018.spectrum import spettro_elastico

        punti = self._profilo()
        for t, se in punti[:5]:
            se_ref = spettro_elastico(
                self._AG, self._F0, self._SS, self._ST, self._TB, self._TC, self._TD, 5.0, t
            )
            assert abs(se - se_ref) < 1e-10
