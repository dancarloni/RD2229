# Verification Module — UML

## Class Diagram

```
┌──────────────────────────────────┐
│         <<enum>>                 │
│         ElementRole              │
├──────────────────────────────────┤
│ PRIMARY                          │
│ SECONDARY                        │
│ UNDETERMINED                     │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│         CalcInput                │
├──────────────────────────────────┤
│ element_name: str                │
│ section: Any                     │
│ material: Any                    │
│ norm_code: str                   │
│ element_role: ElementRole        │
│ N, Mx, My, Tx, Ty: float?       │
│ As, d: float?                    │
│ extra: dict                      │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│         CalcOutput               │
├──────────────────────────────────┤
│ element_name: str                │
│ norm_code: str                   │
│ ok: bool                         │
│ element_role: ElementRole        │
│ profile_used: str                │
│ per_template_results: dict       │
│ summary_metrics: dict            │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      <<abstract>>                │
│       NormAdapter                │
├──────────────────────────────────┤
│ + norm_code: str                 │
│ + description_it: str            │
│ + applicability(CalcInput)       │
│     → EligibilityResult          │
│ + verify(CalcInput) → CalcOutput │
└──────┬──────────────┬────────────┘
       │              │
       ▼              ▼
┌──────────────┐ ┌──────────────┐
│Ntc2018Adapter│ │Rd2229Adapter │
├──────────────┤ ├──────────────┤
│ULS bending   │ │TA bending    │
│ULS shear     │ │TA shear      │
└──────────────┘ └──────────────┘

┌──────────────────────────────────┐
│       VerifierManager            │
├──────────────────────────────────┤
│ - _adapters: list[NormAdapter]   │
│ + available_norms: list[str]     │
│ + verify(CalcInput) → CalcOutput │
│ + verify_bulk(list) → list       │
│ + check_applicability()          │
└──────────────────────────────────┘
```

## Sequence Diagram — verify()

```
Client          VerifierManager    classify_element    NormAdapter
  │                  │                   │                 │
  │  verify(input)   │                   │                 │
  │─────────────────>│                   │                 │
  │                  │  classify(type)   │                 │
  │                  │──────────────────>│                 │
  │                  │   role=PRIMARY    │                 │
  │                  │<─────────────────-│                 │
  │                  │                   │                 │
  │                  │  applicability(input)               │
  │                  │───────────────────────────────────->│
  │                  │   eligible=True                     │
  │                  │<───────────────────────────────────-│
  │                  │                                     │
  │                  │  verify(input)                      │
  │                  │───────────────────────────────────->│
  │                  │   CalcOutput                        │
  │                  │<───────────────────────────────────-│
  │   CalcOutput     │                                     │
  │<─────────────────│                                     │
```
