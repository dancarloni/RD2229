# MODULE CONTRACTS

> Fonte primaria: `docs/MEGAPLAN/AGGREGAZIONE.md` — LOCKED

## Contratto risultato verifica (VerificationResult)

```python
@dataclass(frozen=True)
class VerificationResult:
    id: str                   # UUID hex, non vuoto
    request_id: str           # riferimento a CheckRequest
    project_id: str           # riferimento a Project
    status: Literal["OK", "WARN", "FAIL"]
    value: float              # valore calcolato (rapporto, domanda, etc.)
    trace: TraceRecord        # obbligatorio
    created_at: str           # ISO 8601 UTC
```

## Contratto trace (TraceRecord) — OBBLIGATORIO

```python
@dataclass(frozen=True)
class TraceRecord:
    run_id: str               # UUID hex, non vuoto
    norm_code: str            # codice norma attiva (es. "NTC2018")
    norm_references: list[str]  # ≥ 1 elemento; può essere "TODO(NTC/EC/RD):..."
    method_id: str            # identificatore metodo/check, non vuoto
    assumptions: list[str]    # lista ipotesi (può essere vuota)
    warnings: list[str]       # lista warning (può essere vuota)
```

**Invariante**: `validate_result_contract(result)` deve passare senza eccezioni.

## Contratto CheckRequest

```python
@dataclass(frozen=True)
class CheckRequest:
    id: str
    project_id: str
    element_id: str
    combination_id: str
    check_code: str           # es. "MVP_REAL_MIN", "SLU", "SLE"
    parameters: dict          # parametri aggiuntivi opzionali
```

## Contratto Engine (PlaceholderVerificationEngine / futuro)

- Input: `request`, `element`, `load_case`, `combination`, `config`
- Output: `VerificationResult` che supera `validate_result_contract`
- Invariante: non lancia eccezioni su input validi; aggiunge `warnings` su input incompleti
- Non dipende da GUI o persistenza

## Contratto Plugin (ModuleSpec)

```python
@dataclass
class ModuleSpec:
    id: str                   # identificatore univoco
    version: str              # semver
    description: str
    capabilities: list[str]   # es. ["structural_check", "fire_check"]
    contracts: list[str]      # contratti implementati
    compatible: bool = True   # se False: plugin disabilitato con warning
```

## Contratto Report (MVP)

- Campi obbligatori: `run_id`, `project_id`, `result_id`, `status`, `method_id`, `norm_references`, `norm_code`, `value`, `generated_at`, `check_code`
- Campi audit: `input_hash`, `plugin_versions`, `schema_version`
- Formato primario: JSON
- Formato secondario (futuro): HTML, PDF
