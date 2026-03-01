<<<<<<< HEAD
# Modulo: `core_calculus`

## 1. Scopo e ambito

Motore principale di calcolo strutturale: proprietà di sezione, stati tensionali, verifiche a flessione/pressoflessione/taglio per metodo TA/SLU/SLE. Include il registro normativo con template per RD2229, DM96, NTC2018, incendio.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `normative_registry.py` (1217 righe) contiene template `VerificationTemplate` reali per NTC2018/RD2229/DM96/Fire. `verification_core.py` (655 righe) implementa calcolo asse neutro, stati tensionali, flessione/taglio. `section_calculations.py` (907 righe) calcola proprietà geometriche. `validation_engine.py` (655 righe) valida `CalcInput`. Test su 11+ file.

## 3. Evidenze

- `src/core_calculus/normative_registry.py:1217` — template NTC2018/RD2229/DM96/Fire
- `src/core_calculus/core/verification_core.py` — calcolo asse neutro, tensioni, flessione/taglio
- `src/core_calculus/section_calculations.py` — area, inerzia, baricentro
- `src/core_calculus/validation_engine.py` — validazione `CalcInput`
- Test: `tests/test_verification_pipeline.py`, `tests/test_section_calculations.py`, `tests/test_ntc2018_checks.py`, `tests/test_lc_fc_adjustments.py`, `tests/test_geometry_cache.py`, `tests/test_adapter_and_properties.py` (+5)

## 4. Input/parametri

- `CalcInput` (dataclass in `contracts.py`): `b`, `h`, `As1`, `As2`, `fck`, `fyk`, `MEd`, `NEd`, `VEd`, `norm_code`
- `run_verifications_for_element(element, material, section) -> List[VerificationResult]`

## 5. Output

- `VerificationResult` (dataclass): `check_id`, `passed`, `ratio`, `details`, `norm_ref`
- `SectionProperties`: area, inerzia, baricentro, armatura

## 6. Dipendenze

- `src/core_calculus/contracts.py` — dataclass pubbliche
- `src/core_calculus/core/geometry_model.py` — modello geometria
- Nessuna dipendenza da altri moduli `src/` (autosufficiente)

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| NTC2018 | `src/core_calculus/normative_registry.py` — template SLU/SLE/Fire |
| RD2229 | `src/core_calculus/normative_registry.py` — template TA |
| DM96 | `src/core_calculus/normative_registry.py` — template SLU/SLE DM96 |
| EN 1992-1-2 | `src/core_calculus/normative_registry.py` — clausole incendio |

Clausole: TBD (compaiono come ID stringhe ma non come §articolo verificabile nel codice).

## 8. Gap/TODO/Limitazioni

- `core/materials.py` e `core/reinforcement.py`: molto brevi (19/26 righe), probabilmente incompleti
- `core/examples_sections.py`: solo dati di esempio
- Alcuni TODO in `verification_core.py` per casi degeneri

## 9. Next steps

- [ ] Completare `core/materials.py` con modelli constitutivi completi
- [ ] Aggiungere test golden per ogni template normativo in `normative_registry.py`
- [ ] Documentare le clausole normative esatte per ciascun template
=======
# Documentazione Modulo: `core_calculus`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `core_calculus` |
| **Path** | `src/core_calculus` |
| **Tipo** | package |
| **File .py rilevati** | 21 |
| **Stato** | INCOMPLETO |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

> Descrivere in 2-3 righe il *perché* esiste questo modulo e quale problema risolve.

TBD

---

## 3. File / Classi / Funzioni principali

> Elencare i simboli pubblici rilevanti. Non inventare: se non si conosce la firma esatta, annotare TBD.

| File | Classe/Funzione | Descrizione |
|------|-----------------|-------------|
| TBD | TBD | TBD |

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | TBD | TBD |
| Output | TBD | TBD |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| — | — | Nessun test rilevato meccanicamente. |

---

## 6. Fonti normative

> Solo riferimenti a ID da `docs/NORMATIVE_SOURCES/sources.catalog.json`. NESSUN testo copiato.

| ID fonte | Clausola/Articolo | Nota |
|----------|-------------------|------|
| TBD | TBD | — |

---

## 7. Dipendenze interne

> Moduli `src/` da cui questo modulo dipende (import diretti).

- TBD

---

## 8. Note e TODO

- [ ] Compilare sezioni TBD
- [ ] Verificare test correlati
- [ ] Tracciare fonti normative di riferimento
>>>>>>> d5ef881 (feat: audit/docs infrastructure - audit_repo, RTM, governance, normative catalog, module docs)
