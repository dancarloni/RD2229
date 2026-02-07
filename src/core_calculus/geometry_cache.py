from __future__ import annotations

from functools import lru_cache
from typing import Tuple


@lru_cache(maxsize=1024)
def section_inertia(width: float, height: float, thickness: float = 0.0) -> Tuple[float, float, float]:
    """Compute area and second moment of inertia for a rectangular section.

    Returns:
        (area, I_x, I_y)
    """
    if thickness <= 0:
        area = width * height
        I_x = (width * height**3) / 12.0
        I_y = (height * width**3) / 12.0
    else:
        # hollow rectangle approximation: outer minus inner
        area = width * height - (width - 2 * thickness) * (height - 2 * thickness)
        I_x = (width * height**3 - (width - 2 * thickness) * (height - 2 * thickness) ** 3) / 12.0
        I_y = (height * width**3 - (height - 2 * thickness) * (width - 2 * thickness) ** 3) / 12.0
    return area, I_x, I_y
