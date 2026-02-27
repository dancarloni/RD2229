"""
MVP Report Builder — Stream E1.

Genera un report JSON auditabile a partire da un VerificationResult.
Il report include tutti i campi obbligatori per la tracciabilità compliance:
    - run_id, project_id, result_id
    - status, method_id, norm_references, norm_code
    - value, check_code
    - generated_at (ISO 8601 UTC)
    - input_hash (SHA-256 hex dei parametri input serializzati)
    - plugin_versions (dict id → version)
    - schema_version

Non dipende da GUI, PySide6 o altro layer di presentazione.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import VerificationResult

REPORT_SCHEMA_VERSION = "1.0.0"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class ReportArtifact:
    """Report JSON auditabile per una singola verifica MVP.

    Campi obbligatori (contratto E1):
        run_id, project_id, result_id, status, method_id,
        norm_references, norm_code, value, check_code,
        generated_at, input_hash, plugin_versions, schema_version.
    """

    run_id: str
    project_id: str
    result_id: str
    status: str
    method_id: str
    norm_references: list[str]
    norm_code: str
    value: float
    check_code: str
    generated_at: str
    input_hash: str
    plugin_versions: dict[str, str]
    schema_version: str = REPORT_SCHEMA_VERSION
    assumptions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _hash_inputs(inputs: dict[str, Any]) -> str:
    """SHA-256 hex degli input serializzati (JSON canonico, sorted keys).

    Nota: ``default=str`` è intenzionale per l'hashing — converte oggetti
    non-serializzabili in stringa per garantire un hash stabile.
    """
    serialized = json.dumps(inputs, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def build_report(
    result: VerificationResult,
    *,
    plugin_versions: dict[str, str] | None = None,
    extra_inputs: dict[str, Any] | None = None,
) -> ReportArtifact:
    """Costruisce un ReportArtifact da un VerificationResult.

    Args:
        result: Il risultato della verifica MVP.
        plugin_versions: Dizionario {plugin_id: version} dei plugin attivi.
        extra_inputs: Dati aggiuntivi da includere nell'hash degli input
            (es. parametri della sezione, carichi, etc.).

    Returns:
        ReportArtifact con tutti i campi obbligatori compilati.
    """
    inputs_for_hash: dict[str, Any] = {
        "result_id": result.id,
        "request_id": result.request_id,
        "project_id": result.project_id,
        "value": result.value,
        "method_id": result.trace.method_id,
        "norm_code": result.trace.norm_code,
        "assumptions": sorted(result.trace.assumptions),
    }
    if extra_inputs:
        inputs_for_hash.update(extra_inputs)

    return ReportArtifact(
        run_id=result.trace.run_id,
        project_id=result.project_id,
        result_id=result.id,
        status=result.status,
        method_id=result.trace.method_id,
        norm_references=list(result.trace.norm_references),
        norm_code=result.trace.norm_code,
        value=result.value,
        check_code=result.trace.method_id,
        generated_at=_utc_now_iso(),
        input_hash=_hash_inputs(inputs_for_hash),
        plugin_versions=dict(plugin_versions or {}),
        assumptions=list(result.trace.assumptions),
        warnings=list(result.trace.warnings),
    )


def report_to_dict(report: ReportArtifact) -> dict[str, Any]:
    """Converte il report in dizionario serializzabile JSON."""
    return asdict(report)


def report_to_json(report: ReportArtifact, *, indent: int = 2) -> str:
    """Serializza il report in JSON (UTF-8)."""
    return json.dumps(report_to_dict(report), ensure_ascii=False, indent=indent)


def export_report_json(
    report: ReportArtifact,
    path: str | Path,
) -> Path:
    """Esporta il report in un file JSON con scrittura atomica.

    Args:
        report: Il report da esportare.
        path: Percorso del file di destinazione.

    Returns:
        Il percorso del file scritto.
    """
    dest = Path(path)
    tmp = dest.with_suffix(".tmp")
    try:
        tmp.write_text(report_to_json(report), encoding="utf-8")
        tmp.replace(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    return dest


def validate_report_contract(report: ReportArtifact) -> None:
    """Verifica che il report rispetti il contratto E1 obbligatorio.

    Raises:
        ValueError: se un campo obbligatorio è mancante o invalido.
    """
    if not report.run_id.strip():
        raise ValueError("ReportArtifact.run_id deve essere non vuoto")
    if not report.project_id.strip():
        raise ValueError("ReportArtifact.project_id deve essere non vuoto")
    if not report.result_id.strip():
        raise ValueError("ReportArtifact.result_id deve essere non vuoto")
    if report.status not in {"OK", "WARN", "FAIL"}:
        raise ValueError(f"ReportArtifact.status invalido: {report.status}")
    if not report.method_id.strip():
        raise ValueError("ReportArtifact.method_id deve essere non vuoto")
    if not report.norm_references:
        raise ValueError("ReportArtifact.norm_references deve essere non vuota")
    if not report.norm_code.strip():
        raise ValueError("ReportArtifact.norm_code deve essere non vuoto")
    if not report.check_code.strip():
        raise ValueError("ReportArtifact.check_code deve essere non vuoto")
    if not report.generated_at.strip():
        raise ValueError("ReportArtifact.generated_at deve essere non vuoto")
    if len(report.input_hash) != 64:
        raise ValueError("ReportArtifact.input_hash deve essere un SHA-256 hex (64 chars)")
    if not report.schema_version.strip():
        raise ValueError("ReportArtifact.schema_version deve essere non vuoto")
