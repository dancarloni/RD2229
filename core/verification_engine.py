# Compatibility shim mapping to src.core_calculus.verification_engine
from __future__ import annotations
from importlib import import_module as _im

try:
    _mod = _im("src.core_calculus.core.verification_engine")
except ModuleNotFoundError:
    try:
        _mod = _im("core_calculus.core.verification_engine")
    except ModuleNotFoundError:
        _mod = _im("src.core_calculus.core.verification_engine")

for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Sequence

import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # NOTE: aggiorna questi import in base alla struttura reale del progetto.
    from app.core.contracts import CalcInput  # noqa: F401
    from app.core.norms.plugins import NormPlugin  # noqa: F401
    from app.core.norms.templates import VerificationTemplate  # noqa: F401
    from app.core.validation import ValidationResult  # noqa: F401
    from app.core.norms.references import NormReference  # noqa: F401
else:
    CalcInput = Any  # type: ignore[assignment]
    NormPlugin = Any  # type: ignore[assignment]
    VerificationTemplate = Any  # type: ignore[assignment]
    ValidationResult = Any  # type: ignore[assignment]
    NormReference = Any  # type: ignore[assignment]


# ======================================================================
#  Risultato di una singola verifica (per template)
# ======================================================================


@dataclass
class SingleCheckResult:
    """Risultato di una singola verifica per un template.

    Attributes:
        template_id: Identificativo univoco del template di verifica.
        ok: Esito della verifica (True se soddisfatta).
        utilisation: Rapporto di utilizzazione (es. Ed/Rd, σ/σ_amm, ecc.).
        details: Dizionario di risultati numerici chiave.
        norm_references: Lista di riferimenti normativi associati.
        messages_it: Messaggi sintetici in italiano (per GUI/report).
        check_category: Categoria (flessione, taglio, torsione, ecc.).
        limit_state: Stato limite (TA, SLU, SLE, ...).
    """

    template_id: str
    ok: bool
    utilisation: float | None = None
    details: Dict[str, float | str] = field(default_factory=dict)
    norm_references: List[NormReference] = field(default_factory=list)
    messages_it: List[str] = field(default_factory=list)
    check_category: str | None = None
    limit_state: str | None = None


# ======================================================================
#  Risultato complessivo per un elemento
# ======================================================================


@dataclass
class CalcOutput:
    """Risultato aggregato delle verifiche per un singolo elemento strutturale.

    Attributes:
        element_name: Nome/ID dell'elemento (coerente con CalcInput).
        norm_code: Codice della normativa utilizzata (es. "NTC 2018").
        ok: True se tutte le verifiche richieste sono OK e non ci sono errori
            di validazione.
        per_template_results: Mappa template_id → SingleCheckResult.
        validation_result: Risultato della validazione dei dati di input.
        summary_metrics: Metriche sintetiche (es. utilizzo massimo).
    """

    element_name: str
    norm_code: str
    ok: bool
    per_template_results: Dict[str, SingleCheckResult] = field(default_factory=dict)
    validation_result: ValidationResult | None = None
    summary_metrics: Dict[str, float | bool | str] = field(default_factory=dict)


# ======================================================================
#  Funzioni principali del servizio di verifica
# ======================================================================


def run_verifications_for_element(
    calc_input: CalcInput,
    active_norm: NormPlugin,
    enabled_limit_states: Sequence[str] | None = None,
) -> CalcOutput:
    """Esegue tutte le verifiche previste per un elemento e una normativa.

    Flusso:
      1) Seleziona i VerificationTemplate applicabili (in base a norma, sezione,
         materiale, stati limite abilitati, esistente/nuovo).
      2) Esegue la validazione dei dati (validate_calc_input).
      3) In presenza di errori di validazione:
           - NON esegue alcuna verifica,
           - restituisce un CalcOutput marcato come non verificato.
      4) In assenza di errori:
           - esegue TUTTI i template pertinenti alla norma e agli stati limite
             abilitati,
           - aggrega i risultati in CalcOutput.

    Args:
        calc_input: Dati completi dell'elemento da verificare.
        active_norm: Normativa attiva (plugin/parametri).
        enabled_limit_states: Lista di stati limite da considerare
            (es. ["TA", "SLU", "SLE"]). Se None, usa configurazione di default.

    Returns:
        CalcOutput con risultati per template e flag globale ok/non ok.
    """
    element_name = getattr(calc_input, "element_name", "")
    norm_code = getattr(active_norm, "code", "UNKNOWN")

    logger.debug(
        "Esecuzione verifiche per elemento '%s' con normativa '%s'",
        element_name,
        norm_code,
    )

    # 1) Selezione template applicabili
    templates = _select_templates_for_element(
        calc_input=calc_input,
        active_norm=active_norm,
        enabled_limit_states=enabled_limit_states,
    )

    logger.debug("Selezionati %d template di verifica", len(templates))

    # 2) Validazione input
    from app.core.validation import validate_calc_input  # import locale per evitare cicli

    validation_result = validate_calc_input(
        calc_input=calc_input,
        active_norm=active_norm,
        templates=templates,
    )

    if validation_result.has_errors:
        logger.info(
            "Validazione FALLITA per elemento '%s' con normativa '%s': %d errori",
            element_name,
            norm_code,
            len(validation_result.issues),
        )
        # Nessuna verifica eseguita, output marcato non ok.
        return CalcOutput(
            element_name=element_name,
            norm_code=norm_code,
            ok=False,
            per_template_results={},
            validation_result=validation_result,
            summary_metrics={
                "status": "NON_VERIFICATO_PER_ERRORI_INPUT",
            },
        )

    # 3) Esecuzione verifiche (tutti i template)
    per_template_results: Dict[str, SingleCheckResult] = {}

    for tpl in templates:
        tpl_id = getattr(tpl, "template_id", "<senza_id>")

        logger.debug("Esecuzione template '%s' per elemento '%s'", tpl_id, element_name)

        try:
            check_result = _execute_template(tpl, calc_input, active_norm)
            per_template_results[tpl_id] = check_result
        except Exception as exc:  # pragma: no cover - per log robusti
            logger.exception(
                "Errore durante l'esecuzione del template '%s' per elemento '%s': %s",
                tpl_id,
                element_name,
                exc,
            )
            # In caso di eccezione di programmazione, consideriamo il check fallito.
            per_template_results[tpl_id] = SingleCheckResult(
                template_id=tpl_id,
                ok=False,
                utilisation=None,
                details={"exception": str(exc)},
                norm_references=[],
                messages_it=[
                    "Errore interno durante la verifica. "
                    "Consultare i log per maggiori dettagli."
                ],
                check_category=getattr(tpl, "check_category", None),
                limit_state=getattr(tpl, "limit_state", None),
            )

    # 4) Calcolo flag globale e metriche sintetiche
    global_ok = all(res.ok for res in per_template_results.values())

    max_util = _compute_max_utilisation(per_template_results.values())
    controlling_template_id = _find_controlling_template_id(per_template_results)

    summary_metrics: Dict[str, float | bool | str] = {
        "status": "OK" if global_ok else "NON_OK",
        "utilizzazione_massima": max_util if max_util is not None else 0.0,
        "template_controllante": controlling_template_id or "",
    }

    # Propagazione eventuali warning di validazione (senza errori)
    if validation_result.has_warnings:
        summary_metrics["warning_validazione"] = True

    logger.info(
        "Verifiche completate per elemento '%s' (%s): ok=%s, util_max=%s, ctrl=%s",
        element_name,
        norm_code,
        global_ok,
        max_util,
        controlling_template_id,
    )

    return CalcOutput(
        element_name=element_name,
        norm_code=norm_code,
        ok=global_ok and not validation_result.has_errors,
        per_template_results=per_template_results,
        validation_result=validation_result,
        summary_metrics=summary_metrics,
    )


def run_verifications_for_all(
    calc_inputs: Sequence[CalcInput],
    active_norm: NormPlugin,
    enabled_limit_states: Sequence[str] | None = None,
) -> List[CalcOutput]:
    """Esegue le verifiche per una collezione di elementi (bulk).

    Questa funzione è pensata per essere richiamata dal pulsante
    "Ricalcola tutto" della GUI. Non deve bloccare la GUI: sarà la GUI a
    decidere se eseguirla in un thread separato.

    Args:
        calc_inputs: Sequenza di CalcInput (uno per elemento/righe GUI).
        active_norm: Normativa attiva (plugin/parametri).
        enabled_limit_states: Stati limite abilitati (TA, SLU, SLE, ...).

    Returns:
        Lista di CalcOutput, nello stesso ordine di calc_inputs.
    """
    outputs: List[CalcOutput] = []
    for ci in calc_inputs:
        outputs.append(
            run_verifications_for_element(
                calc_input=ci,
                active_norm=active_norm,
                enabled_limit_states=enabled_limit_states,
            )
        )
    return outputs


# ======================================================================
#  Funzioni interne di supporto
# ======================================================================


def _select_templates_for_element(
    calc_input: CalcInput,
    active_norm: NormPlugin,
    enabled_limit_states: Sequence[str] | None,
) -> List[VerificationTemplate]:
    """Seleziona i template di verifica applicabili per l'elemento.

    La selezione deve essere eseguita nel CORE (non nella GUI) e deve tenere conto di:
      - normativa attiva,
      - tipo di sezione,
      - tipo di materiale,
      - se l'elemento è "nuovo" o "esistente",
      - stati limite abilitati (TA, SLU, SLE),
      - eventuali altre impostazioni centrali (VerificationContext).

    Args:
        calc_input: Dati completi dell'elemento.
        active_norm: Normativa attiva (NormPlugin).
        enabled_limit_states: Lista di stati limite abilitati.

    Returns:
        Lista di VerificationTemplate da eseguire per questo elemento.
    """
    # TODO: recuperare i template dal NormPlugin / registry, filtrando per:
    #   - limit_state,
    #   - check_category,
    #   - applicable_section_types,
    #   - applicable_material_tags,
    #   - requires_existing_structure.
    #
    # Esempio (pseudo-codice):
    #
    # templates = active_norm.get_verification_templates()
    # filtered = []
    # for tpl in templates:
    #     if enabled_limit_states and tpl.limit_state not in enabled_limit_states:
    #         continue
    #     # ulteriori filtri su sezione, materiale, esistente/nuovo...
    #     filtered.append(tpl)
    # return filtered

    return []  # placeholder, da implementare


def _execute_template(
    template: VerificationTemplate,
    calc_input: CalcInput,
    active_norm: NormPlugin,
) -> SingleCheckResult:
    """Esegue la verifica associata a un singolo VerificationTemplate.

    Args:
        template: Template di verifica da eseguire.
        calc_input: Dati completi dell'elemento.
        active_norm: Normativa attiva.

    Returns:
        SingleCheckResult con esito, utilizzazione, dettagli e riferimenti normativi.
    """
    # TODO:
    #  - individuare la funzione di calcolo dal template (function_path o callback),
    #  - passare i dati necessari (idealmente CalcInput o un sotto-insieme ben definito),
    #  - ottenere risultati numerici (Rd, Ed, σ, ecc.),
    #  - calcolare 'ok' e 'utilisation',
    #  - comporre il SingleCheckResult con norm_references e messaggi in italiano.
    #
    # Esempio di struttura:

    function_path = getattr(template, "function_path", "")
    check_category = getattr(template, "check_category", None)
    limit_state = getattr(template, "limit_state", None)
    primary_ref = getattr(template, "primary_reference", None)
    secondary_refs = getattr(template, "secondary_references", []) or []

    # Caricamento dinamico della funzione di verifica (es. via importlib)
    # oppure riferimento diretto se già passato nel template.

    # result_data = verificatore(calc_input, active_norm, template)

    # Per ora, placeholder:
    utilisation = None
    ok = False
    details: Dict[str, float | str] = {}

    messages_it = [
        "TODO: implementare la verifica per questo template "
        "in base alla normativa corrispondente."
    ]

    norm_refs: List[NormReference] = []
    if primary_ref is not None:
        norm_refs.append(primary_ref)
    norm_refs.extend(secondary_refs)

    return SingleCheckResult(
        template_id=getattr(template, "template_id", function_path),
        ok=ok,
        utilisation=utilisation,
        details=details,
        norm_references=norm_refs,
        messages_it=messages_it,
        check_category=check_category,
        limit_state=limit_state,
    )


def _compute_max_utilisation(
    results: Iterable[SingleCheckResult],
) -> float | None:
    """Calcola l'utilizzazione massima tra tutti i risultati disponibili."""
    utilis = [
        r.utilisation for r in results if r.utilisation is not None and r.utilisation >= 0
    ]
    if not utilis:
        return None
    return max(utilis)


def _find_controlling_template_id(
    results: Dict[str, SingleCheckResult],
) -> str | None:
    """Individua il template 'controllante' (utilizzazione massima)."""
    max_util = -1.0
    controlling_id: str | None = None
    for tpl_id, res in results.items():
        if res.utilisation is not None and res.utilisation > max_util:
            max_util = res.utilisation
            controlling_id = tpl_id
    return controlling_id