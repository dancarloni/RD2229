from typing import Any, Protocol


class VerificationMethod(Protocol):
    """Protocol defining the verification method interface."""

    name: str

    def compute(self, inputs: dict[str, Any]) -> dict[str, Any]: ...
