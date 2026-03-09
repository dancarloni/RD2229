# Verification Engine — Architecture

## Overview

The verification engine provides multi-norm structural verification for
RC elements (beams, columns, walls) using an adapter pattern. Each norm
(NTC2018, RD2229, etc.) is implemented as an independent adapter.

## Components

### CalcInput / CalcOutput (contracts.py)

Pure domain data types. `CalcInput` carries element geometry, material,
actions, and normative context. `CalcOutput` aggregates per-check results
with JSON-serializable output.

### ElementRole (contracts.py)

Enum: `PRIMARY`, `SECONDARY`, `UNDETERMINED`. Determines the verification
profile applied.

### NormAdapter (adapters/base.py)

Abstract base class with:

- `applicability(CalcInput) → EligibilityResult`
- `verify(CalcInput) → CalcOutput`

### Ntc2018Adapter (adapters/ntc2018_adapter.py)

ULS checks per NTC 2018 §4.1.2:

- Pressoflessione retta (bending + axial)
- Taglio (shear, concrete only)

### Rd2229Adapter (adapters/rd2229_adapter.py)

TA checks per R.D. 2229/1939:

- Pressoflessione retta (elastic method)
- Taglio (allowable shear stress)

### VerifierManager (verifier_manager.py)

Orchestrates adapter selection, auto-classification, and bulk verification.

### classify_element (classification.py)

Configurable rule-based classification of elements as primary/secondary
per NTC2018 §7.2.3.

## JSON Output Example

```json
{
  "element_name": "Trave T1",
  "norm_code": "NTC2018",
  "ok": true,
  "element_role": "PRIMARY",
  "profile_used": "PROFILE_PRIMARY_FULL",
  "summary_metrics": {
    "status": "OK",
    "utilizzazione_massima": 0.58
  },
  "checks": {
    "ntc2018_slu_pressoflessione": {
      "ok": true,
      "utilisation": 0.58,
      "details": {"M_Ed_kNm": 50.0, "M_Rd_kNm": 85.5},
      "norm_references": [
        {"norm_code": "NTC2018", "chapter": "4.1", "paragraph": "4.1.2.1.3.1"}
      ]
    }
  }
}
```

## Extending with New Adapters

1. Create a new class inheriting from `NormAdapter`
2. Implement `norm_code`, `description_it`, `applicability()`, `verify()`
3. Register with `VerifierManager.register_adapter()`
