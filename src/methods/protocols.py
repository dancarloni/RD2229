from typing import Protocol, Dict, Any


class VerificationMethod(Protocol):
    """Protocol defining the verification method interface."""

    name: str

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        ...
