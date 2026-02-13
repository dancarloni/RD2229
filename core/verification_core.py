# Compatibility shim mapping to src.core_calculus.verification_core
from __future__ import annotations

from importlib import import_module as _im

try:
    # Prefer the path used in project imports
    _mod = _im("src.core_calculus.core.verification_core")
except ModuleNotFoundError:
    # Fallbacks to support different PYTHONPATH setups
    try:
        _mod = _im("core_calculus.core.verification_core")
    except ModuleNotFoundError:
        _mod = _im("src.core_calculus.core.verification_core")

for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # NOTE: aggiorna questi import in base alla struttura reale del progetto
    from app.core.contracts import CalcInput  # noqa: F401
    from app.core.norms.plugins import NormPlugin  # noqa: F401
    from app.core.norms.references import NormReference  # noqa: F401
    from app.core.norms.templates import VerificationTemplate  # noqa: F401
else:
    # Fallback tipo Any per evitare errori in fase di import se i moduli
    # non sono ancora definiti. Copilot dovrà sostituire con i tipi reali.
    NormReference = Any  # type: ignore[assignment]
    CalcInput = Any  # type: ignore[assignment]
    NormPlugin = Any  # type: ignore[assignment]
    VerificationTemplate = Any  # type: ignore[assignment]


@dataclass
class ValidationIssue:
    """Singola anomalia/avvertimento riscontrato in fase di validazione.

    Attributes:
        severity: Livello di gravità ("info", "warning", "error").
        field: Nome simbolico del campo (es. "d", "As", "N", "norma").
        code: Codice macchina (es. "GEOM_D_TOO_LARGE", "MISSING_REQUIRED_INPUT").
        message_it: Messaggio in italiano per GUI, log, report.
        norm_reference: Riferimento normativo associato, se disponibile.
        context: Dati di contesto (valori limite, valore calcolato, ecc.).
    """

    severity: str
    field: str
    code: str
    message_it: str
    norm_reference: NormReference | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def is_error(self) -> bool:
        """Return True se la severità è 'error' (case-insensitive)."""
        return self.severity.lower() == "error"

    def is_warning(self) -> bool:
        """Return True se la severità è 'warning' (case-insensitive)."""
        return self.severity.lower() == "warning"


@dataclass
class ValidationResult:
    """Risultato aggregato della validazione di un elemento strutturale.

    Attributes:
        issues: Lista di problemi (errori/avvertimenti/info).
    """

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """True se è presente almeno un errore."""
        return any(issue.is_error() for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        """True se è presente almeno un warning."""
        return any(issue.is_warning() for issue in self.issues)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Aggiunge una singola anomalia al risultato."""
        self.issues.append(issue)

    def extend(self, issues: Sequence[ValidationIssue]) -> None:
        """Estende il risultato con una lista di anomalie."""
        self.issues.extend(issues)


def validate_calc_input(
    calc_input: CalcInput,
    active_norm: NormPlugin,
    templates: Sequence[VerificationTemplate],
) -> ValidationResult:
    """Valida i dati di input prima dell'esecuzione delle verifiche.

    La funzione esegue in sequenza:
      1) controlli geometrici (sezione, d, d', As, staffe, ecc.),
      2) controlli sui materiali e sulle azioni interne (N, M, T),
      3) controlli di compatibilità tra norma, stati limite e template scelti.

    La GUI deve chiamare questa funzione:
      - per la verifica in tempo reale della singola riga,
      - prima del ricalcolo bulk ("Ricalcola tutto").

    Args:
        calc_input: Dati completi dell'elemento da verificare.
        active_norm: Normativa attiva (plugin/parametri).
        templates: Template di verifica che si intendono applicare.

    Returns:
        ValidationResult: lista di anomalie, con flag has_errors/has_warnings.
    """
    logger.debug("Inizio validazione per elemento: %s", getattr(calc_input, "name", ""))

    result = ValidationResult()

    geom_issues = _validate_geometry(calc_input, active_norm)
    if geom_issues:
        logger.debug("Trovate %d anomalie geometriche", len(geom_issues))
    result.extend(geom_issues)

    material_issues = _validate_materials(calc_input, active_norm)
    if material_issues:
        logger.debug("Trovate %d anomalie materiali/azioni", len(material_issues))
    result.extend(material_issues)

    norm_issues = _validate_norm_compatibility(calc_input, active_norm, templates)
    if norm_issues:
        logger.debug("Trovate %d anomalie di compatibilità normativa", len(norm_issues))
    result.extend(norm_issues)

    logger.debug(
        "Validazione completata: %d anomalie (errori=%s, warning=%s)",
        len(result.issues),
        result.has_errors,
        result.has_warnings,
    )
    return result


def _validate_geometry(
    calc_input: CalcInput,
    active_norm: NormPlugin,
) -> list[ValidationIssue]:
    """Esegue i controlli geometrici di base (indipendenti o quasi dalla norma).

    Esempi di controlli da implementare:
      - 0 < d <= altezza sezione (h),
      - 0 <= d' <= h,
      - As, As' >= 0 e compatibili con l'area di sezione,
      - rapporti di armatura entro limiti ragionevoli,
      - passo e diametro delle staffe positivi e coerenti.

    Alcuni limiti possono derivare direttamente da norme (RD2229/39, NTC, ecc.),
    altri possono essere solo di buona pratica (da documentare in notes_it).

    Args:
        calc_input: Dati completi dell'elemento.
        active_norm: Normativa attiva (può influenzare alcuni limiti).

    Returns:
        Lista di ValidationIssue (può essere vuota).
    """
    issues: list[ValidationIssue] = []

    # Esempio di scheletro (i nomi dei campi vanno adattati a CalcInput reale):

    section = getattr(calc_input, "section", None)
    d = getattr(calc_input, "d", None)
    d_prime = getattr(calc_input, "d_prime", None)

    # Controllo su d con altezza sezione (se disponibili)
    if section is not None and d is not None:
        h = getattr(section, "height", None)
        if h is not None and (d <= 0 or d > h):
            issues.append(
                ValidationIssue(
                    severity="error",
                    field="d",
                    code="GEOM_D_OUT_OF_RANGE",
                    message_it=(
                        "L'altezza utile d deve essere positiva e non superiore "
                        "all'altezza della sezione."
                    ),
                    norm_reference=None,  # TODO: aggiungere NormReference se normativo
                    context={"d": d, "h": h},
                )
            )

    # TODO: aggiungere controlli analoghi per d', As, As', staffe, ecc.

    return issues


def _validate_materials(
    calc_input: CalcInput,
    active_norm: NormPlugin,
) -> list[ValidationIssue]:
    """Controlla coerenza dei materiali e delle azioni interne.

    Esempi di controlli:
      - resistenze caratteristiche in un intervallo plausibile,
      - modulo elastico coerente con la resistenza (se previsto),
      - valori di N, Mx, My, Tx, Ty, Mz finiti e ragionevoli,
      - LC/FC per materiali esistenti coerenti con la norma attiva.

    Args:
        calc_input: Dati completi dell'elemento.
        active_norm: Normativa attiva.

    Returns:
        Lista di ValidationIssue (può essere vuota).
    """
    issues: list[ValidationIssue] = []

    material = getattr(calc_input, "material", None)
    if material is None:
        issues.append(
            ValidationIssue(
                severity="error",
                field="materiale",
                code="MISSING_MATERIAL",
                message_it="Materiale non specificato per l'elemento.",
                norm_reference=None,
                context={},
            )
        )
        return issues

    # Esempio di controllo su resistenza caratteristica (nomi da adattare)
    f_ck = getattr(material, "f_ck", None)
    if f_ck is not None and f_ck <= 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="materiale",
                code="INVALID_FCK",
                message_it="La resistenza caratteristica del calcestruzzo deve essere positiva.",
                norm_reference=None,  # TODO: aggiungere riferimento normativo se serve
                context={"f_ck": f_ck},
            )
        )

    # TODO: aggiungere controlli su LC/FC per materiali esistenti, range di N, M, T, ecc.

    return issues


def _validate_norm_compatibility(
    calc_input: CalcInput,
    active_norm: NormPlugin,
    templates: Sequence[VerificationTemplate],
) -> list[ValidationIssue]:
    """Verifica la compatibilità tra norma attiva, template scelti e dati di input.

    Esempi di controlli:
      - non usare template TA con una norma che prevede solo SLU/SLE, se non permesso,
      - non usare template per opere esistenti su elementi marcati come 'nuovi',
      - non usare template NTC2018 con norm_code impostato su NTC2008, ecc.

    Args:
        calc_input: Dati completi dell'elemento.
        active_norm: Normativa attiva (plugin/parametri).
        templates: Template di verifica selezionati per questo elemento.

    Returns:
        Lista di ValidationIssue (può essere vuota).
    """
    issues: list[ValidationIssue] = []

    # Esempio di scheletro (i campi norm_code/limit_state vanno adattati):

    active_code = getattr(active_norm, "code", None)

    for tpl in templates:
        tpl_norm_code = getattr(tpl, "norm_code", None)
        tpl_limit_state = getattr(tpl, "limit_state", None)

        # Se il template è associato a una normativa diversa da quella attiva
        if tpl_norm_code is not None and active_code is not None:
            if tpl_norm_code != active_code:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        field="norma",
                        code="NORM_TEMPLATE_MISMATCH",
                        message_it=(
                            "Il template di verifica selezionato non è compatibile "
                            "con la normativa attiva."
                        ),
                        norm_reference=None,
                        context={
                            "norm_attiva": active_code,
                            "norm_template": tpl_norm_code,
                            "template_id": getattr(tpl, "template_id", ""),
                        },
                    )
                )

        # TODO: controlli aggiuntivi su limit_state (TA/SLU/SLE) e opere nuove/esistenti

    return issues
