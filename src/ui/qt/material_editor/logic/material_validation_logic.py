"""
MaterialValidationLogic — validazione soft e normativa dei materiali

Tre livelli di validazione:
  validate()            — soft (campi obbligatori mancanti)
  validate_ranges()     — range numerici da config/materials/*_config.json
  validate_coherence()  — coerenza cross-campo (es. E_calcolato vs E_inserito)
  validate_normative()  — vincoli per-norma (NTC2018, DM96, RD2229, ecc.)

Tutti restituiscono ValidationResult con lista di ValidationIssue.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

# Mappa di campi obbligatori per tipologia. Estendere secondo necessità.
REQUIRED_FIELDS_BY_TYPE: Dict[str, List[str]] = {
    'Calcestruzzi': ['codice', 'descrizione', 'f_ck', 'E', 'rho'],
    'Acciai': ['codice', 'descrizione', 'f_yk', 'E', 'rho'],
    'Legno': ['codice', 'descrizione', 'f_m', 'E'],
    'Muratura': ['codice', 'descrizione', 'f_b'],
    'Compositi': ['codice', 'descrizione'],
    'Terreni': ['codice', 'descrizione', 'rho', 'E'],
    'Generic': ['codice', 'descrizione']
}


def _has_value(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str) and v.strip() == '':
        return False
    return True


def get_required_fields(tipo: str) -> List[str]:
    if not tipo:
        return REQUIRED_FIELDS_BY_TYPE['Generic']
    # try exact match, then case-insensitive match
    if tipo in REQUIRED_FIELDS_BY_TYPE:
        return REQUIRED_FIELDS_BY_TYPE[tipo]
    for k in REQUIRED_FIELDS_BY_TYPE:
        if k.lower() == tipo.lower():
            return REQUIRED_FIELDS_BY_TYPE[k]
    return REQUIRED_FIELDS_BY_TYPE['Generic']


def validate(material: Dict[str, Any]) -> Dict[str, Any]:
    """Valida il materiale e ritorna un dict con:
    - is_complete: bool
    - missing: list[str]
    - warnings: list[str]
    """
    tipo = material.get('tipo') or material.get('norma') or 'Generic'
    required = get_required_fields(tipo)
    missing = []
    for field in required:
        if not _has_value(material.get(field)):
            missing.append(field)
    warnings: List[str] = []
    # Esempio: warn se valori numeric sono fuori range (placeholder)
    # if 'f_ck' in material and isinstance(material.get('f_ck'), (int, float)):
    #     if material['f_ck'] <= 0:
    #         warnings.append('f_ck deve essere positivo')

    return {
        'is_complete': len(missing) == 0,
        'missing': missing,
        'warnings': warnings
    }


# ===========================================================================
# Validazione avanzata con ValidationResult
# ===========================================================================

@dataclass
class ValidationIssue:
    """Singolo problema di validazione."""
    field: str
    severity: str  # "error" | "warning" | "info"
    message: str
    suggestion: str = ""


@dataclass
class ValidationResult:
    """Risultato di validazione con lista di issue."""
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def is_valid(self) -> bool:
        """True se nessun errore (i warning non bloccano)."""
        return len(self.errors) == 0

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        return ValidationResult(issues=self.issues + other.issues)


def validate_ranges(
    material: Dict[str, Any],
    norm_schema: Dict[str, Any],
) -> ValidationResult:
    """Valida i valori numerici contro i range definiti nello schema norma.

    Legge il campo ``validation`` da ogni parametro_input e parametri_derivati::

        {"validation": {"min": 12, "max": 100, "severity": "error"}}

    Args:
        material: Dict del materiale.
        norm_schema: Schema norma (da MaterialConfigLoader.get_norm_schema).

    Returns:
        ValidationResult con issue per ogni campo fuori range.
    """
    result = ValidationResult()

    all_params = list(norm_schema.get("parametri_input", [])) + list(
        norm_schema.get("parametri_derivati", [])
    )

    for param in all_params:
        key = param.get("key", "")
        val = material.get(key)
        validation = param.get("validation", {})
        if not validation or val is None:
            continue
        if not isinstance(val, (int, float)):
            continue

        vmin = validation.get("min")
        vmax = validation.get("max")
        severity = validation.get("severity", "warning")

        if vmin is not None and val < vmin:
            label = param.get("label", key)
            unita = param.get("unita", "")
            result.issues.append(ValidationIssue(
                field=key,
                severity=severity,
                message=f"{label} = {val} {unita} è inferiore al minimo ({vmin} {unita})",
                suggestion=f"Impostare {label} ≥ {vmin} {unita}",
            ))
        elif vmax is not None and val > vmax:
            label = param.get("label", key)
            unita = param.get("unita", "")
            result.issues.append(ValidationIssue(
                field=key,
                severity=severity,
                message=f"{label} = {val} {unita} supera il massimo ({vmax} {unita})",
                suggestion=f"Impostare {label} ≤ {vmax} {unita}",
            ))

    return result


def validate_coherence(
    material: Dict[str, Any],
    norm_schema: Optional[Dict[str, Any]] = None,
) -> ValidationResult:
    """Valida la coerenza cross-campo del materiale.

    Regole:
    - Calcestruzzo: E_inserito vs E_calcolato non divergono oltre il 15%
    - Calcestruzzo: f_cd ≤ f_ck sempre
    - Muratura: f_d ≤ f_k sempre
    - Acciaio: f_yd ≤ f_yk sempre

    Args:
        material: Dict del materiale con valori inseriti + derivati calcolati.
        norm_schema: Schema norma opzionale (non usato attualmente, per future estensioni).
    """
    result = ValidationResult()
    famiglia = material.get("famiglia", "")

    if famiglia == "calcestruzzo":
        # Coerenza E: valore inserito vs calcolato
        E_val = material.get("E")
        E_calc = material.get("E_calcolato") or material.get("E_formula")
        if isinstance(E_val, (int, float)) and isinstance(E_calc, (int, float)) and E_calc > 0:
            discrepanza = abs(E_val - E_calc) / E_calc
            if discrepanza > 0.15:
                result.issues.append(ValidationIssue(
                    field="E",
                    severity="warning",
                    message=f"E inserito ({E_val:.0f}) discosta del {discrepanza:.0%} dall'E calcolato ({E_calc:.0f})",
                    suggestion="Verificare il modulo elastico o usare il valore calcolato",
                ))

        # f_cd ≤ f_ck
        f_cd = material.get("f_cd")
        f_ck = material.get("f_ck")
        if isinstance(f_cd, (int, float)) and isinstance(f_ck, (int, float)):
            if f_cd > f_ck:
                result.issues.append(ValidationIssue(
                    field="f_cd",
                    severity="error",
                    message=f"f_cd ({f_cd:.1f}) > f_ck ({f_ck:.1f}): impossibile fisicamente",
                    suggestion="Verificare gamma_c e alpha_cc",
                ))

    elif famiglia == "acciaio":
        f_yd = material.get("f_yd")
        f_yk = material.get("f_yk")
        if isinstance(f_yd, (int, float)) and isinstance(f_yk, (int, float)):
            if f_yd > f_yk:
                result.issues.append(ValidationIssue(
                    field="f_yd",
                    severity="error",
                    message=f"f_yd ({f_yd:.1f}) > f_yk ({f_yk:.1f}): impossibile fisicamente",
                    suggestion="Verificare gamma_s",
                ))

    elif famiglia == "muratura":
        f_d = material.get("f_d")
        f_k = material.get("f_k")
        if isinstance(f_d, (int, float)) and isinstance(f_k, (int, float)):
            if f_d > f_k:
                result.issues.append(ValidationIssue(
                    field="f_d",
                    severity="error",
                    message=f"f_d ({f_d:.1f}) > f_k ({f_k:.1f}): impossibile fisicamente",
                    suggestion="Verificare gamma_M",
                ))

    return result


# Vincoli normativi per-norma ─────────────────────────────────────────────────

_NORMATIVE_RULES: Dict[str, List[Dict[str, Any]]] = {
    # Regola: {famiglia, field, min, max, severity, msg}
    "NTC2018": [
        # Calcestruzzo: f_ck ∈ [12, 90] MPa → [122.4, 917.5] kg/cm²
        {"famiglia": "calcestruzzo", "field": "f_ck",
         "min": 122.4, "max": 917.5, "severity": "error",
         "msg": "NTC2018 §11.2.1: f_ck ∈ [12, 90] MPa = [122, 917] kg/cm²",
         "suggestion": "Usare classi C12/15 … C90/105"},
        # gamma_c ∈ [1.3, 1.6]
        {"famiglia": "calcestruzzo", "field": "gamma_c",
         "min": 1.30, "max": 1.60, "severity": "warning",
         "msg": "NTC2018 Tab.4.1.II: γ_c tipicamente ∈ [1.30, 1.60]",
         "suggestion": "Valore fuori range tipico NTC2018"},
        # Acciaio: f_yk ∈ [400, 600] MPa → [4080, 6120] kg/cm²
        {"famiglia": "acciaio", "field": "f_yk",
         "min": 4080.0, "max": 6120.0, "severity": "error",
         "msg": "NTC2018 §11.3.2: f_yk ∈ [400, 600] MPa = [4080, 6120] kg/cm²",
         "suggestion": "Usare B450C, B450A o B500B"},
        # gamma_s ∈ [1.05, 1.25]
        {"famiglia": "acciaio", "field": "gamma_s",
         "min": 1.05, "max": 1.25, "severity": "warning",
         "msg": "NTC2018 Tab.4.1.II: γ_s tipicamente ∈ [1.05, 1.25]",
         "suggestion": "Valore fuori range tipico NTC2018"},
    ],
    "DM96": [
        # Rck ∈ [150, 600] kg/cm²
        {"famiglia": "calcestruzzo", "field": "sigma_c28",
         "min": 150.0, "max": 600.0, "severity": "warning",
         "msg": "DM96: Rck usualmente ∈ [150, 600] kg/cm²",
         "suggestion": "Verificare il valore di Rck"},
    ],
    "RD2229": [
        # Rck ∈ [100, 400] kg/cm²
        {"famiglia": "calcestruzzo", "field": "sigma_c28",
         "min": 100.0, "max": 400.0, "severity": "warning",
         "msg": "RD2229 art.3: Rck usualmente ∈ [100, 400] kg/cm²",
         "suggestion": "Verificare il valore di Rck (storico)"},
    ],
}


def validate_normative(
    material: Dict[str, Any],
    norm_code: Optional[str] = None,
) -> ValidationResult:
    """Valida il materiale contro i vincoli specifici di una norma.

    Args:
        material: Dict del materiale.
        norm_code: Chiave norma (es. "NTC2018"). Se None, usa norma_riferimento dal materiale.

    Returns:
        ValidationResult con issue per ogni violazione normativa.
    """
    result = ValidationResult()
    norma = norm_code or material.get("norma_riferimento") or material.get("norma", "")
    famiglia = material.get("famiglia", "")

    rules = _NORMATIVE_RULES.get(norma, [])
    for rule in rules:
        if rule.get("famiglia") and rule["famiglia"] != famiglia:
            continue
        field_key = rule["field"]
        val = material.get(field_key)
        if val is None or not isinstance(val, (int, float)):
            continue
        vmin = rule.get("min")
        vmax = rule.get("max")
        violated = (vmin is not None and val < vmin) or (vmax is not None and val > vmax)
        if violated:
            result.issues.append(ValidationIssue(
                field=field_key,
                severity=rule.get("severity", "warning"),
                message=rule.get("msg", f"{field_key} fuori range normativo"),
                suggestion=rule.get("suggestion", ""),
            ))

    return result


def validate_full(
    material: Dict[str, Any],
    norm_schema: Optional[Dict[str, Any]] = None,
    norm_code: Optional[str] = None,
) -> ValidationResult:
    """Esegue tutti i livelli di validazione e restituisce il risultato unificato.

    Ordine: soft → ranges → coherence → normative.
    """
    # Soft (campi obbligatori)
    soft = validate(material)
    result = ValidationResult()
    for m in soft.get("missing", []):
        result.issues.append(ValidationIssue(
            field=m, severity="warning", message=f"Campo obbligatorio mancante: {m}"
        ))

    # Ranges da schema
    if norm_schema:
        result = result.merge(validate_ranges(material, norm_schema))

    # Coerenza cross-campo
    result = result.merge(validate_coherence(material, norm_schema))

    # Normativa per-norma
    result = result.merge(validate_normative(material, norm_code))

    return result
