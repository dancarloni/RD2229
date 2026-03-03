"""
Element role classification policy.

Classifies structural elements as PRIMARY or SECONDARY based on
configurable rules per NTC2018 §7.2.3 and EC8 §4.2.2.
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field
from typing import Any

from src.core_calculus.contracts import ElementRole, NormReference


@dataclass
class ClassificationRule:
    """A single classification rule with rationale."""
    rule_id: str
    description_it: str
    condition: str  # human-readable condition description
    assigned_role: ElementRole = ElementRole.UNDETERMINED
    norm_reference: NormReference | None = None
    priority: int = 0  # higher priority rules override lower ones


@dataclass
class ClassificationResult:
    """Result of classifying an element."""
    role: ElementRole
    rationale: list[str] = field(default_factory=list)
    applied_rules: list[str] = field(default_factory=list)
    norm_references: list[NormReference] = field(default_factory=list)


_DEFAULT_RULES: list[ClassificationRule] = [
    ClassificationRule(
        rule_id="WALL_SECONDARY",
        description_it="Muri di tamponamento e tramezze sono elementi secondari",
        condition="element_type in ('wall', 'partition', 'infill')",
        assigned_role=ElementRole.SECONDARY,
        norm_reference=NormReference(
            norm_code="NTC2018", chapter="7.2", paragraph="7.2.3",
            description_it="Elementi secondari: definizione e criteri",
        ),
        priority=10,
    ),
    ClassificationRule(
        rule_id="BEAM_PRIMARY",
        description_it="Travi del telaio principale sono elementi primari",
        condition="element_type in ('beam', 'column', 'pillar')",
        assigned_role=ElementRole.PRIMARY,
        norm_reference=NormReference(
            norm_code="NTC2018", chapter="7.2", paragraph="7.2.3",
            description_it="Elementi primari: travi e pilastri del telaio",
        ),
        priority=10,
    ),
    ClassificationRule(
        rule_id="FOUNDATION_PRIMARY",
        description_it="Elementi di fondazione sono elementi primari",
        condition="element_type in ('foundation', 'footing', 'pile')",
        assigned_role=ElementRole.PRIMARY,
        norm_reference=NormReference(
            norm_code="NTC2018", chapter="7.2", paragraph="7.2.5",
            description_it="Fondazioni: verifiche specifiche",
        ),
        priority=10,
    ),
]


def classify_element(
    element_type: str,
    properties: dict[str, Any] | None = None,
    custom_rules: list[ClassificationRule] | None = None,
) -> ClassificationResult:
    """Classify an element as primary/secondary.

    Args:
        element_type: Type of structural element (e.g., 'beam', 'wall').
        properties: Optional additional properties for rule evaluation.
        custom_rules: Optional custom rules (overrides defaults).

    Returns:
        ClassificationResult with role, rationale, and norm references.
    """
    rules = custom_rules if custom_rules is not None else _DEFAULT_RULES
    props = properties or {}
    et = element_type.lower().strip()

    matched_rules: list[ClassificationRule] = []
    for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
        # Simple keyword matching for element types
        condition_types = _extract_types_from_condition(rule.condition)
        if et in condition_types:
            matched_rules.append(rule)

    if not matched_rules:
        return ClassificationResult(
            role=ElementRole.UNDETERMINED,
            rationale=[f"Nessuna regola applicabile per element_type='{element_type}'"],
            applied_rules=[],
            norm_references=[],
        )

    best = matched_rules[0]
    refs = [r.norm_reference for r in matched_rules if r.norm_reference]
    return ClassificationResult(
        role=best.assigned_role,
        rationale=[best.description_it],
        applied_rules=[r.rule_id for r in matched_rules],
        norm_references=refs,
    )


def _extract_types_from_condition(condition: str) -> list[str]:
    """Extract element type keywords from a condition string."""
    match = re.search(r"\(([^)]+)\)", condition)
    if match:
        items = match.group(1).split(",")
        return [item.strip().strip("'\"") for item in items]
    return []
