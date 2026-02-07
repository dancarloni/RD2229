from typing import Any, Dict, Protocol


class VerificationMethod(Protocol):
    """Protocol defining the verification method interface."""

    name: str

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]: ...
