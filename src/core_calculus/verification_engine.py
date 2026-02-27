from __future__ import annotations

from typing import Any

from src.methods.protocols import VerificationMethod


class VerificationEngine:
    """Orchestrates verification computations using pluggable methods."""

    def __init__(self, method: VerificationMethod):
        self.method = method

    def compute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        # Validate inputs minimally
        if "width" not in inputs or "height" not in inputs:
            raise ValueError("Input must contain 'width' and 'height'")
        return self.method.compute(inputs)
