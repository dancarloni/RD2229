# Analisi Stub DM72/DM74 — Torsione e Punzonamento

**Data ricerca**: 2026-03-29 | **Scope**: Identificare blocker critici + opzioni fix

---

## 1. PROBLEMA IDENTIFICATO

Due moduli normative contengono **stub falsi che ritornano OK=True**:

- `src/methods/dm72/checks.py:551-605` — 2 funzioni STUB
- `src/methods/dm74/checks.py:476-515` — 2 funzioni STUB (identiche a DM72)

### Funzioni problematiche

| Funzione | Norma | Stato | Problema |
|----------|-------|-------|----------|
| `check_torsione_ta_dm72()` | DM 30/05/1972 | STUB | Ritorna OK=True senza calcolo |
| `check_punzonamento_ta_dm72()` | DM 30/05/1972 | STUB | Ritorna OK=True senza calcolo |
| `check_torsione_ta_dm74()` | DM 30/05/1974 | STUB | Identico a DM72 |
| `check_punzonamento_ta_dm74()` | DM 30/05/1974 | STUB | Identico a DM72 |

### Codice stub (esempio DM72)

```python
def check_torsione_ta_dm72(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica torsione secondo DM 30/05/1972 (STUB)."""
    messages_it = [
        "Torsione DM 30/05/1972 — STUB NON IMPLEMENTATO",
        "TODO: Implementare verifica torsione...",
    ]

    return SingleCheckResult(
        ok=True,  # ❌ FALSO! Non ha fatto nessun calcolo!
        norm_reference={"decreto": "DM 30/05/1972", "norma": "torsione TA"},
        messages_it=messages_it,
        details_json={"status": "NOT_IMPLEMENTED"},
    )
```

### Impatto

| Aspetto | Impatto | Severità |
|---------|---------|----------|
| **Verifiche DM72/74** | Sempre ritornano OK (anche se non implementate) | 🔴 CRITICA |
| **Risultati ingegneristici** | Falsi positivi (strutture approvate senza verifica) | 🔴 CRITICA |
| **Test suite** | Test passano anche se verifiche non implementate | 🟠 ALTA |
| **Usabilità** | Utente non sa che DM72/74 non sono supportati | 🟠 ALTA |
| **Linea codice** | ~55 linee di codice morto | 🟢 BASSA |

---

## 2. OPZIONI DI FIX

### ✅ OPZIONE A: Rimuovere moduli (Consigliato)

**Azione**:
1. Rimuovere `src/methods/dm72/` directory completamente
2. Rimuovere `src/methods/dm74/` directory completamente
3. Rimuovere import in pipeline (P01-P06) se presente
4. Update ARCHITECTURE.md per remover DM72/74 dalla lista norme supportate

**Pro**:
- ✅ Clean codebase (no dead code)
- ✅ No false positives
- ✅ Chiarisce che DM72/74 non sono supportati

**Contro**:
- ❌ Rimuove opzione futura di supportare DM72/74
- ❌ Breaking change se qualcuno usa DM72/74 (unlikely)

**Costo implementazione**: ~10 minuti

---

### 🔄 OPZIONE B: Marcare @deprecated + raise NotImplementedError (Conservativo)

**Azione**:
1. Aggiungere decorator `@deprecated` a entrambe le funzioni
2. Cambiare `return SingleCheckResult(ok=True)` con `raise NotImplementedError()`
3. Update docstring con motivo deprecation + data rimozione (es. 2026-06-01)
4. Aggiungere warning in docstring: "DM72/74 non supportati — usare DM96 o NTC2018"

**Pro**:
- ✅ Fail loudly invece di silent false positive
- ✅ Possibilità futura di implementare
- ✅ Gradual deprecation (warning→error→removal)

**Contro**:
- ❌ Più codice di supporto (deprecated wrapper)
- ❌ Prolonga il problema

**Costo implementazione**: ~15 minuti

---

### ❌ OPZIONE C: Implementare formule DM72/74 (Costoso)

**Azione**:
1. Ricercare formule DM 30/05/1972 e 30/05/1974 (online, PDF, letteratura)
2. Implementare `check_torsione_ta_dm72()` con logica di calcolo reale
3. Implementare `check_punzonamento_ta_dm72()` con logica di calcolo reale
4. Replicare in DM74 (norme storiche sono molto simili)
5. Aggiungere test benchmark

**Pro**:
- ✅ DM72/74 fully supported
- ✅ Completezza storica

**Contro**:
- ❌ 50-100 ore di lavoro (ricerca, implementazione, test)
- ❌ DM72/74 sono **obsoleti** (non usati in pratica moderna)
- ❌ ROI basso (2 norme non più in uso)

**Costo implementazione**: ~50-100 ore

---

## 3. RACCOMANDAZIONE

**OPZIONE A (Rimuovere moduli)** è consigliata.

**Motivi**:
1. **DM72/74 sono obsoleti** — RD2229/1939 < DM 30/05/1972 < DM 30/05/1974 < DM 14/02/1992 < **DM 09/01/1996** ← Modern starting point
2. **False positives sono pericolosi** — Better to fail loudly
3. **Zero ROI** — Nessun utente moderno usa DM72/74
4. **Code quality** — Rimuovere dead code mantiene codebase pulito
5. **Veloce** — 10 minuti di lavoro

---

## 4. PIANO DI IMPLEMENTAZIONE (OPZIONE A)

### Step 1: Rimuovere moduli
```bash
rm -rf src/methods/dm72/
rm -rf src/methods/dm74/
```

### Step 2: Audit import
```bash
grep -r "dm72\|dm74\|DM72\|DM74" src/ tests/ docs/ --include="*.py" --include="*.md"
```

### Step 3: Update pipeline se necessario
- Verificare che P01-P06 non includano DM72/74
- Se includono, rimuovere step

### Step 4: Update documentazione
- ARCHITECTURE.md: Rimuovere DM72/74 dalla lista norme
- CLAUDE.md: Aggiornare norme coperte
- PIANO_LAVORO.md: Nota di rimozione

### Step 5: Update test
- Rimuovere `tests/test_dm72.py`, `tests/test_dm74.py` se esistono
- Verificare che nessun test dipenda da DM72/74

### Step 6: Commit
```bash
git commit -m "Sprint B2: Rimuovere moduli stub DM72/DM74 (obsoleti, false positives)
- Removed src/methods/dm72/, src/methods/dm74/
- Rationale: norme obsolete post-1972, false positives risk
- DM96 + NTC2018 sono standard attuali"
```

---

## 5. TESTING STRATEGY

Dopo rimozione, verificare:

1. **Pipeline runs** — Nessun test fallisce
2. **Import check** — Nessun import a dm72/dm74 rimasto
3. **Documentation consistency** — Norme documentate = implementate
4. **Coverage** — Test count non cambia (nessun test orfano)

---

## 6. TIMELINE

- **Sprint B2** (Sessione 3-4): Implementare Opzione A
- **Effort**: 20-30 minuti (audit + removal + testing)
- **Risk**: Bassa (nessuno usa DM72/74)
- **Impact**: Codice più pulito, risultati più affidabili

---

**Documento**: Sprint B2 Analysis | **Status**: Ready for decision
**Modello LLM**: Sonnet 4.6 | **Autore**: Claude AI (2026-03-29)
