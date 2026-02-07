from __future__ import annotations

from typing import Iterable, Tuple


def linear_interpolate(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if x1 == x0:
        raise ValueError("Interpolazione non definita per x0 == x1")
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def linear_interpolate_table(x: float, table: Iterable[Tuple[float, float]]) -> float:
    """Interpolazione lineare su tabella ordinata per x."""
    items = sorted(table, key=lambda t: t[0])
    if len(items) < 2:
        raise ValueError("Tabella insufficiente per interpolazione")

    if x <= items[0][0]:
        return items[0][1]
    if x >= items[-1][0]:
        return items[-1][1]

    for (x0, y0), (x1, y1) in zip(items, items[1:]):
        if x0 <= x <= x1:
            return linear_interpolate(x, x0, x1, y0, y1)

    raise ValueError("Valore x fuori dalla tabella")
