from __future__ import annotations

from typing import Dict, Any, Optional

from src.methods.protocols import VerificationMethod


class VerificationEngine:
    """Orchestrates verification computations using pluggable methods."""

    def __init__(self, method: VerificationMethod):
        self.method = method

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Validate inputs minimally
        if "width" not in inputs or "height" not in inputs:
            raise ValueError("Input must contain 'width' and 'height'")
        return self.method.compute(inputs)
