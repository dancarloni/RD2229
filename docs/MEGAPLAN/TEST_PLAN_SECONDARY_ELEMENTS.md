docs/MEGAPLAN/TEST_PLAN_SECONDARY_ELEMENTS.md e tests)
VRd,c (unit tests)
Case A (PASS): inputs (vedi SPEC). Expected: status=OK, V_Rd,c ≈ 96.0 kN, utilisation ≈ 0.625. Assumption: γ_c=1.5 (confirm NA).
Case B (FAIL): expected status=NOT_OK.
Case D (axial): expected V_Rd,c ≈ 156.8 kN (with σ_cp=3 MPa, γ_c=1.5).
Boundary case for v_min: check V_Rd,c ≥ v_min (v_min ≈ 55.7 kN for Case A).
Secondary templates (integration tests; expected status only)
Cantilever basic: expect bending OK / anchor check depending on embedment (define accepted embedment).
Signage (wind dominated): expect anchor capacity check → status per ETA values (TODO: attach ETA).
Partition: SLE deflection & cracking tests (expected PASS/FAIL per thresholds in DM96).
Chimney: stability / overturning check (expected: PASS for short chimney, FAIL for high wind case).
Note: numerical expected values that depend on NA or ETA are marked TODO until source attached.

- Fixture SE-NA-01: elemento non applicabile per geometria
- Fixture SE-OK-01: elemento conforme