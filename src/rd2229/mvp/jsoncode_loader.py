from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class JsonCodeConfig:
    id: str
    version: str
    namespace: str
    check_code: str
    provenance: dict[str, str]
    payload: dict[str, Any]


def load_jsoncode_config(path: str) -> JsonCodeConfig:
    raw = _read_json(path)
    _validate_jsoncode(raw)
    payload = dict(raw["payload"])
    check_code = str(payload.get("check_code") or raw["id"])
    provenance_raw = payload.get("provenance") or {}
    return JsonCodeConfig(
        id=str(raw["id"]),
        version=str(raw["version"]),
        namespace=str(raw["namespace"]),
        check_code=check_code,
        provenance={str(k): str(v) for k, v in dict(provenance_raw).items()},
        payload=payload,
    )


def _read_json(path: str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(".jsoncode root must be an object")
    return data


def _validate_jsoncode(raw: dict[str, Any]) -> None:
    required = ("id", "version", "namespace", "payload")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Missing required keys in .jsoncode: {', '.join(missing)}")
    payload = raw["payload"]
    if not isinstance(payload, dict):
        raise ValueError(".jsoncode payload must be an object")

    threshold = payload.get("threshold")
    if threshold is None:
        raise ValueError(".jsoncode payload.threshold is required")
    if not isinstance(threshold, (int, float)):
        raise ValueError(".jsoncode payload.threshold must be numeric")
    if float(threshold) <= 0.0:
        raise ValueError(".jsoncode payload.threshold must be > 0")

    refs = payload.get("norm_references")
    if not isinstance(refs, list) or not refs:
        raise ValueError(".jsoncode payload.norm_references must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in refs):
        raise ValueError(".jsoncode payload.norm_references items must be non-empty strings")

    check_code = payload.get("check_code")
    if check_code is not None and (not isinstance(check_code, str) or not check_code.strip()):
        raise ValueError(".jsoncode payload.check_code must be a non-empty string when provided")

    provenance = payload.get("provenance")
    if provenance is not None:
        if not isinstance(provenance, dict):
            raise ValueError(".jsoncode payload.provenance must be an object")
        for key, value in provenance.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(".jsoncode payload.provenance keys must be non-empty strings")
            if not isinstance(value, str) or not value.strip():
                raise ValueError(".jsoncode payload.provenance values must be non-empty strings")
