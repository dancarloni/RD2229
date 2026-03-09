# Verification Gap Analysis

## Layout sorgenti confermato

- Sorgenti principali: `src/`
- Core calculus: `src/core_calculus/`
- Verification engine legacy: `src/core_calculus/core/verification_engine.py`
- Contratti dati: `src/core_calculus/contracts.py`
- Check registry: `src/checks/registry.py`
- Normative registry: `src/core_calculus/normative_registry.py`
- Secondary elements: `src/codes/ntc2018/secondary_elements/`
- Test: `tests/`
- Docs: `docs/`

## Cosa è già presente (derivato da Issue #42 e sub-issue merge)

- `VerificationEngine` legacy per TA/SLU/SLE (singola norma)
- `CheckRegistry` con CheckSpec per RD2229/DM96/NTC2018/fire/wind
- `NormReference`, `VerificationTemplate`, `CalcInput`, `CalcOutput`, `SingleCheckResult`
- `SecondaryElementSpec` con `DriftSpec`
- `normative_registry.py` con template per NTC2018/RD2229/DM96
- GUI skip pattern in `conftest.py`
- CI workflows: `python-ci.yml`, `lint-test.yml`

## Gap residui per questa sub-issue

1. ✅ `ElementRole` enum (PRIMARY/SECONDARY/UNDETERMINED) — IMPLEMENTATO
2. ✅ Classificazione automatica primario/secondario — IMPLEMENTATO
3. ✅ Adapter pattern multi-norma (`NormAdapter` ABC) — IMPLEMENTATO
4. ✅ NTC2018 adapter (ULS pressoflessione + taglio) — IMPLEMENTATO
5. ✅ RD2229 adapter (TA pressoflessione + taglio) — IMPLEMENTATO
6. ✅ `VerifierManager` orchestratore — IMPLEMENTATO
7. ✅ Serializzazione JSON (`calc_output_to_dict`) — IMPLEMENTATO
8. ✅ Test unitari + integration test — IMPLEMENTATO (31 test)

## Non fare / Non duplicare

- Non modificare `VerificationEngine` legacy in `verification_engine.py`
- Non creare nuovi entry per `CheckRegistry` (esiste già)
- Non duplicare `normative_registry.py` templates
- Non toccare legacy GUI Tkinter
- Non modificare `conftest.py` pattern
