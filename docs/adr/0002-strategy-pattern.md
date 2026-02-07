# ADR 0002 — Strategy selection for verification methods

Decision: Use a `VerificationMethod` Protocol and a registry for method implementations (TA/SLU/SLE/Santarella). Methods implement `compute(inputs) -> dict` and report applicability.

Rationale: Provides extensibility and allows adding new historical methods without touching engine code.
