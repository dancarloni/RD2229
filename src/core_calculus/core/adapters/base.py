"""
Base adapter interface for normative verification.

Each norm adapter implements:
- applicability(): whether this adapter can verify a given element
- verify(): perform the verification and return a CalcOutput
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field

from src.core_calculus.contracts import CalcInput, CalcOutput, NormReference


@dataclass
class EligibilityResult:
    """Result of checking whether an adapter is applicable."""

    eligible: bool
    reasons: list[str] = field(default_factory=list)
    norm_references: list[NormReference] = field(default_factory=list)


class NormAdapter(abc.ABC):
    """Abstract base for norm-specific verification adapters."""

    @property
    @abc.abstractmethod
    def norm_code(self) -> str:
        """Norm code identifier (e.g., 'NTC2018', 'RD2229')."""
        ...

    @property
    @abc.abstractmethod
    def description_it(self) -> str:
        """Italian description of this adapter."""
        ...

    @abc.abstractmethod
    def applicability(self, calc_input: CalcInput) -> EligibilityResult:
        """Check if this adapter is applicable to the given input."""
        ...

    @abc.abstractmethod
    def verify(self, calc_input: CalcInput) -> CalcOutput:
        """Perform verification and return output."""
        ...
