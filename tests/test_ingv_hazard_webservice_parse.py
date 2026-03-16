"""Test per parsing payload webservice INGV (rami privati)."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pytest

from src.codes.ntc2018 import ingv_hazard
from src.codes.ntc2018.spectrum_paste_service import Ntc2018HazardRow


@pytest.fixture
def parse_func() -> Callable[[dict[str, list[float]], int], Ntc2018HazardRow]:
    raw = getattr(ingv_hazard, "_parse_ingv_response")
    return cast(Callable[[dict[str, list[float]], int], Ntc2018HazardRow], raw)


def test_parse_ingv_response_standard_keys(
    parse_func: Callable[[dict[str, list[float]], int], Ntc2018HazardRow]
) -> None:
    data: dict[str, list[float]] = {
        "tr": [50, 201, 475],
        "ag": [0.08, 0.16, 0.24],
        "fo": [2.2, 2.3, 2.4],
        "tc": [0.25, 0.30, 0.35],
    }

    row = parse_func(data, 475)

    assert row.tr_years == 475.0
    assert abs(row.ag_g - 0.24) < 1e-12
    assert abs(row.f0 - 2.4) < 1e-12
    assert abs(row.tc_star_s - 0.35) < 1e-12


def test_parse_ingv_response_alternative_keys(
    parse_func: Callable[[dict[str, list[float]], int], Ntc2018HazardRow]
) -> None:
    data: dict[str, list[float]] = {
        "TR": [50, 201, 475],
        "ag": [0.08, 0.16, 0.24],
        "f0": [2.2, 2.3, 2.4],
        "TC": [0.25, 0.30, 0.35],
    }

    row = parse_func(data, 205)

    # nearest su TR -> 201
    assert row.tr_years == 205.0
    assert abs(row.ag_g - 0.16) < 1e-12
    assert abs(row.f0 - 2.3) < 1e-12
    assert abs(row.tc_star_s - 0.30) < 1e-12


def test_parse_ingv_response_missing_tr_raises(
    parse_func: Callable[[dict[str, list[float]], int], Ntc2018HazardRow]
) -> None:
    with pytest.raises(ValueError, match="campo 'tr' mancante"):
        parse_func({"ag": [0.2], "fo": [2.3], "tc": [0.3]}, 475)


def test_parse_ingv_response_malformed_raises(
    parse_func: Callable[[dict[str, list[float]], int], Ntc2018HazardRow]
) -> None:
    bad: dict[str, list[float]] = {
        "tr": [50, 201],
        "ag": [0.08],
        "fo": [2.2, 2.3],
        "tc": [0.25, 0.30],
    }
    with pytest.raises(ValueError, match="formato inatteso"):
        parse_func(bad, 201)
