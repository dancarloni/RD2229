# Fase D — Cordoli Metallici

## Subfasi, checklist e storico

### D.1 Sagomario EN 10365

**Stato**: COMPLETATO

- [x] Database profili IPE (18), HEA (19), HEB (19), HEM (19), UPN (12) in JSON — 87 profili totali
- [x] Import CSV custom utente — `carica_da_csv()` + `genera_template_csv()` in sagomario.py
- [x] Ricerca e filtro profili (per famiglia, Wx minimo, altezza, profilo ottimale)
- [x] Test: tests/test_sagomario_acciaio.py (38 test — 32 esistenti + 6 TestCSVImport)

### D.2 Verifiche profilo singolo

**Stato**: COMPLETATO — commit corrente

- [x] Flessione (σ = M/W ≤ σ_adm)
- [x] Taglio (τ = V/A_anima ≤ τ_adm)
- [x] Instabilità (ω·N/A, tabella CNR 10011)
- [x] Pressoflessione (N + Mx + My)
- [x] Combinata Von Mises (σ_VM = √(σ² + 3τ²))
- [x] Selezione profilo ottimale per momento
- [x] Test: tests/test_verifiche_acciaio_ta.py (33 test)

### D.3 Traliccio reticolare piano — cordolo metallico reticolare

**Stato**: COMPLETATO — commit 23f3300

- [x] SezioneAsta, piatti, angolari, verifica_aste_traliccio()
- [x] Generatore schemi traliccio (Howe, Pratt)
- [x] Adattamento solutore traliccio_2d
- [x] Modulo cordolo reticolare
- [x] Verifiche aste del traliccio
- [x] Integrazione con cinematica.py
- [x] Nodo d'angolo (cantonali)
- [x] Report e tabulato
- [x] Test: test_sezione_asta.py, test_traliccio_generatore.py, test_cordolo_reticolare.py

### D.4 Solutore traliccio 2D

**Stato**: COMPLETATO — commit corrente

- [x] Metodo della rigidezza diretta (Gauss con pivoting parziale)
- [x] Input nodi + aste + vincoli (cerniera, carrello_x, carrello_y) + carichi
- [x] Sforzi normali nelle aste (trazione/compressione)
- [x] Reazioni vincolari con verifica equilibrio globale
- [x] Verifiche a compressione/trazione con instabilità (ω)
- [x] Test: tests/test_traliccio_2d.py (19 test)

### D.5 Connessioni

**Stato**: COMPLETATO — commit corrente

- [x] Saldature a cordone d'angolo (frontale, laterale, combinata)
- [x] Saldature testa a testa (completa penetrazione)
- [x] Bullonature: taglio (gambo/filetto), trazione, interazione, rifollamento
- [x] Coefficienti β_w (CNR 10011), classi 4.6÷10.9, M12÷M36
- [x] Test: tests/test_connessioni_acciaio.py (24 test)

### D.6 Modello cordolo (CA + metallico)

**Stato**: COMPLETATO — commit corrente

- [x] Cordolo CA: sezione, armatura, minimi NTC2018 §7.8.1.6
- [x] Cordolo metallico: profilo singolo, flessione/taglio TA
- [x] Verifica flessione e taglio per entrambi i tipi
- [x] Posizione: sommitale, intermedio, fondazione

### D.7 GUI Qt cordoli

**Stato**: COMPLETATO — 2026-03-09

#### Architettura decisa (2026-03-09)
- Tipo finestra: **QWidget embeddabile** (inseribile in MainWindow futura)
- Navigazione: **QTabWidget** — 4 tab, salto libero
- Visualizzazione sezione: **QPainter custom**
- Tipi cordolo gestiti: **metallico + CA + reticolare** (tutti e tre)
- Output: **QTextEdit video + esportazione HTML** via modulo report centralizzato
- Test: logica di business + pytest-qt per componenti chiave

#### Struttura tab prevista
```
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
- [x] Tab 4: output via TabulatoCalcolo centralizzato (ASCII + HTML)
- [x] Registrazione auto-discovery in `src/ui/qt/__init__.py`
- [x] Test logica: `tests/test_cordoli_widget_logica.py` (10 test)
- [x] Test UI: `tests/test_cordoli_widget_qt.py` (skip se Qt non disponibile)

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

#### D.1 — Import CSV custom utente

| Domanda | Risposta |
|---------|----------|
| D.1.a Famiglia | Stringa libera — qualsiasi valore accettato |
| D.1.b Conflitti nome | Sovrascrittura + warning nel log |
| D.1.c Validazione | Range fisici (h>0, Wx>0, tf>0, ecc.) |
| D.1.d Persistenza | `data/steel/sagomario_custom.json` (caricato automaticamente) |

#### D.7 — GUI Qt cordoli

| Domanda | Risposta |
|---------|----------|
| D.7.1 Tipo finestra | QWidget embeddabile |
| D.7.2 Navigazione | QTabWidget (4 tab, salto libero) |
| D.7.3 Vis. sezione | QPainter custom |
| D.7.4 Tipi cordolo | Tutti e tre: metallico + CA + reticolare |
| D.7.5 Output | QTextEdit video + HTML, via modulo report centralizzato |
| D.7.6 Test | Logica di business + pytest-qt sui componenti chiave |

**Vincolo architetturale D.7.5**: ogni modulo di calcolo produce un dizionario
(`passaggi_calcolo`, `risultati`) compatibile con `src/report/`. La GUI non ha
logica di formattazione propria.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
