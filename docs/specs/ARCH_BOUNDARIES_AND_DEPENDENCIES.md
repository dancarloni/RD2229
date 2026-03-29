# ARCH BOUNDARIES AND DEPENDENCIES

> Fonte primaria: `docs/MEGAPLAN/archived/AGGREGAZIONE.md` — LOCKED

## Layer architetturali

```
┌──────────────────────────────────────────────────────────────┐
│  Presentation (GUI)                                          │
│  src/rd2229/ui_qt/  |  src/rd2229/ui_legacy/                 │
│  → usa SOLO Application Services                            │
├──────────────────────────────────────────────────────────────┤
│  Application Services / Orchestration                        │
│  src/rd2229/viewmodels/  |  future: src/rd2229/app_services/ │
│  → usa Domain/Engine + Repository Contracts                  │
├──────────────────────────────────────────────────────────────┤
│  Domain / Engine                                             │
│  src/rd2229/mvp/engine.py  |  src/rd2229/seismic/            │
│  src/fire/  |  src/wind/  |  src/core_calculus/             │
│  → usa SOLO Domain Models + Config Provider                  │
├──────────────────────────────────────────────────────────────┤
│  Persistence / Repository                                    │
│  src/rd2229/mvp/sqlite_store.py  |  src/project/repository.py│
│  → usa Repository Contracts                                  │
├──────────────────────────────────────────────────────────────┤
│  Config / Plugin                                             │
│  src/rd2229/mvp/jsoncode_loader.py  |  src/rd2229/plugin_registry.py │
│  config/calculation_codes/                                   │
└──────────────────────────────────────────────────────────────┘
```

## Dipendenze consentite

| Da → Verso | Consentita | Note |
|-----------|-----------|------|
| GUI → Application Services | ✅ | via contratti/interfacce |
| GUI → Domain/Engine | ❌ | vietato diretto |
| GUI → Persistence | ❌ | vietato diretto |
| Application Services → Domain/Engine | ✅ | via contratti |
| Application Services → Persistence | ✅ | via Repository contracts |
| Domain/Engine → GUI | ❌ | vietato |
| Domain/Engine → Persistence | ❌ | vietato diretto |
| Persistence → Domain Models | ✅ | solo lettura/scrittura modelli |
| Config → qualsiasi | 🔒 | readonly, caricato da Application Services |

## Matrice Coupling attuale

| Modulo | Tipo | Severità | Azione |
|--------|------|----------|--------|
| `src/rd2229/mvp/` | NUOVO/OK | LOW | Nessuna |
| `src/rd2229/seismic/rd2229_39/` | OK | LOW | Nessuna |
| `src/core_calculus/section_calculations.py → apps/sections/` | BREAKS-BOUNDARY | HIGH | Da rifattorizzare (stream futuro) |
| `src/ui/modern/` | OK (MVVM) | LOW | Nessuna |
| `apps/sections/` | LEGACY | MEDIUM | Deprecazione pianificata |

## Regole anti-accoppiamento

1. Nessuna importazione diretta da `src.ui` in moduli `src.core_calculus` o `src.rd2229.mvp`.
2. Nessun widget/dialog importato in Engine o Repository.
3. Nessun parametro normativo hardcoded: configurazioni caricate da `config/`.
4. I moduli Fire (`src/fire/`) e Wind (`src/wind/`) non devono importare da moduli strutturali reciprocamente.
