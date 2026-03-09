# Fase L — Telai Piani Cross-Pozzati (RD 2229/39)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | `f041b45` |
| **Data completamento** | 2026-03-09 |
| **Test aggiunti** | 40 (totale progetto dopo: 2383) |
| **Norma/e di riferimento** | RD 2229/1939, Pozzati vol.II, Santarella vol.II |

---

## Descrizione

Implementa il modulo completo di calcolo per telai piani in c.a. secondo il metodo storico di Hardy Cross / Pozzati (distribuzione iterativa dei momenti, 1930). Copre l'intero ciclo progettuale:

1. Modellazione geometrica e dei carichi
2. Calcolo Cross iterativo (con correzione sway multi-piano)
3. Sollecitazioni M/V/N per asta (3 sezioni + diagramma continuo)
4. Inviluppo combinazioni RD 2229/39 (LC1-LC6)
5. Verifiche tensioni ammissibili (TA)
6. Progetto armature (workflow Santarella)
7. Tabulati storici ASCII + report HTML
8. GUI Qt completa (TelaioWindow)

**Riferimenti normativi e bibliografici**: RD 2229/39; Pozzati "Teoria e Tecnica delle Strutture" vol.II §§3.4-3.8; Santarella "Il Cemento Armato" vol.II cap.3.

---

## Dipendenze tra subfasi

```text
L.1 — modello_telaio.py
 └── L.2 — carichi_fissi.py
      └── L.3 — cross_pozzati.py
           └── L.4 — solver_telaio.py
                ├── L.5 — combinazioni_rd2229.py + sisma_telaio.py
                │    ├── L.6 — verifiche_telaio.py
                │    └── L.7 — armature_telaio.py
                │         └── L.8 — export_telaio.py
                └── L.9 — GUI Qt (in parallelo a L.6-L.8)

L.10 — test (uno per subfase, da L.2 in poi)
```

---

## Dipendenze da moduli esistenti (riutilizzati)

| Modulo esterno | File | Utilizzo in Fase L |
| --- | --- | --- |
| `src/methods/rd2229/checks.py` | `verifiche_telaio.py` | `check_flessione_ta_rett`, `check_pressoflessione_ta_rett`, `check_taglio_ta_rett`, `check_minimi_armatura_ta` |
| `src/core_calculus/contracts.py` | `verifiche_telaio.py` | `CalcInput`, `SingleCheckResult`, `VerificationTemplate` |
| `src/report/tabulati_calcolo.py` | `export_telaio.py` | `TabulatoCalcolo`, `RigaCalcolo`, `EsitoVerifica` |
| `src/report/renderer_html.py` | `export_telaio.py` | `HTMLReportRenderer.render()` |
| `src/grafici/sollecitazioni.py` | `export_telaio.py` | `DiagrammaSollecitazioni`, `grafico_sollecitazioni()` |
| `src/grafici/interazione.py` | `export_telaio.py` | `DominioFactory`, `sovrapponi_punto_lavoro()` |
| `src/ui/qt/visualizzatore_sezione.py` | `telaio_window.py` | `VisualizzatoreSezione.imposta_armatura()` |
| `src/ui/qt/aiuto_contestuale.py` | `telaio_window.py` | `apri_aiuto("telaio_rd2229", contesto)` |

---

## Riferimenti bibliografici e normativi

| Riferimento | Utilizzo |
| --- | --- |
| **RD 2229/1939** — Norme per la esecuzione delle opere in conglomerato cementizio semplice od armato | Norma di riferimento per verifiche TA, minimi armatura, combinazioni di carico |
| **Pozzati**, "Teoria e Tecnica delle Strutture" vol.II, cap.3 §§3.4-3.8 | Algoritmo Cross no-sway; correzione sway multi-piano (sistema n×n); formule MIP per casi speciali |
| **Santarella**, "Il Cemento Armato" vol.II cap.3, Tab.9 | Formule MIP (uniforme, concentrato, trapezoidale); schede verifica armatura; formati tabulati storici |
| **Hardy Cross**, "Analysis of Continuous Frames by Distributing Fixed-End Moments" (1930) | Algoritmo originale distribuzione momenti (carry-over, fattori di distribuzione) |
| **Ciribini**, note integrative sulla correzione sway per telai irregolari | Correzione sway per telai con geometria non regolare |

---

## Subfasi, checklist e storico

### L.1 — Modello dati (`modello_telaio.py`)

**Stato**: COMPLETATO

- [x] `TipoVincoloEsterno` (9 tipi): Incastro, Cerniera, Carrello X/Y, Pattino X/Y, Pendolo, Bipendolo, Libero
- [x] `VincoloEsterno` con proprieta `gdl_bloccati`, `blocca_rotazione`, `n_reazioni`
- [x] `TipoRilascioInterno` (5 tipi): Nodo rigido, Cerniera, Manicotto, Pattino, Bipendolo
- [x] `RilascioEstremita` con proprieta `k_factor` e `carry_over`
- [x] `TipoAsta` (6 tipi): Trave, Pilastro, Setto, Mensola, Inclinata, Pendolo
- [x] `TipoCarico` (5 tipi): Distribuito uniforme, Trapezoidale, Concentrato, Momento nodale, Peso proprio
- [x] `CaricoAsta`, `SezioneTelaio`, `NodoTelaio`, `AstaTelaio`, `PianoTelaio`, `ModelloTelaio`
- [x] `AstaTelaio.rigidezza_from_i/j()` — rigidezza considerando rilasci interni
- [x] `ModelloTelaio`: `nodo_by_id()`, `asta_by_id()`, `aste_per_nodo()`, `aste_per_piano()`, `colonne_piano()`, `lunghezza_asta()`, `to_dict()`

**Dipendenze**: nessuna (base del modulo)

---

### L.2 — Carichi fissi (`carichi_fissi.py`)

**Stato**: COMPLETATO

- [x] `mip_uniforme(w, L)` — risultato `(-wL^2/12, +wL^2/12)` — Santarella Tab.9
- [x] `mip_concentrato(P, a, L)` — risultato `(-Pa*b^2/L^2, +Pa^2*b/L^2)` con `b = L - a`
- [x] `mip_triangolare_crescente(w, L)` — risultato `(-wL^2/20, +wL^2/30)`
- [x] `mip_triangolare_decrescente(w, L)` — risultato `(-wL^2/30, +wL^2/20)`
- [x] `mip_trapezoidale(w_sx, w_dx, L)` — decomposizione uniforme + triangolare con segno corretto per delta_w < 0
- [x] `mip_peso_proprio(sezione, L)` — w_pp = A * gamma, poi mip_uniforme
- [x] `mip_momento_nodale(M, at_i)` — momento nodale con carry-over
- [x] `mip_sway_colonna(E, I, h)` — risultato `(-6EI/h^2, -6EI/h^2)` — FEM per spostamento unitario
- [x] `calcola_mip_asta(asta, includi_peso_proprio)` — somma contributi, audit completo

**Dipendenze**: L.1 (`AstaTelaio`, `SezioneTelaio`, `TipoCarico`)

---

### L.3 — Algoritmo Cross-Pozzati (`cross_pozzati.py`)

**Stato**: COMPLETATO

- [x] `calcola_rigidezze(modello)` — ritorna `(k_from_i, k_from_j, lunghezze)` — rigidezze per ogni asta con rilasci, `TipoAsta.PENDOLO` produce k=0
- [x] `calcola_fattori_distribuzione(modello, k_from_i, k_from_j)` — ritorna `{id_nodo: {id_asta: mu}}` con verifica Sigma_mu=1
- [x] `esegui_cross_no_sway(modello, mip, fattori, tolleranza, max_iter)` — iterazione classica Cross, tabella storica per riga
- [x] `calcola_forze_bloccaggio(modello, risultato_no_sway)` — tagli di piano da no-sway
- [x] `analisi_sway_unitario_piano(modello, id_piano, fattori)` — FEM sway delta=1, Cross distribution
- [x] `esegui_correzione_sway(modello, risultato_no_sway, forze_per_piano, fattori)` — matrice n×n (Pozzati §3.8), Gauss con pivoting
- [x] `calcola_cross_pozzati(modello, forze_orizzontali_per_piano, includi_peso_proprio, tolleranza, max_iter)` — entry point completo
- [x] `DatiCross`: rigidezze, fattori, MIP, iterazioni, momenti_finali, n_iterazioni, errore_residuo, convergenza, passaggi

**Dipendenze**: L.1, L.2

---

### L.4 — Solver sollecitazioni (`solver_telaio.py`)

**Stato**: COMPLETATO

- [x] `calcola_sollecitazioni_trave(asta, M_i, M_j)` — V da equilibrio, M(x) con contributi carichi, diagramma su n_punti
- [x] `calcola_sollecitazioni_pilastro(asta, M_i, M_j, N_cumulativo)` — V costante, N cumulativo da carichi verticali
- [x] `calcola_caso_carico(modello, id_caso, descrizione, override_carichi, forze_orizzontali, forze_verticali)` — orchestratore completo: MIP → Cross → sollecitazioni → reazioni vincoli
- [x] `SollecitazioniAsta`: M/V/N per 3 sezioni critiche + diagramma continuo (x_cm, M_kgcm, V_kg, N_kg)
- [x] `RisultatoCasoCarico`: dati_cross, sollecitazioni, reazioni, passaggi

**Dipendenze**: L.1, L.2, L.3

---

### L.5 — Combinazioni e inviluppo (`combinazioni_rd2229.py`, `sisma_telaio.py`)

**Stato**: COMPLETATO

- [x] `combinazioni_attive(zona_sismica)` — ritorna `list[str]` — LC1..LC6 in base a zona (non_sismico/bassa/media/alta)
- [x] `calcola_forze_sismiche(modello)` — ritorna `ForzeSismicheTelaio` — ondulatorio X (C_s × P_piano) + sussultorio Z (×1.25)
- [x] `InviluppoSollecitazioniAsta` — attributi per-sezione: M_max/min_i/m/j, V_max/min_i/m/j, N_max/min_i/m/j + coppia governante M_gov/N_gov (da sisma) con metodi `M_gov(idx)`, `V_gov(idx)`
- [x] `_aggiorna_inviluppo_sezione()` — aggiornamento incrementale per ogni combinazione
- [x] `calcola_tutte_le_combinazioni(modello, carichi_variabili)` — ritorna `RisultatoCombinazioni` con loop su tutte le combinazioni attive e costruzione inviluppo

**Dipendenze**: L.1, L.4

---

### L.6 — Verifiche TA (`verifiche_telaio.py`)

**Stato**: COMPLETATO

- [x] `ArmaturaSezioneSemplice` — barre inf/sup (n, diametro), staffe (n bracci, diametro, passo), aree calcolate, flag `modificata_manualmente`
- [x] `_SezioneProxy`, `_MaterialeProxy` — adattatori per interfaccia `CalcInput` (unita kN/kNm, mm)
- [x] `_crea_calc_input(asta, M, V, N, armatura, tipo)` — bridge verso `checks.py` con conversioni kg/cm verso kN/kNm
- [x] `verifica_sezione_ta(asta, M_kgcm, V_kg, N_kg, posizione, armatura)` — chiama `check_flessione_ta_rett`, `check_pressoflessione_ta_rett`, `check_taglio_ta_rett`, `check_minimi_armatura_ta`
- [x] `verifica_completa_telaio(modello, inviluppo, armature)` — ritorna `{id_asta: {posizione: {check_id: SingleCheckResult}}}`
- [x] Costanti: `SIGMA_C_ADM_DEFAULT = 60.0 kg/cm2`, `SIGMA_S_ADM_DEFAULT = 1400.0 kg/cm2`, `N_PILASTRO_KG = 500.0`

**Dipendenze**: L.1, L.5; `src/methods/rd2229/checks.py`; `src/core_calculus/contracts.py`

---

### L.7 — Armature (`armature_telaio.py`)

**Stato**: COMPLETATO

- [x] Catalogo diametri standard: 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30 mm
- [x] `_momento_resistente_rett(b, h, As, sigma_c, sigma_s)` — capacita flessionale TA, metodo Navier
- [x] `_As_minima_flessione(b, h, M, sigma_c, sigma_s)` — armatura minima iterativa
- [x] `_Asw_minima_taglio(b, h, V, sigma_c, sigma_s)` — staffe minime
- [x] `_sceglie_barre(As_necessaria, n_min)` — ritorna `(n, diam_mm)` — selezione ottimale da catalogo
- [x] `_sceglie_staffe(Asw_necessaria)` — ritorna `(n_bracci, diam_mm, passo_cm)`
- [x] `calcola_armatura_teorica_minima(asta, M_gov, N_gov, V_gov, posizione)` — ritorna `ArmaturaSezioneSemplice`
- [x] `proponi_armature_telaio(modello, inviluppo)` — ritorna `{id_asta: {posizione: ArmaturaSezioneSemplice}}`
- [x] `copia_armatura(sorgente, destinazioni, catalogo)` — deep copy tra aste simili
- [x] `serializza_armature()` / `deserializza_armature()` — JSON round-trip
- [x] `SchedaArmatura`, `genera_schede_santarella()` — schede stile "Il Cemento Armato"
- [x] Helper `_gov_M(inv, idx)`, `_gov_N(inv, idx)`, `_gov_V(inv, idx)` — usano `inv.M_gov(idx)` / `inv.V_gov(idx)`

**Dipendenze**: L.1, L.5, L.6; `src/methods/rd2229/checks.py`

---

### L.8 — Export e tabulati storici (`export_telaio.py`)

**Stato**: COMPLETATO

- [x] **Tabella 0** — Vincoli strutturali (esterni + rilasci interni, GDL, n. reazioni, iperstaticita)
- [x] **Tabella 1** — Caratteristiche sezioni (L, b, h, I, E, k=4EI/L)
- [x] **Tabella 2** — Fattori di distribuzione mu per nodo (k_ij, Sigma_k, mu, Sigma_mu=1)
- [x] **Tabella 3** — Analisi carichi e MIP per asta (formula, valori, totale)
- [x] **Tabella 4** — Distribuzione Cross iterativa (formato storico Pozzati: MIP / Dis / T-O / ... / Totale)
- [x] **Tabella 5** — Sollecitazioni per asta x caso di carico (M_i, M_mid, M_j, V_i, V_j, N)
- [x] **Tabella 6** — Inviluppo sollecitazioni (M_max, M_min, V_max, V_min, N_max, N_min, M_gov, N_gov)
- [x] **Tabella 7** — Schede verifica armatura stile Santarella (M_gov, As_inf, As_sup, staffe, esito)
- [x] `genera_tabulato_ascii(modello, risultati, inviluppo, armature, verifiche)` — tabulato completo
- [x] `genera_report_html(tabulato, modello, grafici)` — report HTML con CSS inline
- [x] `salva_tabulato(percorso, formato)` — salvataggio su file (formato "txt" o "html")

**Dipendenze**: L.1, L.3, L.4, L.5, L.6, L.7; `src/report/tabulati_calcolo.py`; `src/report/renderer_html.py`; `src/grafici/sollecitazioni.py`

---

### L.9 — GUI Qt (`src/ui/qt/telaio/`)

**Stato**: COMPLETATO

#### `telaio_window.py` — TelaioWindow (QMainWindow)

- [x] 4 dock: Left (input nodi/aste/sisma), Central (canvas), Right (risultati), Bottom (tabulato preview)
- [x] CRUD completo nodi e aste (QTableWidget + pulsanti Aggiungi/Modifica/Elimina)
- [x] Tab sisma: zona sismica, pesi piani, forze automatiche
- [x] `_esegui_calcolo()` (LC1+LC2), `_esegui_calcolo_completo()` (tutte le combinazioni)
- [x] `_proponi_armature()`, `_verifica_armature()`
- [x] Salvataggio/caricamento JSON progetto
- [x] Export ASCII e HTML da menu
- [x] `MODULE_SPEC` + `create_module()` per `ModuleRegistry`

#### `canvas_telaio.py` — CanvasTelaio (QGraphicsView)

- [x] 3 modalita: SELEZIONE, AGGIUNGI_NODO, AGGIUNGI_ASTA
- [x] Simboli grafici per tutti i 9 tipi di vincolo esterno
- [x] Overlay diagrammi M/V/N (fill colorato sopra la geometria del telaio)
- [x] Zoom con rotellina, pan con drag, inversione asse Y
- [x] Segnali: `nodo_cliccato`, `asta_cliccata`, `nodo_richiesto`, `asta_richiesta`

#### `dialogo_nodo.py` — DialogoNodo (QDialog)

- [x] Coordinate x/y [cm], piano, etichetta
- [x] QComboBox per 9 tipi vincolo esterno con info live (GDL bloccati, n. reazioni)

#### `dialogo_asta.py` — DialogoAsta (QDialog)

- [x] 4 tab: Generale, Sezione (b, h, E, gamma, sigma_c_adm, sigma_s_adm), Rilasci (info k e c live), Carichi (lista + CRUD)
- [x] `get_dati()` — ritorna dict completo con `SezioneTelaio` costruita

**Dipendenze**: L.1, L.4, L.5, L.6, L.7, L.8; `src/ui/qt/visualizzatore_sezione.py`; `src/ui/qt/aiuto_contestuale.py`

---

### L.10 — Test benchmark numerici

**Stato**: COMPLETATO — 40 test, tutti verdi

#### `tests/test_carichi_fissi_telaio.py` — 16 test

- [x] `mip_uniforme(5, 300)` — atteso `(-37500, +37500)` tol 0.1%
- [x] `mip_concentrato(1000, 100, 300)` — verifica formula Pa*b^2/L^2
- [x] `mip_trapezoidale` — casi crescente, decrescente, uniforme, mix (verifica segno delta_w < 0 corretto)
- [x] `mip_peso_proprio` — w_pp = A * gamma, poi uniforme
- [x] Simmetria: mip_triangolare_crescente verso mip_triangolare_decrescente

#### `tests/test_cross_pozzati.py` — 11 test

- [x] Trave continua 2 campate: convergenza (< 200 iter), equilibrio nodo B (`|M_BA + M_BC| < 10`)
- [x] Portale 1 piano: convergenza, equilibrio nodi B e C, simmetria incastri A-D
- [x] Fattori di distribuzione: Sigma_mu=1 per ogni nodo libero, rigidezze k > 0
- [x] Telaio 2 piani con sway: convergenza, momenti finali non nulli

#### `tests/test_solver_telaio.py` — 4 test

- [x] Equilibrio verticale trave (Sigma_Fy=0)
- [x] Momenti agli incastri non nulli
- [x] Caso senza carichi: M/V/N = 0
- [x] Pilastro: assiale corretto

#### `tests/test_combinazioni_rd2229_telaio.py` — 9 test

- [x] `combinazioni_attive`: LC1/LC2 sempre, LC3/LC4 per bassa/media/alta, LC5/LC6 solo media/alta
- [x] Inviluppo: M_max >= M_min per ogni sezione, tutte le aste presenti
- [x] Coppia governante: `M_gov(idx)` e `N_gov(idx)` sono float, `combo_gov` e stringa

**Dipendenze**: L.2, L.3, L.4, L.5

---

## File creati

| File | Righe | Descrizione |
| --- | --- | --- |
| `src/methods/rd2229/telaio/__init__.py` | 1 | Package marker |
| `src/methods/rd2229/telaio/modello_telaio.py` | ~350 | Strutture dati modello |
| `src/methods/rd2229/telaio/carichi_fissi.py` | ~250 | Formule MIP |
| `src/methods/rd2229/telaio/cross_pozzati.py` | ~770 | Algoritmo Cross + sway |
| `src/methods/rd2229/telaio/solver_telaio.py` | ~350 | Sollecitazioni M/V/N |
| `src/methods/rd2229/telaio/sisma_telaio.py` | ~120 | Forze sismiche per piano |
| `src/methods/rd2229/telaio/combinazioni_rd2229.py` | ~370 | Combinazioni + inviluppo |
| `src/methods/rd2229/telaio/verifiche_telaio.py` | ~300 | Verifiche TA |
| `src/methods/rd2229/telaio/armature_telaio.py` | ~600 | Progetto armature |
| `src/methods/rd2229/telaio/export_telaio.py` | ~520 | Tabulati ASCII + HTML |
| `src/ui/qt/telaio/__init__.py` | 1 | Package marker |
| `src/ui/qt/telaio/canvas_telaio.py` | ~350 | Canvas QGraphicsView |
| `src/ui/qt/telaio/dialogo_nodo.py` | ~150 | Dialog nodo vincoli |
| `src/ui/qt/telaio/dialogo_asta.py` | ~250 | Dialog asta sezione/rilasci/carichi |
| `src/ui/qt/telaio/telaio_window.py` | ~550 | Finestra principale Qt |
| `tests/test_carichi_fissi_telaio.py` | ~200 | 16 test MIP |
| `tests/test_cross_pozzati.py` | ~340 | 11 test Cross |
| `tests/test_solver_telaio.py` | ~150 | 4 test solver |
| `tests/test_combinazioni_rd2229_telaio.py` | ~165 | 9 test combinazioni |

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| `InviluppoSollecitazioniAsta` con attributi per-sezione (`_i`, `_m`, `_j`) + metodi `M_gov(idx)`, `V_gov(idx)` | Accesso diretto O(1), evita indicizzazione su liste di lunghezza variabile |
| `calcola_rigidezze()` ritorna `(k_from_i, k_from_j, lunghezze)` come 3 dict separati | La rigidezza dipende dalla direzione di vista (nodo vicino), separazione chiarisce semantica |
| `calcola_cross_pozzati()` legge `modello.zona_sismica` (non parametro esterno) | La zona sismica e proprieta del modello, non del caso di carico |
| Unit bridge `_SezioneProxy` / `_MaterialeProxy` per verifiche TA | Adatta le unita kg/cm del telaio alle kN/kNm richieste da `CalcInput` senza modificare `checks.py` |
| Correzione sway: sistema n×n con Gauss + pivoting | Generalizza per qualsiasi numero di piani; alternativa iterativa non converge per molti piani |

---

## Bug corretti durante lo sviluppo

| Bug | File | Descrizione |
| --- | --- | --- |
| Segno errato `mip_trapezoidale` per delta_w < 0 | `carichi_fissi.py` | Per carico decrescente (w_sx > w_dx), la componente triangolare va negata rispetto a `mip_triangolare_crescente`, non rispetto a `mip_triangolare_decrescente` |
| API mismatch `InviluppoSollecitazioniAsta` | `armature_telaio.py`, `export_telaio.py` | Codice generato usava `inv.M_max[idx]` (lista); struttura reale usa attributi `inv.M_max_i`, `inv.M_max_m`, `inv.M_max_j` |
| Firma errata `calcola_fattori_distribuzione` nei test | `test_cross_pozzati.py` | Funzione accetta `(modello, k_from_i, k_from_j)`; test passava la tupla intera `(modello, rigidezze)` |
| `calcola_tutte_le_combinazioni` — zona come secondo arg | `test_combinazioni_rd2229_telaio.py` | La zona non e parametro della funzione (viene da `modello.zona_sismica`); i test passavano `"bassa"` come secondo arg (che e `carichi_variabili`) |
| `combinazioni_attive` ritorna `list[str]` | `test_combinazioni_rd2229_telaio.py` | Test accedevano a `c.id_caso` come se fossero oggetti; la funzione ritorna direttamente le stringhe `["LC1", "LC2", ...]` |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

**Contesto**: La Fase L e stata pianificata (ExitPlanMode da `fizzy-gliding-turing.md`) e implementata in 2 sessioni chat consecutive.

**Decisioni prese senza Q&A esplicito** (implementazione autonoma da piano dettagliato):

- Strutture dati: scelta di attributi per-sezione vs liste per `InviluppoSollecitazioniAsta` — **per-sezione** (accesso diretto)
- Correzione sway: sistema n×n con Gauss vs iterazione a blocchi — **Gauss** (convergenza garantita)
- GUI: 4 dock (left/central/right/bottom) vs layout a tab — **4 dock** (accesso parallelo)
- Test: benchmark da Santarella/Pozzati con verifica equilibrio vs test puramente strutturali — **entrambi**

---

## Note storiche/archivio (appendice)

Il metodo di Cross (1930) e il metodo storico per eccellenza nel calcolo dei telai piani in c.a. in Italia, adottato da tutti i testi classici:

- **Pozzati**, "Teoria e Tecnica delle Strutture", vol.II §§3.4-3.8 — algoritmo no-sway e correzione sway multi-piano
- **Santarella**, "Il Cemento Armato" vol.II cap.3 — tabelle MIP, fattori di distribuzione, schede armatura
- **Ciribini**, note integrative sulla correzione sway per telai irregolari

La correzione sway (Pozzati §3.8) risolve il sistema n×n `H * lambda = R` dove `H[i,j]` e il taglio al piano i per sway unitario al piano j. Per telai regolari con piani numerosi, il sistema e ben condizionato; per telai irregolari o con pilastri molto rigidi puo richiedere pivoting.
