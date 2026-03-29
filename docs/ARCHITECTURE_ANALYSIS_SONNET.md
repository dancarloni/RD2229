# Architettura RD2229 — Analisi Approfondita Sonnet

**Generato**: 2026-03-29 | **Modello**: Claude Sonnet 4.6 | **Scope**: Grafo dipendenze, metriche, percorsi dati, consigli refactoring

---

## EXECUTIVE SUMMARY

Architettura RD2229 ha **4 HUB critici** (criticità 10-60):

1. **pipeline/module_registry.py** — IN: 27, OUT: 2 → **Criticità 54** ⭐⭐⭐⭐⭐
   - Entry point registrazione moduli, punto di estensione centrale

2. **core_models/materials.py** — IN: 20+, OUT: 3 → **Criticità 60** ⭐⭐⭐⭐⭐
   - Modello dati più condiviso, Material.id è chiave di lookup ovunque

3. **shared/ui/base_module_window.py** — IN: 10, OUT: 2 → **Criticità 20** ⭐⭐⭐⭐
   - Base class per tutti i 10 moduli GUI, interfaccia utente uniforme

4. **src/core_calculus/contracts.py** — IN: 10, OUT: 1 → **Criticità 10** ⭐⭐⭐
   - Contratti I/O (CalcInput/CalcOutput), foglia isolata ma dati critici

---

## 1. GRAFO DIPENDENZE COMPLETO

### Layer Architecture

```
LAYER 0 — ENTRY POINTS
  dashboard/gui/main_window.py   ui/module_selector.py   tools/*.py
                        │
                        ▼ usa
LAYER 1 — ORCHESTRATION [HUB CRITICO]
  pipeline/module_registry.py   src/core/pipeline.py   orchestrator.py
                    │        │        │
              ┌─────┼────────┼────────┴─────┐
              ▼     ▼        ▼              ▼
LAYER 2 — MODULES (10 calcolo) + SHARED (modelli, UI) + REPORTING
              │
              ▼
LAYER 3 — CORE CALCULUS (verification_core.py, verifier_manager.py)
              │
              ▼
LAYER 4 — DOMAIN MODELS [HUB DATI]
  core_models/materials.py   src/project/schema.py   contracts.py
              │
              ▼
LAYER 5 — NORM METHODS [FOGLIE]
  src/methods/rd2229/   src/methods/ntc2018/   src/wind/
```

### Grafo Mermaid (semplificato)

```
Entry Points (UI/CLI/tools)
    ↓
[★] pipeline/module_registry (Criticità 54)
    ↓ coordina
10 moduli verifiche → [★] shared/ui/base_module_window (Criticità 20)
    ↓ usano
[★] core_models/materials (Criticità 60)
    ↓
[★] src/core_calculus/contracts (Criticità 10)
    ↓
src/methods/*/checks.py [FOGLIE]
    ↓
reporting/engine/ → relazione tecnica
```

---

## 2. METRICHE CONNETTIVITÀ DETTAGLIATE

| Modulo | In-degree | Out-degree | Criticità | Tipo |
|--------|-----------|-----------|-----------|------|
| `pipeline/module_registry.py` | 27 | 2 | **54** | HUB CRITICO |
| `core_models/materials.py` | 20+ | 3 | **60** | HUB DATI |
| `shared/ui/base_module_window.py` | 10 | 2 | **20** | HUB UI |
| `src/core_calculus/contracts.py` | 10 | 1 | **10** | HUB CONTRACTS |
| `src/core_calculus/verification_engine.py` | 5 | 3 | **15** | INTERMEDIARIO |
| `src/project/schema.py` | 6 | 1 | **6** | INTERMEDIARIO |
| `src/methods/rd2229/checks.py` | 2 | 3 | **6** | FOGLIA |
| `reporting/engine/collector.py` | 1 | 1 | **1** | FOGLIA |
| `shared/norms/engine/norm_material_map.py` | 0 | 1 | **0** | FOGLIA ISOLATA ⚠️ |
| `reporting/engine/report_builder.py` | 0 | 0 | **0** | FOGLIA ISOLATA ⚠️ |

**Foglie isolate** (0 dipendenti attivi):
- `norm_material_map.py` — mapping norma→materiali non utilizzato in produzione
- `report_builder.py` — generator markdown/html/export standalone, non integrato

---

## 3. DUPLICAZIONI CRITICHE

| Classe | Definizioni | Localizzazioni | Problema |
|--------|------------|-----------------|----------|
| `SectionGeometry` | 6 | apps/, core_calculus/, softw_components/ | **Incompatibili tra loro** |
| `LoadCondition` | 2 | pipeline/module_registry, shared/loads/engine | Versioni diverse (str vs Enum) |
| `MaterialProperties` | Locale | verification_core.py | Non condivisa |
| `VerificationInput` | 2 | src/domain/ + app proxy | Duplicazione tramite importlib |

---

## 4. PERCORSI DATI CRITICI

### Flusso principale (Moderno)

```
ProjectModel (Pydantic)
    ↓
src/core/pipeline.py
    ↓
src/core_calculus/verification_service.py
    ↓
CalcInput → VerifierManager → NormAdapter (NTC2018/RD2229)
    ↓
CalcOutput (strutturato, SingleCheckResult)
    ↓
ResultsModel → reporting/ → Relazione tecnica
```

### Flusso alternativo (Legacy — PATH B)

```
VerificationInput (dispatcher legacy)
    ↓
src/methods/verification/dispatcher.py
    ↓
VerificationOutput (flat dict-like)
```

**Problema**: Entrambi i percorsi coesistono senza bridge formale.

### Colli di bottiglia

1. **module_registry.py** — Tutti i moduli lo importano → punto di rottura singolo
2. **materials.py** — 20+ dipendenti sparsi senza interfaccia astratta
3. **DOPPIO SISTEMA VERIFICA** — CalcInput vs VerificationInput → duplicazione logica, inconsistenza

---

## 5. HUB CRITICI — CONSIGLI DETTAGLIATI

### HUB 1: `pipeline/module_registry.py`

**Status**: ⭐⭐⭐⭐⭐ Criticità 54

**Cosa PROTEGGERE**:
- Firme `ModuleEngine` (validate_input, run, run_batch)
- Dataclass `ModuleResult` (I/O standard)
- Metodo `ModuleRegistry.register()`

**Cosa può diventare PLUGIN**:
- ModuleInfo.extra_metadata: dict (parametri norma-specifici)
- run_batch() progress callback opzionale

**Rischi di modifica**:
- Aggiungere campo obbligatorio a ModuleEngine → Rompe 10 dispatcher
- Rinominare ModuleResult.checks_slu → Rompe reporting + tests

**Refactoring consigliato**:
```python
# Separare interfacce da implementazione
from pipeline.interfaces import ModuleEngine, ModuleInfo, ModuleResult
# Riduce import chaos da 10 file a 1 punto centrale
```

---

### HUB 2: `core_models/materials.py`

**Status**: ⭐⭐⭐⭐⭐ Criticità 60

**Cosa PROTEGGERE**:
- `Material.id` (UUID — chiave lookup ovunque)
- `Material.properties: dict` (schema flessibile)
- `MaterialRepository.find_by_name()`, `.get_all()`

**Cosa può diventare PLUGIN**:
- EventBus è già opzionale → Bene
- FRC params → MaterialExtension opzionale
- JSON serialization → MaterialSerializer separato

**Rischi di modifica**:
- Rinominare `Material.properties` → Migrazione JSON necessaria
- EventBus required → Molti test rompono

**Refactoring consigliato**:
```python
# Protocol/ABC per decoupling
from typing import Protocol

class MaterialLike(Protocol):
    id: str
    name: str
    properties: dict[str, float]

# Uso in CalcInput
CalcInput.material: MaterialLike  # Non Material diretto
```

---

### HUB 3: `shared/ui/base_module_window.py`

**Status**: ⭐⭐⭐⭐ Criticità 20

**Cosa PROTEGGERE**:
- 4 metodi astratti (_create_*_panel)
- Segnali: calculation_completed, data_changed
- norm_bar (norm_combo, sl_combo, lc_combo)

**Cosa può diventare PLUGIN**:
- Toolbar configurabile tramite ToolbarConfig
- norm_bar filtra norme da ModuleInfo
- Segnali generici: Signal[ModuleResult]

**Refactoring consigliato**:
```python
# Separare logica da GUI
class BaseModuleController:  # Pure Python
    def on_calculate() -> ModuleResult: ...

class BaseModuleWindow(BaseModuleController, QMainWindow): ...
# → Testabile senza Qt
```

---

### HUB 4: `src/core_calculus/contracts.py`

**Status**: ⭐⭐⭐ Criticità 10

**Cosa PROTEGGERE**:
- `CalcInput` (campi con None default → flessibilità)
- `CalcOutput.per_template_results`
- `SingleCheckResult.utilisation`, `.ok`
- `ElementRole` enum

**Cosa può diventare PLUGIN**:
- VerificationTemplate.function_path (già stringa importabile)

---

## 6. PRIORITÀ REFACTORING

| P | Azione | Impatto | Effort |
|---|--------|---------|--------|
| **P1** | Unificare `SectionGeometry` in core_calculus/core/ | Elimina 5 duplicati | 1h |
| **P2** | Definire `Protocol MaterialLike`, `SectionLike` | Rimuove dipendenza diretta | 2h |
| **P3** | Bridge `CalcInput → VerificationInput` | Riduce duplicazione verifica | 3h |
| **P4** | Collegare `NormMaterialMap` a BaseModuleWindow | Attiva foglia isolata | 1h |
| **P5** | Collegare `ReportBuilder` a ResultsCollector | Chiude ciclo pipeline→report | 1.5h |

---

## 7. FILE CHIAVE PER REFERENCE

### HUB POINTS
- `/home/user/RD2229/pipeline/module_registry.py` — Entry point registrazione
- `/home/user/RD2229/core_models/materials.py` — Modello dati principale
- `/home/user/RD2229/shared/ui/base_module_window.py` — Base UI
- `/home/user/RD2229/src/core_calculus/contracts.py` — I/O contracts

### CORE CALCULUS
- `/home/user/RD2229/src/core_calculus/core/verification_core.py` — Motore TA/SLU/SLE
- `/home/user/RD2229/src/core_calculus/core/verifier_manager.py` — Orchestrazione
- `/home/user/RD2229/src/core/pipeline.py` — Pipeline deterministica

### PROJECTS & SCHEMAS
- `/home/user/RD2229/src/project/schema.py` — ProjectModel Pydantic (unica fonte)
- `/home/user/RD2229/src/project/model.py` — Project operations

### FOGLIE ISOLATE (DA COLLEGARE)
- `/home/user/RD2229/shared/norms/engine/norm_material_map.py` ⚠️
- `/home/user/RD2229/reporting/engine/report_builder.py` ⚠️

---

## CONCLUSIONE

**Forze**:
- ✅ Pipeline/module_registry contratto chiaro
- ✅ CalcInput/CalcOutput I/O pulito
- ✅ Separazione GUI/Engine per modulo
- ✅ ProjectModel Pydantic versionato

**Debolezze**:
- ❌ DUE sistemi verifica coesistenti (no bridge)
- ❌ 6x SectionGeometry (incompatibili)
- ❌ materials.py 20+ dipendenti (no astrattezza)
- ❌ 2 foglie isolate mai integrate (norm_material_map, report_builder)

**Prossimi step** (Sessioni 3-4, Sprint B4):
1. P1-P2: Eliminare duplicazioni geometry + materials
2. P3: Unificare verifica con bridge adapter
3. P4-P5: Integrare foglie isolate

---

**Documento**: Sprint B4 Reference | **Status**: Ready for implementation
**Autore**: Sonnet 4.6 | **Data**: 2026-03-29
