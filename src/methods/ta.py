from __future__ import annotations

from typing import Any


class TangentialAreaMethod:
    name = "TA"

    def compute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Minimal example computation: neutral axis depth for rectangular beam under given M
        width = float(inputs.get("width", 1.0))
        height = float(inputs.get("height", 1.0))
        M = float(inputs.get("M", 0.0))
        # NA depth approximation (not a real formula, placeholder)
        na = height / 2.0 + M / (width * height**2)
        return {"NA_depth": na}
