from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class CanvasTransform:
    """Trasformazione per mappare coordinate reali su canvas Tkinter."""

    scale: float
    offset_x: float
    offset_y: float

    def to_canvas(self, x: float, y: float, height: float) -> Tuple[float, float]:
        """Converte coordinate con origine in basso a sinistra (x,y) al canvas."""
        cx = self.offset_x + x * self.scale
        cy = self.offset_y + (height - y) * self.scale
        return cx, cy


def compute_transform(width: float, height: float, canvas_width: int, canvas_height: int, padding: int = 20) -> CanvasTransform:
    """Calcola il fattore di scala per adattare la sezione al canvas."""
    if width <= 0 or height <= 0:
        return CanvasTransform(scale=1.0, offset_x=padding, offset_y=padding)
    scale = min((canvas_width - 2 * padding) / width, (canvas_height - 2 * padding) / height)
    offset_x = (canvas_width - width * scale) / 2
    offset_y = (canvas_height - height * scale) / 2
    return CanvasTransform(scale=scale, offset_x=offset_x, offset_y=offset_y)
