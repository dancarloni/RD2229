from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import Apertura


@dataclass
class ApertureEditorState:
    """Backend state for graphical aperture editor (geometry-only layer).

    UI widgets can consume this state and operations to implement a visual editor
    without duplicating geometric logic.
    """

    aperture: List[Apertura]

    @classmethod
    def empty(cls) -> "ApertureEditorState":
        return cls(aperture=[])

    def add_apertura(self, apertura: Apertura) -> None:
        self.remove_apertura(apertura.id)
        self.aperture.append(apertura)

    def remove_apertura(self, apertura_id: str) -> None:
        self.aperture = [a for a in self.aperture if a.id != apertura_id]

    def get_apertura(self, apertura_id: str) -> Optional[Apertura]:
        for a in self.aperture:
            if a.id == apertura_id:
                return a
        return None

    def move_apertura(self, apertura_id: str, x: float, y: float) -> bool:
        a = self.get_apertura(apertura_id)
        if a is None:
            return False
        a.posizione["x"] = float(x)
        a.posizione["y"] = float(y)
        return True

    def resize_apertura(self, apertura_id: str, h: float, b: float) -> bool:
        a = self.get_apertura(apertura_id)
        if a is None:
            return False
        a.dimensioni["h"] = float(h)
        a.dimensioni["b"] = float(b)
        return True

    def to_canvas_items(self) -> List[Dict[str, float | str]]:
        """Export items for canvas rendering (Qt/SVG/other frontends)."""
        out: List[Dict[str, float | str]] = []
        for a in self.aperture:
            dims = a.normalized_dimensions()
            out.append(
                {
                    "id": a.id,
                    "x": float(a.posizione.get("x", 0.0)),
                    "y": float(a.posizione.get("y", 0.0)),
                    "h": float(dims.get("h", 0.0)),
                    "b": float(dims.get("b", 0.0)),
                    "stato": a.stato,
                    "tipo": a.tipo,
                }
            )
        return out
