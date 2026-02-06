from app.ui.rebar_calculator import calculate_rebar_total
import math


def test_calculate_rebar_total_simple():
    counts = {8: 2, 12: 1}
    total = calculate_rebar_total(counts)
    expected = 2 * (math.pi * ((8 / 10.0) ** 2) / 4.0) + 1 * (math.pi * ((12 / 10.0) ** 2) / 4.0)
    assert abs(total - expected) < 1e-9


def test_calculate_rebar_total_with_invalid_values():
    counts = {8: "3", 10: "bad", 25: None}
    total = calculate_rebar_total(counts)
    # 8->3 bars, 10->0, 25->0
    expected = 3 * (math.pi * ((8 / 10.0) ** 2) / 4.0)
    assert abs(total - expected) < 1e-9
