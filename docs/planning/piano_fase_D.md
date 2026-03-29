# Fase D — Cordoli Metallici e Acciaio TA

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | `368910a` (D.1/D.7), `23f3300` (D.3) |
| Data completamento | 2026-03-09 |
| Test totali | ~124 (38+33+~15+19+24+10+skip-qt) |
| File principali | `src/steel/sagomario.py`, `src/steel/verifiche_ta.py`, `src/steel/traliccio_2d.py`, `src/ui/qt/cordoli_widget.py` |

---

## Descrizione

La Fase D implementa l'intero stack di calcolo per **cordoli metallici e strutture in acciaio** secondo le Tensioni Ammissibili (TA — RD 2229, CNR 10011). Copre:

- Sagomario EN 10365 con 87 profili standard + import CSV custom
- Verifiche profilo singolo (flessione, taglio, instabilità, Von Mises)
- Traliccio 2D piano — solver rigidezza diretta + verifica aste
- Connessioni (saldature + bullonature CNR 10011)
- Modello unificato cordolo CA / metallico / reticolare
- GUI Qt embeddabile a 4 tab con QPainter e export HTML

---

## Teoria e formule chiave

### D.2 — Verifiche TA profilo singolo

```text
Flessione:      σ = M / W_x  ≤  σ_adm
Taglio:         τ = V / A_anima  ≤  τ_adm
Instabilità:    σ_inst = ω · N / A  ≤  σ_adm    (ω da tabella CNR 10011 per λ = L/i)
Pressoflessione: σ = N/A + Mx/Wx + My/Wy  ≤  σ_adm
Von Mises:      σ_VM = √(σ² + 3τ²)  ≤  σ_adm

dove:
  W_x   modulo di resistenza flessionale  [cm³]
  A     area sezione lorda               [cm²]
  A_anima = h_w · t_w                    [cm²]  (solo anima)
  ω     coefficiente di instabilità (CNR 10011 Tab. 9) — funzione di λ = L_lib / i_min
  i_min = √(I_min / A)                   [cm]
```

### D.4 — Solutore traliccio 2D (rigidezza diretta)

```text
Matrice di rigidezza asta (sistema globale):
  k_e = (EA/L) · [c²   cs  -c²  -cs ]
                 [cs   s²  -cs  -s² ]
                 [-c²  -cs  c²   cs ]
                 [-cs  -s²  cs   s² ]

dove c = cos(θ), s = sin(θ), E = modulo elastico, A = area asta, L = lunghezza

Assemblaggio:  [K]{u} = {F}
Risoluzione:   Gauss con pivoting parziale (numpy.linalg.solve dopo riduzione vincoli)
Sforzo asta:   N_e = (EA/L) · [-c, -s, c, s] · {u_e}
```

### D.5 — Connessioni

```text
Saldatura cordone d'angolo:
  τ⊥ = F / (a · l_eff)  ≤  τ_adm_sald   (frontale: F perp. al cordone)
  τ‖ = F / (a · l_eff)  ≤  τ_adm_sald   (laterale: F parallelo al cordone)
  a = gola effettiva del cordone [cm],  l_eff = lunghezza efficace [cm]

Bullonatura a taglio (gambo):
  τ_b = V / (n · A_b)  ≤  τ_adm_bull
  σ_rif = F / (d · t · n)  ≤  σ_rif_adm  (rifollamento)

Interazione taglio-trazione:
  (V/V_Rd)² + (N/N_Rd)²  ≤  1.0

Coefficienti β_w per saldature (CNR 10011):
  Fe360 → β_w = 0.80,  Fe430 → 0.85,  Fe510 → 0.90
```

---

## Diagramma dipendenze

```text
Fase D — dipendenze interne

  data/steel/sagomario_en10365.json ──────────┐
  data/steel/sagomario_custom.json  ──────────┤
                                              ▼
  src/steel/sagomario.py  ←── D.1  ──▶  SagomarioAcciaio
       │  carica_da_csv()                    │
       │  cerca_profilo_ottimale()           │
       ▼                                    ▼
  src/steel/verifiche_ta.py ←── D.2 ──▶  VerificheTA
       │  verifica_flessione()              │
       │  verifica_taglio()                 │
       │  verifica_instabilita(ω)           │
       │  verifica_von_mises()              │
       ▼                                    │
  src/steel/traliccio_generatore.py ─ D.3 ──┤
  src/steel/traliccio_2d.py ────────── D.4 ──┤
  src/steel/connessioni.py ──────────── D.5 ──┤
  src/steel/modello_cordolo.py ─────── D.6 ──┘
       │
       ▼
  src/ui/qt/cordoli_widget.py ─────── D.7
       │  CordoliWidget(QWidget)
       │  4 tab: Profilo | Sezione | Sollecitazioni | Output
       ▼
  src/report/ ─── TabulatoCalcolo (ASCII + HTML)
```

---

## Dipendenze da altri moduli

| Modulo esterno | Ruolo |
| --- | --- |
| `src/report/tabulato.py` | Formattazione output ASCII/HTML |
| `src/core/registro_log.py` | Log operazioni GUI |
| `src/methods/rd2229/instabilita.py` | Coefficienti ω instabilità |
| `src/ui/qt/__init__.py` | Auto-discovery widget |
| Fase E (muratura) | Usa cordoli come elementi di catena/cerchiatura |
| Fase L (telai) | Cordoli come travi metalliche nei telai piani |

---

## Riferimenti normativi

| Norma | Articolo/Tabella | Contenuto |
| --- | --- | --- |
| CNR 10011/1985 | Tab. 9 | Coefficienti ω instabilità per λ = L/i |
| CNR 10011/1985 | §4.2 | Tensioni ammissibili acciaio (σ_adm, τ_adm) |
| CNR 10011/1985 | §7 | Connessioni bullonate e saldate |
| EN 10365:2017 | — | Profili laminati a caldo: IPE, HEA/B/M, UPN |
| NTC2018 | §7.8.1.6 | Cordoli CA: armatura minima e dimensioni |
| RD 2229/1939 | §66-72 | Strutture metalliche, verifiche TA |

---

## Struttura file

```text
src/steel/
├── sagomario.py              # D.1 — SagomarioAcciaio, carica_da_csv, genera_template_csv
├── verifiche_ta.py           # D.2 — verifica_flessione, verifica_taglio, verifica_von_mises
├── traliccio_generatore.py   # D.3 — genera_schema_howe, genera_schema_pratt
├── traliccio_2d.py           # D.4 — Solutore rigidezza diretta, sforzi aste
├── connessioni.py            # D.5 — saldature, bullonature, rifollamento
├── modello_cordolo.py        # D.6 — CordoloCA, CordoloMetallico, CordoloReticolare
└── sezione_asta.py           # D.3 — SezioneAsta (piatti, angolari)

data/steel/
├── sagomario_en10365.json    # 87 profili standard (IPE/HEA/HEB/HEM/UPN)
└── sagomario_custom.json     # profili importati da CSV utente (auto-generato)

src/ui/qt/
└── cordoli_widget.py         # D.7 — CordoliWidget, 4 tab, QPainter

tests/
├── test_sagomario_acciaio.py        # 38 test (D.1)
├── test_verifiche_acciaio_ta.py     # 33 test (D.2)
├── test_sezione_asta.py             # D.3
├── test_traliccio_generatore.py     # D.3
├── test_cordolo_reticolare.py       # D.3
├── test_traliccio_2d.py             # 19 test (D.4)
├── test_connessioni_acciaio.py      # 24 test (D.5)
├── test_cordoli_widget_logica.py    # 10 test (D.7 — logica pura)
└── test_cordoli_widget_qt.py        # skip se Qt non disponibile (D.7)
```

---

## Subfasi, checklist e storico

### D.1 — Sagomario EN 10365

**Stato**: ✅ COMPLETATO

- [x] Database profili IPE (18), HEA (19), HEB (19), HEM (19), UPN (12) in JSON — 87 profili totali
- [x] Import CSV custom utente — `carica_da_csv()` + `genera_template_csv()` in `sagomario.py`
- [x] Ricerca e filtro profili (per famiglia, Wx minimo, altezza, profilo ottimale)
- [x] Test: `tests/test_sagomario_acciaio.py` (38 test — 32 esistenti + 6 TestCSVImport)

### D.2 — Verifiche profilo singolo (TA)

**Stato**: ✅ COMPLETATO

- [x] Flessione (σ = M/W ≤ σ_adm)
- [x] Taglio (τ = V/A_anima ≤ τ_adm)
- [x] Instabilità (ω·N/A, tabella CNR 10011)
- [x] Pressoflessione (N + Mx + My)
- [x] Combinata Von Mises (σ_VM = √(σ² + 3τ²))
- [x] Selezione profilo ottimale per momento
- [x] Test: `tests/test_verifiche_acciaio_ta.py` (33 test)

### D.3 — Traliccio reticolare piano (cordolo metallico reticolare)

**Stato**: ✅ COMPLETATO — commit `23f3300`

- [x] `SezioneAsta`, piatti, angolari, `verifica_aste_traliccio()`
- [x] Generatore schemi traliccio (Howe, Pratt)
- [x] Adattamento solutore `traliccio_2d`
- [x] Modulo cordolo reticolare
- [x] Verifiche aste del traliccio
- [x] Integrazione con `cinematica.py`
- [x] Nodo d'angolo (cantonali)
- [x] Report e tabulato
- [x] Test: `test_sezione_asta.py`, `test_traliccio_generatore.py`, `test_cordolo_reticolare.py`

### D.4 — Solutore traliccio 2D

**Stato**: ✅ COMPLETATO

- [x] Metodo della rigidezza diretta (Gauss con pivoting parziale)
- [x] Input nodi + aste + vincoli (cerniera, carrello_x, carrello_y) + carichi
- [x] Sforzi normali nelle aste (trazione/compressione)
- [x] Reazioni vincolari con verifica equilibrio globale
- [x] Verifiche a compressione/trazione con instabilità (ω)
- [x] Test: `tests/test_traliccio_2d.py` (19 test)

### D.5 — Connessioni (saldature e bullonature)

**Stato**: ✅ COMPLETATO

- [x] Saldature a cordone d'angolo (frontale, laterale, combinata)
- [x] Saldature testa a testa (completa penetrazione)
- [x] Bullonature: taglio (gambo/filetto), trazione, interazione, rifollamento
- [x] Coefficienti β_w (CNR 10011), classi 4.6÷10.9, M12÷M36
- [x] Test: `tests/test_connessioni_acciaio.py` (24 test)

### D.6 — Modello cordolo (CA + metallico)

**Stato**: ✅ COMPLETATO

- [x] Cordolo CA: sezione, armatura, minimi NTC2018 §7.8.1.6
- [x] Cordolo metallico: profilo singolo, flessione/taglio TA
- [x] Verifica flessione e taglio per entrambi i tipi
- [x] Posizione: sommitale, intermedio, fondazione

### D.7 — GUI Qt cordoli

**Stato**: ✅ COMPLETATO — 2026-03-09

#### Architettura decisa

- Tipo finestra: **QWidget embeddabile** (inseribile in MainWindow futura)
- Navigazione: **QTabWidget** — 4 tab, salto libero
- Visualizzazione sezione: **QPainter custom**
- Tipi cordolo gestiti: **metallico + CA + reticolare** (tutti e tre)
- Output: **QTextEdit video + esportazione HTML** via modulo report centralizzato
- Test: logica di business + pytest-qt per componenti chiave

#### Struttura tab

```text
CordoliWidget (QWidget embeddabile)
├── Tab 1: Selezione Profilo
│   ├── Combo famiglia (stringa libera)
│   ├── Combo tipo cordolo (metallico | CA | reticolare)
│   ├── Tabella profili QTableWidget sortable
│   ├── Filtri: Wx_min, h_min/h_max
│   └── Bottone "Importa CSV custom"
├── Tab 2: Visualizzazione Sezione
│   ├── QPainter sezione trasversale
│   └── Tabella proprietà (h, b, A, Ix, Wx, …)
├── Tab 3: Input Sollecitazioni
│   ├── Posizione cordolo (sommitale | intermedio | fondazione)
│   ├── M, V, N + materiale (σ_adm da archivio)
│   └── Per reticolare: schema traliccio + carichi
└── Tab 4: Output Verifiche
    ├── QTextEdit risultati formattati
    ├── Stato globale (VERIFICATO / NON VERIFICATO)
    └── Bottone "Esporta HTML"
```

#### Checklist implementazione

- [x] `src/ui/qt/cordoli_widget.py` — QWidget principale con 4 tab
- [x] Tab 1: selezione profilo + importa CSV (Metallico) / form completo (CA, Reticolare)
- [x] Tab 2: QPainter sezione IPE/HEA/HEB/HEM/UPN + CA + reticolare
- [x] Tab 3: input sollecitazioni (Metallico) — nascosto per CA/Reticolare
- [x] Tab 4: output via `TabulatoCalcolo` centralizzato (ASCII + HTML)
- [x] Registrazione auto-discovery in `src/ui/qt/__init__.py`
- [x] Test logica: `tests/test_cordoli_widget_logica.py` (10 test)
- [x] Test UI: `tests/test_cordoli_widget_qt.py` (skip se Qt non disponibile)

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| JSON per sagomario (non CSV) | Struttura annidata, tipizzazione, caricamento diretto in dict Python |
| Import CSV → JSON custom separato | Non inquinare il catalogo standard; sovrascrittura con warning |
| Gauss con pivoting (non numpy.linalg.solve) | Controllo esplicito per sistemi mal condizionati con vincoli incompleti |
| QPainter custom (non matplotlib embed) | Leggerezza, risposta immediata, nessuna dipendenza matplotlib in GUI |
| GUI non ha logica di formattazione | Vincolo architetturale: ogni modulo produce `{passaggi_calcolo, risultati}` per `src/report/` |
| CordoliWidget embeddabile (non QDialog) | Riusabilità in MainWindow multi-pannello futura |
| Tab 3 nascosto per CA/Reticolare | Input specifici per tipo, evita confusione utente |

---

## Bug corretti

| Bug | Causa | Fix |
| --- | --- | --- |
| Import CSV falliva con virgola decimale locale | `float(val)` su "1,5" → ValueError | `val.replace(',', '.')` prima del cast |
| Solutore traliccio singolare con vincoli mancanti | Matrice [K] non ridotta correttamente | Riduzione DOF vincolati prima di solve |
| QPainter fuori bounds su profili piccoli | Scala fissa senza normalizzazione | Calcolo scala adattiva su bounding box profilo |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

#### D.1 — Import CSV custom utente

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| D.1.a Famiglia | Stringa libera — qualsiasi valore accettato | `famiglia: str` senza enum |
| D.1.b Conflitti nome | Sovrascrittura + warning nel log | `registro_log.warning(f"Profilo {nome} sovrascritto")` |
| D.1.c Validazione | Range fisici (h>0, Wx>0, tf>0, ecc.) | Raising `ValueError` con messaggio descrittivo |
| D.1.d Persistenza | `data/steel/sagomario_custom.json` (caricato automaticamente) | Caricamento all'avvio via `SagomarioAcciaio.__init__` |

#### D.7 — Sessione Q&A GUI Qt cordoli

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| D.7.1 Tipo finestra | QWidget embeddabile | Nessun `exec_()`, inseribile in layout |
| D.7.2 Navigazione | QTabWidget (4 tab, salto libero) | Nessun wizard sequenziale |
| D.7.3 Vis. sezione | QPainter custom | Disegno geometrico parametrico per ogni famiglia |
| D.7.4 Tipi cordolo | Tutti e tre: metallico + CA + reticolare | Combo tipo cordolo in Tab 1 cambia Tab 2-4 dinamicamente |
| D.7.5 Output | QTextEdit video + HTML, via modulo report centralizzato | `TabulatoCalcolo.come_html()` → QTextEdit + salva file |
| D.7.6 Test | Logica di business + pytest-qt sui componenti chiave | Test separati: logica pura (no Qt) + UI (skip se Qt assente) |

**Vincolo architetturale D.7.5**: ogni modulo di calcolo produce un dizionario (`passaggi_calcolo`, `risultati`) compatibile con `src/report/`. La GUI non ha logica di formattazione propria.

---

## Note storiche/archivio

- Sagomario originariamente flat dict — refactoring a JSON strutturato per supportare famiglie custom
- Schemi Howe e Pratt generati proceduralmente (no dati fissi): `n_campate`, `h_traliccio` come parametri
- `SezioneAsta` estende `Profilo` con attributo `tipo_asta` (corrente_sup, corrente_inf, diagonale, montante)
- Test cordoli_widget_qt usa `pytest-qt` con `QApplication` fixture — skip automatico se PySide6/PyQt6 non installato
