"""
Core contracts for the verification module.
These are pure domain types with NO GUI dependencies, NO file I/O.

All user-facing messages must be in Italian.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any


@dataclass
class NormReference:
    """Reference to a normative document section.

    Provides traceability from check results back to norm requirements.
    """

    norm_code: str  # e.g., "NTC2018", "RD2229", "EC2"
    chapter: str  # e.g., "4.1", "Cap. 8"
    paragraph: str  # e.g., "4.1.2.1.3.1"
    formula_label: str | None = None  # e.g., "(4.1)", "Eq. 7.2"
    description_it: str = ""  # Italian description of what this reference covers
    notes_it: str | None = None  # Additional Italian notes
    source_type: str | None = None  # e.g., "norm", "code", "standard"
    priority: int | None = None  # For ordering multiple references


@dataclass
class ValidationIssue:
    """Single validation issue found in input data.

    Represents problems with CalcInput before verification can run.
    """

    severity: str  # "info", "warning", "error"
    field: str  # Which field has the issue
    code: str  # Machine-readable code (e.g., "NEGATIVE_D", "INVALID_LC")
    message_it: str  # Italian message for user
    norm_reference: NormReference | None = None  # If issue comes from norm requirement
    context: dict[str, Any] = dataclasses.field(default_factory=dict)  # Additional context


@dataclass
class ValidationResult:
    """Result of validating a CalcInput.

    If has_errors is True, verification MUST NOT run.
    """

    issues: list[ValidationIssue] = dataclasses.field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.severity == "warning" for issue in self.issues)


@dataclass
class VerificationTemplate:
    """Template/configuration for a single verification check.

    Each template represents one normative check (e.g., flessione SLU NTC2018).
    Templates are loaded from normative registry (JSON/CSV/Python).
    """

    template_id: str  # Unique ID, e.g., "ntc2018_slu_flessione_rett"
    norm_code: str  # e.g., "NTC2018"
    norm_version: str | None = None  # e.g., "2018" (if norm has versions)
    verification_type: str = ""  # e.g., "flessione", "taglio", "torsione"
    limit_state: str = ""  # e.g., "SLU", "SLE", "TA"
    description_it: str = ""  # Italian description shown to user
    check_category: str = ""  # e.g., "resistenza", "minimi_armatura", "tensioni"
    required_inputs: list[str] = dataclasses.field(
        default_factory=list
    )  # e.g., ["N", "Mx", "As", "d"]
    optional_inputs: list[str] = dataclasses.field(default_factory=list)  # e.g., ["My", "Mz"]
    output_metrics: list[str] = dataclasses.field(
        default_factory=list
    )  # e.g., ["M_Rd", "utilisazione"]
    primary_reference: NormReference | None = None
    secondary_references: list[NormReference] = dataclasses.field(default_factory=list)
    function_path: str = ""  # e.g., "src.methods.verification.methods_slu.check_flessione_slu"
    can_batch: bool = True  # Can this check be batched for multiple elements?
    supports_real_time: bool = True  # Can run in real-time per-row?
    applicable_section_types: list[str] | None = None  # e.g., ["rectangular", "circular"]
    applicable_material_tags: list[str] | None = None  # e.g., ["concrete", "RC"]
    requires_existing_structure: bool = False  # True if check only for existing structures (LC/FC)
    extra_params: dict[str, Any] = dataclasses.field(
        default_factory=dict
    )  # Template-specific params


@dataclass
class SingleCheckResult:
    """Result of executing one VerificationTemplate on one element.

    Contains ok/non-ok status, utilisation, details, and normative references.
    """

    template_id: str  # Which template was executed
    ok: bool  # True if check passed, False if failed
    utilisation: float | None = None  # Utilisation ratio (e.g., 0.85 = 85%)
    details: dict[str, float | str] = dataclasses.field(default_factory=dict)  # Intermediate values
    norm_references: list[NormReference] = dataclasses.field(default_factory=list)  # Norms used
    messages_it: list[str] = dataclasses.field(default_factory=list)  # Italian messages for user
    check_category: str | None = None  # e.g., "resistenza", "minimi_armatura"
    limit_state: str | None = None  # e.g., "SLU", "SLE"


@dataclass
class CalcInput:
    """Complete input data for verifying one structural element.

    Built by GUI controller from:
    - GUI fields (N, M, As, etc.)
    - Section repository (resolves section_id → section geometry)
    - Material repository (resolves material_id → material properties)

    This is a pure domain object with NO GUI dependencies.
    """

    # Basic identification
    element_name: str = ""

    # Geometry (resolved from repository, NOT from GUI)
    section: Any = None  # SectionLike object from repository

    # Materials (resolved from repository, NOT from GUI)
    material: Any = None  # MaterialLike object from repository

    # Normative context
    norm_code: str = ""  # e.g., "NTC2018", "RD2229"
    limit_states_enabled: list[str] = dataclasses.field(
        default_factory=list
    )  # e.g., ["SLU", "SLE"]

    # LC/FC for existing structures (optional)
    lc: str | None = None  # Livello di Conoscenza: "LC1", "LC2", "LC3"
    fc: float | None = None  # Fattore di Confidenza: typically 1.0 - 1.35

    # Internal forces (design actions, already combined by engineer)
    N: float | None = None  # Normal force [kN or kg]
    Mx: float | None = None  # Bending moment about x [kNm or kgm]
    My: float | None = None  # Bending moment about y [kNm or kgm]
    Mz: float | None = None  # Torsional moment [kNm or kgm]
    Tx: float | None = None  # Shear force along x [kN or kg]
    Ty: float | None = None  # Shear force along y [kN or kg]

    # Reinforcement geometry
    As: float | None = None  # Tension reinforcement area [cm² or mm²]
    As_prime: float | None = None  # Compression reinforcement area [cm² or mm²]
    d: float | None = None  # Effective depth [cm or mm]
    d_prime: float | None = None  # Compression reinforcement depth [cm or mm]

    # Stirrups/shear reinforcement
    staffe_diametro: float | None = None  # Stirrup diameter [mm]
    staffe_num_bracci: int | None = None  # Number of stirrup legs
    staffe_passo: float | None = None  # Stirrup spacing [cm or mm]
    area_ferri_piegati: float | None = None  # Bent-up bars area [cm² or mm²]

    # Extra data (for circular rebar layouts, custom parameters, etc.)
    extra: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclass
class CalcOutput:
    """Complete output from verifying one structural element.

    Contains:
    - Validation result (input errors/warnings)
    - Per-template check results
    - Global ok/non-ok status
    - Summary metrics
    """

    element_name: str = ""
    norm_code: str = ""
    ok: bool = False  # Global ok/non-ok (all checks passed)
    per_template_results: dict[str, SingleCheckResult] = dataclasses.field(
        default_factory=dict
    )  # template_id → result
    validation_result: ValidationResult | None = None
    summary_metrics: dict[str, float | bool | str] = dataclasses.field(
        default_factory=dict
    )  # e.g., {"status": "OK", "utilizzazione_massima": 0.85, "template_controllante": "ntc2018_slu_flessione"}
