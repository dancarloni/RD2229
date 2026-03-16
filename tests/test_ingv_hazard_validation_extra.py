"""Test aggiuntivi di validazione INGV e fallback sorgente.

Coprono rami non ancora verificati in test_ingv_hazard_csv.py:
- fallback automatico webservice -> CSV
- preferenza LOCAL_CSV senza chiamata al webservice
- selezione indice TR dal webservice
- edge cases di interpolazione e nearest-neighbor
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import pytest

from src.codes.ntc2018 import ingv_hazard
from src.codes.ntc2018.ingv_hazard import HazardSource, get_hazard_params_site
from src.codes.ntc2018.spectrum_paste_service import Ntc2018HazardRow


@pytest.fixture
def sample_row() -> Ntc2018HazardRow:
    return Ntc2018HazardRow(
        limit_state_label="TR=475anni",
        tr_years=475.0,
        ag_g=0.22,
        f0=2.4,
        tc_star_s=0.33,
    )


def test_get_hazard_params_site_fallback_to_csv(
    monkeypatch: pytest.MonkeyPatch, sample_row: Ntc2018HazardRow
) -> None:
    """Se il webservice fallisce, deve essere usato il CSV locale."""

    def _raise_webservice(lat: float, lon: float, tr: int) -> Ntc2018HazardRow:
        del lat, lon, tr
        raise OSError("webservice non disponibile")

    def _fake_csv(lat: float, lon: float, tr: int, csv_path: Any = None) -> Ntc2018HazardRow:
        del lat, lon, tr, csv_path
        return sample_row

    monkeypatch.setattr(ingv_hazard, "get_hazard_params_ingv", _raise_webservice)
    monkeypatch.setattr(ingv_hazard, "get_hazard_params_csv", _fake_csv)

    row, source = get_hazard_params_site(42.8, 13.1, 475)

    assert source == HazardSource.LOCAL_CSV
    assert abs(row.ag_g - sample_row.ag_g) < 1e-12


def test_get_hazard_params_site_prefer_local_csv(
    monkeypatch: pytest.MonkeyPatch, sample_row: Ntc2018HazardRow
) -> None:
    """Con prefer=LOCAL_CSV il webservice non deve essere interrogato."""
    called = {"web": False, "csv": False}

    def _web_should_not_run(lat: float, lon: float, tr: int) -> Ntc2018HazardRow:
        del lat, lon, tr
        called["web"] = True
        raise AssertionError("Webservice non doveva essere chiamato")

    def _fake_csv(lat: float, lon: float, tr: int, csv_path: Any = None) -> Ntc2018HazardRow:
        del lat, lon, tr, csv_path
        called["csv"] = True
        return sample_row

    monkeypatch.setattr(ingv_hazard, "get_hazard_params_ingv", _web_should_not_run)
    monkeypatch.setattr(ingv_hazard, "get_hazard_params_csv", _fake_csv)

    row, source = get_hazard_params_site(42.8, 13.1, 475, prefer=HazardSource.LOCAL_CSV)

    assert source == HazardSource.LOCAL_CSV
    assert called["csv"] is True
    assert called["web"] is False
    assert row.tr_years == 475.0


def test_interpola_indice_tr_webservice_chooses_nearest() -> None:
    """La scelta indice TR dal payload webservice deve usare nearest."""
    trs: list[float] = [30, 50, 72, 101, 140, 201, 475, 975, 2475]
    pick_index_raw = getattr(ingv_hazard, "_interpola_indice_tr_webservice")
    pick_index = cast(
        Callable[[list[float], int], int],
        pick_index_raw,
    )

    idx_300 = pick_index(trs, 300)
    idx_960 = pick_index(trs, 960)

    assert trs[idx_300] == 201
    assert trs[idx_960] == 975


def test_interpola_log_lineare_handles_non_positive_with_linear_fallback() -> None:
    """Se un parametro e' non positivo, deve attivarsi fallback lineare."""
    value, _, _ = ingv_hazard._interpola_log_lineare_tr(  # pyright: ignore[reportPrivateUsage]
        TR=300,
        tr1=201,
        tr2=475,
        ag1=0.0,
        f0_1=2.2,
        tc1=0.30,
        ag2=0.20,
        f0_2=2.4,
        tc2=0.35,
    )
    assert 0.0 <= value <= 0.20


def test_cerca_punto_piu_vicino_selects_correct_row() -> None:
    """Nearest-neighbor deve selezionare il punto con distanza minima."""
    points: list[tuple[float, float, dict[str, str]]] = [
        (40.0, 10.0, {"T475ag": "1.962", "T475F0": "2.30", "T475Tc": "0.28"}),
        (42.8, 13.1, {"T475ag": "3.924", "T475F0": "2.45", "T475Tc": "0.33"}),
        (45.0, 12.0, {"T475ag": "2.943", "T475F0": "2.20", "T475Tc": "0.30"}),
    ]
    nearest_raw = getattr(ingv_hazard, "_cerca_punto_piu_vicino")
    nearest = cast(
        Callable[
            [float, float, int, list[tuple[float, float, dict[str, str]]]],
            tuple[float, float, float],
        ],
        nearest_raw,
    )

    ag_g, f0, tc = nearest(42.81, 13.09, 475, points)

    # 3.924 m/s² -> 0.4 g circa
    assert abs(ag_g - (3.924 / 9.81)) < 1e-8
    assert abs(f0 - 2.45) < 1e-12
    assert abs(tc - 0.33) < 1e-12


def test_get_hazard_params_site_with_real_csv_when_available() -> None:
    """Smoke test integrazione su CSV reale quando presente in repo."""
    csv_path = Path(__file__).parent.parent / "data" / "seismic" / "griglia_ingv.csv"
    if not csv_path.exists():
        pytest.skip("CSV griglia INGV non disponibile")

    row, source = get_hazard_params_site(
        41.9,
        12.5,
        475,
        prefer=HazardSource.LOCAL_CSV,
        csv_path=csv_path,
    )

    assert source == HazardSource.LOCAL_CSV
    assert row.ag_g > 0.0
    assert row.f0 > 0.0
    assert row.tc_star_s > 0.0
