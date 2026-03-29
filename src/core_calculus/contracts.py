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
    """Input normalizzato completo per la verifica di un elemento strutturale.

    Costruito dal controller GUI a partire da:
    - Campi GUI (N, M, As, ecc.)
    - Repository sezioni (risolve section_id → geometria sezione)
    - Repository materiali (risolve material_id → proprietà materiale)

    Unità interne standard:
    - Tensioni/resistenze: **MPa** (N/mm²)
    - Forze: **kN**
    - Momenti: **kN·m**
    - Geometria: **cm**
    - Armature: **cm²**

    Oggetto di dominio puro: NESSUNA dipendenza GUI.
    """

    # --- Identificazione ---
    element_name: str = ""

    # --- Geometria (risolta dal repository, NON dalla GUI) ---
    section: Any = None  # Oggetto SectionLike dal repository

    # --- Materiali (risolti dal repository, NON dalla GUI) ---
    #     I materiali devono avere tensioni PRE-NORMALIZZATE a MPa.
    #     La normalizzazione avviene tramite normalization.normalize_to_mpa().
    material: Any = None  # Oggetto MaterialLike dal repository

    # --- Contesto normativo ---
    norm_code: str = ""  # es. "NTC2018", "RD2229", "DM96"
    limit_states_enabled: list[str] = dataclasses.field(
        default_factory=list
    )  # es. ["SLU", "SLE", "TA"]
    combinazione: str = ""  # es. "rara", "frequente", "sismica"

    # --- LC/FC per strutture esistenti (opzionali) ---
    lc: str | None = None  # Livello di Conoscenza: "LC1", "LC2", "LC3"
    fc: float | None = None  # Fattore di Confidenza: tipicamente 1.0 - 1.35

    # --- Sollecitazioni (azioni di progetto, già combinate) ---
    N: float | None = None  # Sforzo normale [kN]
    Mx: float | None = None  # Momento flettente asse x [kN·m]
    My: float | None = None  # Momento flettente asse y [kN·m]
    Mz: float | None = None  # Momento torcente [kN·m]
    Tx: float | None = None  # Taglio lungo x [kN]
    Ty: float | None = None  # Taglio lungo y [kN]

    # --- Geometria armature ---
    As: float | None = None  # Area armatura tesa [cm²]
    As_prime: float | None = None  # Area armatura compressa [cm²]
    d: float | None = None  # Altezza utile [cm]
    d_prime: float | None = None  # Copriferro armatura compressa [cm]

    # --- Staffe / armatura a taglio ---
    staffe_diametro: float | None = None  # Diametro staffe [mm]
    staffe_num_bracci: int | None = None  # Numero bracci staffe
    staffe_passo: float | None = None  # Passo staffe [cm]
    area_ferri_piegati: float | None = None  # Area ferri piegati [cm²]

    # --- Classificazione ruolo elemento ---
    element_role: ElementRole = ElementRole.UNDETERMINED

    # --- Parametri calcolo opzionali ---
    environment_class: str = ""  # es. "X0", "XC1", "XC2" (EC2 §4.2)
    durability: dict[str, Any] = dataclasses.field(
        default_factory=dict
    )  # es. {"copriferro": 40, "acciaio": "B500B"}

    # --- Metadata ---
    timestamp: str = ""  # ISO-8601 del momento di creazione
    user_notes: str = ""

    # --- Extra (layout circolari, parametri custom, ecc.) ---
    extra: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        """Imposta timestamp se non fornito."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat(timespec="seconds")


@dataclass
class CalcOutput:
    """Output standardizzato dalla verifica di un elemento strutturale.

    Contiene:
    - Risultato validazione (errori/warning input)
    - Risultati per-template delle verifiche eseguite
    - Esito globale OK/non-OK
    - Metriche di sintesi
    - Passaggi di calcolo aggregati per tracciabilità tabulato
    - Serializzazione per report (``to_dict()``, ``to_latex()``)

    Unità interne: MPa per tensioni, kN/kN·m per forze/momenti.
    La conversione alle unità di output avviene tramite
    ``normalization.denormalize_for_output()``.
    """

    element_name: str = ""
    norm_code: str = ""
    ok: bool = False  # Esito globale (True se tutte le verifiche passano)

    # --- Risultati per template ---
    per_template_results: dict[str, SingleCheckResult] = dataclasses.field(
        default_factory=dict
    )  # template_id → risultato

    # --- Validazione input ---
    validation_result: ValidationResult | None = None

    # --- Classificazione elemento ---
    element_role: ElementRole = ElementRole.UNDETERMINED
    profile_used: str = ""  # es. "PROFILE_PRIMARY_FULL"

    # --- Metriche di sintesi ---
    summary_metrics: dict[str, float | bool | str] = dataclasses.field(
        default_factory=dict
    )

    # --- Campi protocollo I/O standard ---
    rapporto_verifica: float = 0.0  # Rapporto max di utilizzazione (≤1 → OK)
    passaggi_calcolo: list[str] = dataclasses.field(default_factory=list)
    formule_usate: list[str] = dataclasses.field(default_factory=list)
    norma_riferimento: NormReference | None = None
    warnings: list[str] = dataclasses.field(default_factory=list)
    errors: list[str] = dataclasses.field(default_factory=list)

    # --- Tensioni principali (unità interne MPa) ---
    stress_max: float | None = None  # Massima tensione calcolata [MPa]
    stress_limit: float | None = None  # Limite ammissibile [MPa]
    deformation: float | None = None  # Freccia / deformazione [mm]

    # --- Metadata ---
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Imposta timestamp e aggrega risultati dai template."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat(timespec="seconds")

    def aggregate_from_templates(self) -> None:
        """Aggrega passaggi_calcolo, formule_usate e rapporto_verifica dai template.

        Chiamare dopo che tutti i risultati per-template sono stati inseriti.
        Aggiorna ``rapporto_verifica`` con il massimo rapporto di utilizzazione,
        e raccoglie tutti i ``passaggi_calcolo`` e ``formule_usate`` dai template.
        """
        all_passaggi: list[str] = []
        all_formule: list[str] = []
        max_util = 0.0

        for tid, result in self.per_template_results.items():
            # Passaggi
            if result.passaggi_calcolo:
                all_passaggi.append(f"── {tid} ──")
                all_passaggi.extend(result.passaggi_calcolo)
            # Formule
            all_formule.extend(result.formule_usate)
            # Utilizzazione
            if result.utilisation is not None and result.utilisation > max_util:
                max_util = result.utilisation

        self.passaggi_calcolo = all_passaggi
        self.formule_usate = list(dict.fromkeys(all_formule))  # Deduplica preservando ordine
        self.rapporto_verifica = max_util

        # Aggiorna stress_max/stress_limit dal template controllante
        for result in self.per_template_results.values():
            if result.utilisation is not None and math.isclose(
                result.utilisation, max_util, rel_tol=1e-9
            ):
                if result.stress_max is not None:
                    self.stress_max = result.stress_max
                if result.stress_limit is not None:
                    self.stress_limit = result.stress_limit
                if result.deformation is not None:
                    self.deformation = result.deformation
                break

    def to_dict(self) -> dict[str, Any]:
        """Serializza il risultato in un dizionario JSON-compatibile.

        Restituisce
        -----------
        dict
            Dizionario completo per esportazione JSON / report.
        """
        result: dict[str, Any] = {
            "element_name": self.element_name,
            "norm_code": self.norm_code,
            "ok": self.ok,
            "rapporto_verifica": self.rapporto_verifica,
            "stress_max": self.stress_max,
            "stress_limit": self.stress_limit,
            "deformation": self.deformation,
            "passaggi_calcolo": self.passaggi_calcolo,
            "formule_usate": self.formule_usate,
            "warnings": self.warnings,
            "errors": self.errors,
            "timestamp": self.timestamp,
        }

        # Template results
        result["verifiche"] = {}
        for tid, scr in self.per_template_results.items():
            result["verifiche"][tid] = scr.to_dict()

        # Validation
        if self.validation_result is not None:
            result["validazione"] = {
                "has_errors": self.validation_result.has_errors,
                "has_warnings": self.validation_result.has_warnings,
                "issues": [dataclasses.asdict(i) for i in self.validation_result.issues],
            }

        # Norma riferimento
        if self.norma_riferimento is not None:
            result["norma_riferimento"] = dataclasses.asdict(self.norma_riferimento)

        # Summary metrics
        result["summary_metrics"] = dict(self.summary_metrics)

        return result

    def to_latex(self) -> str:
        """Genera rappresentazione LaTeX del risultato per report PDF.

        Restituisce
        -----------
        str
            Stringa LaTeX con tabella risultati e passaggi di calcolo.
        """
        lines: list[str] = []
        lines.append(r"\subsection{Verifica: " + _latex_escape(self.element_name) + "}")
        lines.append("")

        # Tabella riassuntiva
        esito_str = r"\textbf{OK}" if self.ok else r"\textbf{NON VERIFICATO}"
        lines.append(r"\begin{tabular}{ll}")
        lines.append(r"\hline")
        lines.append(f"Normativa & {_latex_escape(self.norm_code)} \\\\")
        lines.append(f"Esito & {esito_str} \\\\")
        lines.append(f"Rapporto verifica & {self.rapporto_verifica:.3f} \\\\")
        if self.stress_max is not None:
            lines.append(f"$\\sigma_{{max}}$ & {self.stress_max:.2f} MPa \\\\")
        if self.stress_limit is not None:
            lines.append(f"$\\sigma_{{lim}}$ & {self.stress_limit:.2f} MPa \\\\")
        if self.deformation is not None:
            lines.append(f"Deformazione & {self.deformation:.2f} mm \\\\")
        lines.append(r"\hline")
        lines.append(r"\end{tabular}")
        lines.append("")

        # Passaggi di calcolo
        if self.passaggi_calcolo:
            lines.append(r"\subsubsection{Passaggi di calcolo}")
            lines.append(r"\begin{enumerate}")
            for passo in self.passaggi_calcolo:
                if passo.startswith("──"):
                    lines.append(r"\item[\textbf{" + _latex_escape(passo) + "}]")
                else:
                    lines.append(r"\item " + _latex_escape(passo))
            lines.append(r"\end{enumerate}")

        # Formule usate
        if self.formule_usate:
            lines.append(r"\subsubsection{Riferimenti normativi}")
            lines.append(r"\begin{itemize}")
            for formula in self.formule_usate:
                lines.append(r"\item " + _latex_escape(formula))
            lines.append(r"\end{itemize}")

        # Warnings
        if self.warnings:
            lines.append(r"\subsubsection{Avvertenze}")
            lines.append(r"\begin{itemize}")
            for w in self.warnings:
                lines.append(r"\item " + _latex_escape(w))
            lines.append(r"\end{itemize}")

        return "\n".join(lines)


def _latex_escape(text: str) -> str:
    """Escape di caratteri speciali LaTeX.

    Parametri
    ----------
    text : str
        Testo da rendere sicuro per LaTeX.

    Restituisce
    -----------
    str
        Testo con caratteri speciali escaped.
    """
    special_chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text
