"""Fire curves – curva di incendio standard ISO 834.

Riferimento: ISO 834-1:1999 (standard fire exposure curve)
Formula pubblica:  T(t) = 20 + 345 * log10(8*t + 1)
dove t è il tempo in minuti e T è la temperatura in °C.

Questa formula è ampiamente riportata in letteratura tecnica pubblica,
incluso l'Eurocodice EN 1991-1-2 e il NTC 2018.
"""

from __future__ import annotations

import math


def iso834_temperature(t_min: float) -> float:
    """Temperatura [°C] della curva di incendio standard ISO 834 al tempo t.

    Args:
        t_min: Tempo in minuti (>= 0).

    Returns:
        Temperatura in °C secondo la curva ISO 834.

    Raises:
        ValueError: se ``t_min`` è negativo.
    """
    if t_min < 0:
        raise ValueError(f"t_min deve essere >= 0, ricevuto: {t_min}")
    return 20.0 + 345.0 * math.log10(8.0 * t_min + 1.0)


def iso834_profile(
    t_max_min: float,
    n_points: int = 50,
) -> list[tuple[float, float]]:
    """Profilo temporale della curva ISO 834.

    Args:
        t_max_min: Tempo massimo [min].
        n_points: Numero di punti del profilo.

    Returns:
        Lista di coppie ``(t_min, T_celsius)``.
    """
    if n_points < 2:
        n_points = 2
    dt = t_max_min / (n_points - 1)
    return [(i * dt, iso834_temperature(i * dt)) for i in range(n_points)]
