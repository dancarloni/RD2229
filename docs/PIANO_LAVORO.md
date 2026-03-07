# PIANO DI LAVORO — RD2229 Software di Calcolo Strutturale

> **⭐ QUESTO FILE È LA FONTE DI VERITÀ DEL PROGETTO.**
>
> Funzioni di questo documento:
> 1. **Registro attività** — ogni completamento è marcato con hash commit
> 2. **Guida operativa** — ogni fase ha sub-plan dettagliati con checkbox [x]/[ ]
> 3. **Stato avanzamento** — contatori test, moduli, norme sempre aggiornati
> 4. **Continuità tra sessioni** — dopo compattazione contesto, rileggi questo file
>
> **Regola**: PRIMA di lavorare su qualsiasi fase, leggere questo file.
> **Regola**: DOPO aver completato qualsiasi sotto-punto, aggiornare questo file.
> **Riferimento**: `CLAUDE.md` alla radice del repo punta a questo file.

**Ultimo aggiornamento**: 2026-03-06
**Branch**: `main`

---

## Stato Generale

| Indicatore | Valore |
|---|---|
| Test totali | ~2233 |
| Test falliti | 0 |
| Moduli implementati | 69+ |
| Norme coperte | 10 (RD2229, DM72, DM87, DM92, DM96, NTC2008, NTC2018, Circ81, OPCM3274, EC8) |

---

## FASE A — Database Materiali Multi-Normativa

### A.1 Cataloghi JSON per tutte le norme ✅
**Stato**: COMPLETATO — commit `a0f05aa`

| Catalogo | File | Materiali | Note |
|---|---|---|---|
| NTC2018 | `data/materials/catalogo_ntc2018.json` | 18 | C12/15→C50/60, B450C/A, muratura |
| RD2229 | `data/materials/catalogo_rd2229.json` | 10 | Cls storici Rck 120-300, Aq.42/50/60 |
| DM72 | `data/materials/catalogo_dm72.json` | 8 | Cls Rck 150-350, Aq.42/50/60, FeB32k |
| DM87 | `data/materials/catalogo_dm87_muratura.json` | 9 | Muratura: mattoni, blocchi, tufo, pietra |
| DM92 | `data/materials/catalogo_dm92.json` | 10 | Cls Rck 150-400, FeB22k/32k/38k/44k |
| DM96 | `data/materials/catalogo_dm96.json` | 12 | Come DM92 + classi alte (Rck 450, 500) |
| NTC2008 | `data/materials/catalogo_ntc2008.json` | 12 | C12/15→C50/60, B450C/A |
| Circ81 | `data/materials/catalogo_circ81_muratura.json` | 5 | Muratura storica, γ_M≥5.0 |
| Legno | `data/materials/catalogo_legno.json` | 6 | EN 338/14080 |
| OPCM3274 | `data/materials/catalogo_opcm3274.json` | 7 | Stessi valori DM96, γ_c=1.60, γ_s=1.15 |
| **Totale** | | **97** | |

- `material_repo.py`: metodi `list_by_norma()`, `list_norme_disponibili()`, `carica_tutti_cataloghi()`
- Test: `tests/test_cataloghi_materiali.py` (22 test)

### A.2 MaterialSource strutturata

**Stato**: TODO
**Priorita**: MEDIA (prerequisito per Fase Q — Report relazione di calcolo)

**Obiettivo**: Collegare ogni materiale alla sua fonte normativa con riferimento preciso
(norma, articolo, paragrafo, tabella), abilitando citazione automatica nei tabulati.

#### Analisi stato attuale

Esistono **3 entita' parallele** per i riferimenti normativi, non collegate tra loro:

| Entita' | File | Uso attuale | Azione |
|---------|------|-------------|--------|
| `MaterialSource` | `src/legacy/material_sources.py` | Legacy, 9 norme predefin. | Estrarre dati utili, eliminare file |
| `NormRef` | `src/checks/registry.py` | CheckSpec (source_id + clause) | Mantenere (scope diverso: check) |
| `NormReference` | `src/core_calculus/contracts.py` | SingleCheckResult | Mantenere (scope diverso: risultati) |

Il modello `Material` (`src/materials/material_model.py`) ha solo `norma_riferimento: str`
(es. "NTC2018") — un semplice codice, senza articolo/paragrafo/tabella.

I cataloghi JSON (`data/materials/catalogo_*.json`) hanno solo `"norma_riferimento": "NTC2018"`.

Il file `docs/normative/sources.yaml` contiene 8 fonti con id, title, year, authority.

**File legacy da analizzare e poi eliminare**:
- `src/legacy/material_sources.py` (~330 righe): contiene `MaterialSource` dataclass,
  `MaterialSourceLibrary` CRUD, `_get_default_sources()` (9 norme), logica di calcolo
  per RD2229/DM72/DM92/DM96. La logica di calcolo e' gia' coperta da
  `src/materials/material_model.py` (parametri derivati) e `src/tools/concrete_strength.py`.
  I dati delle 9 fonti vanno migrati in `data/materials/material_sources.json`.
  Il `CalculationMethod` enum (TA/SL/SP/SPER) e' utile e va incorporato.

#### Sub-plan dettagliato

- [ ] **A.2.1** Creare `src/materials/material_source.py` (NUOVO, nella struttura attiva)
  - Dataclass `MaterialSource` con campi: `id`, `name`, `year`, `calculation_method`,
    `is_historical`, `reference`, `description`, `notes`
  - Enum `MetodoCalcolo` (TA, SL, SP, SPER) — incorporato da legacy `CalculationMethod`
  - Dataclass `MaterialNormRef` per riferimenti puntuali ai parametri:
    - `norma_id: str` (es. "NTC2018")
    - `articolo: str` (es. "§4.1.2.1.1")
    - `tabella: str | None` (es. "Tab. 4.1.I")
    - `formula: str | None` (es. "f_cd = alpha_cc * f_ck / gamma_c")
    - `parametro: str` (es. "f_ck", "gamma_c")
    - `descrizione_it: str`
  - `to_dict()` / `from_dict()` per serializzazione JSON

- [ ] **A.2.2** Creare `data/materials/material_sources.json`
  - Migrare le 9 fonti predefinite da `src/legacy/material_sources.py`
    (RD2229, DM72, DM92, DM96, OPCM3274, NTC2008, NTC2018, LAB_TEST, CUSTOM)
  - Aggiungere fonti da `docs/normative/sources.yaml` non gia' presenti
    (DM87, Circ81, ISO834, EN1992_1_2, EN1991_1_4, CNR_DT207, NTC2018_CIRC)
  - Formato JSON nativo (no dipendenza PyYAML)

- [ ] **A.2.3** Collegare `MaterialNormRef` a `Material`
  - Aggiungere campo `source_refs: list[dict]` a `Material` in `material_model.py`
  - Default: lista vuota (retrocompatibilita' con materiali esistenti)
  - Aggiornare `to_dict()` / `from_dict()` per serializzazione

- [ ] **A.2.4** Aggiornare `MaterialRepository` per gestire `MaterialSource` tipizzata
  - `load_sources()` gia' presente ma usa `list[dict]` generico
  - Sostituire con `list[MaterialSource]` tipizzato
  - `get_source()` restituisce `MaterialSource` anziche' `dict`

- [ ] **A.2.5** Popolare cataloghi JSON con riferimenti normativi (incrementale)
  - `catalogo_ntc2018.json`: §4.1 cls, §4.2 acciaio, §4.5 muratura, Tab. 4.1.I, 4.2.I
  - `catalogo_rd2229.json`: Art. 10-14 tensioni ammissibili cls/acciaio
  - Altri cataloghi: aggiungere progressivamente (non bloccante)

- [ ] **A.2.6** Integrare nel report
  - `src/report/tabulati_calcolo.py`: sezione "Riferimenti normativi materiali"
  - Help contestuale: mostrare §/tabella nel tooltip parametro (material_editor)

- [ ] **A.2.7** Eliminare file legacy
  - Eliminare `src/legacy/material_sources.py` (dati migrati, logica gia' coperta)
  - Verificare che nessun import attivo punti a questo file
  - Aggiornare eventuali import in `src/legacy/ui/historical_material_window.py`

- [ ] **A.2.8** Test
  - Serializzazione/deserializzazione `MaterialSource` e `MaterialNormRef`
  - `Material.to_dict()` con source_refs presente e assente
  - Caricamento catalogo con riferimenti
  - Retrocompatibilita' cataloghi senza riferimenti
  - `MaterialRepository.load_sources()` con nuovi tipi

#### Dipendenze

| Dipende da | Modulo | Stato |
|-----------|--------|-------|
| `Material` model | `src/materials/material_model.py` | COMPLETATO |
| `MaterialRepository` | `src/materials/material_repo.py` | COMPLETATO |
| `sources.yaml` | `docs/normative/sources.yaml` | COMPLETATO (8 fonti) |

#### Abilitato da A.2 (dipendenze inverse)

| Fase | Beneficio |
|------|-----------|
| Q — Report relazione di calcolo | Citazione automatica norma/§/tabella per ogni materiale |
| GUI material editor | Help contestuale con § e tabella |
| Fase H — Riorganizzazione | Unificazione eventuale NormRef/NormReference/MaterialSource |

#### Note architetturali

- `MaterialNormRef` e' specifica per i materiali; NON unificare ora con `NormRef` o
  `NormReference` (scope diversi: check vs risultati vs materiali)
- `source_refs` opzionale in Material — cataloghi esistenti continuano a funzionare
- JSON nativo, no PyYAML

### A.3 Adapter unità (kg/cm² ↔ MPa)
**Stato**: COMPLETATO — `src/materials/adapter.py` (112 righe)

---

## FASE B — Torsione RD2229 TA

### B.1 Modulo torsione TA ✅
**Stato**: COMPLETATO — commit 394dc31

**File**: `src/methods/rd2229/torsione.py` (~310 righe)

Tradotto da VB `Sub Torsione()` (PrincipCA_TA.bas riga 3818).

#### Sub-plan B.1:
- [x] Dataclass `InputTorsione` con tutti i parametri geometrici e materiali
- [x] Enum `TipoSezione` (Rettangolare, Circolare, T, T rovescia, Doppio T, Scatolare)
- [x] Enum `EsitoTorsione` (nessuna_armatura, armatura_necessaria, sezione_insufficiente)
- [x] `calcola_tau_max_rettangolare()` — Ψ = 3 + 2.6/(0.45 + a/b)
- [x] `calcola_tau_max_circolare()` — τ = 2·|Mx|·Re / (π·(Re⁴-Ri⁴))
- [x] `calcola_tau_max_T()` — τ = 3·|Mx|·b_max / (a1·b1³ + a2·b2³)
- [x] `calcola_tau_max_doppio_T()` — denominatore con 2·a1·b1³
- [x] `calcola_tau_max_scatolare()` — τ = |Mx| / (2·Am·s_min)
- [x] Calcolo area/perimetro tubolare equivalente per tutte le sezioni
- [x] `verifica_torsione_ta()` — flusso completo verifica/progetto
- [x] Interazione T+V: τ_c1,t = τ_c1 × 1.1
- [x] Progetto armatura (Al_to, Pst_to, n_barre)
- [x] Verifica armatura esistente (σ_l, σ_st vs σ_s_adm)
- [x] `RisultatoTorsione.to_dict()` per report
- [x] Passaggi di calcolo tracciabili

**Test**: `tests/test_torsione_rd2229.py` (23 test)

---

## FASE C — Instabilità RD2229 TA

### C.1 Modulo instabilità (carico di punta) ✅
**Stato**: COMPLETATO — commit 394dc31

**File**: `src/methods/rd2229/instabilita.py` (~270 righe)

Tradotto da VB `Sub VerifStabilitàAstaCA()` (riga 4057) e `Function f_OmegaCA()` (riga 4272).

#### Sub-plan C.1:
- [x] `omega_ca(lambda)` — tabella interpolata (λ=50→140, ω=1.0→3.0)
- [x] `sigma_c_adm_ridotta()` — riduzione per sezioni snelle (a < 25 cm)
- [x] Dataclass `InputStabilita` con geometria, sollecitazioni, materiali, vincoli
- [x] Calcolo snellezza λ = L₀/r in entrambi i piani
- [x] Carico critico Euleriano Pcr = π²·(0.4·Ec)·I/L₀²
- [x] Verifica compressione semplice: σ_c = ω·|N|/A_ci
- [x] Verifica pressoflessione (3 verifiche):
  - [x] 1ª: N amplificato (ω·N)
  - [x] 2ª: N e M amplificati (ω·N, α_M·M)
  - [x] 3ª: solo M amplificato (N, α_M·M)
- [x] α_M = 1/(1 - |N|/Pcr_y)
- [x] `RisultatoStabilita.to_dict()` per report
- [x] Passaggi di calcolo tracciabili

**Test**: `tests/test_instabilita_rd2229.py` (23 test)

---

## FASE D — Cordoli Metallici

**Stato**: PARZIALMENTE COMPLETATO

### D.1 Sagomario EN 10365 ✅
**Stato**: COMPLETATO — commit corrente
- [x] Database profili IPE (18), HEA (19), HEB (19), HEM (19), UPN (12) in JSON — 87 profili totali
- [ ] Import CSV custom utente
- [x] Ricerca e filtro profili (per famiglia, Wx minimo, altezza, profilo ottimale)

**File**: `src/steel/sagomario.py` (~188 righe), `data/steel/sagomario_*.json`
**Test**: `tests/test_sagomario_acciaio.py` (32 test)

### D.2 Verifiche profilo singolo ✅
**Stato**: COMPLETATO — commit corrente
- [x] Flessione (σ = M/W ≤ σ_adm)
- [x] Taglio (τ = V/A_anima ≤ τ_adm)
- [x] Instabilità (ω·N/A, tabella CNR 10011)
- [x] Pressoflessione (N + Mx + My)
- [x] Combinata Von Mises (σ_VM = √(σ² + 3τ²))
- [x] Selezione profilo ottimale per momento

**File**: `src/steel/verifiche_ta.py` (~410 righe)
**Test**: `tests/test_verifiche_acciaio_ta.py` (33 test)

### D.3 Traliccio reticolare piano — cordolo metallico reticolare

**Stato**: COMPLETATO (commit da aggiornare dopo push)
**Priorita**: ALTA (collegamento diretto con Fase E.3 meccanismi fuori piano muratura)

#### D.3.0 — SezioneAsta (PREREQUISITO per tutte le fasi D.3)

**Stato**: COMPLETATO

- [x] `src/steel/sezione_asta.py` (NUOVO)
  - Dataclass `SezioneAsta`: `A, Ix, Iy, ix, iy, nome, tipo (enum TipoSezioneAsta)`
  - Enum `TipoSezioneAsta` (PIATTO, ANGOLARE, PROFILO_STANDARD)
  - `SezioneAsta.da_piatto(b, t)` — orientamento FLAT (b in Y=spessore muro, t in Z=verticale)
    ix=b/sqrt(12) in-piano, iy=t/sqrt(12) fuori-piano (governa lambda)
  - `SezioneAsta.da_angolare_pari(b, t)` — calcolo esatto centroide + I
  - `SezioneAsta.da_profilo(profilo: ProfiloAcciaio)` — wrapper
  - `to_dict()` / `from_dict()`
- [x] `data/steel/piatti.json` (NUOVO) — 15 taglie standard serie UNI 5679
- [x] `data/steel/angolari.json` (NUOVO) — 10 taglie EN 10056-1 L30..L150
- [x] Refactoring `verifica_aste_traliccio()` in `src/steel/traliccio_2d.py`
  - Usa `SezioneAsta.ix`/`iy` reali per instabilita' biassiale
  - lambda_in_piano = L/ix, lambda_fuori_piano = L/iy; omega = omega_acciaio(max)
- [x] Aggiungere `verifica_asta_ta()` in `src/steel/verifiche_ta.py`
- [x] Test: `tests/test_sezione_asta.py` — 38 test, tutti verdi

**Obiettivo**: Modulo per tralicci piani in acciaio (piatti saldati/bullonati, angolari,
profili standard), con caso d'uso primario come **cordolo reticolare orizzontale** su
muratura per contrastare meccanismi fuori piano, ma utilizzabile anche standalone
come verifica generica traliccio 2D.

#### Concetto strutturale

Il traliccio e' disposto **orizzontalmente in pianta** sulla sommita' del muro.
Entrambi i correnti e le diagonali sono nello spessore della muratura.
Il cordolo reticolare si oppone ai meccanismi fuori piano (ribaltamento, spanciamento,
cuneo d'angolo) con la sua rigidezza e resistenza nel piano di maggiore inerzia.

La forza F proviene dall'analisi cinematica (`src/methods/muratura/cinematica.py`) e
viene applicata come carico distribuito sul corrente superiore (variabile in funzione
del segno di F / direzione sisma). Il traliccio e' caricato sempre nella direzione
di maggiore rigidezza.

#### Decisioni architetturali (da Q&A)

| Aspetto | Decisione |
|---------|-----------|
| Schemi | Warren, Pratt, custom (disegno grafico libero — fase futura) |
| Profili aste | Piatti, angolari, profili standard da sagomario |
| Solutore | Riuso `src/steel/traliccio_2d.py` (rigidezza diretta) |
| Orientamento | Piano XY reinterpretato come orizzontale (X=lungo muro, Y=spessore) |
| Profondita' traliccio | Configurabile, default = spessore muro |
| Sviluppo in pianta | Singolo muro rettilineo OPPURE anello chiuso perimetrale |
| Angoli (se anello) | Nodo rigido saldato OPPURE piastra d'angolo bullonata |
| Carichi | Solo forze orizzontali nel piano del traliccio |
| F da cinematica | Automatico da `cinematica.py`, distribuzione proporzionale al modo o discreta ai nodi, a scelta utente |
| Vincoli | Appoggi estremi + molle distribuite lungo corrente (configurabili) |
| Collaborazione muro | Grado configurabile: vincolo cinematico puro / azione composta / intermedio |
| Corrente caricato | Entrambi, in funzione della direzione del sisma |
| Combinazioni | Tutte le norme supportate + custom utente (attivabili/disattivabili) |
| Verifiche | SLU + SLE + fatica ciclica (TODO placeholder) |
| Instabilita' | Entrambi i piani (orizzontale e verticale), selezionabile dall'utente |
| Normativa acciaio | Selezionabile (NTC2018 SLU / TA storica) |
| Meccanismi fuori piano | Tutti attivi di default, disattivabili singolarmente |
| Collegamento muro | Barre inghisate / tasselli chimici / connettori, selezionabile |
| Rigidezza collegamento | Configurabile (cerniera / incastro parziale) |
| Unita' misura | Selezionabile tramite `unita_misura.py` |
| Report | Tabulato integrato nell'edificio + esportabile standalone |
| Uso standalone | Si', anche senza contesto muratura |

#### Sub-plan dettagliato

**D.3.1 — Generatore schemi traliccio**
- [x] `src/steel/traliccio_generatore.py` (NUOVO)
- [x] `genera_howe(L, h, n_campate, sezione_corrente, sezione_diagonale)` → nodi + aste (4n+1 barre)
- [x] `genera_pratt(L, h, n_campate, ...)` → nodi + aste (4n+1 barre)
- [x] `predimensiona_sezione(N_max, L_asta, tipo_acciaio)` — profili minimi
- [x] `valida_geometria(nodi, aste)` — warning angoli piatti (<20°), snellezze
- [x] `applica_vincoli_cordolo()` — cerniera / incastro / semi_incastro agli estremi
- [x] Test: `tests/test_traliccio_generatore.py` — 27 test, tutti verdi
- NOTE: Schema WARREN eliminato (struttura labile per n>3); sostituito da HOWE e PRATT
  con n+1 montanti verticali (topologia sempre stabile: b+r = 4n+7 > 4n+4)

**D.3.2 — Adattamento solutore traliccio_2d**
- [x] `distribuisci_carico_corrente()` — carico distribuito → forze nodali equivalenti
- [x] `K_globale` e `delta_max` in `RisultatoTraliccio`
- [x] Retrocompatibilita': 19 test originali invariati

**D.3.3 — Modulo cordolo reticolare**
- [x] `src/elements/cordolo_reticolare.py` (NUOVO)
- [x] Dataclass `CordoloReticolare`: schema, profili, L, h, vincoli, collegamento_muro, tipo_estremi
- [x] `verifica_cordolo_reticolare()` → `RisultatoCordoloReticolare` completo
- [x] `dimensiona_cordolo_reticolare()` → ricerca profilo minimo per F_y dato
- [x] Enum `SchemaReticolare` (HOWE, PRATT)

**D.3.4 — Verifiche aste del traliccio**
- [x] Verifica compressione + instabilita' biassiale (lambda_in_piano, lambda_fuori_piano)
- [x] Verifica trazione
- [x] Verifica collegamento traliccio-muro F3 (tau nodi vs tau_adm)
- [x] Normativa: TA storica (verifiche_ta.py)

**D.3.5 — Integrazione con cinematica.py**
- [x] `ritegno_sommitale: float = 0.0` aggiunto a tutti i meccanismi fuori piano
- [x] `M_rib_coeff` aggiunto a `RisultatoCinematica` per calcolo D1
- [x] `ribaltamento_semplice`, `ribaltamento_composto`, `flessione_orizzontale`,
      `flessione_verticale`, `analisi_meccanismi_locali`, `analisi_tutti_meccanismi`
- [x] Retrocompatibilita': 49 test originali invariati

**D.3.6 — Nodo d'angolo (cantonali)**
- [x] `InputNodoAngolo` + `verifica_nodo_angolo()` in `cordolo_reticolare.py`
- [x] Equilibrio locale: F_risultante = vettoriale F1 + F2
- [x] Verifica saldatura nodo tramite `verifica_saldatura_ta()`

**D.3.7 — Report e tabulato**
- [x] `sezione_cordolo_reticolare()` in `src/report/tabulati_calcolo.py`
- [x] Tabella aste ASCII (ID / tipo / L / N / sigma / sfruttamento / esito)
- [x] Collegamento muro F3, esito finale

**D.3.8 — Test**
- [x] 97 nuovi test (test_sezione_asta: 38, test_traliccio_generatore: 27, test_cordolo_reticolare: 32)
- [x] Retrocompatibilita': traliccio_2d (19 test) + cinematica_muratura (49 test) tutti verdi
- [x] Suite completa: 2237 passed (esclusi test_carote e test_por_verifiche pre-esistenti)

**D.3.9 — Tool disegno grafico avanzato (FASE FUTURA)**
- [ ] Disegno intuitivo nodi e aste per configurazione custom
- [ ] Da implementare dopo D.3.1-D.3.8

#### Dipendenze

| Dipende da | Modulo | Stato |
|-----------|--------|-------|
| Solutore traliccio 2D | `src/steel/traliccio_2d.py` (D.4) | COMPLETATO |
| Connessioni acciaio | `src/steel/connessioni.py` (D.5) | COMPLETATO |
| Verifiche acciaio TA | `src/steel/verifiche_ta.py` (D.2) | COMPLETATO |
| Sagomario profili | `src/steel/sagomario.py` (D.1) | COMPLETATO |
| Meccanismi fuori piano | `src/methods/muratura/cinematica.py` (E.3) | COMPLETATO |
| Cordolo base | `src/elements/cordolo.py` (D.6) | COMPLETATO (enum METALLICO_RETICOLARE dichiarato, non implementato) |
| Unita' misura | `src/core/unita_misura.py` | COMPLETATO |

#### Abilitato da D.3 (dipendenze inverse)

| Fase | Beneficio |
|------|-----------|
| E.3 Meccanismi locali | Ritegno sommitale migliora alpha_0 |
| E.6 Cantonali | Verifica nodo d'angolo del cordolo |
| D.7 GUI cordoli | Interfaccia per configurazione reticolare |
| Fase R — Edifici esistenti | Intervento di miglioramento sismico tipico |

#### Note architetturali

- Il solutore `traliccio_2d.py` e' gia' generico (piano XY); non serve flag orientamento
- `CordoloReticolare` estende concettualmente `CordoloMetallico` (D.6) ma e' classe separata
- La fatica ciclica sismica e' un TODO placeholder — metodo da definire in fase successiva
- Il flusso iterativo cinematica ↔ traliccio (Q26c) e' un TODO futuro, non bloccante

### D.4 Solutore traliccio 2D ✅
**Stato**: COMPLETATO — commit corrente
- [x] Metodo della rigidezza diretta (Gauss con pivoting parziale)
- [x] Input nodi + aste + vincoli (cerniera, carrello_x, carrello_y) + carichi
- [x] Sforzi normali nelle aste (trazione/compressione)
- [x] Reazioni vincolari con verifica equilibrio globale
- [x] Verifiche a compressione/trazione con instabilità (ω)

**File**: `src/steel/traliccio_2d.py` (~330 righe)
**Test**: `tests/test_traliccio_2d.py` (19 test)

### D.5 Connessioni ✅
**Stato**: COMPLETATO — commit corrente
- [x] Saldature a cordone d'angolo (frontale, laterale, combinata)
- [x] Saldature testa a testa (completa penetrazione)
- [x] Bullonature: taglio (gambo/filetto)
- [x] Bullonature: trazione
- [x] Bullonature: interazione taglio+trazione (V/V_Rd)²+(N/N_Rd)²≤1
- [x] Bullonature: rifollamento lamiera
- [x] Coefficienti β_w (CNR 10011), classi 4.6÷10.9, M12÷M36

**File**: `src/steel/connessioni.py` (~380 righe)
**Test**: `tests/test_connessioni_acciaio.py` (24 test)

### D.6 Modello cordolo (CA + metallico) ✅
**Stato**: COMPLETATO — commit corrente
- [x] Cordolo CA: sezione, armatura, minimi NTC2018 §7.8.1.6
- [x] Cordolo metallico: profilo singolo, flessione/taglio TA
- [x] Verifica flessione e taglio per entrambi i tipi
- [x] Posizione: sommitale, intermedio, fondazione

**File**: `src/elements/cordolo.py` (~350 righe)

### D.7 GUI Qt cordoli
- [ ] Interfaccia selezione profilo
- [ ] Visualizzazione sezione
- [ ] Input sollecitazioni
- [ ] Output verifiche

---

## FASE E — Muratura Verifiche Locali

**Stato**: PARZIALMENTE COMPLETATO

### E.1 Compressione + snellezza ✅
**Stato**: COMPLETATO — commit corrente
- [x] σ ≤ f_d / γ_M con riduzione snellezza Φ
- [x] Tabella Φ da NTC2018 Tab 4.5.V (interpolazione bilineare λ×e/t)
- [x] Eccentricità e/t da momento flettente
- [x] Fattore vincolo ρ per altezza efficace

### E.2 Taglio nel piano ✅
**Stato**: COMPLETATO — commit corrente
- [x] Criterio diagonale (Turnšek-Čačovič) — NTC2018 §7.8.2.2.1
- [x] Criterio di scorrimento (Mohr-Coulomb: fvk = fvk0 + μ·σ_n)
- [x] Pressoflessione nel piano — V_pf = (L²×t×σ₀)/(2h₀)×(1-σ₀/(0.85fd))
- [x] Verifica combinata con ordinamento per V_Rd (criterio più restrittivo)

### E.3 Fuori piano + ribaltamento (meccanismi locali) ✅
**Stato**: COMPLETATO — commit corrente
- [x] Ribaltamento semplice (parete ruota alla base)
- [x] Ribaltamento composto (parete + cuneo sovrastante)
- [x] Flessione verticale (cerniera a metà altezza, meccanismo a 2 corpi)
- [x] Flessione orizzontale (arco a 3 cerniere tra vincoli laterali)
- [x] Cinematica lineare (§C8A.4.1): α₀, M*, e*, a₀*, verifica a terra e in quota
- [x] Cinematica non lineare (§C8A.4.2): d₀*, d*_u = 0.4·d₀*, T_s, domanda spostamento
- [x] Integrazione catene/tiranti (ForzaCatena con angolo, contributo stabilizzante)
- [x] Analisi completa tutti i meccanismi ordinati per α₀ crescente
- [x] Parametri sismici manuali (a_g, S, q, FC) + predisposizione INGV

**File**: `src/methods/muratura/cinematica.py` (~654 righe)
**Test**: `tests/test_cinematica_muratura.py` (49 test)

### E.4 Spanciamento ✅
**Stato**: COMPLETATO — commit corrente
- [x] Verifica snellezza muro λ = h_eff/t ≤ λ_max
- [x] Limiti configurabili (20 ordinario, 15 esistente, 12 sismico)

**File**: `src/methods/muratura/verifiche.py` (~400 righe)
**Test**: `tests/test_muratura_verifiche.py` (34 test)

### E.5 Catene e paletti ✅
**Stato**: COMPLETATO — commit corrente
- [x] Tipi piastre (circolare, quadrata, a paletto)
- [x] Verifica trazione catena (σ = F/A ≤ σ_s_adm)
- [x] Verifica punzonamento locale piastra (σ_p ≤ fd_mur)

**File**: `src/elements/cordolo.py` (catene + cordoli)
**Test**: `tests/test_cordolo.py` (25 test)

### E.6 Cantonali e aperture — meccanismo ribaltamento cantonale + riduzione resistenza

**Stato**: TODO
**Priorita**: ALTA (collegamento diretto con E.3 + D.3)

**Obiettivo**: Implementare (A) il meccanismo di ribaltamento del cantonale (cuneo 3D),
(B) la riduzione di resistenza dei maschi d'angolo per aperture ravvicinate.
L'apertura di nuovi vani in pareti portanti (confronto prima/dopo) e' in fase separata (Fase R).

#### E.6.A — Ribaltamento del cantonale (meccanismo 3D)

**Concetto**: Un cuneo di muratura delimitato da fratture diagonali a ~45° nelle due
pareti concorrenti si stacca e ribalta. Tipico di tetti a padiglione con puntoni
spingenti. L'asse di rotazione e' perpendicolare al piano a 45° tra le due pareti.

**Modellazione**: Modello semplificato 2D (proiezione del cuneo su piano a 45°, come
3Muri/PRO_CineM). Modello 3D completo come TODO futuro.

Riferimenti: Schede ReLUIS meccanismi locali, Circ. n.7/2019 §C8A.4, Casapulla & Maione (2020).

#### Decisioni architetturali (da Q&A)

| Aspetto | Decisione |
|---------|-----------|
| Geometria cuneo | Selezione 2 pareti dal modello + input diretto, entrambi |
| Angolo asse rotazione | Configurabile (default 45°) + auto-calcolabile da spessori pareti |
| Modulo | Separato: `src/methods/muratura/cantonale.py` (massima modularita') |
| Carichi sul cuneo | Tutti configurabili: peso proprio, puntone, solaio, catena, cordolo D.3 |
| Spinta puntone | Input manuale + calcolo automatico (2 formulazioni) |
| Tipologie copertura | Padiglione, capanna, generica (forza diretta) |
| Distanza min apertura-angolo | Normativa + regola pratica (t_muro) + configurabile |
| Riduzione resistenza | Warning + coefficiente + check PASS/FAIL, utente sceglie quali |
| Riduzione agisce su | Selezionabile: V_Rd taglio, ammorsamento (alpha_0), o entrambi |
| Flag maschio d'angolo | Automatico con override manuale |
| Collegamento con D.3 | Default: cordolo come ritegno generico (D.3.5). Evoluzione: nodo angolo D.3.6 fornisce H specifica |
| In analisi_tutti_meccanismi | Si', con flag "3D" per distinguerlo dai 2D |

#### Sub-plan dettagliato

**E.6.1 — Modulo cantonale.py (meccanismo ribaltamento)**

- [ ] `src/methods/muratura/cantonale.py` (NUOVO, modulo separato)
- [ ] Dataclass `InputCantonale`: 2 pareti (h, t, L_distacco), carichi, catene, ritegni
- [ ] Dataclass `SpintaPuntone`: pendenza, luce, carico_mq OPPURE forza_diretta
  - Formula A: F_h = q * L / (2 * tan(alpha)) — da carico distribuito
  - Formula B: F_h = V / tan(alpha) — da forza verticale
- [ ] Enum `TipoCopertura` (PADIGLIONE, CAPANNA, GENERICA)
- [ ] `calcola_spinta_puntone(tipo, ...)` → F_h [kg]
- [ ] `ribaltamento_cantonale(input)` → `RisultatoMeccanismo`
  - Geometria cuneo 3D proiettata su piano a 45°
  - Peso cuneo = 0.5 * h * L1_dist * t1 * gamma + 0.5 * h * L2_dist * t2 * gamma
  - Bracci stabilizzanti e ribaltanti come da schede ReLUIS
  - Angolo asse rotazione: configurabile (default 45°), auto = arctan(t2/t1)
  - Contributo catene/tiranti come in cinematica.py (ForzaCatena)
  - Contributo ritegno cordolo D.3 (opzionale)
- [ ] `RisultatoCantonale(RisultatoMeccanismo)`: alpha_0, passaggi, tipo="3D"
- [ ] Aggiungere `RIBALTAMENTO_CANTONALE` a `TipoMeccanismo` in cinematica.py
- [ ] Integrare in `analisi_tutti_meccanismi()` con flag 3D

**E.6.2 — Riduzione resistenza maschi d'angolo per aperture**

- [ ] `src/methods/muratura/cantonale.py` — funzioni aggiuntive nello stesso modulo
- [ ] `diagnostica_apertura_angolo(parete, aperture)` → warning/check
  - Calcola distanza apertura piu' vicina dall'angolo della parete
  - Soglie: normativa NTC2018 (se presente), regola pratica d_min = max(t, 100 cm),
    configurabile dall'utente
  - Esito: OK / WARNING / FAIL con messaggio e distanza misurata
- [ ] `coefficiente_riduzione_angolo(distanza, t, criterio)` → float [0..1]
  - Riduzione lineare: k = min(distanza / d_min, 1.0)
  - Criterio selezionabile: taglio V_Rd, ammorsamento alpha_0, entrambi
- [ ] `flag_maschio_cantonale(maschio, parete)` → bool
  - Automatico: maschio il cui bordo sinistro == x_ini parete (inizio) o destro == x_fin (fine)
  - Override manuale tramite campo opzionale `is_cantonale` su Maschio
- [ ] Integrazione in `discretizza_parete()`:
  - Maschi d'angolo ricevono automaticamente `is_cantonale = True`
  - Se apertura ravvicinata: `fattore_riduzione_angolo` calcolato e assegnato

**E.6.3 — Spinta puntoni copertura**

- [ ] Calcolo automatico per tetto a padiglione (puntone diagonale + correnti)
- [ ] Calcolo automatico per tetto a capanna (spinta su timpano)
- [ ] Input generico: forza F, direzione, punto di applicazione
- [ ] Integrazione come carico esterno nel meccanismo cantonale

**E.6.4 — Integrazione con cordolo reticolare D.3**

- [ ] Il cordolo D.3 modellato come ritegno sommitale generico (forza H o rigidezza K)
  - Default: stessa logica di D.3.5 (ritegno_sommitale in cinematica)
- [ ] Evoluzione: il nodo d'angolo D.3.6 fornisce la forza H specifica al cantonale
  - Il traliccio ad anello distribuisce le forze ai nodi d'angolo
  - H_angolo = reazione del nodo d'angolo del traliccio sotto i carichi cinematici
- [ ] Entrambi gli approcci implementati, selezionabili dall'utente
- [ ] Note: l'approccio (c) D.3.6 e' piu' preciso ma richiede D.3 completato

**E.6.5 — Test**

- [ ] Ribaltamento cantonale: cuneo simmetrico (2 pareti uguali, alpha_0 noto)
- [ ] Ribaltamento cantonale: cuneo asimmetrico (spessori diversi)
- [ ] Angolo asse rotazione: 45° vs auto-calcolato
- [ ] Spinta puntone: padiglione, capanna, generica
- [ ] Effetto catena/tirante sul cantonale
- [ ] Effetto ritegno cordolo D.3
- [ ] Diagnostica apertura-angolo: OK, WARNING, FAIL
- [ ] Coefficiente riduzione: lineare, applicazione a V_Rd e alpha_0
- [ ] Flag maschio cantonale: automatico e override
- [ ] Integrazione in analisi_tutti_meccanismi (ordinamento alpha_0 con 3D)
- [ ] Retrocompatibilita': cinematica.py test esistenti (49) invariati

**E.6.6 — Report e tabulato**

- [ ] Sezione "Meccanismo cantonale" nel tabulato
- [ ] Sezione "Diagnostica aperture d'angolo" con warning
- [ ] Passaggi calcolo tracciabili (decision_log)

#### Dipendenze

| Dipende da | Modulo | Stato |
|-----------|--------|-------|
| Meccanismi fuori piano | `src/methods/muratura/cinematica.py` (E.3) | COMPLETATO |
| Discretizzazione | `src/methods/muratura/discretizzazione.py` (F.2) | COMPLETATO |
| Modello edificio | `src/methods/muratura/modello_edificio.py` (F.1) | COMPLETATO |
| Cordolo reticolare | `src/elements/cordolo_reticolare.py` (D.3) | TODO (non bloccante) |

#### Abilitato da E.6 (dipendenze inverse)

| Fase | Beneficio |
|------|-----------|
| D.3.5 Integrazione cinematica | Meccanismo cantonale disponibile come target per ritegno |
| D.3.6 Nodo d'angolo | H_angolo calcolabile per dimensionamento nodo |
| Fase R — Edifici esistenti | Vulnerabilita' cantonali quantificabile |
| Fase K — Grafici | Disegno cuneo 3D proiettato |

#### Riferimenti normativi e letteratura

- Circ. n.7/2019 §C8A.4.1 — cinematica lineare meccanismi locali
- Schede ReLUIS — meccanismi di collasso locali (ribaltamento cantonale)
- Casapulla & Maione (2020) — rocking analysis of corner mechanisms
- D'Ayala & Speranza (2003) — mechanisms for historic masonry
- Dolce M. — schematizzazione e modellazione pareti, altezza efficace maschi
- NTC2018 §7.8.2 — resistenza maschi murari nel piano

### E.7 Muratura multipiano ✅
**Stato**: COMPLETATO — commit corrente

#### E.7.1 Carichi verticali per aree di influenza ✅
- [x] `CaricoSolaio` — input per parete: G1, G2, Q, luce_sx, luce_dx
- [x] `CaricoMaschio` — componenti scomposti (peso proprio, solaio G1/G2/Q, superiore)
- [x] `_area_influenza_maschio()` — metà luce tra maschi adiacenti
- [x] `distribuisci_carichi_solaio()` — da CaricoSolaio a N per maschio
- [x] `calcola_N_multipiano()` — accumulo top-down realistico

**File**: `src/methods/muratura/carichi_verticali.py` (~260 righe)
**Test**: `tests/test_carichi_verticali.py` (20 test)

#### E.7.2 Combinazioni personalizzabili ✅
- [x] `CombinazioneCarico` — γ_G1, γ_G2, γ_Q, ψ, attiva/disattiva
- [x] `GestoreCombinazioni` — CRUD + attiva/disattiva + ripristino default
- [x] 6 combinazioni default NTC2018 §2.5.3 (SLU sfav/fav, SLE rara/freq/qperm, sismica)
- [x] Coefficienti ψ₀/ψ₁/ψ₂ per categorie A÷H (Tab. 2.5.I)
- [x] `calcola_N_tutte()` / `N_Ed_max()` — N combinato per tutte le attive

**File**: `src/methods/muratura/combinazioni_muratura.py` (~260 righe)
**Test**: `tests/test_combinazioni_muratura.py` (31 test)

#### E.7.3 Verifiche compressione multipiano ✅
- [x] `Eccentricita` — 4 fonti: geometrica, carico solaio, accidentale, vento/sisma
- [x] `calcola_eccentricita()` — e_a = max(h_eff/200, 2 cm)
- [x] `verifica_multipiano()` — Φ(λ, e/t) × fd × A per ogni maschio
- [x] `RigaVerificaMaschio` — dettaglio: N_Ed, σ₀, e/t, λ, Φ, N_Rd, D/C
- [x] `RigaVerificaPiano` — riepilogo: D/C_max, n_verificati
- [x] `TabellaVerificheMultipiano` — tabella sintetica + dettagliata + formato_testo ASCII

**File**: `src/methods/muratura/verifiche_multipiano.py` (~290 righe)
**Test**: `tests/test_verifiche_multipiano.py` (22 test)

---

## FASE F — Metodo POR (Telaio Equivalente)

**Stato**: COMPLETATO — commit corrente

### F.1 Modello edificio + Tabella C8.5.I ✅
**Stato**: COMPLETATO
- [x] `Edificio`, `Piano`, `Parete`, `Apertura` — modello gerarchico
- [x] `MaterialeMuratura` con fd, tau_0d, fvk0d proprietà derivate (γ_M × FC)
- [x] `ParametriSismiciEdificio` con spettro elastico/progetto NTC2018 §3.2.3.2.1
- [x] `ConfigPOR` con drift, criteri collasso, eccentricità, n_passi configurabili
- [x] Enums: `TipoApertura`, `TipoDiaframma`, `LivelloConoscenza`, `TipoMuraturaC85I`
- [x] FC_DA_LC: LC1→1.35, LC2→1.20, LC3→1.00
- [x] `data/materials/tabella_c85i.json` — 11 tipologie murarie complete

**File**: `src/methods/muratura/modello_edificio.py` (~300 righe)
**Test**: `tests/test_modello_edificio.py` (47 test)

### F.2 Discretizzazione ✅
**Stato**: COMPLETATO
- [x] `Maschio` dataclass con geometria, materiale, N, vincolo, drift
- [x] `Fascia` dataclass con ha_cordolo, e_biella
- [x] `discretizza_parete()` — genera maschi/fasce da parete + aperture
- [x] `discretizza_piano()` — processa tutte le pareti di un piano
- [x] `calcola_N_gravitazionale()` — accumulo top-down carichi verticali
- [x] `determina_vincoli_maschi()` — vincoli automatici da rigidezza fasce

**File**: `src/methods/muratura/discretizzazione.py` (~350 righe)
**Test**: `tests/test_discretizzazione.py` (26 test)

### F.3 Rigidezza + distribuzione forze ✅
**Stato**: COMPLETATO
- [x] `rigidezza_maschio()` — Timoshenko (flessione + taglio), doppio incastro / mensola
- [x] `rigidezza_fascia()` — analoga, ridotta per biella
- [x] `CentroRigidezzaPiano` — x_CR, y_CR, K_x, K_y, K_θ, eccentricità
- [x] `assembla_matrice_piano()` — matrice 3×3 condensata [K_xx, K_xy, K_xθ; ...]
- [x] `distribuisci_forza_piano()` — 3 GDL/piano (ux, uy, θz) + fallback per DOF ridotti
- [x] Solver 3×3 Gauss con pivoting parziale + solver 2×2 ridotto

**File**: `src/methods/muratura/rigidezza.py` (~350 righe)
**Test**: `tests/test_rigidezza.py` (25 test)

### F.4 Resistenza maschi/fasce ✅
**Stato**: COMPLETATO
- [x] `ResistenzaMaschio` — V_Rd, curva bilineare (k, δ_y, δ_u), `forza_per_spostamento()`, `stato_per_spostamento()`
- [x] `calcola_resistenza_maschio()` — integra 3 criteri E.2 (diagonale, scorrimento, pressoflessione)
- [x] `ResistenzaFascia` — con/senza cordolo
- [x] `calcola_resistenze_piano()` — batch
- [x] Criterio dominante determina drift limite (taglio 0.5%, pressoflessione 1.0%)

**File**: `src/methods/muratura/resistenza.py` (~280 righe)
**Test**: `tests/test_resistenza_maschio.py` (21 test)

### F.5 Analisi pushover ✅
**Stato**: COMPLETATO
- [x] `forze_in_altezza()` — NTC2018 §7.3.4.1 (modo 1 + uniforme)
- [x] `pushover_piano()` — POR singolo piano incrementale
- [x] `pushover_multipiano()` — spostamenti proporzionali, criterio collasso
- [x] `bilinearizza_curva()` — equipartizione energetica, SDOF T*
- [x] `analisi_por_completa()` — 2 dir × 2 distr × ±ecc = 8 curve, curva governante
- [x] Calcolo ζ_E = a*_y / S_d(T*)

**File**: `src/methods/muratura/por_analisi.py` (~380 righe)
**Test**: `tests/test_por_analisi.py` (18 test)

### F.6 Fattore di comportamento q ✅
**Stato**: COMPLETATO
- [x] `ALPHA_U_ALPHA_1_TAB` — tabella NTC2018 Tab. 7.3.II
- [x] `calcola_fattore_comportamento()` — q = q₀ × K_R
- [x] Limiti per edifici esistenti (α_u/α_1 ≤ 1.50, Circ. §C8.5.5.1)
- [x] Override manuale q e α_u/α_1
- [x] Irregolarità pianta (media α) e altezza (K_R = 0.8)

**File**: `src/methods/muratura/fattore_comportamento.py` (~180 righe)
**Test**: `tests/test_fattore_comportamento.py` (22 test)

### F.7 Verifiche e report ✅
**Stato**: COMPLETATO
- [x] `RigaMaschio`, `TabellaVerificheMaschi` — tabella stile 3Muri/Aedes
- [x] `formato_testo()` — output ASCII per tabulati
- [x] `genera_tabella_maschi()` — D/C per ogni maschio
- [x] `RiepilogoRischio` — confronto ζ_E globale vs locale
- [x] `plot_curva_pushover()` — matplotlib con bilineare sovrapposta

**File**: `src/methods/muratura/por_verifiche.py` (~280 righe)
**Test**: `tests/test_por_verifiche.py` (25 test)

---

## FASE G — Elementi Secondari

**Stato**: COMPLETATO

### G.1 SLU forza inerziale F_a ✅
**Stato**: COMPLETATO (formula e contratto) — PARZIALMENTE per test tipi specifici

**Riferimento normativo**: NTC2018 §7.2.3

> **Nota file**: Il modulo reale e' `src/codes/ntc2018/secondary_elements/checks.py`,
> NON `checks_ntc2018.py` (che riguarda CA NTC2018 e non contiene elementi secondari).

#### G.1 — Implementato

- [x] `src/codes/ntc2018/secondary_elements/checks.py` — `check_slu(inputs)`:
  F_a = S_a · W_a · γ_a / q_a; verifica F_a ≤ F_Rd (utilisation, esito OK/NON OK)
- [x] Contratto output obbligatorio: `trace.run_id`, `norm_references`, `decision_log`
- [x] Gestione assenza F_Rd: solo calcolo F_a senza verifica
- [x] `src/codes/ntc2018/secondary_elements/models.py` — `SecondaryElementSpec`, `DriftSpec`,
  `SecondaryElementInput` (alias), metodo `validate()`
- [x] `src/codes/ntc2018/secondary_elements/__init__.py` — esporta checks, models, storage_adapter
- [x] `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode` — check `NS_SLU_InertialForce`
- [x] Gating `influence_on_global_model=True` → NOT_APPLICABLE (in dispatcher)
- [x] Test: `tests/test_secondary_elements_gating.py` (5 test — contratto, trace, gating,
  validazione spec, config loader)

#### G.1 — Dipendenze

| Dipende da | Modulo | Stato |
| --- | --- | --- |
| Stima T_a + S_a floor | `src/codes/ntc2018/secondary_elements/ta_models.py` (G.5) | COMPLETATO |
| Dispatcher multi-norma | `verifications/secondary_elements/dispatcher.py` (G.4) | COMPLETATO |
| Config loader | `config/calculation_codes_loader.py` | COMPLETATO |

#### G.1 — TODO aperti

- [ ] `src/codes/ntc2018/secondary_elements/anchors_capacity.py` — attualmente stub
  (echo del valore ETA dichiarato, nessun calcolo); implementare verifica ETA reale
- [ ] `tests/codes/test_secondary_elements_cantilever.py` — placeholder `assert True`,
  aggiungere test numerici per mensole (F_a, ancoraggio, instabilita')
- [ ] `tests/codes/test_secondary_elements_chimney.py` — placeholder `assert True`,
  aggiungere test per ciminiere/parapetti
- [ ] `tests/codes/test_secondary_elements_partition.py` — placeholder `assert True`,
  aggiungere test per pareti divisorie (SLE drift dominante)
- [ ] `tests/codes/test_secondary_elements_signage.py` — placeholder `assert True`,
  aggiungere test per segnaletica/elementi appesi
- [x] **G.1.a** Modulo spettro NTC2018 `src/codes/ntc2018/spectrum.py` — COMPLETATO
  Implementato: CategoriaSuolo, CategoriaTopografica, ClasseUso; calcola_SS(),
  calcola_ST(), calcola_CC(), calcola_alpha_S(), spettro_elastico(),
  spettro_progetto(), calcola_S_d_T1(), spettro_da_hazard_row().
  Test: `tests/test_spettro_ntc2018.py` (47 test).
- [x] **G.1.b** Integrazione check_slu: calcolo S_a interno da parametri sito
  Se `S_a` assente e presenti ag_g, F0, TC_star, cat_suolo, cat_topografica,
  z, H, T_a, T_1 → S_a calcolata internamente via spectrum.py. Backward compat.

### G.2 SLE compatibilità spostamento ✅
**Stato**: COMPLETATO (formula e contratto) — PARZIALMENTE per test tipi specifici

**Riferimento normativo**: NTC2018 §7.2.3 (drift)

> **Nota file**: Come G.1, implementato in `src/codes/ntc2018/secondary_elements/checks.py`,
> NON in `checks_ntc2018.py`.

#### Implementato

- [x] `src/codes/ntc2018/secondary_elements/checks.py` — `check_sle(inputs)`:
  verifica drift ≤ limit (default 0.005 = h/200 per elementi fragili)
- [x] Gestione source GLOBAL / ESTIMATED / USER; confidence=LOW automatico se ESTIMATED
- [x] Contratto output obbligatorio: `trace.run_id`, `norm_references`, `decision_log`
- [x] Gestione assenza drift.value: verifica non eseguita, esito OK per default
- [x] `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode` — check `NS_SLE_DriftCompatibility`,
  policy `allow_estimated_drift: true`
- [x] Test: `tests/test_secondary_elements_gating.py` — `test_estimated_drift_warning`
  (confidence=LOW con source=ESTIMATED)

#### Dipendenze

| Dipende da | Modulo | Stato |
|-----------|--------|-------|
| Stima drift Metodo B | `src/codes/ntc2018/secondary_elements/drift_models.py` (G.5) | COMPLETATO |
| Dispatcher multi-norma | `verifications/secondary_elements/dispatcher.py` (G.4) | COMPLETATO |

#### TODO ancora da completare

- [ ] Test numerici golden per SLE: drift ok (h/200), drift non ok, limite personalizzato
  (attualmente solo gating coperto da `test_secondary_elements_gating.py`)
- [ ] Alias `check_partition` / `check_parapet` presenti nel file ma non testati
  separatamente — valutare se tenerli o rimuoverli

### G.3 Storage adapter CRUD ✅
**Completato** — commit 45e4648

### G.4 Verifiche elementi secondari per normative storiche ✅
**Stato**: COMPLETATO — commit corrente
- [x] Elementi secondari RD2229 — `src/codes/rd2229/secondary_elements/checks.py`
  - Verifica stabilità TA (omega * N / A) per elementi snelli sotto gravità
  - SLE: NOT_APPLICABLE (norma pre-sismica)
- [x] Elementi secondari DM92/DM96 — `src/codes/dm96/secondary_elements/checks.py`
  - SLU: F_h = C * beta * W (coefficiente sismico semplificato per zona e piano)
  - SLE: drift h/300
  - Modello `SecondaryElementSpecDM96` con zona_sismica, piano, beta
- [x] Dispatcher multi-norma — `verifications/secondary_elements/dispatcher.py`
  - Routing basato su norma_attiva: NTC2018 (default), DM96/DM92, RD2229

**Test**: `tests/test_secondary_elements_historical.py` (35 test) + `tests/test_secondary_elements_gating.py` (5 test) = 40 test totali

### G.5 Stima periodo T_a e drift Metodo B (NTC2018)

**Stato**: COMPLETATO — commit corrente

- [x] `ta_models.py` — stima periodo fondamentale T_a con 4 modelli (RIGID, CANTILEVER_EQ, SDOF_EQ, MANUAL)
- [x] `spectral_acceleration_floor()` — S_a al piano (NTC2018 eq. 7.2.5)
- [x] `drift_models.py` — stima drift Metodo B (shear-building proxy) + USER + GLOBAL
- [x] Validazione parametri con messaggi errore chiari
- [x] decision_log tracciabile per ogni calcolo

**File**: `src/codes/ntc2018/secondary_elements/ta_models.py`, `src/codes/ntc2018/secondary_elements/drift_models.py`
**Test**: `tests/test_ta_drift_models.py` (37 test)

---

## FASI SUCCESSIVE (PRIORITÀ DECRESCENTE)

### FASE H — Riorganizzazione methods/
- [ ] Package per norma (rd2229/, ntc2018/, dm96/, ec2/)
- [ ] Migrazione checks esistenti nei rispettivi package

### FASE I — Sezioni parametri statici completi

**Stato**: COMPLETATO — commit `3bed1a7`
**Test**: 91 test (test_sezione_omogenizzata.py), tutti passati

#### I.1 Rapporto di omogeneizzazione n per norma ✅

- [x] `src/codes/section_params/norme_n.py` — n per RD2229 (8/10/12/15), DM92, DM96, NTC2008, NTC2018, EC2
- [x] RD2229: opzioni selezionabili 8/10/12/15, default 15
- [x] NTC2018/NTC2008 §4.1.2.1.4.2: default n=15 (long-term quasi-permanente)
- [x] DM92/DM96: calcolo automatico E_s/E_c o default 10
- [x] EC2 §7.4.3: n = E_s/E_c_eff = E_s/(E_c/(1+phi))
- [x] Precedenza utente (n_user) su tutti

#### I.2 Sezione omogeneizzata integra + fessurata ✅

- [x] `src/codes/section_params/omogenizzata.py`
- [x] `BarraArmatura(y, A, zona)` — livello armatura
- [x] `calcola_sezione_omogenizzata()` — A_om, y_G_om, I_om, W_sup, W_inf
- [x] `calcola_asse_neutro_fessurato()` — analitico (rettangolare, N=0) + iterativo bisect (tutti i tipi)
- [x] `calcola_tensioni_sle()` — sigma_c, sigma_s per ogni livello armatura
- [x] `calcola_parametri_sezione_completi()` — pipeline unificata
- [x] Tutti i tipi di sezione (duck-typed tramite section_fiber.py)

#### I.3 Parametri torsionali ✅ (pre-esistenti)

- [x] J_t, C_w, x_s, y_s implementati in `apps/sections/models/sections.py`
- [x] Test: `tests/test_section_torsion.py` (27 test esistenti)

#### I.4 Sezione composta acciaio-cls ✅

- [x] `src/codes/section_params/composita.py`
- [x] `IPE_TABLE` — 18 profili IPE standard (IPE80÷IPE600)
- [x] `calcola_sezione_composta()` — A_comp, y_G_comp, I_comp, W_a, W_c
- [x] `calcola_tensioni_sle_composita()` — sigma_a_inf, sigma_a_sup, sigma_c_sup

#### I.5 Disegno sezione c.a. ✅

- [x] `src/codes/section_params/disegno_sezione.py` — matplotlib (headless OK)
- [x] `disegna_sezione()` — profilo + barre + asse neutro + zona compressa + diagramma tensioni
- [x] `crea_figura_sezione_sle()` — pipeline da output calcola_parametri_sezione_completi
- [x] `salva_figura()` — export PNG/PDF/SVG
- [x] `src/gui/widgets/sezione_canvas.py` — widget Qt (PySide6/PyQt6) con FigureCanvasQTAgg

**File**: `src/codes/section_params/` (5 file), `src/gui/widgets/sezione_canvas.py`
**Test**: `tests/test_sezione_omogenizzata.py` (91 test)

### FASE J — Pressoflessione deviata multinorma

**Stato**: COMPLETATO — commit `73482f0`
**Priorita'**: MEDIA
**Test**: 70 test in `tests/test_pressoflessione_deviata.py`, 0 falliti
**Retrocompat**: 91 test `test_sezione_omogenizzata.py` invariati

**Obiettivo**: Package `src/codes/pressoflessione/` — verifica e dominio 3D N-Mx-My
per 6 norme (RD2229, DM92, DM96, NTC2008, NTC2018, EC2).

#### J.1 — Refactoring BarraArmatura
- [x] Aggiunto `x: float = 0.0` in `src/codes/section_params/omogenizzata.py`
- [x] Retrocompat verificata (91 test invariati)

#### J.2 — Tipi e sezione omogenizzata biassiale
- [x] `src/codes/pressoflessione/base.py` — PressoflessSpec, PressoflessResult, DominioNMy
- [x] `calcola_omogenizzata_biassiale()` — A_om, I_x_om, I_y_om, I_xy_om, Wx, Wy
- [x] `crea_armatura_rettangolare()` — helper layout barre con coordinate (x, y)

#### J.3 — Verifica TA calcestruzzo
- [x] `src/codes/pressoflessione/ta_cls.py`
- [x] Sovrapposizione elastica: sigma = N/A + Mx*y/Ix + My*x/Iy
- [x] Bresler TA: (|Mx|/M_Rdx)^alpha + (|My|/M_Rdy)^alpha <= 1
- [x] alpha selezionabile (1.0 conservativo, 4/3 Giangreco)
- [x] Norme: RD2229 Art.29, DM92 §7, DM96 §3.4

#### J.4 — Verifica SLU (NTC2018/NTC2008/EC2)
- [x] `src/codes/pressoflessione/slu.py` — wrapper checks_ntc2018
- [x] Conversione unita' cm/kg -> mm/kN
- [x] Norme: NTC2018 §4.1.2.1.3.1, NTC2008, EC2 §5.8.9

#### J.5 — Dominio 3D N-Mx-My
- [x] `src/codes/pressoflessione/dominio.py`
- [x] `calcola_dominio_3d()` — generazione griglia (N, theta) -> (Mx_Rd, My_Rd)
- [x] `disegna_dominio_3d()` — surface plot mplot3d
- [x] `disegna_dominio_2d_mxmy()` — curva Mx-My a N costante
- [x] `disegna_dominio_2d_nm()` — curva N-M a theta costante

#### J.6 — Instabilita' biassiale
- [x] `src/codes/pressoflessione/instabilita_biassiale.py`
- [x] `amplifica_momenti_biassiale()` — omega_x, omega_y, Mx_amp, My_amp
- [x] Riusa `omega_ca()` da `src/methods/rd2229/instabilita.py`

#### J.7 — Dispatcher multinorma
- [x] `src/codes/pressoflessione/dispatcher.py`
- [x] `calcola_pressoflessione_deviata(spec)` — entry-point unico
- [x] Routing: TA per RD2229/DM92/DM96, SLU per NTC2018/NTC2008/EC2
- [x] Amplificazione instabilita' opzionale integrata

#### J.8 — Widget Qt
- [x] `src/gui/widgets/dominio_canvas.py` — DominioNMyCanvas
- [x] 3 viste: 3D surface, 2D Mx-My, 2D N-M
- [x] Slider interattivi per N e theta

**File**: `src/codes/pressoflessione/` (7 file), `src/gui/widgets/dominio_canvas.py`
**Test**: `tests/test_pressoflessione_deviata.py` (70 test)

### FASE K — Grafici
- [ ] Sollecitazioni, inviluppi
- [ ] Diagrammi di interazione
- [ ] Spostamenti

### FASE L — Cross-Pozzati (telai piani)
- [ ] Carichi fissi
- [ ] Predisposizione carichi mobili

### FASE M — FEM beam 2D
- [ ] scipy sparse
- [ ] Assemblaggio matrice globale

### FASE N — Carote cls in sito ✅

**Stato**: COMPLETATO — commit `8f52479`
**Test**: 70 in `tests/test_carote.py`, 0 falliti
**Retrocompat**: 2233 test suite completa, 0 falliti

**Architettura**: `src/codes/carote/` (9 moduli) + `src/gui/widgets/carote_canvas.py`

- [x] **N.1** `core_sample.py`: CoreSample, CorrectionFactors, ConversionResult (dataclass)
- [x] **N.2** `formulas.py`: 10 formulazioni (BS1881, ACI214, TR11, RILEM, Masi, Fiore, NTC2018, EN13791, Giacchetti, custom) + custom engine 3 livelli
- [x] **N.3** `statistics.py`: NTC2018, EN 13791 A/B, Grubbs, Chauvenet, classificazione cls
- [x] **N.4** `derived_params.py`: f_cm, E_cm, f_ctm, Rck, sigma_c_adm storica
- [x] **N.5** `analysis.py` + `__init__.py`: pipeline list[CoreSample] -> CoreAnalysisResult
- [x] **N.6** `integration.py`: LC/FC bridge + registra_materiale_in_situ()
- [x] **N.7** `report.py`: HTML report + JSON/CSV export
- [x] **N.8** `plots.py`: 4 grafici matplotlib headless (istogramma, scatter, boxplot, barre)
- [x] **N.9** `tests/test_carote.py` (70 test) + pytest green
- [x] **N.10** `carote_canvas.py`: widget Qt (4 viste, combo formulazione)
- [x] **N.11** Aggiornamento docs (PIANO_LAVORO, PIANO_SVILUPPO_CORRENTE, memory)

### FASE O — Griglia sismica INGV + Spettro NTC2018

**Stato**: PARZIALMENTE COMPLETATO — commit `d6e589a` (O.2 completo; O.1 CSV richiede griglia utente)
**Priorita'**: ALTA (prerequisito per G.1.a, G.5, POR, elementi secondari, FASE U)

**Obiettivo**: Due sotto-fasi strettamente collegate:
(O.1) Import pericolosita' sismica dal webservice INGV (o da tabella locale);
(O.2) Calcolo spettro di risposta NTC2018 dal sito fino a S_a e S_d pronti per le verifiche.

**Nota**: Il modulo O.2 e' un gap critico identificato (2026-03-06) nell'analisi G.1:
tutti i moduli che usano l'accelerazione sismica (check_slu, spectral_acceleration_floor,
drift Metodo B, POR, cinematica) ricevono S_a/alpha_S/S_d come parametri esterni.
Il software dipende attualmente da EdiLus-MS (spectrum_paste_service.py) per ag, F0, TC*
ma non calcola SS, ST, alpha_S, Se(T), Sd(T) in modo autonomo.

#### O.1 — Import dati pericolosita' sismica INGV

- [x] Import dati INGV da webservice (lat, lon -> ag, F0, TC* per TR) —
  `src/codes/ntc2018/ingv_hazard.py`: get_hazard_params_ingv(), webservice ESSE1
- [x] Tabella locale griglia INGV (fallback offline, CSV) —
  get_hazard_params_csv() con interpolazione bilineare; CSV da fornire dall'utente
  (placeholder `data/seismic/.gitkeep`)
- [x] Funzione unificata con routing webservice/CSV —
  get_hazard_params_site(lat, lon, TR, prefer, csv_path)
- [ ] File CSV griglia INGV NTC2018 Allegato B (~1.5MB) — da fornire dall'utente
- [x] Import parametri da EdiLus-MS (gia' in spectrum_paste_service.py — invariato)
- [x] Validazione e normalizzazione formato output uniforme (Ntc2018HazardRow)

#### O.2 — Modulo spettro NTC2018 (`src/codes/ntc2018/spectrum.py`) ✅

Prerequisito per: G.1.a (check_slu), G.5 (S_d Metodo B), F.1 (POR spettro),
E.3 (cinematica parametri sismici), FASE U (sismica dettagliata).

- [x] Enum `CategoriaSuolo` (A, B, C, D, E) con SS da Tab. 3.2.V
- [x] Enum `CategoriaTopografica` (T1, T2, T3, T4) con ST da Tab. 3.2.VI
- [x] Enum `ClasseUso` (I, II, III, IV) con Cu da Tab. 2.4.II
- [x] `calcola_VR(vita_nominale, classe_uso)` -> VR = VN * Cu (min 35a)
- [x] `calcola_CC(cat_suolo, tc_star)` -> coefficiente CC (formula power-law)
- [x] `calcola_SS(ag_g, F0, cat_suolo)` -> SS Tab. 3.2.V (1 iterazione)
- [x] `calcola_ST(cat_topografica)` -> ST Tab. 3.2.VI
- [x] `calcola_alpha_S(ag_g, SS, ST)` -> alpha_S = (ag/g) * SS * ST
- [x] `calcola_periodi(TC_star, CC, ag_g)` -> (TB, TC, TD)
- [x] `spettro_elastico(ag_g, F0, SS, ST, TB, TC, TD, xi, T)` -> Se(T) [m/s2]
- [x] `spettro_progetto(...)` -> Sd(T) = Se(T)/q [m/s2]
- [x] `calcola_S_d_T1(T_1, ...)` -> S_d [m] per drift Metodo B
- [x] `spettro_da_hazard_row(row, cat_suolo, cat_topogr.)` -> dict end-to-end
- [ ] `profilo_spettrale_completo(...)` -> dict con range T (TODO futuro)
- [x] Integrazione con spectrum_paste_service: Ntc2018HazardRow come input
- [x] Integrazione con O.1 (INGV): via ingv_hazard.py -> Ntc2018HazardRow -> spettro

#### O.2 — Integrazioni nei moduli esistenti ✅

- [x] `ta_models.py`: +`spectral_acceleration_floor_from_site()` (alpha_S da sito)
- [x] `checks.py`: +calcolo S_a interno in check_slu se ag_g/F0/TC_star/cat_suolo presenti
- [x] `cinematica.py`: +`parametri_sismici_da_sito()` factory (S=SS*ST automatico)

#### O.2 — Test ✅

- [x] `tests/test_spettro_ntc2018.py` — 47 test
  - Valori di riferimento Roma (SLV, cat B/T1): ag=0.168g, F0=2.398, TC*=0.327s
  - Copertura: VR, SS, ST, CC, periodi, alpha_S, Se, Sd, S_d, end-to-end, integrazioni

#### O.2 — Dipendenze

| Abilitato da O.2 | Modulo | Beneficio |
|-----------|--------|-------|
| G.1.a check_slu | `src/codes/ntc2018/secondary_elements/checks.py` | alpha_S calcolato internamente |
| G.5 drift Metodo B | `src/codes/ntc2018/secondary_elements/drift_models.py` | S_d(T_1) calcolato |
| F.1 POR spettro | `src/methods/muratura/modello_edificio.py` | spettro da sito invece che manuale |
| E.3 Cinematica | `src/methods/muratura/cinematica.py` | parametri sismici da sito |
| FASE U sismica | da implementare | q, duttilita', gerarchia |

#### O.2 — Note normative

- NTC2018 §3.2.3 — Azione sismica: definizione spettro di risposta elastico
- NTC2018 Tab. 3.2.V — Valori dei parametri SS per le categorie di sottosuolo
- NTC2018 Tab. 3.2.VI — Valori del coefficiente topografico ST
- NTC2018 Tab. 2.4.II — Coefficienti Cu per classe d'uso
- NTC2018 §2.4.1 — Vita di riferimento VR = VN * Cu

#### O.3 — Azioni sismiche multinorma (`src/codes/seismic/`) ✅

**Stato**: COMPLETATO — commit `d6e589a` — 54 test in `test_azioni_sismiche_multinorma.py`

Package per calcolo taglio alla base + distribuzione triangolare ai piani per 7 norme.

- [x] `base.py`: `PianoEdificio`, `distribuzione_triangolare`, `_base_contract`
- [x] `rd2229.py`: coefficienti storici 0.00/0.05/0.07/0.10 (STATICO_EQUIVALENTE)
- [x] `dm92.py`: F_h = C*I*eps*W, zone 1-3 (C=0.10/0.07/0.04) — DM 3/6/1981+1992
- [x] `dm96.py`: idem DM92 con norm_ref DM 16/1/1996
- [x] `opcm3274.py`: 4 zone ag fisso, F0=2.5, spettro via spectrum.py (SPETTRALE)
- [x] `ec8.py`: Tipo1/Tipo2, S fisso per cat suolo, F0=2.5 (SPETTRALE)
- [x] `ntc2008.py`: riusa spectrum.py, norm_ref=NTC2008 §3.2.3 (SPETTRALE)
- [x] `dispatcher.py`: routing per norma_attiva (RD2229/DM92/DM96/OPCM3274/EC8/NTC2008/NTC2018)
- [x] `tests/test_azioni_sismiche_multinorma.py` — 54 test (8 classi)

### FASE P — Fondazioni e geotecnica
- [ ] Portanza, cedimenti, pali, muri, liquefazione

### FASE Q — Report relazione di calcolo professionale
- [ ] Citazione automatica norma/articolo/paragrafo
- [ ] Confronto tra norme

### FASE R — Edifici esistenti
- [ ] LC/FC, vulnerabilità, miglioramento/adeguamento

### FASE S — Normative aggiuntive
- [ ] DM92 verifiche complete, NTC2008 verifiche, EC2/3/8, CNR-DT 200

### FASE T — Fuoco avanzato
- [ ] Isoterma 500°C, FEM termico

### FASE U — Sismica dettagliata
- [ ] q, duttilità, gerarchia, nodi

### FASE V — Solai, Scale
- [ ] Laterocemento, alveolari, rampe

### FASE W — OCR manuali tecnici
- [ ] Pipeline OCR per Santarella/Giangreco

---

## GIÀ COMPLETATO (da sessioni precedenti)

| Funzionalità | Commit | Modulo |
|---|---|---|
| Log centralizzato + listener GUI | edddc19 | `src/core/registro_log.py` |
| Sistema unità selezionabile | edddc19 | `src/core/unita_misura.py` |
| Debug viewer Qt | edddc19 | `src/ui/qt/debug_viewer.py` |
| Help contestuale YAML | edddc19 | `src/ui/qt/aiuto_contestuale.py` |
| Visualizzatore sezione Qt | edddc19 | `src/ui/qt/visualizzatore_sezione.py` |
| Tabulati calcolo ASCII/HTML | edddc19 | `src/report/tabulati_calcolo.py` |
| Material model (804+ righe) | a85e0e3 | `src/materials/material_model.py` |
| Material repo CRUD + JSON | a85e0e3 | `src/materials/material_repo.py` |
| Validazione materiali | a85e0e3 | `src/materials/validation.py` |
| Adapter kg/cm²↔MPa | a85e0e3 | `src/materials/adapter.py` |
| Material editor Qt | a85e0e3 | `src/ui/qt/material_editor.py` |
| 12 tipi sezione + torsionali | bdd8c6a | `src/sections/` |
| Pressoflessione SLU fiber | 2ae516d | `checks_ntc2018.py`, `section_fiber.py` |
| Flessione SLU | 2ae516d | `checks_ntc2018.py` |
| Taglio SLU (V_Rd,s) | 2ae516d | `checks_ntc2018.py` |
| Minimi armatura | 2ae516d | `checks_ntc2018.py` |
| Torsione SLU (thin-walled truss) | 6a76847 | `checks_ntc2018.py` |
| Tensioni SLE | 6a76847 | `checks_ntc2018.py` |
| Fessurazione SLE (w_k) | 6a76847 | `checks_ntc2018.py` |
| Deformazioni SLE | d625efd | `checks_ntc2018.py` |
| Verifiche DM96 complete | 45e4648 | `checks_dm96.py` |
| V_Rd,c senza armatura | 45e4648 | `checks_ntc2018.py` |
| Combinazioni NTC2018 | 45e4648 | `src/combinations/` |
| Elementi secondari SLU/SLE | 45e4648 | `checks_ntc2018.py` |
| Fuoco tabellare | b452ede | `src/fire/rc_fire_check.py` |
| Vento completo (160+ test) | 0a3d436→d8c88b5 | `src/wind/` |
| Registries e routing | c153792 | `section_registry`, `code_registry` |
| Pipeline verifiche + report | cbb07c5 | 6 verification actions, CLI |
| Cataloghi multi-norma (97 mat.) | a0f05aa + corrente | `data/materials/catalogo_*.json` |
| Torsione RD2229 TA | 394dc31 | `src/methods/rd2229/torsione.py` |
| Instabilità RD2229 TA (ω) | 394dc31 | `src/methods/rd2229/instabilita.py` |
| Sagomario acciaio EN 10365 (87 profili) | corrente | `src/steel/sagomario.py`, `data/steel/` |
| Verifiche acciaio TA (flessione, taglio, instabilità) | corrente | `src/steel/verifiche_ta.py` |
| Solutore traliccio 2D (rigidezza diretta) | corrente | `src/steel/traliccio_2d.py` |
| Connessioni acciaio (saldature + bulloni) | corrente | `src/steel/connessioni.py` |
| Verifiche muratura (compressione, taglio, spanciamento) | corrente | `src/methods/muratura/verifiche.py` |
| Modello cordolo CA + metallico | corrente | `src/elements/cordolo.py` |
| Catene e paletti (trazione + punzonamento) | corrente | `src/elements/cordolo.py` |
| Meccanismi locali fuori piano (4 mecc. + cin. lin./non lin.) | corrente | `src/methods/muratura/cinematica.py` |
| POR modello edificio + Tab. C8.5.I | corrente | `src/methods/muratura/modello_edificio.py` |
| POR discretizzazione maschi/fasce | corrente | `src/methods/muratura/discretizzazione.py` |
| POR rigidezza + distribuzione forze 3 GDL | corrente | `src/methods/muratura/rigidezza.py` |
| POR resistenza maschi/fasce (bilineare) | corrente | `src/methods/muratura/resistenza.py` |
| POR pushover multipiano + bilinearizzazione | corrente | `src/methods/muratura/por_analisi.py` |
| POR fattore comportamento q (NTC2018 Tab.7.3.II) | corrente | `src/methods/muratura/fattore_comportamento.py` |
| POR verifiche tabella maschi + riepilogo rischio | corrente | `src/methods/muratura/por_verifiche.py` |
| Carichi verticali multipiano (aree influenza, top-down) | corrente | `src/methods/muratura/carichi_verticali.py` |
| Combinazioni di carico personalizzabili NTC2018 | corrente | `src/methods/muratura/combinazioni_muratura.py` |
| Verifiche compressione multipiano (4 eccentricità, Φ) | corrente | `src/methods/muratura/verifiche_multipiano.py` |
| Elementi secondari DM96/DM92 (F_h = C*beta*W, drift h/300) | corrente | `src/codes/dm96/secondary_elements/checks.py` |
| Elementi secondari RD2229 (stabilità TA, omega) | corrente | `src/codes/rd2229/secondary_elements/checks.py` |
| Dispatcher multi-norma elementi secondari | corrente | `verifications/secondary_elements/dispatcher.py` |
| Stima periodo T_a (4 modelli) + S_a floor NTC2018 | corrente | `src/codes/ntc2018/secondary_elements/ta_models.py` |
| Stima drift Metodo B + USER + GLOBAL | corrente | `src/codes/ntc2018/secondary_elements/drift_models.py` |
| Spettro NTC2018 §3.2.3 (SS, ST, CC, Se, Sd) + INGV webservice/CSV | d6e589a | `src/codes/ntc2018/spectrum.py`, `ingv_hazard.py` |
| Azioni sismiche multinorma (7 norme, forza base + distrib. piani) | d6e589a | `src/codes/seismic/` (8 moduli + dispatcher) |
| Pressoflessione deviata multinorma (6 norme, dominio 3D, TA+SLU) | 73482f0 | `src/codes/pressoflessione/` (7 moduli) |
| Carote cls in situ (10 formul., statistiche, LC/FC, report, 70 test) | 8f52479 | `src/codes/carote/` (9 moduli) |

---

## Memoria Persistente AI

File di contesto dettagliato per continuita' tra sessioni, in `docs/memory/`:

| File | Contenuto |
|------|-----------|
| `MEMORY.md` | Indice e convenzioni utente |
| `subplan_D3_traliccio.md` | D.3: Q&A completo, decisioni, architettura, interfacce, file da creare/modificare |
| `subplan_E6_cantonali.md` | E.6: Q&A, formule ribaltamento cantonale, riduzione resistenza, letteratura |
| `subplan_A2_material_source.md` | A.2: analisi 3 entita' parallele, strutture dati, piano migrazione legacy |
| `codebase_map.md` | Mappa moduli muratura/acciaio con file, righe chiave, TODO per fase |

---

## Principi Architetturali (VINCOLI DURI)

1. Modularità estrema — ogni modulo sostituibile senza refactoring globale
2. Zero duplicazione — archivi centralizzati, unica fonte per ogni parametro
3. SOLO Qt (PySide6/PyQt6) — legacy Tkinter deprecato
4. Dropdown + input manuale — sempre entrambi per campi con archivio
5. Log pervasivo — registro_log collegato a tutto
6. Help contestuale — stralci normativi, §, formule
7. Formule nei tabulati — passaggi, risultati, riferimenti normativi
8. Visualizzazione sezioni — zone tese/compresse in scala
9. NTC2018 + Circolare n.7/2019 — sempre insieme
10. No allucinazioni — formula mancante → TODO + chiedi all'utente
11. Rigore scientifico — formule da normativa/letteratura/VB
12. UI in italiano — tutto il testo visibile in italiano
13. Memoria AI nel repository — file di contesto in `docs/memory/`, mai in directory esterne al repo
14. Aggiornamento memoria dopo ogni modulo — salvare contesto implementativo in `docs/memory/` dopo ogni fase completata
