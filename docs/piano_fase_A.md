# Fase A — Database Materiali Multi-Normativa

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | `a0f05aa` |
| **Data completamento** | 2026-03-07 |
| **Test aggiunti** | 22 |
| **Norma/e di riferimento** | RD2229, DM72, DM87, DM92, DM96, Circ81, NTC2008, NTC2018, OPCM3274 |

---

## Descrizione

Fase fondamentale del progetto: definisce la **base dati centralizzata dei materiali** per tutte le normative storiche e vigenti coperte dal software.

L'obiettivo è avere un archivio JSON per ogni norma (9 cataloghi, 97 materiali totali) accessibili tramite un'interfaccia unificata (`MaterialRepository`). A questo si aggiunge la struttura `MaterialSource` che traccia la provenienza normativa di ogni parametro (§, tabella, formula).

---

## Teoria e fondamenti strutturali

### Materiali nel calcolo strutturale storico italiano

Il sistema dei materiali segue le prescrizioni delle normative storiche:

- **RD 2229/1939** — tensioni ammissibili per c.a.:
  - `σ_c_amm ≈ σ_c28 / 4.5` (cls ordinario)
  - `E_c = 550000 · σ_c28 / (σ_c28 + 200)` [kg/cm²]
  - `G_c ≈ 0.43 · E_c`
  - `τ_service ≈ 0.07 · σ_c28`

- **DM96/NTC2018** — stati limite:
  - `f_cd = f_ck / (γ_c · α_cc)`  [MPa]
  - `E_cm = 22000 · (f_cm/10)^0.3` [MPa] — EN 1992

### Conversioni critiche

```text
1 kg/cm² = 0.0980665 MPa        (src/materials/adapter.py)
E_c RD2229 = 550000 · σ_c28 / (σ_c28 + 200)   [kg/cm²]
E_cm NTC2018 = 22000 · (fcm/10)^0.3            [MPa]
σ_c_adm cls_norm = σ_c28 / 4.5                 [kg/cm²]
```

### Struttura MaterialSource

```text
MaterialSource
├── id_sorgente     (es. "ntc2018_tab_C3_1")
├── norma           (Enum Norma)
├── paragrafo       (es. "§C3.1")
├── tabella         (es. "Tab.C3.1-I")
├── tipo_fonte      (Enum: tabella_normativa | formula | catalogo_produttore)
└── nota            (stringa libera)
```

---

## Diagramma dipendenze subfasi

```text
A.1 — Cataloghi JSON (9 norme, 97 materiali)
 └── A.2 — MaterialSource strutturata
          ├── material_source.py (dataclass + enum)
          ├── material_sources.json (9 fonti)
          └── Integrazione MaterialRepository + GUI + report
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo in Fase A |
| --- | --- | --- |
| `src/materials/material_repository.py` | Repository materiali | Aggiornato per gestire `MaterialSource` tipizzata |
| `src/core/unita_misura.py` | Sistema unità | Selettore kg/cm² ↔ MPa per output |
| `src/materials/adapter.py` | Conversioni unità | Conversioni automatiche tra sistemi |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| **RD 2229/1939** art.1-5 | Tensioni ammissibili cls, acciaio dolce/semiduro/duro |
| **DM 30/05/1972** | Materiali cls per costruzioni ordinarie |
| **DM 20/11/1987** (muratura) | f_d, f_vk0, E_m per muratura |
| **Circ. 30/07/1981** | Muratura zona sismica |
| **DM 14/02/1992** | Rck, FeB32k/FeB44k |
| **DM 09/01/1996** | fck, fyk — revisione DM92 |
| **OPCM 3274/2003** | Materiali per zona sismica |
| **NTC 2008/2018** Tab. C3.1-I | C12/15÷C90/105, B450C, S275÷S460 |
| **Circ. n.7/2019** | Integrazioni NTC2018 |

---

## Struttura file/directory

```text
data/materials/
├── catalogo_ntc2018.json          (18 materiali — C12/15÷C90/105, B450C, S275÷S460)
├── catalogo_rd2229.json           (10 materiali — cls Rck150÷450, acc. dolce/semiduro/duro)
├── catalogo_dm72.json             (8 materiali)
├── catalogo_dm87_muratura.json    (9 materiali — mattone, tufo, pietra)
├── catalogo_dm92.json             (10 materiali)
├── catalogo_dm96.json             (12 materiali)
├── catalogo_ntc2008.json          (12 materiali)
├── catalogo_circ81_muratura.json  (5 materiali — muratura zona sismica)
├── catalogo_legno.json            (6 materiali — C16÷GL32h)
├── catalogo_opcm3274.json         (7 materiali)
└── material_sources.json          (9 fonti migrate)

src/materials/
├── material_source.py             (MaterialSource dataclass + Enum TipoFonte)
├── material_repository.py         (CRUD + list_by_norma + carica_tutti_cataloghi)
├── adapter.py                     (conversioni kg/cm² ↔ MPa)
└── validation.py                  (validazione range fisici)

tests/
└── test_cataloghi_materiali.py    (22 test)
```

---

## Subfasi, checklist e storico

### A.1 — Cataloghi JSON per tutte le norme

**Stato**: COMPLETATO — commit `a0f05aa`

- [x] `catalogo_ntc2018.json` — 18 materiali (C12/15÷C90/105, B450C, S275, S355, S460)
- [x] `catalogo_rd2229.json` — 10 materiali (cls Rck150÷450, acciaio dolce/semiduro/duro/extra)
- [x] `catalogo_dm72.json` — 8 materiali
- [x] `catalogo_dm87_muratura.json` — 9 materiali (mattone forato, pieno, tufo, pietra, cls cellulare)
- [x] `catalogo_dm92.json` — 10 materiali
- [x] `catalogo_dm96.json` — 12 materiali
- [x] `catalogo_ntc2008.json` — 12 materiali
- [x] `catalogo_circ81_muratura.json` — 5 materiali (muratura zona sismica)
- [x] `catalogo_legno.json` — 6 materiali (C16, C24, C30, GL24h, GL28h, GL32h)
- [x] `catalogo_opcm3274.json` — 7 materiali
- [x] Totale materiali: **97**
- [x] Metodi: `list_by_norma()`, `list_norme_disponibili()`, `carica_tutti_cataloghi()`
- [x] Test: `tests/test_cataloghi_materiali.py` — 22 test

**Dipendenze**: nessuna (base del progetto)

---

### A.2 — MaterialSource strutturata

**Stato**: COMPLETATO — commit `a0f05aa`

- [x] `src/materials/material_source.py` — `MaterialSource` (dataclass), `TipoFonte` (Enum), `to_dict()`/`from_dict()`
- [x] `data/materials/material_sources.json` — 9 fonti migrate
- [x] Collegamento `source_refs: list[str]` in ogni `Material`
- [x] Aggiornamento `MaterialRepository` per caricare e risolvere le sorgenti
- [x] Cataloghi aggiornati con `source_refs` per ogni voce
- [x] Integrazione riferimenti in report (§paragrafo accanto al valore)
- [x] Integrazione in GUI Qt (tooltip normativo per ogni campo)
- [x] Eliminazione file legacy `src/legacy/material_sources.py`
- [x] Test round-trip: serializzazione → deserializzazione, `load_sources()`, `get_source(id)`

**Dipendenze**: A.1

---

## File creati/modificati

| File | Righe | Descrizione |
| --- | --- | --- |
| `data/materials/catalogo_*.json` | ~20-50 cad. | 9 cataloghi materiali per norma |
| `data/materials/material_sources.json` | ~60 | 9 fonti normative migrate |
| `src/materials/material_source.py` | ~80 | `MaterialSource`, `TipoFonte`, serializzazione |
| `src/materials/material_repository.py` | ~200 | Repository CRUD + supporto `MaterialSource` |
| `src/materials/adapter.py` | ~50 | Conversioni kg/cm² ↔ MPa |
| `tests/test_cataloghi_materiali.py` | ~120 | 22 test cataloghi e sorgenti |

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Cataloghi separati per norma (9 JSON) | Ogni catalogo è manutenibile indipendentemente; aggiunta di nuove norme non richiede modifica degli altri |
| `MaterialSource` come entità separata (non inline in `Material`) | Una stessa fonte può essere condivisa da più materiali; evita duplicazione dei metadati |
| Unità primarie kg/cm² nei cataloghi RD2229/DM72/DM92/DM96 | Fedeltà storica; conversione a MPa solo per output su richiesta |
| Schema `source_refs: list[str]` (lista di ID sorgente) | Permette riferimenti multipli (es. tabella + nota circolare) |

---

## Bug corretti durante lo sviluppo

| Bug | File | Descrizione |
| --- | --- | --- |
| Encoding UTF-8 in JSON muratura | `catalogo_dm87_muratura.json` | Caratteri accentati (è, à) causavano errore su Windows; risolto con `encoding="utf-8"` esplicito |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-07

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Schema catalogo: uno per norma o unico? | Un file per norma | 9 JSON separati, più manutenibili |
| Unità nei cataloghi storici (RD2229, DM72…)? | kg/cm² storici | Mantiene fedeltà con la norma originale |
| `MaterialSource`: inline o entità separata? | Entità separata | Riduce duplicazione, permette riuso cross-norma |
| Eliminazione legacy `material_sources.py`? | Sì, dopo migrazione | Eliminato a commit `a0f05aa` |

---

## Note storiche/archivio

Il sistema dei materiali del RD 2229/1939 è peculiare: la resistenza caratteristica (σ_c28) è in kg/cm² e le tensioni ammissibili derivano da coefficienti empirici elaborati prima della meccanica della frattura. La formula di Young `E_c = 550000 · σ_c28 / (σ_c28 + 200)` è la formula storica italiana, diversa dalla formula EN1992.

La presenza di cataloghi sia per la muratura (DM87, Circ81) che per cls e acciaio consente di coprire l'intero patrimonio edilizio italiano del XX secolo, obiettivo primario del software.
