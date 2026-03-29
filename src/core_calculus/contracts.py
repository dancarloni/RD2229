"""Contratti I/O standard per verifiche strutturali.

Protocollo CalcInput/CalcOutput unificato per TUTTE le verifiche.
Tipi di dominio puri: NESSUNA dipendenza GUI, NESSUN I/O su file.

Pipeline di conversione unità::

    Input utente (unità GUI)
      → [gestore_unita.da_input()]
    Catalogo (kg/cm² storage)
      → [normalize_to_mpa()]
    CalcInput (MPa interno, SI)
      → [ENGINE DI VERIFICA — tutte in MPa]
    CalcOutput (MPa/SI interno)
      → [denormalize_for_output()]
    Output (unità GUI)
      → [gestore_unita.converti()]
    Display (kg/cm², MPa, kPa)

Immutabilità
------------
``CalcInput`` e ``CalcOutput`` sono dataclass **non** frozen per retrocompatibilità
con il service di verifica esistente (che assegna campi post-creazione).
I campi ``passaggi_calcolo`` e ``formule_usate`` sono obbligatori nel risultato.

Tutti i messaggi visibili all'utente sono in italiano.
"""

from __future__ import annotations

import dataclasses
import enum
import json
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any


class ElementRole(enum.Enum):
    """Structural role of an element per NTC2018 §7.2.3 / EC8 §4.2.2."""

    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    UNDETERMINED = "UNDETERMINED"


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
    """Risultato dell'esecuzione di un singolo template di verifica su un elemento.

    Contiene esito OK/non-OK, rapporto di utilizzazione, dettagli intermedi
    e riferimenti normativi per la tracciabilità.

    Il campo ``passaggi_calcolo`` è **obbligatorio** per la generazione
    dei tabulati di calcolo (report ASCII/HTML/LaTeX).
    """

    template_id: str  # Quale template è stato eseguito
    ok: bool  # True se la verifica è soddisfatta, False altrimenti
    utilisation: float | None = None  # Rapporto di utilizzazione (es. 0.85 = 85%)
    details: dict[str, float | str] = dataclasses.field(default_factory=dict)
    norm_references: list[NormReference] = dataclasses.field(default_factory=list)
    messages_it: list[str] = dataclasses.field(default_factory=list)
    check_category: str | None = None  # es. "resistenza", "minimi_armatura"
    limit_state: str | None = None  # es. "SLU", "SLE", "TA"

    # --- Campi aggiunti per protocollo I/O standard ---
    passaggi_calcolo: list[str] = dataclasses.field(default_factory=list)
    formule_usate: list[str] = dataclasses.field(default_factory=list)
    stress_max: float | None = None  # Massima tensione calcolata [MPa]
    stress_limit: float | None = None  # Limite ammissibile [MPa]
    deformation: float | None = None  # Freccia / deformazione [mm]

    def to_dict(self) -> dict[str, Any]:
        """Serializza il risultato in un dizionario JSON-compatibile.

        Restituisce
        -----------
        dict
            Dizionario con tutti i campi, NormReference espansi.
        """
        d = dataclasses.asdict(self)
        return d


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

    # Element role classification
    element_role: ElementRole = ElementRole.UNDETERMINED

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
    element_role: ElementRole = ElementRole.UNDETERMINED
    profile_used: str = ""  # e.g. "PROFILE_PRIMARY_FULL", "PROFILE_SECONDARY_STABILITY"
    summary_metrics: dict[str, float | bool | str] = dataclasses.field(
        default_factory=dict
    )  # e.g., {"status": "OK", "utilizzazione_massima": 0.85, "template_controllante": "ntc2018_slu_flessione"}
