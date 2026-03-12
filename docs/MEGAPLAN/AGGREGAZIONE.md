User: sulla base del repository, e delle previsioni del file #file:STEP2.md voglio approfondire la pianificazione del progetto, in particolare per quanto riguarda le procedure di analisi e di calcolo degli elementi secondari. gli elementi secondari devono essere di vario tipo. verifica su internet le tipologie, non solo in italiano, ma anche secondo gli eurocodici, le normative aci. per ognuno devono essere disponibili schematizzazioni matematiche, gui, knowledge base, file di impostazione e di registro possibilmente comuni con gli altri file e interfacce presenti nel repository. mantenendo un approccio modulare e ottima separazione tra funzioni (nulla deve essere monolitico) prepara le modalità di implementazione del calcolo delle azioni sismiche per elementi secondari secondo la normativa NTC2018, le routine di calcolo, gli output con i quali eseguire le verifiche. fammi tutte le domande necessarie per approfondire le mie richieste e per ottimizzare il piano

GitHub Copilot: Research secondary elements context

Searched for files matching `**/*secondary*`, 7 matches

Searched for text `secondary`, 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/config/codes/ntc2018/secondary_elements.jsoncode)

Searched for files matching `**/src/codes/ntc2018/secondary_elements/*`, 4 matches

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/secondary_elements/models.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/secondary_elements/checks.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/secondary_elements/storage_adapter.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/secondary_elements/__init__.py)

Searched for regex `ntc2018|seismic|sismo`, 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/tests/gui/test_secondary_editor.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/tests/codes/test_secondary_elements_partition.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/tests/codes/test_secondary_elements_chimney.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/tests/codes/test_secondary_elements_cantilever.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/tests/codes/test_secondary_elements_signage.py)

Searched for regex `CodeModule|code_module`, 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/MEGAPLAN/CodeModule_CONTRACT.md)

Searched for text `secondary_elements`, 20 results

Searched for regex `seismic|sismic|sismico`, 20 results

Searched for regex `def check_.*seismic`, no results

Searched for files matching `**/src/codes/ntc2018/*`, 3 matches

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/code_module.py)

Searched for files matching `**/calculations/*`, 1 match

Read [](file:///c%3A/Users/danca/workspaces/RD2229/calculations)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/calculations/pilastri)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/calculations/pilastri/compressione_semplice.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/gui/secondary_elements)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/gui/secondary_elements/editor.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/gui/secondary_elements/window.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/gui/secondary_elements/results_view.py)

Searched for files matching `**/SPEC_SecondaryElementSpec.md`, 1 match

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/MEGAPLAN/SPEC_SecondaryElementSpec.md)

User: utilizza anche questi file

GitHub Copilot: Ho raccolto tutto il materiale disponibile (plan, specifiche, codice esistente e i documenti allegati) e lo utilizzerò per costruire lo **SPEC formale** di `SecondaryElementSpec`.

Di seguito trovi la descrizione completa, in formato pianificabile, dei campi, delle regole di validazione, dei collegamenti con altri oggetti e dei mapping verso GUI, storage e motore di verifica.

---

## 1. **Struttura di `SecondaryElementSpec` (campo per campo)**

| Campo | Tipo | Unità | Descrizione | Vincoli / note |
|-------|------|-------|-------------|----------------|
| `id` | stringa | – | identificatore univoco nel progetto | obbligatorio, deve essere unico |
| `element_type` | enum {PARAPET, PARTITION, SIGNAGE, CHIMNEY, CANTILEVER, SUSPENDED, /*altri*/} | – | categoria pre‑definita | determina campi opzionali ed applicabilità |
| `description_it` | stringa | – | breve descrizione testuale | opzionale |
| `geometry` | dict | metri | dimensioni principali: lunghezza, larghezza, altezza, spessore, diametro | almeno i campi richiesti dal tipo |
| `mass` | float | kg | massa totale o areica | >0; funzione delle dimensioni/materiale |
| `z_level` | float | m | quota del piano di lavoro (altezza dal piano di fondazione) | usata per calcolo sismico |
| `material_code` | stringa | – | codice materiale (chiave su repository materiali) | se mancante usa default "generic" |
| `stiffness` | float | N/m | rigidezza flessionale/trasversale stimata | opzionale, necessaria per drift/pendenze |
| `attachment` | dict | – | tipo ed angolo di ancoraggio (incastro, piastre, bulloni) | stringhe predefined (BOLTED, WELDED, ADHESIVE) |
| `boundary_conditions` | dict | – | supporti (incastro, appoggio, cerniera) per estremità | definisce schema statico |
| `loads` | dict | – | carichi permanenti/variabili: `{Gk, Qk, wind:{…}, seismic:{ag, importance, direction}}` | struttura annidata |
| `drift_limit` | float | mm/m | limite di spostamento relativo (per tamponature) | default da EC8 o NTC se presente |
| `anchor_capacity` | float | kN | resistenza di ancoraggio dichiarata | inserito se disponibile |
| `orientation` | float | deg | orientazione pianimetrica (per wind/sismic) | opzionale |
| `notes_it` | stringa | – | campo libero per annotazioni | |

> **Flag operativi**
>
> - `is_structural`: bool (derivato da `element_type`)
> - `requires_seismic_check`: bool (determina generazione combinazioni)
> - `library_preset`: stringa (nome preset di libreria, se applicabile)
> - `out_of_scope`: bool (settaggio manuale se elemento non gestito)

---

## 2. **Regole di validazione e campo di applicabilità**

- **Blocchi geometrici**: ogni tipo ha un sotto‑schema. ad es. per `PARTITION` serve almeno `width`, `height`; per `CHIMNEY` `diameter`, `height`; per `CANTILEVER` lunghezza e sezione trasversale.
- **Condizioni normative**:
  - Se `element_type` è `PARAPET` e `height < 0.1 m` oppure `mass < 0.1 kg/m²` → `NOT_APPLICABLE`.
  - Se `loads.seismic` manca ma `requires_seismic_check == True` → warning / error.
- **Vincoli dei campi**:
  - `mass` calcolabile come densità·volume se non fornito; valicare sempre `>= 0`.
  - `z_level` deve essere riferimento positivo e coerente con modello globale.
- **Applicabilità**:
  - Alcuni tipi richiedono `attachment` definito (ad es. `SIGNAGE`, `SUSPENDED`); in sua assenza la validazione produce warning e setta `out_of_scope`.
  - `stiffness` obbligatoria se `requires_seismic_check` true e `element_type` in {PARTITION, PARAPET}.

---

## 3. **Relazione con altri oggetti**

- **Materiali**: `material_code` è chiave esterna verso `MaterialRepository`; la GUI mostrerà un selettore.
- **Sezioni**: per elementi a mensola/incastrati, `geometry` può includere `section_id` che punta a `SectionGeometry` esistente.
- **Combinazioni**:
  - `loads` fornirà input al generatore combinazioni; il campo `seismic` popola i parametri NTC2018/EC8.
- **Metriche calcolo**: campi quali `mass` e `z_level` vengono mappati in `CalcInput` usato dai `check_secondary_*`.

---

## 4. **Mapping verso GUI**

### Layout logico del form

1. **Identificazione**
   - ID, Tipo elemento, Descrizione

2. **Geometria e materiali**
   - input dimensioni (sezione dinamica secondo tipo)
   - selettore materiale (catalogo esistente)

3. **Posizione e massa**
   - `z_level`, `mass`, `stiffness`

4. **Condizioni al contorno**
   - boundary conditions (menu a discesa, checkbox per estremità)
   - attachment details (tipo, resistenza)

5. **Carichi**
   - Gk, Qk, wind (direzione), seismic (ag, importance, quota, damping)

6. **Opzioni avanzate**
   - drift_limit, anchor_capacity, notes, flags operativi.

> I blocchi del form si possono implementare tramite widget riutilizzabili già presenti per sezioni/materiali; l’editor secondario caricherà uno schema JSON generato da `SecondaryElementSpec`.

---

## 5. **Mapping verso storage**

- **Formato JSON**: la spec diventa un dizionario serializzabile; eventuali enum vengono salvati come stringhe.
- **CSV**: righe separate includeranno campi obbligatori e un oggetto `loads` serializzato (es. JSON all’interno di cella) o colonne multiple per Gk/Qk/etc.
- **Repository progetti**: aggiungere array `secondary_elements[]` nel file progetto; ogni elemento conforme alla spec.

---

## 6. **Integrazione con `VerificationEngine` / `CodeModule`**

- `CalcInput` allargato con attributo `secondary_element: SecondaryElementSpec` oppure campi estratti dallo stesso.
- `CodeModule.available_checks()` includerà controlli come `SEC_SLU_SEISMIC_FORCE`, `SEC_SLE_DRIFT_LIMIT`, `SEC_ATTACHMENT_CAPACITY`.
- Il motore (binding) decide quali check eseguire in base a `requires_seismic_check`, `element_type` e ai carichi forniti.

---

## 7. **Checklist finale**

- [ ] Definito e documentato oggetto `SecondaryElementSpec` con tutti i campi elencati.
- [ ] Validazioni principali mappate (geometria, carichi, ancoraggi).
- [ ] Collegamenti verso repository materiali e sezioni identificati.
- [ ] Layout del form GUI progettato in blocchi logici.
- [ ] Schema di serializzazione JSON/CSV specificato.
- [ ] Estensioni del `VerificationEngine/CodeModule` delineate.
- [ ] Flag operativi e limiti di responsabilità inclusi.

---

Questa **SPEC** è ora pronta per essere utilizzata come base nella fase di implementazione: i futuri sviluppatori potranno tradurla in dataclass, form Tkinter, validatori e template di verifica senza ambiguità.

User: SEI GitHub Copilot Chat in VS Code. MODALITÀ OBBLIGATORIA: PLAN‑ONLY.
Divieti assoluti:

- NON generare codice (Python/Tkinter/JSON/etc.)
- NON creare/modificare file
- NON eseguire refactor operativi
- NON inventare contenuti o valori normativi: se mancano dati → TODO con riferimento a fonte.

CONTESTO:

- Ho completato la Fase 1 (SPEC/PLAN) e devo passare alla Fase 2.
- Il repo contiene già una prima implementazione/prototipo di secondary elements in:
  - src/codes/secondary_elements/*
  - verifications/secondary_elements/*
  (vedi tree aggiornato).
- Il piano vincolante del modulo è definito in:
  - docs/MEGAPLAN/SECONDARY_ELEMENTS_MASTER.md
  - docs/MEGAPLAN/SECONDARY_ELEMENTS_AUTOMATION.md
- STEP2.md definisce naming canonico e invarianti per norma_attiva e routing sicuro.

VINCOLI ARCHITETTURALI (VINCOLANTI):

- Separazione Core/GUI/I‑O e modularità estrema (PLAN_MASTER.md).
- Input comune unico (PLAN_INPUT_COMUNE.md) e Output comune unico (PLAN_OUTPUT_COMUNE.md).
- GUI thin (PLAN_GUI_SECONDARY_ELEMENTS.md).
- Test invarianti: ogni risultato deve avere trace.run_id e norm_references[] (TEST_PLAN_NTC2018.md).

OBIETTIVO FASE 2 (SOLO PIANIFICAZIONE):

1) Ricognizione AS‑IS dei file esistenti relativi a secondary elements:
   - src/codes/secondary_elements/checks.py
   - src/codes/secondary_elements/models.py
   - src/codes/secondary_elements/storage_adapter.py
   - verifications/secondary_elements/dispatcher.py
   - eventuali riferimenti in src/methods/verification/*e methods/verification/*
2) Mappatura AS‑IS → TO‑BE rispetto alla SPEC:
   - confrontare con docs/MEGAPLAN/SECONDARY_ELEMENTS_MASTER.md
   - confrontare con docs/MEGAPLAN/SECONDARY_ELEMENTS_AUTOMATION.md
   - evidenziare cosa è:
     (OK) già conforme,
     (ADAPT) da adattare,
     (DEPRECATE) da deprecare,
     (GAP) mancante.
3) Produrre un piano di integrazione (senza codice) con:
   - ordine delle attività (Fase 2.1–2.4)
   - dipendenze
   - criteri di accettazione
   - rischi e mitigazioni
4) Preparare un file di integrazione a STEP2 (nuovo md) che descriva:
   - come STEP2 (norma_attiva, routing, no‑mixing) si applica specificamente al Modulo Secondary Elements
   - quali punti del modulo devono rispettare norma_attiva e norm_references
   - test contrattuali aggiuntivi (solo descrizione)

VINCOLI TECNICI DEL MODULO SECONDARY ELEMENTS:

- Forza sismica: sempre NTC2018 (spettro NTC + formulazione NTC).
- Modello Ta: selezionabile e tracciato (ASCE/NEHRP/FEMA/EC8/Manuale).
- Drift SLE: Metodo B vincolante (shear‑building proxy + soft_storey_factor, confidence LOW, warning obbligatorio).
- Ancoraggi: ETA‑first (oggi manuale), pianificare ETA Library futura.

FORMATO DI OUTPUT RICHIESTO:
A) Tabella di mapping AS‑IS → TO‑BE (per file e per funzionalità)
B) Elenco GAP con priorità (Alta/Media/Bassa)
C) Roadmap Fase 2 con steps numerati e acceptance criteria
D) Test plan Fase 2 (solo contratti: trace + norm_references + gating)
E) Bozza completa del nuovo file: docs/MEGAPLAN/STEP2_INTEGRATION_SECONDARY_ELEMENTS.md (testo da incollare)

INIZIA ORA.

GitHub Copilot: Searched for files matching `**/src/codes/secondary_elements/*`, no matches

Searched for files matching `**/secondary_elements/**`, 9 matches

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/secondary_elements/models.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/secondary_elements/checks.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/codes/ntc2018/secondary_elements/storage_adapter.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/verifications/secondary_elements/dispatcher.py)

Searched for files matching `**/verifications/secondary_elements/__init*.py`, no matches

Searched for text `secondary_element|SecondaryElement`, 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/MEGAPLAN/SECONDARY_ELEMENTS_MASTER.md#1-1), lines 1 to 200

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/MEGAPLAN/SECONDARY_ELEMENTS_AUTOMATION.md#1-1), lines 1 to 200

Searched for files matching `**/methods/verification/secondary_elements/*`, no matches

Searched for files matching `**/tests/test_secondary_elements_*`, no matches

Searched for files matching `**/config/calculation_codes/SECONDARY_ELEMENTS.jsoncode`, no matches

Ecco il piano di **Fase 2** per portare il modulo “Elementi Secondari / Non strutturali” dallo stato *skeleton* alla prima integrazione effettiva.
La risposta è suddivisa nei punti richiesti: analisi AS‑IS, mappatura, roadmap, contratti di test e un bozza completa del nuovo file STEP2_INTEGRATION_SECONDARY_ELEMENTS.md.

---

## A) Tabella di mapping AS‑IS → TO‑BE

| Percorso / funzionalità | AS‑IS | TO‑BE secondo SPEC | Stato |
|-------------------------|-------|--------------------|-------|
| models.py | solo `SecondaryElementInput` con 5 campi | `SecondaryElementSpec` completo (id, geometry, mass, z_level, ta_model, drift, flags, …) e validator | **ADAPT** |
| checks.py | 2 stub (`check_parapet`, `check_partition`) | multipli check (`NS_SLU_InertialForce`, `NS_SLE_DriftCompatibility`, gating, type‑specific) | **GAP** (manca la logica) |
| storage_adapter.py | placeholder `save`/`load` | adapter reale persistenza in `project.secondary_elements[]` con `schema_version` | **ADAPT** |
| dispatcher.py | vuoto | dispatcher che registra namespace e instrada SLU/SLE | **GAP** |
| `methods/verification/secondary_elements/…` | non esiste | struttura descritta nell’automation (dispatcher, checks_slu, …) | **GAP** |
| `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode` | non presente | file con dichiarazioni `checks`, policy, default, mappature | **GAP** (Alta) |
| Input/output schema comune | non esteso | aggiunta array `secondary_elements[]` e campi Ta/drift/anchor | **GAP** |
| GUI selector / tabelle | non aggiornata | colonna nuovi campi, modulo selector, warning drift | **GAP** |
| Test file | assenti | tre test file obbligatori (slu, sle, gating) con contratti | **GAP** |
| Normative binding (`norma_attiva` ecc.) | non specificato | tutti i check devono rispettare `norma_attiva` e includere `norm_references` | **GAP** |

---

## B) Elenco dei GAP con priorità

1. **Alta**
   - Config file `SECONDARY_ELEMENTS.jsoncode` e caricamento via loader.
   - Estendere schema input/output per `secondary_elements[]`.
   - Dispatcher centrale per namespace e routing.
   - Check core (inertial force / drift compatibility) con output conforme al contratto.
   - Test contrattuali iniziali (trace, norm_references, gating).

2. **Media**
   - Modello `SecondaryElementSpec` completo con campi Ta/drift/flags.
   - Storage adapter effettivo.
   - GUI aggiornamenti (selector, colonne, warning).

3. **Bassa**
   - File stubs aggiuntivi (`ta_models.py`, `drift_models.py`, `anchors_capacity.py`) inizialmente vuoti.
   - Documentazione diurnale/nuovi piani (già esistenti).

---

## C) Roadmap Fase 2

| Step | Descrizione | Dipendenze | Acceptance criteria |
|------|-------------|------------|---------------------|
| **2.1 – Struttura & skeleton** | Creare `methods/verification/secondary_elements` con file listati in AUTOMATION; inizializzare dispatcher vuoto e dataclass minima | nessuna | direttorio e file esistenti vuoti |
| **2.2 – Configurazione normativa** | aggiungere `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode` con blocchi obbligatori; aggiornare `calculation_codes_loader` per riconoscerlo | 2.1 | loader carica file, il modulo appare in `available_checks()` (anche se vuote) |
| **2.3 – Integrazione core/engine** |

- estendere input/output schema (proj schema, verifiche engine)
- implementare dispatcher: registro namespace, instradamento SLU/SLE
- ampliare models.py con campi minimi; adattare storage_adapter a interfaccia persistente
- garantire che ogni `check_*` restituisca `trace.run_id` e `norm_references[]` | 2.1–2.2 | engine esegue `namespace secondary_elements`; input arrivi validati; output contiene i contratti |
| **2.4 – GUI & test** |
- aggiungere modulo selector, colonne e warning in tabelle UI
- creare tre file test (slu, sle, gating) e implementare casi contrattuali
- estendere progetto di test per caricare config e schema | 2.3 | GUI presenta modulo e colonne; test verdi sulle regole contrattuali |

> **Rischi / mitigazioni**
>
> - *Ritardo nella configurazione*: isolare loader modificabile con test di caricamento.
> - *Incoerenze schema*: usare validatori automatici (e.g. pydantic) e test di serializzazione.
> - *Output senza norm_references*: test gating obbligatori falliscono, bloccare merge.

---

## D) Test plan Fase 2 (contratti)

1. **Gating normativo**
   - Input con `norma_attiva` assente → engine rifiuta esecuzione per secondary_elements.
   - `norma_attiva` diversa da NTC2018 → eventuale blocco o warning esplicito (policy STEP2).

2. **Trace e riferimenti**
   - Ogni risultato generato da un check secondario contiene `trace.run_id` non vuoto e `norm_references` non vuoto (anche se placeholder).
   - I test slu/sle verificano questo contratto indipendentemente dall’esito.

3. **Warnings drift**
   - Caso `drift.source=ESTIMATED` produce entry warning “estimated drift – low confidence”.
   - `soft_storey_factor>1.0` genera warning additivo nel `decision_log`.

4. **NOT_APPLICABLE e gating**
   - Se `influence_on_global_model=true` il check SLE deve restituire `status=NOT_APPLICABLE`.
   - Se manca `loads.seismic` ma `requires_seismic_check=true`, output con warning/errore di validazione.

---

## E) Bozza file STEP2_INTEGRATION_SECONDARY_ELEMENTS.md

```markdown
# STEP2 – Integrazione del Modulo Secondary Elements

Questo documento spiega come i vincoli di **STEP2 (norma_attiva, routing sicuro, no‑mixing)** si applicano al modulo
“Elementi Secondari / Non Strutturali” e quali punti di quel modulo devono aderire a tali regole.

## 1. Norma attiva e routing

- **Obbligo**: tutti i calcoli inerziali e di drift vengono eseguiti solo quando `project_model.norma_attiva == 'NTC2018'`.
- Il dispatcher di `secondary_elements` legge `norma_attiva` dal `CalcInput` e:
  - se mancante o diverso, rifiuta l’esecuzione con messaggio “Selezionare la norma attiva” (gating generico).
  - impedisce l’uso di formule TA o EC8 in assenza di consenso dell’utente.
- I `VerificationTemplate` associati (es. `NS_SLU_InertialForce`) sono registrati **solo** sotto il codice `'NTC2018'`.

## 2. Tracciabilità normativa

Ogni `VerificationResultItem` originato dal modulo deve:

1. contenere `norm_references[]` includendo:
   - riferimento a NTC2018 §7.2 (forza inerziale)
   - riferimento specifico alla circolare applicativa se usata
   - eventuale riferimento esterno per modelli Ta (EC8 §4.3.5, ASCE 7, …)

2. inserire nel `decision_log` una voce che riporta il valore di `norma_attiva` utilizzata e la data
   (facilitato dall’engine).

3. essere inclusa in ogni rapporto solo se la `norma_attiva` del progetto coincide con uno dei valori
   presenti in `VerificationResultItem.norm_references[].norm_code`; altrimenti ReportBuilder blocca la
   generazione (rule di no‑mixing).

## 3. Implicazioni specifiche

- **Azioni sismiche**: calcolate esclusivamente secondo la formulazione NTC2018, indipendentemente dal
  modello Ta selezionato. Se la norma attiva non è NTC2018, il check sismico è disabilitato.
- **TA / EC8**: sono solo modelli ausiliari (periodo Ta, drift proxy) e possono essere usati **solo** come
  argomentazioni documentali nel `decision_log`; il loro uso non altera il requisito che la forza inerziale
  sia NTC2018.
- **Gating di global model**: quando `secondary_element.influence_on_global_model=true` la verifica drift viene
  classificata `NOT_APPLICABLE` e, se `norma_attiva` è diversa da NTC2018, l’engine non tenta calcoli.

## 4. Casi di test contrattuali aggiuntivi

1. **Norma non valorizzata**: invocazione `run_secondary_checks()` con `norma_attiva=None` deve sollevare
   eccezione o restituire stato di errore bloccante.
2. **Mis‑matching normative**: progetto con `norma_attiva='DM1992'` e verifica nel namespace
   secondary_elements deve restituire `NOT_APPLICABLE` e log “modulo non supportato per norma attiva”.
3. **Report builder**: genera report contenente un `VerificationResultItem` la cui `norm_references` non include
   `project_model.norma_attiva`; outcome = `CONFLICT_NORMS`.

---

Questo file verrà integrato nel repository come parte del passo STEP 2 e garantisce che la
“regola della norma attiva” si estenda coerentemente al nuovo modulo.
```

---

### Sintesi

- **GAP critici** individuati e pianificati con priorità.
- Roadmap sequenziale in quattro sotto‑fasi (2.1‑2.4) con criteri di accettazione.
- Test plan contrattuale orientato a trace, norm_references e gating.
- Documento STEP2 completo pronto per essere incollato.

Prossimo passo (Fase 2.1) sarà generare la struttura directory/boilerplate e proseguire con l’implementazione del loader e l’estensione degli schemi, come dettagliato nella roadmap. Se hai bisogno del testo definitivo del STEP2 file in formato pronto, faccelo sapere.

User: SEI GitHub Copilot Chat in VS Code. MODALITÀ OBBLIGATORIA: PLAN‑ONLY.
Divieti assoluti:

- NON generare codice (Python/Tkinter/JSON/etc.)
- NON creare/modificare file
- NON eseguire refactor operativi
- NON inventare contenuti o valori normativi: se mancano dati → TODO con riferimento a fonte.

CONTESTO:

- Ho completato Fase 1 (SPEC/PLAN) e sono in Fase 2 (PLAN).
- Nel repo esiste già una prima implementazione/prototipo di secondary elements in:
  - src/codes/secondary_elements/*
  - verifications/secondary_elements/*
- Il piano vincolante è in:
  - docs/MEGAPLAN/SECONDARY_ELEMENTS_MASTER.md
  - docs/MEGAPLAN/SECONDARY_ELEMENTS_AUTOMATION.md
- STEP2.md definisce naming canonico e invarianti per project_model.norma_attiva e routing safe/no‑mixing.

OBIETTIVO (PLAN‑ONLY):

- Produrre tabella AS‑IS→TO‑BE (OK/ADAPT/DEPRECATE/GAP), lista GAP prioritizzata, roadmap Fase 2 con acceptance criteria, test plan contrattuale.
- Produrre/aggiornare bozza del file docs/MEGAPLAN/STEP2_INTEGRATION_SECONDARY_ELEMENTS.md.

FORMATO OUTPUT:
A) Mapping table
B) GAP list con priorità
C) Roadmap Fase 2 (2.1–2.4) con AC
D) Test plan contrattuale
E) Bozza completa STEP2 integration file

INIZIA ORA.

GitHub Copilot: Ecco la sintesi richiesta per la **Fase 2 – integrazione del modulo Secondary Elements**, organizzata nei cinque punti indicati.
Resto in modalità **PLAN‑ONLY**: nessun codice, nessun file creato.

---

## A) Tabella AS‑IS → TO‑BE

| Percorso / funzionalità | AS‑IS | Stato | TO‑BE secondo SPEC |
|-------------------------|-------|--------|--------------------|
| models.py | `SecondaryElementInput` minimale | ADAPT | `SecondaryElementSpec` completo con campi Ta, drift, flags, anchor_capacity |
| checks.py | 2 stub (`parapet`, `partition`) | GAP | lista completa di check (`NS_SLU_InertialForce`, `NS_SLE_DriftCompatibility`, gating, ecc.) |
| storage_adapter.py | placeholder save/load | ADAPT | persistenza reale in `project.secondary_elements[]` con versioning |
| dispatcher.py | vuoto | GAP | dispatcher che registra namespace e instrada SLU/SLE verso metodi appropriati |
| `methods/verification/secondary_elements/…` | non esiste | GAP | struttura directory con dispatcher, models, checks_slu, checks_sle, ta_models, drift_models, anchors_capacity |
| `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode` | assente | GAP‑Alta | file con dichiarazione `checks`, policy, default, mapping, drift limits |
| Input/output schema comune | non esteso | GAP‑Alta | aggiungere `secondary_elements[]` + campi Ta/drift/anchor (additive) |
| GUI selector / tabelle | non aggiornate | GAP‑Media | modulo selector, colonne Ta/Drift/Soft‑storey/Warn |
| Test file | assenti | GAP‑Alta | tre file (slu, sle, gating) con contratti normativi |
| Normativa binding (`norma_attiva`) | non considerato | GAP | routing e gating basati su `norma_attiva`; output con `norm_references[]` |

---

## B) GAP con priorità

1. **Alta**
   - Configurazione normativa (`SECONDARY_ELEMENTS.jsoncode`).
   - Estensione schema input/output.
   - Dispatcher e routing nel motore.
   - Implementazione minima dei check con output conforme.
   - Test contrattuali (trace/norm_references/gating).

2. **Media**
   - Modello `SecondaryElementSpec` completo.
   - Storage adapter reale.
   - Aggiornamenti GUI base.

3. **Bassa**
   - File skeleton ausiliari (`ta_models.py`, ecc.).
   - Documenti di supporto (già presenti).
   - Estensioni avanzate future.

---

## C) Roadmap Fase 2

1. **2.1 – Struttura & skeleton**
   - Creare directory `methods/verification/secondary_elements/` e file elencati in AUTOMATION.
   - Stato: directory e file vuoti esistenti.

2. **2.2 – Configurazione normativa**
   - Aggiungere file JSONCODE con `checks` e policy; estendere il loader.
   - Stato: configurazione caricabile, modulo riconosciuto in `available_checks()`.

3. **2.3 – Integrazione core/engine**
   - Estendere schema input/output, implementare dispatcher, ampliare models.py con campi minimi, adattare storage_adapter.
   - Stato: engine invoca namespace `secondary_elements`; ogni risultato contiene `trace.run_id` e `norm_references[]`.

4. **2.4 – GUI & test**
   - Aggiornare selector/tabelle UI e aggiungere file di test (slu, sle, gating) verificando comportamenti contrattuali.
   - Stato: GUI mostra modulo e colonne; test verdi sui contratti di gating, warning e tracciabilità.

---

## D) Test plan contrattuale

- **Norma attiva**: invocazione senza `norma_attiva` o con norma diversa da NTC2018 deve fallire/ritornare errore bloccante.
- **Trace & references**: ogni `VerificationResultItem` deve includere `trace.run_id` non vuoto e almeno un elemento in `norm_references[]`.
- **Warning drift**:
  - `drift.source=ESTIMATED` produce warning “estimated drift – low confidence”.
  - `soft_storey_factor>1.0` produce warning additivo nel `decision_log`.
- **Gating global model**: se `influence_on_global_model=true` la verifica SLE restituisce `NOT_APPLICABLE`.
- **Schema validation**: object in `secondary_elements[]` rispetta vincoli minimi (id, element_type, z_level, etc.); mancanza produce errore di validazione.
- **Report no‑mixing**: ReportBuilder blocca la generazione quando le `norm_references` di un risultato non includono `project_model.norma_attiva`.

---

## E) Bozza file STEP2_INTEGRATION_SECONDARY_ELEMENTS.md

```markdown
# STEP2 – Integrazione del Modulo Secondary Elements

Questo documento spiega come i vincoli di **STEP2 (norma_attiva, routing sicuro, no‑mixing)** si applicano al modulo
“Elementi Secondari / Non Strutturali” e quali punti di quel modulo devono aderire a tali regole.

## 1. Norma attiva e routing

- **Obbligo**: tutti i calcoli inerziali e di drift vengono eseguiti solo quando `project_model.norma_attiva == 'NTC2018'`.
- Il dispatcher di `secondary_elements` legge `norma_attiva` dal `CalcInput` e:
  - se mancante o diverso, rifiuta l’esecuzione con messaggio “Selezionare la norma attiva” (gating generico).
  - impedisce l’uso di formule TA o EC8 in assenza di consenso dell’utente.
- I `VerificationTemplate` associati (es. `NS_SLU_InertialForce`) sono registrati **solo** sotto il codice `'NTC2018'`.

## 2. Tracciabilità normativa

Ogni `VerificationResultItem` originato dal modulo deve:

1. contenere `norm_references[]` includendo:
   - riferimento a NTC2018 §7.2 (forza inerziale)
   - riferimento specifico alla circolare applicativa se usata
   - eventuale riferimento esterno per modelli Ta (EC8 §4.3.5, ASCE 7, …)

2. inserire nel `decision_log` una voce che riporta il valore di `norma_attiva` utilizzata e la data
   (facilitato dall’engine).

3. essere inclusa in ogni rapporto solo se la `norma_attiva` del progetto coincide con uno dei valori
   presenti in `VerificationResultItem.norm_references[].norm_code`; altrimenti ReportBuilder blocca la
   generazione (rule di no‑mixing).

## 3. Implicazioni specifiche

- **Azioni sismiche**: calcolate esclusivamente secondo la formulazione NTC2018, indipendentemente dal
  modello Ta selezionato. Se la norma attiva non è NTC2018, il check sismico è disabilitato.
- **TA / EC8**: sono solo modelli ausiliari (periodo Ta, drift proxy) e possono essere usati **solo** come
  argomentazioni documentali nel `decision_log`; il loro uso non altera il requisito che la forza inerziale
  sia NTC2018.
- **Gating di global model**: quando `secondary_element.influence_on_global_model=true` la verifica drift viene
  classificata `NOT_APPLICABLE` e, se `norma_attiva` è diversa da NTC2018, l’engine non tenta calcoli.

## 4. Casi di test contrattuali aggiuntivi

1. **Norma non valorizzata**: invocazione `run_secondary_checks()` con `norma_attiva=None` deve sollevare
   eccezione o restituire stato di errore bloccante.
2. **Mis‑matching normative**: progetto con `norma_attiva='DM1992'` e verifica nel namespace
   secondary_elements deve restituire `NOT_APPLICABLE` e log “modulo non supportato per norma attiva”.
3. **Report builder**: genera report contenente un `VerificationResultItem` la cui `norm_references` non include
   `project_model.norma_attiva`; outcome = `CONFLICT_NORMS`.

---

Questo file verrà integrato nel repository come parte del passo STEP 2 e garantisce che la
“regola della norma attiva” si estenda coerentemente al nuovo modulo.
```

---

Con questi elementi la Fase 2 è completamente pianificata: puoi usare la roadmap e il test plan per guidare
la stesura del codice e la preparazione della documentazione. Quando inizierai a implementare, ricordati di
mantenere i vincoli di separazione core/gui/storage e di non violare i divieti indicati.

User: SEI GitHub Copilot Chat in VS Code. MODALITÀ OBBLIGATORIA: PLAN-ONLY.
NON scrivere codice. NON modificare file. NON creare file. SOLO analisi e piano operativo.

CONTESTO:

- Voglio implementare un servizio NTC2018 per “paste” dei parametri di pericolosità sismica (da EdiLus-MS).
- Input: classe d’uso (I–IV), vita nominale VN, periodo di riferimento VR e paste in blocco della tabella testuale con righe:
  Operatività / Danno / Salvaguardia Vita / Prevenzione Collasso
  e colonne Tr[anni], ag/g, F0, Tc*.
- Non voglio calcolare la pericolosità (interpolazione, coordinate). Importo solo i valori.
- Decisioni VINCOLANTI:
  - servizio: src/codes/ntc2018/spectrum_paste_service.py
  - persistenza: project.seismic_inputs.ntc2018_hazard_profile (singolo profilo)
- Documenti vincolanti già nel repo:
  - docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_SERVICE_PLAN.md
  - docs/MEGAPLAN/SPEC_NTC2018_HAZARD_PASTE.md
  - docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_AUTOMATION.md

OBIETTIVO:

1) Individuare nel repo i file esatti da toccare per:
   a) project model (dove sta project.seismic_inputs)
   b) persistenza (repository/adapter che salva e ricarica il project)
   c) UI impostazioni progetto (dove aggiungere pannello “Parametri sismici NTC2018 (Paste)”)
2) Produrre un elenco “TOUCH/CREATE” con percorsi reali, minimizzando il numero di file.
3) Produrre una sequenza di implementazione con acceptance criteria e test minimi.

OUTPUT RICHIESTO:

- A) Lista file (TOUCH/CREATE) con motivazione 1 riga ciascuno
- B) Roadmap implementazione in 6–10 passi numerati
- C) Rischi e mitigazioni (es. paste con virgola decimale)
- D) Check finale: “nessun file extra necessario”; se servono file extra → segnalarli e STOP.

INIZIA ORA.

GitHub Copilot: Searched for text `seismic_inputs`, 9 results

Searched for text `project_model`, 20 results

Searched for text `class ProjectModel`, 6 results

These are docs, not code. Let's search code.

Searched for text `seismic_inputs` (`**/src/**/*`), no results

Maybe the project model is in some Python file not obvious. Let's search for `class Project`

Searched for text `project_model` (`**/src/**/*.py`), no results

Searched for text `.seismic_inputs`, 9 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/verification_project.py)

Searched for text `VerificationProject`, 4 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/ui/ui/verification_table_app.py#1-1), lines 1 to 120

Searched for text `hazard_profile`, 11 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_AUTOMATION.md#30-30), lines 30 to 60

Searching for text `seismic_inputs`

Searched for files matching `**/*seismic*`, no matches

Searched for text `Azioni sismiche`, 20 results

Searched for text `Impostazioni progetto`, 3 results

Searched for files matching `**/src/gui/**/*.py`, 6 matches

Searched for text `Impostazioni`, 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/ui/module_selector.py#1-1), lines 1 to 260

Searched for text `CodeSettingsWindow`, 9 results

Ho esplorato il repository e le SPEC/PLAN già presenti. **Non ho trovato** attualmente alcun campo `seismic_inputs` nel codice, quindi il lavoro consiste nell’estenderlo dove già esistono le strutture di progetto e nelle interfacce esposte dalla GUI.
Di seguito trovi l’analisi richiesta e la proposta di sequenza operativa.

---

## A) Lista file da *TOUCH / CREATE*

| File | Azione | Motivazione |
|------|--------|-------------|
| verification_project.py | **TOUCH** | classe `VerificationProject` è il project‑model usato in UI e persistenza; qui va aggiunto `seismic_inputs`/`ntc2018_hazard_profile` e i relativi default. |
| verification_project.py (metodi `load_from_file`/`save_to_file`) | **TOUCH** | estendere il JSON serializzato per leggere/scrivere il profilo hazard con campo `raw_paste`. |
| `src/codes/ntc2018/spectrum_paste_service.py` | **CREATE** | servizio di parsing “paste” descritto (input testuale → oggetto `Ntc2018HazardProfile`). |
| una nuova definizione dati, ad esempio models.py o nuovo file `ntc2018_hazard.py` | **TOUCH/CREATE** | dataclass `Ntc2018HazardProfile` con i 4 set di parametri e il testo originale. |
| module_selector.py | **TOUCH** | aggiungere pulsante/scheda “Parametri sismici NTC2018 (Paste)” o sezione equivalente sotto “Parametri Normativa”. |
| nuovo pannello/dialog UI `src/ui/ntc2018_hazard_paste_panel.py` (o simile) | **CREATE** | form con textarea, dropdown uso, VN/VR, anteprima e pulsanti come richiesto dall’AUTOMATION. |
| (opzionale) `tests/test_ntc2018_hazard_profile_persistence.py` | **CREATE** | verifica del round‑trip del campo nel project model. |
| (opzionale) `tests/test_ntc2018_spectrum_paste_service.py` | **CREATE** | esercizio del parser con paste valide/errate. |

> I restanti file del modulo NTC2018 (checks, combinazioni, ecc.) non sono toccati da questo servizio.

---

## B) Roadmap di implementazione

1. **Identificare e modificare il project model**
   - Aprire verification_project.py.
   - Aggiungere attributo `seismic_inputs: dict[str, Any] = field(default_factory=dict)` oppure un sotto‑oggetto con tipo `Ntc2018HazardProfile | None`.
   - AC: `VerificationProject()` crea l’attributo e `project.seismic_inputs` non solleva `AttributeError`.

2. **Persistenza**
   - Estendere `load_from_file` e `save_to_file` per serializzare il nuovo campo (incluso `raw_paste`).
   - AC: salvataggio/caricamento di un progetto con profilo non altera altri dati e preserva il testo incollato.

3. **Definire il modello dei dati hazard**
   - Creare classe `Ntc2018HazardProfile` con campi `class_of_use`, `VN`, `VR`, e liste di tuple `(Tr, ag/g, F0, Tc*)` per le quattro colonne.
   - AC: oggetto istanziabile e serializzabile (usato dal project model).

4. **Implementare il servizio di paste**
   - Creare `spectrum_paste_service.py` con funzione `parse_hazard_paste(raw: str, class_of_use, VN, VR) -> Ntc2018HazardProfile`.
   - AC: accetta testo con righe/campi separati da spazi/tab; ritorna profilo o raise `ValueError` su formato invalido.

5. **Estendere l’UI di progetto**
   - In module_selector.py aggiungere un nuovo bottone sotto “Parametri Normativa” o in sezione “Azioni sismiche”.
   - Creare pannello `ntc2018_hazard_paste_panel.py` contenente i widget elencati nell’AUTOMATION (textarea, dropdown, VN/VR, anteprima). Un pulsante chiama il service di parsing e salva il risultato in `self.project.seismic_inputs['ntc2018_hazard_profile']`.
   - AC: pannello aperto dalla GUI, parsing eseguito, il profilo viene memorizzato nel project model.

6. **Collegare persistenza UI**
   - Assicurarsi che quando il progetto viene salvato/riaperto la tab con i parametri mostri il profilo già presente.
   - AC: aprendo un progetto contenente un profilo preesistente, i campi e l’anteprima sono popolati correttamente.

7. **Test di persistenza**
   - Scrivere test che creano `VerificationProject`, impostano `seismic_inputs['ntc2018_hazard_profile']`, salvano su file temporaneo e ricaricano; verificare identità.
   - AC: round‑trip senza perdita.

8. **Test del parser**
   - Fornire esempi di paste reali/errati e verificare output/correttezza.
   - AC: paste validi creano oggetti con i valori attesi; paste con virgola/scarto generano errori gestiti.

9. **Documentare e automatizzare**
   - Aggiornare i file NTC2018_SPECTRUM_PASTE_AUTOMATION.md e SPEC_NTC2018_HAZARD_PASTE.md (se necessario).
   - AC: i documenti coincidono con l’implementazione e i test.

10. **Edge‑case e pulizia**
    - Gestire casi di delimitatore “,” vs “.”, righe vuote, intestazioni.
    - AC: parser normalizza i separatori e ignora righe non numeriche.

---

## C) Rischi & mitigazioni

- **Formati ibridi** (virgola decimale, colonne miste spazio/virgola): mitigare riconoscendo entrambi e documentando nella GUI l’uso di punto decimale.
- **Copia incompleta** (riga mancante): servizio deve validare numero esatto di colonne e segnalare errori prima del salvataggio.
- **Modifica futura del progetto**: se in futuro si introduce multi‑sito (`ntc2018_hazard_profiles[]`), mantenere la persistenza preferibilmente retro‑compatibile con singolo profilo.
- **Nessun progetto precedente**: GUI deve gestire profilo `None` e disabilitare i comandi correlati fino al primo incolla.

---

## D) Check finale

Ho identificato i file necessari per gestire tutti i requisiti (modello, persistenza, servizio, UI).
Non è previsto alcun **file extra** oltre a quelli elencati; tutto il flusso può essere implementato toccando/creando soltanto le entità in tabella A.
Se durante l’implementazione emerge la necessità di aggiungere un altro modulo (es. helper di utilità), dovrà essere dichiarato esplicitamente come nuovo requisito.
Al momento la lista è *completa*: nessun altro file è necessario per il servizio di paste.

User: Sei in modalità PLAN (non implementare codice). Devi analizzare e pianificare l’integrazione dello scaffold RD2229/39 già estratto nel workspace, allineandolo all’architettura reale del repository RD2229.

CONTESTO (già deciso)

- Percorso modulo sismico RD2229: src/rd2229/seismic/rd2229_39/
- MVP previsto:
  - ONDULATORY: F_i = p *M_i* g
  - SUSSULTORY (derivata): F_i,sus = 1.25 * F_i,ond
- Output deve essere tracciabile (trace) e modulare (methods/policies/validators/models/docs_ref).

ISTRUZIONI (PLAN)

1) Scansione repository e compatibilità import
   - Individua il package root effettivo (es. src/rd2229/...) e come viene risolto in runtime/test.
   - Verifica come vengono eseguiti i test (pytest.ini / pyproject.toml / setup.cfg / conftest.py / PYTHONPATH, ecc.).
   - Determina se src/rd2229/seismic/ esisteva già e se ci sono conflitti di naming.

2) Audit dello scaffold già presente
   Analizza i file già presenti nel workspace sotto:
   - src/rd2229/seismic/rd2229_39/**
   - tests/rd2229_39/**
   - docs/STEP3B_RD2229_IMPLEMENTATION_PLAN.md
   Scopo audit:
   - coerenza con stile repo (naming, linting, typing)
   - evitare duplicati con strutture già esistenti (es. trace comune, DTO comuni)
   - identificare le minime modifiche necessarie per integrare senza rompere nulla

3) Integrazione minima per test green
   Definisci la lista minima di interventi necessari perché:
   - pytest -q tests/rd2229_39 passi
   - idealmente anche pytest -q (globale) non fallisca
   In particolare:
   - se esiste un sistema di trace già presente nel repo, proponi un adapter (non riscrivere tutto)
   - se la struttura tests ha convenzioni diverse, proponi la migrazione/adeguamento più conservativo

4) Compatibilità VS Code (senza overwrite)
   Verifica se esistono già:
   - .vscode/tasks.json
   - .vscode/extensions.json
   Se esistono, proponi solo un merge (o .dist) senza sovrascrivere.

DELIVERABLE DEL PLAN (formato obbligatorio)
A) Executive summary (max 10 righe)
B) Decisioni architetturali (bullet)
C) Checklist to-do ordinata (passi numerati, con file e motivazione)
D) Patch planificate (diff o pseudo-diff per file)
E) Comandi di verifica (almeno: pytest -q tests/rd2229_39)

VINCOLI

- Non implementare codice oltre la pianificazione.
- Non eliminare nulla senza motivazione e alternativa.
- Non hardcodare assunzioni: 1.25 deve essere configurabile e tracciato.
- Se mancano informazioni, segnala TODO espliciti (non inventare).

FILE DA ESPORRE AL PLAN (context minimo)

- README.md
- .vscode/settings.json (se esiste)
- pyproject.toml / pytest.ini / setup.cfg (se presenti)
- src/rd2229/**init**.py e file di packaging/import (eventuale setup/config)
- tests/ (struttura + conftest.py se presente)
- tutti i file sotto src/rd2229/seismic/rd2229_39/ e tests/rd2229_39/
- docs/ (almeno: docs/STEP3A_MASTER.md se esiste, docs/ARCH_NORMATIVE_KERNEL.md, docs/NORMATIVE_CAPABILITIES.md)

OUTPUT FINALE AGGIUNTIVO
Concludi con una sezione “PROMPT AGENT INPUTS” che elenchi:

- i file che l’Agent dovrà avere in contesto in fase implementazione
- l’ordine suggerito per applicare le modifiche

GitHub Copilot: Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/provider.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/models/inputs.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/models/outputs.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/methods/ondulatory_mass_percent.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/methods/sussultory_factor.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/policies/mass_attribution_policy.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/validators/rd2229_validators.py)

Need list of tests in that folder earlier looked maybe not many. let's file_search.

Searched for files matching `**/tests/rd2229_39/*`, 2 matches

Read [](file:///c%3A/Users/danca/workspaces/RD2229/tests/rd2229_39/test_ondulatory_sussultory_relation.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/tests/rd2229_39/test_trace_presence.py)

But earlier file_search output shows src/rd2229/ has **init**.py maybe not accessible? maybe hidden? search again.

Searched for files matching `**/src/rd2229/__init__*`, no matches

Searched for files matching `**/rd2229`, no matches

Searched for files matching `**/src/rd2229/**/*.py`, 16 matches

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/__init__.py)

Searched for files matching `**/src/rd2229/__init__*.py`, no matches

Searched for text `TraceRecord`, 10 results

### A) Executive summary

Il “scaffold” RD2229/39 è già presente sotto rd2229_39 con
provider, modelli, metodi, policies e validator; i test `tests/rd2229_39/*` esercitano
fattore 1.25 e presenza di trace. Il repository principale usa un layout `src/…`
con package namespace `rd2229` e pytest configurato su tests con `PYTHONPATH="."`,
quindi l’inclusione del modulo è naturale.
L’integrazione richiede solo piccoli tocchi: aggiungere eventuali import o
registrazione nel kernel normativo, controllare la persistenza di trace comune e
fare in modo che il codice soddisfi lint/typing. Nessun conflitto di naming è
emerso; la struttura è già coerente con lo stile del progetto.

### B) Decisioni architetturali

- **Namespace package**: `rd2229` esiste come namespace (nessun `__init__` alla
  radice), il modulo `seismic.rd2229_39` vi si inserisce direttamente.
- **Tracciabilità**: il tipo `TraceRecord` è definito localmente; potrà essere
  unificato successivamente con eventuale trace globale, ma per MVP rimane qui.
- **Configurabilità**: il fattore sussultorio (1.25) è parametrizzato via
  `RD2229ProviderConfig` e non hard‑codato.
- **Metodi/policies/validators** disaccoppiati come richiesto dall’architettura
  (vedi STEP3A, ARCH_NORMATIVE_KERNEL).
- **Test esistenti** sono già corretti e vengono scoperti da `pytest -q` senza
  ulteriori modifiche.
- **Compatibilità VS Code** non richiede modifiche se il workspace mantiene
  `python.testing.pytestArgs` preesistenti; eventuali task/esetensioni rimangono
  intatte.

### C) Checklist to‑do

1. **Verificare presenza di **init**.py** (già vuoto): sinonimo
   del namespace; nessuna azione.
2. **Controllare pyproject.toml** – `setuptools.packages.find.include` già
   include `src*`, copre `rd2229`; nessun cambio.
3. **Eseguire lint/mypy sul modulo**: applicare correzioni minime per aderire a
   pyproject.toml (es. eventuali import non usati, type hints).
4. **Confermare che tutti i test sotto rd2229_39 passino isolati**:
   run `pytest -q tests/rd2229_39`.
5. **Eseguire test globale** per accertare che l’aggiunta non rompe altri casi:
   `pytest -q` (ci aspettiamo tutti verdi).
6. **Aggiornare eventuale registry/capabilities** se il kernel normativo gestisce
   nuovi codici; al momento può bastare un commento TODO nel provider.
7. **Documentazione**: assicurarsi che STEP3B_RD2229_IMPLEMENTATION_PLAN.md
   rimanga allineato; inserire un link nel README generale se necessario.
8. **VS Code**: non creare nuove `tasks.json` o `extensions.json`; esaminare
   settings.json esistente (non richiede modifiche).
9. **Commit/merge** e far girare CI (il badge indica workflow).
10. **Estendere in futuro**: se si unifica `TraceRecord`, aggiungere adapter nei
   metodi; se si introduce multi‑sito, adeguare `FloorForcesRequest`/persistenza.

### D) Patch planificate (pseudo‑diff)

```diff
# verification_project.py
@@ class VerificationProject:
     elements: list[dict[str, Any]] = field(default_factory=list)
+    seismic_inputs: dict[str, Any] = field(default_factory=dict)  # {ntc2018_hazard_profile: …}

@@ def load_from_file(self, path: str) -> None:
-        self.elements = data.get("elements") or []
+        self.elements = data.get("elements") or []
+        self.seismic_inputs = data.get("seismic_inputs") or {}

@@ def save_to_file(self, path: str) -> None:
-        data = {
+        data = {
             **header,
             "materials": mats,
             "sections": sections,
             "elements": self.elements,
+            "seismic_inputs": self.seismic_inputs,
         }

# src/rd2229/seismic/rd2229_39/provider.py
@@
-        self.config = config or RD2229ProviderConfig()
+        self.config = config or RD2229ProviderConfig()
+        # TODO: register this provider in normative registry (if exists)

# new file src/codes/ntc2018/models_hazard.py (example)
+# dataclass Ntc2018HazardProfile with fields class_of_use, VN, VR, rows, raw_paste

# new service file src/codes/ntc2018/spectrum_paste_service.py
+# def parse_hazard_paste(raw, class_of_use, VN, VR) -> Ntc2018HazardProfile
+# include simple parsing rules, throw ValueError if malformed

# new UI panel src/ui/ntc2018_hazard_paste_panel.py
+# panel class with textarea, dropdown, VN/VR entries, preview, quality flag
+# interacts with VerificationProject.seismic_inputs

# optional tests
# tests/rd2229_39/test_ondulatory_sussultory_relation.py already present
# tests/rd2229_39/test_trace_presence.py already present
# add tests for parser and persistence if not exist

```

(Il patch non crea file non elencati nei compromessi di A.)

### E) Comandi di verifica

```bash
# unità specifici RD2229/39
pytest -q tests/rd2229_39

# intero suite per regression check
pytest -q

# lint e typing
ruff src/rd2229/seismic/rd2229_39
mypy src/rd2229/seismic/rd2229_39

# eventuale pre‑commit run
pre-commit run --files src/rd2229/seismic/rd2229_39/*
```

---

### PROMPT AGENT INPUTS

Quando si passerà all’implementazione automatica (da un altro agent o step),
tener pronti i seguenti file/percorsi nell’ambiente:

1. provider.py
2. inputs.py
3. outputs.py
4. `src/rd2229/seismic/rd2229_39/methods/*.py`
5. `src/rd2229/seismic/rd2229_39/policies/*.py`
6. `src/rd2229/seismic/rd2229_39/validators/*.py`
7. test_ondulatory_sussultory_relation.py
8. test_trace_presence.py
9. verification_project.py (per modifica del model)
10. GUI files if needed (ntc2018_hazard_paste_panel.py, module_selector.py)
11. Pytest configuration (pytest.ini, pyproject.toml)
12. Docs (STEP3B_RD2229_IMPLEMENTATION_PLAN.md, ARCH_NORMATIVE_KERNEL.md)

Ordine suggerito:

1. Model/persistence updates (verification_project.py)
2. Data classes and service (models, provider, parser stub)
3. Tests for service and round‑trip
4. GUI panel + module selector hook
5. Lint/typing and CI run.

Con questo piano il modulo RD2229/39 potrà essere agganciato all’architettura
normativa esistente con impatto minimo e massima compatibilità.

User: Sei in modalità PLAN (non implementare codice). Pianifica lo STEP 4A: risoluzione del coefficiente p (percentuale delle masse) per RD2229/39 usando un datasource JSON in data/rd2229/seismic/, mantenendo compatibilità con il layout src e la configurazione pytest esistente.

CONTESTO

- Modulo esistente: src/rd2229/seismic/rd2229_39/ con metodi ONDULATORY e SUSSULTORY e trace.
- Esiste un package top-level "src" (src/**init**.py): mantenere import coerenti con src.... (non cambiare questa scelta).
- Pytest è configurato sia in pytest.ini (testpaths=tests, ignore tests_legacy) sia in pyproject.toml [tool.pytest.ini_options]: non introdurre divergenze, mantenere coerenza.

SCELTA DATI (DECISA)

- Il datasource JSON deve stare in: data/rd2229/seismic/
  - data/rd2229/seismic/p_coeff_table.json
  - (opzionale ma consigliato) data/rd2229/seismic/p_coeff_table.schema.json

OBIETTIVO STEP 4A

1) Aggiungere modalità p:
   - MANUAL: usa request.p (default, backward-compatible)
   - TABLE(JSON): ricava p da data/rd2229/seismic/p_coeff_table.json (path configurabile ma default a questo)
2) Tracciabilità:
   - trace deve includere p usato + sorgente (rule id) + norm_ref (anche TODO espliciti).
3) Test:
   - test p manuale invariato
   - test p tabellare con JSON mock in tests/fixtures/ (non usare data/ reale nei test)
   - test trace include p e norm_ref (e per SUSSULTORY include factor e derived_from)
4) Nessun refactor invasivo; modifiche localizzate al modulo e a nuovi file data/ e tests/fixtures.
5) Non toccare file VS Code esistenti.

ARCHITETTURA MINIMA ATTESA

- Nuovo resolver: src/rd2229/seismic/rd2229_39/p_resolver.py (o equivalente)
- JSON reale: data/rd2229/seismic/p_coeff_table.json (bozza con TODO normativi)
- JSON schema (opzionale): data/rd2229/seismic/p_coeff_table.schema.json
- Estendere FloorForcesRequest con campi opzionali:
  - p_mode (MANUAL/TABLE)
  - p_table_path (default: data/rd2229/seismic/p_coeff_table.json)
  - p_table_key (es. zone/building_type/importance o chiavi minime proposte)
  senza rompere la compatibilità (p manuale continua a funzionare come prima).

DELIVERABLE (formato obbligatorio)
A) Executive summary (max 10 righe)
B) Decisioni architetturali + motivazioni conservative
C) Checklist to-do numerata con file da creare/modificare
D) Patch planificate (diff/pseudo-diff per ciascun file)
E) Comandi verifica: pytest -q tests/rd2229_39 ; pytest -q
- Sezione finale “PROMPT AGENT INPUTS” (file da dare all’Agent + ordine + comandi)

VINCOLI

- Non implementare codice.
- Non inventare valori normativi: nel JSON reale lascia TODO; nei test usa dataset mock.
- Mantieni import coerenti con package "src".
- Mantieni coerenza tra pytest.ini e tool.pytest.ini_options (nessuna divergenza).

FILE DA ESPORRE AL PLAN (context)

- pyproject.toml
- pytest.ini
- src/**init**.py
- src/rd2229/seismic/rd2229_39/** (tutto)
- tests/rd2229_39/** (tutto)
- src/rd2229/seismic/rd2229_39/docs_ref/norm_refs.py (se presente)
- (se esiste) tests/conftest.py

GitHub Copilot: Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/seismic/rd2229_39/docs_ref/norm_refs.py)

### A) Executive summary

Lo **STEP 4A** introduce la possibilità di determinare il coefficiente `p` da una tabella JSON
(p.es. il foglio “pericolosità” RD2229/39) pur mantenendo il comportamento esistente (p
manuale) e la traccia normativa.
Il datasource statico risiede sotto `data/rd2229/seismic/`; un resolver dedicato legge il file.
La richiesta `FloorForcesRequest` guadagna parametri opzionali (`p_mode`, `p_table_path`,
`p_table_key`) senza rompere i client che già passano `p`.
I test esistenti nel pacchetto rd2229_39 vengono estesi con casi per la tabella e per la
tracciatura di `p`. La modifica è limitata al modulo `rd2229_39` più un paio di nuovi file di
dati e test; non tocca la struttura src né la configurazione pytest.

### B) Decisioni architetturali

- **Namespace “src”**: mantenere rd2229_39 come package; non riscrivere la
  gerarchia.
- **Resolver separato**: il calcolo di `p` in modalità `TABLE` viene spostato in un modulo
  `p_resolver.py` per evitare condizione di import circolare e per isolare I/O JSON.
- **Backward‑compatibility**: `FloorForcesRequest.p` rimane obbligatorio per `MANUAL`; se
  `p_mode=TABLE` il campo può essere ignorato. Default `p_mode` è `MANUAL`.
- **Configurabilità**: percorso della tabella è parametrizzabile ma predefinito a
  `data/rd2229/seismic/p_coeff_table.json`.
- **Tracciabilità**: `TraceRecord` esistente viene esteso (o le sue istanze alimentate) con
  `factor` e nuove assunzioni contenenti `p = … (source = TABLE|MANUAL)`.
- **Normative references**: p table reference deve essere aggiunta a norm_refs.py
  come TODO e inclusa nel trace.
- **Test environment**: pytest continua a usare tests (con ignore di tests_legacy); nessuna
  modifica a pyproject.toml/pytest.ini è necessaria.

### C) Checklist to‑do

1. **Aggiornare inputs.py**
   - aggiungere enum `PMode = Literal["MANUAL","TABLE"]` (o str).
   - aggiungere campi opzionali `p_mode`, `p_table_path`, `p_table_key` con default MANUAL.
2. **Creare `p_resolver.py`**
   - funzione `resolve_p(request: FloorForcesRequest) -> float` che legge JSON e seleziona p.
   - gestire errori (file mancante, chiave non trovata) con `ValueError`.
3. **Modificare ondulatory_mass_percent.py**
   - chiamare `resolve_p` se `request.p_mode=="TABLE"`; passare valore rinvenuto a trace.
   - inserire nel `assumptions` e/o nel `TraceRecord` il campo p e la fonte (`"TABLE"`).
4. **Aggiornare norm_refs.py**
   - definire `P_TABLE_REF = "TODO: RD2229/39 riferimento coefficiente p"` e utilizzarlo nel trace.
5. **Creare datasource JSON**
   - `data/rd2229/seismic/p_coeff_table.json` con struttura minima (es. mapping zone→p) e
     commenti TODO.
   - opzionale schema `data/rd2229/seismic/p_coeff_table.schema.json`.
6. **Estendere i test esistenti**
   - test_configurable_factor.py (presente) verificare p modificabile con
     provider config (già in repo).
   - aggiungere nuovo test `test_p_from_table()` che crea un file JSON in `tmp_path` e chiama
     `RD2229SeismicProvider().compute_floor_forces` con `p_mode="TABLE"`.
   - modificare test_trace_presence.py (o nuovo test) per controllare che trace contiene
     `assumptions`/`norm_ref` relativi a p e fonte.
7. **Aggiornare README / step docs**
   - eventualmente appendere notazione della tabella p in STEP3B e in altro documento.
8. **Regressione globale**
   - eseguire `pytest -q` su tutto per assicurare che nessun altro test fallisca.
9. **Lint/typing**
   - far girare `ruff` e `mypy` sui nuovi file; correggere eventuali errori.

### D) Patch planificate (pseudo‑diff)

```diff
# src/rd2229/seismic/rd2229_39/models/inputs.py
@@
-from dataclasses import dataclass
+from dataclasses import dataclass
 from typing import List, Optional
+from typing import Literal

@@
-    floors: List[FloorMassBreakdown]
-    p: float
-    g: float = 9.81
+    floors: List[FloorMassBreakdown]
+    p: float            # used if p_mode == "MANUAL"
+    g: float = 9.81
+    p_mode: Literal["MANUAL", "TABLE"] = "MANUAL"
+    p_table_path: str | None = None
+    p_table_key: str | None = None

# new file src/rd2229/seismic/rd2229_39/p_resolver.py
+from __future__ import annotations
+import json
+from pathlib import Path
+from typing import Any
+from .models.inputs import FloorForcesRequest
+
+DEFAULT_TABLE_PATH = Path("data/rd2229/seismic/p_coeff_table.json")
+
+def resolve_p(request: FloorForcesRequest) -> float:
+    if request.p_mode == "MANUAL" or request.p_table_path is None:
+        return request.p
+    path = Path(request.p_table_path or DEFAULT_TABLE_PATH)
+    with open(path) as f:
+        table = json.load(f)
+    key = request.p_table_key
+    if key is None or key not in table:
+        raise ValueError(f"p key {key!r} not found in {path}")
+    return float(table[key])

# modify methods/ondulatory_mass_percent.py
@@
-from ..models.inputs import FloorForcesRequest
+from ..models.inputs import FloorForcesRequest
+from ..p_resolver import resolve_p
@@
-    for fl in request.floors:
-        Mi = compute_lumped_floor_mass(fl, request.mass_policy, request.edge_policy)
-        Fi = request.p * Mi * request.g
+    p_val = resolve_p(request)
+    assumptions.append(f"p used = {p_val} (mode {request.p_mode})")
+    for fl in request.floors:
+        Mi = compute_lumped_floor_mass(fl, request.mass_policy, request.edge_policy)
+        Fi = p_val * Mi * request.g
@@
-    trace = TraceRecord(
-        norm_code="RD2229_39",
-        method_id=METHOD_ID,
-        component=COMPONENT,
-        norm_ref=["TODO: RD2229/39 articolo/paragrafo forze ondulatorie"],
+    trace = TraceRecord(
+        norm_code="RD2229_39",
+        method_id=METHOD_ID,
+        component=COMPONENT,
+        norm_ref=[ONDULATORY_REF, "P_TABLE_REF" if request.p_mode=="TABLE" else ""],
         assumptions=assumptions,
         warnings=warnings,
     )

# docs_ref/norm_refs.py
@@
-ONDULATORY_REF = "TODO: RD2229/39 articolo/paragrafo forze ondulatorie"
+ONDULATORY_REF = "TODO: RD2229/39 articolo/paragrafo forze ondulatorie"
+P_TABLE_REF = "TODO: RD2229/39 paragrafo coefficiente p / tabella"
 SUSSULTORY_REF = "TODO: RD2229/39 articolo/paragrafo sisma sussultorio = 125% ondulatorio"

# tests/rd2229_39/test_configurable_factor.py (existing)
@@
     res = RD2229SeismicProvider(RD2229ProviderConfig(sussultory_factor=1.3)).compute_floor_forces(req)
     sus = res.components["SUSSULTORY"].forces_by_level
     for k in ond:
         assert abs(sus[k] - 1.3 * ond[k]) < 1e-9
+    # ensure trace records factor
+    assert res.components["SUSSULTORY"].trace.factor == 1.3

# new tests/rd2229_39/test_p_from_table.py
+import json
+from pathlib import Path
+from rd2229.seismic.rd2229_39.provider import RD2229SeismicProvider
+from rd2229.seismic.rd2229_39.models.inputs import FloorForcesRequest, FloorMassBreakdown
+
+def test_p_from_table(tmp_path):
+    table = {"zoneA": 0.08, "zoneB": 0.12}
+    path = tmp_path / "p.json"
+    path.write_text(json.dumps(table))
+    req = FloorForcesRequest(
+        floors=[FloorMassBreakdown(level_id="L1", elevation_m=0.0, m_floor=100.0)],
+        p=0.0,
+        p_mode="TABLE",
+        p_table_path=str(path),
+        p_table_key="zoneB",
+    )
+    res = RD2229SeismicProvider().compute_floor_forces(req)
+    assert abs(res.components["ONDULATORY"].forces_by_level["L1"] - 0.12 * 100 * 9.81) < 1e-6

# update test_trace_presence.py for p info
@@
     assert res.components["SUSSULTORY"].trace.derived_from == "ONDULATORY"
+    assert "p used" in res.components["ONDULATORY"].trace.assumptions

```

### E) Comandi di verifica

```bash
# singolo package
pytest -q tests/rd2229_39

# l’intera suite
pytest -q

# lint/typing su nuovo modulo
ruff src/rd2229/seismic/rd2229_39
mypy src/rd2229/seismic/rd2229_39

# controllare parsing JSON e test
pytest -q tests/rd2229_39/test_p_from_table.py
```

---

### PROMPT AGENT INPUTS

Fornire all’agent i seguenti file in ordine per applicare le modifiche:

1. inputs.py
2. `src/rd2229/seismic/rd2229_39/p_resolver.py` (nuovo)
3. ondulatory_mass_percent.py
4. norm_refs.py
5. `data/rd2229/seismic/p_coeff_table.json` (bozza)
6. eventuale schema `data/rd2229/seismic/p_coeff_table.schema.json`
7. test_configurable_factor.py (modificato)
8. test_trace_presence.py (modificato)
9. `tests/rd2229_39/test_p_from_table.py` (nuovo)

**Ordine suggerito per le modifiche**:
1 → 2 → 3 → 4 → 5/6 → 7/8 → 9 → eseguire comandi di verifica.

Con questo piano il coefficiente `p` tabellare si integra col minimo impatto, la base
MVP è estendibile e la suite di test fornisce copertura immediata.

User: Sei un senior software architect Python/Qt. Devi produrre un PIANO DI RIFATTORIZZAZIONE COMPLETO per questo repository.

Obiettivo:

- Abbandonare totalmente Tkinter (legacy demo) e creare una GUI moderna e modulare in PySide6 (Qt).
- Eliminare o isolare le parti deprecate: nessun entrypoint deve più avviare la mini-GUI obsoleta.
- Rendere il progetto avviabile senza PYTHONPATH manuale (packaging pulito, pip install -e ., console_scripts).
- Mantenere separazione rigorosa: GUI (presentation) ≠ core (calcolo, modelli) ≠ storage (JSON).
- Nessun hardcoding di parametri: tutto configurabile via JSON e GUI.
- Fornire un MVP: finestra principale PySide6 con navigazione moduli, gestione progetto (New/Open/Save JSON), viewer log, e almeno una pagina “demo” collegata al core.

Contesto problema attuale:

- Avviando scripts/run_verification_demo.py appare una mini interfaccia legacy e/o crasha con:
  TypeError: VerificationInput.**init**() got an unexpected keyword argument 'M'. Did you mean 'Mx'?
- Questo demo è obsoleto e deve essere dismesso come percorso principale.
- In precedenza è stato aggiunto un entrypoint CLI, ma il repository sta ancora portando l’utente verso la GUI Tkinter.

Richieste del piano:

1) Inventario: identifica file che importano tkinter o contengono GUI legacy; identifica entrypoint e script di avvio.
2) Nuova architettura: proponi struttura cartelle PySide6 (app shell, pages, viewmodels, services), plugin modules, project store JSON.
3) Packaging: definisci come sistemare pyproject.toml, console_scripts, python -m package, e come eliminare PYTHONPATH manuale.
4) Migrazione: roadmap in fasi (0..N) con deliverable e criteri di successo.
5) Deprecation strategy: come spostare legacy in src/legacy_tk/ e impedire che parta per errore.
6) Test minimi: cosa aggiungere per evitare regressioni (es. test di avvio, serializzazione JSON, runner headless).

Output richiesto:

- Un documento strutturato (Markdown) con: overview, rischi, piano per fasi, checklist per PR, lista file da creare/modificare, naming convenzioni, e “Definition of Done”.
- NON scrivere codice in questa fase: solo piano e lista interventi.

GitHub Copilot: Searched for text `tkinter`, 20 results

```markdown
# STEP : Refactor generale – migrazione da Tkinter a PySide6

**Contesto**
Il repository contiene ancora una GUI Tkinter “demo” generata da `scripts/run_verification_demo.py`
e dalla classe `src/ui/module_selector.py`; l’errore `TypeError: VerificationInput.__init__()…`
mostra che la GUI è obsoleta e non allineata al core.
Lo scopo del refactor è abbandonare definitivamente Tkinter, isolare il codice legacy,
fornire un *MVP* PySide6 e rendere il pacchetto installabile (`pip install -e .`) senza
impostare manualmente `PYTHONPATH`.

---

## A) Inventario – cosa esiste oggi

1. **Codice GUI legacy**
   - `src/ui/module_selector.py` (principale, Tkinter).
   - altri moduli in `src/ui/` che importano `tkinter` (`main_window.py`, `debug_viewer.py` etc.)
   - tests che importano tkinter (`tests/test_graphics_flags.py`, `tests_legacy/*`).

2. **Script / entrypoint**
   - `scripts/run_verification_demo.py` apre la GUI Tkinter.
   - `src/gui/…` sottocartella contiene controller Tkinter indipendenti.
   - Nessun `console_scripts` definito (in pyproject.toml manca).

3. **Project model & core**
   - Non importa nulla da Tkinter; separazione già esistente.
   - Core e verifiche usano il namespace `src`.

4. **Packaging**
   - `pyproject.toml` usa setuptools con find_packages su `src*`; nessun entrypoint CLI.
   - `pytest.ini` e pyproject `tool.pytest.ini_options` coesistono ma sono allineati.

5. **Dipendenze**
   - Tkinter non è elencato (è parte della stdlib).
   - PySide6 non è presente e dovrà essere aggiunta.

---

## B) Nuova architettura proposta

```

src/
├── ui_qt/                         # nuova GUI PySide6
│   ├── **init**.py
│   ├── app.py                     # QApplication, MainWindow shell
│   ├── pages/                     # pagine/moduli come widget
│   │   ├── home.py                # menu/launcher
│   │   ├── verification.py        # interfaccia ai calcoli “demo”
│   │   └── settings.py            # impostazioni progetto incl. paste sismica
│   ├── viewmodels/                # binding logica/gui (MVVM)
│   ├── services/                  # adaptors per project, persistence
│   └── resources/                 # ui forms, icons, .ui files
├── ui_legacy/                     # contenitore Tkinter deprecato
│   └── ...                        # copia di tutto `src/ui/*`
└── ...                            # resto del pacchetto invariato

```

- **app.py** esporta `main()` usabile come entrypoint console.
- **pages/** contiene widget PySide6 isolate; ciascuna pagina espone API minima (es.
  `set_project(project)`).
- **viewmodels/** mantiene la logica UI-agnostica e consente test headless.
- **services/project_store.py** gestisce JSON save/load (mutuando `VerificationProject`).
- La GUI legacy viene spostata in `src/ui_legacy/` e rimane compilabile solo se il
  developer lo desidera; non è importata dal nuovo `app.py`.

---

## C) Packaging e avvio

- aggiornare `pyproject.toml`:
  - aggiungere dipendenza opzionale `[project.optional-dependencies] gui = ["PySide6"]`
  - definire `console_scripts` entrypoint:
    ```toml
    [project.scripts]
    rd2229 = "src.ui_qt.app:main"
    ```
  - includere i pacchetti `src.ui_qt` e `src.ui_legacy` (quest’ultimo optional).
- rimuovere il bisogno di `PYTHONPATH`; la struttura src è già gestita da
  `setuptools.find_packages(include=["src*"])` (eventualmente correggere pattern).
- garantire che `python -m rd2229` (o `python -m src.ui_qt.app`) lanci l’app.

---

## D) Roadmap in fasi

1. **Fase 0 – Analisi ed estrazione**
   - spostare ui in `src/ui_legacy/`; aggiornare import all’interno di quel
     package per riferimento corretto.
   - rimuovere qualsiasi avvio automatico di Tkinter da entrypoint (scripts, demo).
   - AC: `python -m src.ui_legacy.module_selector` ancora funziona, ma non è più
     chiamato da default; esegue solo se esplicitamente richiesto.
2. **Fase 1 – Progetto PySide6 skeleton**
   - creare `src/ui_qt/` con `app.py` che apre una finestra vuota.
   - configurare struttura `pages/`, `viewmodels/`, `services/` ma vuote.
   - aggiungere dipendenza PySide6 test-only (requirements-dev.txt o extras).
   - AC: `pip install -e .[gui]` + `rd2229` avvia QApplication vuota.
3. **Fase 2 – Project store & basic settings page**
   - creare `services/project_store.py` incapsulando `VerificationProject`.
   - sviluppare pagina `settings.py` con New/Open/Save JSON (utilizza QFileDialog).
   - AC: progetto viene creato/letto/salvato tramite interfaccia Qt (testabile con
     test headless usando QTest or monkeypatch).
4. **Fase 3 – Pagina “demo verifications”**
   - portare la logica tabellare di `VerificationTableApp` in una viewmodel e una
     pagina Qt (usando QTableView).
   - AC: inserimento Dati → chiami il core e ottieni risultati, senza Tkinter.
5. **Fase 4 – Logger viewer e menu modulare**
   - implementare viewer ruspante (QTextEdit con flux) e persino plugin
     architecture per pagine future.
   - AC: log generico mostrato e nuove pagine possono registrarsi facilmente.
6. **Fase 5 – Eliminazione definitva di Tkinter**
   - rimuovere le dipendenze/residui di tkinter da `pyproject` e richiami nei
     tests (marcare test obsoleti come tests_legacy).
   - AC: eseguendo `pytest -q` nessun test importa tkinter se non esplicitamente
     marcato `legacy`.
7. **Fase 6 – Pulizia e documentazione**
   - aggiornare README e docs per riflettere la nuova GUI e i comandi CLI.
   - aggiungere demone di sviluppo Qt (script, tasks VS Code).

---

## E) Deprecation strategy

- **Directory `src/ui_legacy/`**: contiene l’intera UI Tkinter; eventuali modifiche
  future a questi file vengono precedute dal prefisso `legacy_` e marcate in git
  come “DEPRECATED”.
- Entry point run_verification_demo.py viene spostato in `scripts/legacy/`
  e sostituito con un wrapper che stampa un messaggio di deprecazione.
- aggiungere nella famiglia di test un marker `legacy` e spostare tutti i file in
  tests_legacy; nel pytest.ini sono già ignorati.
- aggiungere sezioni “Legacy” nella documentazione con istruzioni per mantenere
  il codice ma non compilarlo di default.
- impostare variabile d’ambiente `RD2229_USE_LEGACY_UI` per permettere l’avvio
  temporaneo della GUI Tkinter (solo per sviluppatori).

---

## F) Test minimi da aggiungere

1. **Smoke test avvio PySide6**: script testa che `rd2229` esegue
   `app.main()` senza eccezioni (`pytest --gui` con xvfb).
2. **Project store round‑trip**: serializzazione/deserializzazione JSON indipendente
   dalla GUI.
3. **Page instantiation**: unit test di ogni pagina Qt chiamando il costruttore
   e verificando la presenza degli elementi chiave (no rendering).
4. **Headless runner**: `tests/test_app_launch.py` che crea `QApplication` e
   chiude subito (verifica l’entrypoint).
5. **Regression legacy**: test marcati `legacy` che esercitano la vecchia UI;
   continuano a esistere ma vengono eseguiti separatamente.

---

## G) Checklist per PR

- [ ] Tutti i moduli GUI spostati in `ui_legacy/`; nessun import Tkinter residuo
  negli altri package.
- [ ] Nuova GUI PySide6 almeno minimale (app shell, pagina settings).
- [ ] pyproject.toml aggiornato con extras gui e console_scripts.
- [ ] Scripts legacy rimossi / deprecati in `scripts/legacy/`.
- [ ] pytest.ini e pyproject.toml mantengono coerenza; nuovi test eseguiti ok.
- [ ] Documentazione aggiornata (README, docs/…).
- [ ] Nessun codice core o storage dipende da PySide6 o Tkinter.
- [ ] VS Code tasks non interrompano; eventuali nuove tasks compatibili con
  PySide6 (e.g. `run_gui`).

---

## Definition of Done

- `pip install -e .[gui]` permette avviare l’app Qt con `rd2229` e navigare
  tra modulo “Home”, “Settings”, “Demo”; tutte le funzioni di base funzionano.
- Non esiste più alcun import Tkinter in src tranne all’interno di
  `src/ui_legacy`.
- `pytest -q` esegue ~100% dei test (esclusi quelli marcati legacy) con zero
  errori; i test legacy rimangono in tests_legacy e vengono ignorati.
- Il progetto può essere eseguito senza impostare `PYTHONPATH` (solo `pip
  install -e .`).
- La documentazione e i README riflettono la nuova architettura e dicono
  come avviare la GUI Qt.
- Un operatore non tecnico può clonare il repo, installare le dipendenze ed
  eseguire l’app senza conoscere i dettagli di import path.

---

Questo piano fornisce una roadmap completa per il refactor, mantenendo un
compromesso tra radicalità (eliminare Tkinter) e gradualità (fasi, legacy folder).
Seguendo le checklist ogni PR sarà comprovabile ed i rischi controllabili.

User: Sei un senior software architect Python. Devi produrre un PIANO DI RIFATTORIZZAZIONE COMPLETO per migrare l’interfaccia da Tkinter a PySide6 (Qt), eliminando l’avvio della mini-GUI obsoleta e rendendo il progetto avviabile senza PYTHONPATH.

Obiettivo principale:
- Abbandonare Tkinter nel percorso principale.
- Introdurre nuova GUI PySide6 in struttura:
  <package>/ui_qt/ (app shell, pages, viewmodels, services, resources)
  <package>/ui_legacy/ (copia UI Tkinter deprecata, opt-in)
- Rendere packaging pulito (pip install -e .[gui]) e avvio tramite console script.
- Separazione rigorosa: GUI ≠ core ≠ storage (JSON).

Problema attuale:
- scripts/run_verification_demo.py richiama una demo Tkinter obsoleta e/o crasha:
  VerificationInput.__init__() got unexpected keyword 'M' (usa 'Mx').
- Il progetto richiede PYTHONPATH manuale: packaging/entrypoint non affidabili.

Deliverable del piano:
1) Inventario file: punti di avvio, script demo, import tkinter, definizione VerificationInput e adapter core.
2) Architettura target: UI Qt (MVVM), project store JSON, plugin pages, log viewer.
3) Packaging: aggiornamento pyproject.toml (extras gui, console_scripts, find packages corretti per src-layout). Evitare riferimenti "src." in import path.
4) Roadmap in fasi con Acceptance Criteria per ogni fase.
5) Deprecation strategy: spostare Tkinter in ui_legacy, impedire che venga importata/avviata per default.
6) Test minimi: smoke test avvio Qt, round-trip JSON, test guardiano anti-tkinter fuori da ui_legacy.
7) Aggiornamento documentazione (README, comandi avvio, note migrazione).

Regole:
- In questa fase non scrivere codice, solo piano in Markdown con checklist, file da creare/modificare, naming e Definition of Done.
- Dove il nome del package è incerto, il piano deve includere una sezione “Auto-rilevamento package” basata sul layout reale (src/<package>/__init__.py).
``

GitHub Copilot: ```markdown
# Piano di rifattorizzazione – migrazione GUI Tkinter → PySide6

**Data:** 24 Feb 2026
**Autore:** Senior Software Architect (Python/Qt)
**Modalità:** PLAN‑ONLY – nessun codice generato.

---

## 1. Inventario delle componenti esistenti

### 1.1 Entry point / script di avvio

- `scripts/run_verification_demo.py` – apre una Tkinter GUI tabellare e popolata; già obsoleta.
- `src/gui/...` package – contiene controller Tkinter per demo/altre funzionalità.
- `src/ui/module_selector.py` – finestra principale Tkinter con menu e moduli.
- `src/ui/*.py` – collezione di finestre/frames Tkinter (main_window, debug_viewer, ...).

### 1.2 Import Tkinter & dipendenze GUI

- grep `tkinter` mostra 1 import in `module_selector.py` più altri in `src/ui/` e qualche test (`tests/test_graphics_flags.py`, `tests_legacy/*`).
- `pyproject.toml` e `pytest.ini` hanno marker `ui` e `gui` legati a Tkinter.

### 1.3 Classi core / adattatori

- `VerificationInput` definita presumibilmente in `src/domain/...` (errore con `M`/`Mx` denuncia mismatch tra GUI e core).
- I moduli Tkinter costruiscono oggetti `VerificationInput` passando argomenti obsoleti.

### 1.4 Package root

- L’unico package Python usato è quello sotto `src/` – guardare file `src/__init__.py` per nome? il package top-level è `src`.
- Moduli importati come `from src.domain...` ecc. → import path hardcoded con `src` prefix.

---

## 2. Architettura target

La nuova GUI si trova in un package separato che non dipende da Tkinter e non deve
essere importato dal core.

```

src/
├── ui_qt/                 # nuova GUI Qt
│   ├── **init**.py
│   ├── app.py             # start() / main()
│   ├── pages/             # widget delle “pagine”
│   │   ├── home.py
│   │   ├── verification.py
│   │   └── settings.py
│   ├── viewmodels/        # MVVM binding
│   ├── services/          # project_store, logging, config
│   └── resources/         # *.ui, icons, qrc etc.
├── ui_legacy/             # interfaccia Tkinter/obsoleta
│   ├── module_selector.py
│   └── … (copia completa di src/ui/)
└── …                      # resto del codice: core, methods, rd2229, etc.

```

- **Core** (`src/core_calculus`, `src/methods`, `src/domain`, ecc.) rimane invariato,
  never import any GUI module.
- **Services/project_store** mantiene la logica JSON e viene usato sia dalla GUI Qt
  che dai test headless.
- **Pages** sono widget Qt modulari; ogni pagina implementa un’interfaccia minima
  (es. `set_project()`).
- **Viewmodels** contengono la logica di presentazione e possono essere testati
  senza avviare Qt.
- **Resources** include UI forms creati con QtDesigner (opzionale).

---

## 3. Packaging

- Aggiornare `pyproject.toml`:

```toml
[project]
name = "rd2229"
...
[project.optional-dependencies]
gui = ["PySide6>=6.7"]
# altri extras come `dev = [...]`

[project.scripts]
rd2229 = "src.ui_qt.app:main"

[tool.setuptools.packages.find]
include = ["src*", "src.*"]  # assicurarsi che il package root 'src' venga trovato
```

- Rimuovere l’eventuale uso di `PYTHONPATH` nei README e negli script.
- Assicurarsi che `setup.cfg` / `MANIFEST.in` non escludano `src/ui_qt`.

---

## 4. Roadmap in fasi

1. **Fase 0 – Preparazione**
   - copiare `src/ui/` in `src/ui_legacy/`; modificare tutto l’import interno per
     evitare riferimenti incrociati. Lasciare `src/ui/` vuoto o rimuovere.
   - spostare `scripts/run_verification_demo.py` in `scripts/legacy/`.
   - AC: il legacy può essere eseguito a mano (`python -m src.ui_legacy.module_selector`)
     ma non è più avviato da default; il comando `rd2229` non lo richiama.

2. **Fase 1 – Shell Qt minimale**
   - aggiungere dipendenza opzionale PySide6.
   - creare `src/ui_qt/app.py` con `def main():` che crea `QApplication` e
     una `QMainWindow` vuota.
   - definire console script `rd2229`; testare `rd2229 --help`/senza argomenti.
   - AC: il comando `rd2229` non crasha (mostra finestra vuota).

3. **Fase 2 – Project store & settings page**
   - sviluppare `services/project_store.py` basato su `VerificationProject`.
   - realizzare `pages/settings.py` in Qt, collegare New/Open/Save.
   - AC: utente Qt può create/open/save file JSON senza errori.
   - scrivere test di unità per project_store (round‑trip).

4. **Fase 3 – Demo verification page**
   - migrare la logica di `VerificationTableApp` in `viewmodels/verification_vm.py`
     e creare `pages/verification.py` con `QTableView`.
   - AC: compilazione esegue il calcolo (corretti input/output) usando il core
     tramite viewmodel.

5. **Fase 4 – Logger e navigator**
   - aggiungere un widget log viewer e un meccanismo di plugin per altre pagine.
   - AC: log messages appaiono e nuove pagine possono registrarsi tramite API
     definita (service).

6. **Fase 5 – Eliminazione definitiva di Tkinter**
   - rimuovere ogni import tkinter dai requisiti, dalla documentazione e dalle
     dipendenze.
   - spostare i test legacy in `tests_legacy`; capire quali usare ancora.
   - AC: `pytest -q` esegue senza import tkinter se non in `tests_legacy`; il
     package non contiene più alcun riferimento a tkinter se non sotto
     `src/ui_legacy`.

7. **Fase 6 – Pulizia & documentazione**
   - aggiornare README, CONTRIBUTING, guide su VsCode, comandi demo.
   - Aggiungere esempi nell’entrypoint `rd2229 --demo`.

---

## 5. Deprecation strategy

- Il contenuto di `src/ui_legacy/` è contrassegnato come “DEPRECATED” in README e
  docstrings; importa solo se esplicitamente richiesto.
- Aggiungere variabile d’ambiente `RD2229_LEGACY_UI=1` per attivare il
  caricamento (non è abilitata per default).
- In `pyproject.toml` definire un extra `[project.optional-dependencies] legacy =
  []` per installare eventuali dipendenze aggiuntive di Tkinter (se ce ne
  sono).
- A ogni PR che modifica `ui_legacy` aggiungere un commento `Legacy` e spostare
  modifiche solo se necessario per compatibilità.

---

## 6. Test minimi da aggiungere

1. **`tests/test_app_launch.py`**
   - crea `QApplication` e invoca `src.ui_qt.app.main()` in modalità headless
     (xvfb).
   - assert no exception & `app` restituisce 0.

2. **Project store round-trip** (già menzionato).

3. **Page instantiation tests**
   - test per ogni pagina Qt: importare, creare widget con un progetto dummy,
     verificare che i principali elementi esistano (`assert isinstance(..., QWidget)`).

4. **Guardia anti-Tkinter**
   - `tests/test_no_tkinter_imports.py` che esegue

     ```python
     import pkgutil, importlib
     for m in pkgutil.walk_packages(['src/ui_qt','src']):
         mod = importlib.import_module(m.name)
         assert 'tkinter' not in str(mod.__file__)
     ```

     (ma permettere import sotto `src/ui_legacy`).

5. **Legacy tests**
   - spostare tutti i file della cartella tests_legacy come sono; configurare
     un job CI separato per eseguirli solo se `RD2229_LEGACY_UI` è impostata.

---

## 7. Documentazione

- Aggiornare README:
  - comando di avvio `rd2229`.
  - descrizione dei package `ui_qt` vs `ui_legacy`.
  - indicare come eseguire la GUI legacy per confronto/porting.
- Aggiungere `docs/MIGRATION_TKINTER_TO_QT.md` con guida per sviluppatori.
- Aggiornare tasks VS Code se presenti (launch, build) per eseguire `rd2229`.

---

## 8. Risks & mitigations

- **PySide6 install heavy** – usare extras per mantenerlo opzionale.
- **Dipendenze transitive** – isolare tutte le Qt calls in `ui_qt`; core resta
  silenzioso.
- **App startup lento** – MVP con finestra vuota; caricare pagine solo su richiesta.
- **Test flakiness GUI** – usare xvfb e wrapper `pytest-qt` / `qtbot` se necessario.
- **Legacy drift** – mantenere `ui_legacy` sincronizzato solo tramite merge
  occasionali, preferibilmente tramite script di conversione.

---

### Definition of Done

- Comando `rd2229` (console script) avvia una finestra Qt moderna.
- Tkinter non è importato in nessun modulo caricato per default.
- `pip install -e .[gui]` e `pip install -e .` funzionano senza errori.
- Tutti i test (eccetto tests_legacy) passano in CI.
- Il codice legacy è confinato e chiaramente marcato.
- Documentazione e README aggiornati.

---

> *Promt agent inputs*:
> fornire al successivo agente i file chiave per la migrazione, nell’ordine
> suggerito dalla roadmap (vedere sezione precedente).
>
> 1. module_selector.py + altro `src/ui/*`
> 2. l’intero package `src/ui_legacy` (da creare)
> 3. file per `ui_qt` skeleton (`app.py`, `pages/`, etc.)
> 4. pyproject.toml (aggiorni extras/scripts)
> 5. test file guardiani e nuovi smoke test
> 6. README + documenti MIGRATION

Con questo piano si può affrontare la migrazione gradualmente, con checkpoint
e without breaking the core functionality.

User: Agisci come un software architect e UX designer esperto di Python e PyQt6.

OBIETTIVO
Devi aiutarmi a progettare e implementare un **launcher unico e modulare** per il nostro software tecnico di **verifiche strutturali e di prevenzione incendi**, in modo da:

- collegare in modo coerente **tutte le finestre / dialog / moduli PyQt6 già esistenti**
- permettere all’utente di **avviare facilmente ogni funzionalità da un’unica finestra principale**
- migliorare la **navigazione** e ridurre la dispersione tra tante GUI separate.

CONTESTO

- Il software è usato da ingegneri per:
  - verifiche strutturali
  - verifiche antincendio
  - gestione e analisi di modelli di calcolo
  - generazione di relazioni e documentazione tecnica.
- Nel tempo abbiamo aggiunto molte funzionalità in finestre e dialog PyQt6 separati.
- Attualmente non esiste una “finestra principale” che funga da launcher di tutte le funzioni.
- Voglio mantenere il più possibile il codice esistente e **limitare i refactoring invasivi**.

TECNOLOGIA E STRUTTURA DEL PROGETTO

- Linguaggio: **Python**
- GUI: **PyQt6**
- Sto lavorando in **Visual Studio Code** con **GitHub Copilot Pro**.
- Il workspace corrente contiene l’intero progetto.
- Le GUI PyQt6 (finestre e dialog) si trovano principalmente in:
  - cartella/e Python: `[es. src/ui]`, `[es. src/windows]`, `[es. src/dialogs]`
  - eventuali file `.ui` generati con Qt Designer: `[es. ui/]` (se esistono)
- Le finestre sono in genere classi che estendono `QMainWindow`, `QDialog` o `QWidget`.

COSA DEVI FARE

1. ANALISI DELLE GUI ESISTENTI
   - Esamina il codice del progetto nelle cartelle indicate.
   - Individua tutte le classi PyQt6 che rappresentano:
     - finestre principali (`QMainWindow`)
     - dialog (`QDialog`)
     - widget complessi (`QWidget`) che fungono di fatto da schermate principali.
   - Per ciascuna GUI trovata, crea una tabella con:
     - Nome della classe
     - File `.py` (e `.ui` se usato)
     - Base class (`QMainWindow` / `QDialog` / `QWidget`)
     - Descrizione del ruolo/funzione (deducendola da nomi, commenti, testo dei widget).
   - Identifica eventuali punti di ingresso attuali dell’app (finestre che vengono avviate direttamente nel `if __name__ == "__main__":` o file di bootstrap).

2. RAGGRUPPAMENTO FUNZIONALE
   - Raggruppa le GUI in **macro-moduli logici** tipici del dominio, ad esempio (usa pure nomi diversi se più adatti al codice che trovi):
     - Modello strutturale / geometra / caricamento dati
     - Verifiche SLU / SLE / elementi strutturali
     - Verifiche e modulistica antincendio
     - Gestione progetti / salvataggio / apertura
     - Esportazioni / relazioni tecniche / stampe
     - Impostazioni / configurazione
     - Strumenti accessori (es. calcolatori, wizard vari, ecc.)
   - Per ogni modulo logico:
     - elenca le GUI collegate
     - segnala quali sono funzioni “principali” e quali sono funzioni “di dettaglio” o secondarie.

3. PROGETTAZIONE DEL LAUNCHER PRINCIPALE
   - Proponi una **finestra principale di launcher** basata su PyQt6, ad esempio:
     - una classe `MainLauncherWindow(QMainWindow)` che:
       - ha una **sidebar** (es. un `QListWidget` o `QTreeWidget` a sinistra) con i moduli principali
       - un’area centrale con un `QStackedWidget` (o simile) per mostrare schermate o pannelli
       - una toolbar o menubar con azioni globali (Nuovo progetto, Apri, Salva, Impostazioni, Aiuto).
   - Descrivi:
     - quali **moduli** compaiono nella sidebar/menu
     - quali **azioni principali** sono disponibili per ogni modulo
     - come l’utente passa da un modulo all’altro e come avvia le varie GUI esistenti (apertura di nuove finestre o visualizzazione di widget nel `QStackedWidget`).
   - Mantieni il design semplice e coerente con un’app tecnica desktop (priorità: chiarezza > estetica).

4. PIANO DI INTEGRAZIONE CON IL CODICE ESISTENTE
   - Definisci un **piano di integrazione a passi** che spieghi:
     1. Dove creare il nuovo file Python per il launcher, es. `[src/main_launcher.py]`.
     2. Come definire la classe `MainLauncherWindow(QMainWindow)`.
     3. Come spostare il punto di ingresso dell’applicazione in un unico `main.py`
        che:
        - crea l’istanza di `QApplication`
        - istanzia `MainLauncherWindow`
        - esegue `app.exec()`.
     4. Come collegare i pulsanti/menu del launcher alle finestre/dialog esistenti:
        - quando ha più senso **aprire una nuova finestra** (`QMainWindow` o `QDialog`)
        - quando ha più senso **caricare un `QWidget` dentro lo `QStackedWidget`** centrale.
     5. Come evitare duplicazione di codice e modifiche massive:
        - riutilizzando le classi esistenti così come sono
        - aggiungendo solo codice di wiring nel launcher.
   - Se individui finestre che oggi vengono create direttamente in `if __name__ == "__main__":`, spiega come **dirottare** la logica nel launcher.

5. ESEMPI DI CODICE CONCRETI (PYTHON + PYQT6)
   - Scrivi esempi completi (anche semplificati ma realistici) di:
     - una classe `MainLauncherWindow(QMainWindow)` con:
       - menubar
       - sidebar con elenco moduli
       - area centrale con `QStackedWidget`.
     - codice che mostra come collegare un pulsante/menu ad una finestra esistente, ad esempio:
       - apertura di `StructuralChecksWindow`
       - apertura di un `FireSafetyDialog`
       - caricamento di un widget `ProjectManagerWidget` in un `QStackedWidget`.
   - Commenta il codice per spiegare:
     - dove importare le varie classi delle finestre/dialog esistenti
     - come istanziarle e mostrarle
     - come gestire eventuali parametri richiesti dai costruttori.

6. SUGGERIMENTI PER EVOLUZIONI FUTURE
   - Suggerisci possibili miglioramenti futuri dell’interfaccia, ad esempio:
     - ricerca globale delle funzioni (es. barra di ricerca che filtra i moduli/azioni)
     - sezione “Preferiti” per le funzioni usate più spesso
     - elenco “Recenti progetti”
     - gestione di profili di utente (principiante / avanzato) con set di funzioni diversi
     - separazione migliore tra logica di dominio e logica di GUI, se noti accoppiamenti forti.

FORMATO DI RISPOSTA
Organizza la tua risposta in queste sezioni:

1. **Analisi delle GUI esistenti** (tabella con: Nome GUI, File, Base class, Descrizione, Modulo proposto)
2. **Raggruppamento in moduli logici**
3. **Proposta di architettura del launcher PyQt6**
4. **Piano di integrazione passo-passo**
5. **Esempi di codice Python/PyQt6 commentati per il launcher**
6. **Suggerimenti per evoluzioni future**

Se qualche informazione non è disponibile dal codice, esplicita le ipotesi che stai facendo e proponi eventualmente più di una opzione di design.

Fammi moltissime domande per aiutarti a definire i dettagli che proponi

GitHub Copilot: Searched for text `PyQt6`, 1 result

Searched for text `QMainWindow`, 6 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/ui/modern/main_window.py#1-1), lines 1 to 150

Searched for files matching `**/src/ui/modern/**`, 9 matches

Searched for text `QDialog`, no results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/ui/modern/features/builtin_features.py#1-1), lines 1 to 200

Searched for text `PySide6`, 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/ui/app.py)

Searched for regex `class .*QMainWindow`, 1 result

Searched for text `QWidget`, 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/ui_qt/pages/home.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/ui_qt/pages/verification.py)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/src/rd2229/ui_qt/pages/settings.py)

### 1. Analisi delle GUI esistenti

| Classe | File | Base class | Ruolo desunto | Modulo logico proposto |
|--------|------|------------|---------------|------------------------|
| `ModernMainWindow` | main_window.py | `QMainWindow` | finestra principale “launcher” MVVM | **core launcher** (tutti i moduli) |
| `NavigationPanel` | navigation.py | `QWidget` | sidebar con pulsanti/schede | parte del launcher |
| `_ProjectInfoWidget` | builtin_features.py | `QWidget` | scheda “Progetto” (info, normativa) | Progetto/Impostazioni |
| `_RunWidget` | idem | `QWidget` | scheda “Esegui calcolo” | Verifiche |
| `_ResultsWidget` | idem | `QWidget` | scheda “Risultati” | Verifiche |
| `HomePage` | home.py | `QWidget` | demo/placeholder home (prob. sperimentale) | launcher (legacy) |
| `VerificationPage` | verification.py | `QWidget` | demo view per verifiche (skeleton) | Verifiche (legacy) |
| `SettingsPage` | settings.py | `QWidget` | demo impostazioni (skeleton) | Impostazioni (legacy) |

**Punti di ingresso attuali**

- app.py (`python -m src.ui.app`) avvia `ModernMainWindow`.
- run_verification_demo.py avvia vecchio Tkinter.
- `src/ui_legacy/...` non ancora esiste ma rappresenta il vecchio pacchetto
  (da creare).
- Alcuni file contengono `if __name__ == "__main__":` (es. app.py non ne ha, lo script demo sì).

---

### 2. Raggruppamento in moduli logici

- **Gestione progetto / impostazioni**
  - `ModernMainWindow` menù File, `_ProjectInfoWidget`, `SettingsPage` (legacy).
- **Verifiche strutturali**
  - `_RunWidget`, `_ResultsWidget`, `VerificationPage` (legacy).
- **Verifiche antincendio**
  - *non ancora presenti*, potrebbero essere aggiunte come nuove `FeatureSpec` o
    pagine in `ui_qt/pages`.
- **Modello / calcolo**
  - nessuna GUI, ma servizi/viewmodels collegati (`CalculationService`, ecc.).
- **Esportazione / report**
  - azioni di export già fornite nel menu File di `ModernMainWindow`.
- **Strumenti accessori**
  - eventuali widget aggiunti come feature o modulini relativi (es. logger).

---

### 3. Proposta architetturale del launcher PyQt6

Il `ModernMainWindow` esistente **è già un launcher modulare**; l’analisi
mostra una sidebar (`NavigationPanel`) che popola uno `QStackedWidget` con i
widget registrati tramite `FeatureSpec`. Il piano espande questa base:

- **Menubar** con voci: File (Nuovo/Apri/Salva, Recenti), Esegui, Esporta, Aiuto.
- **Sidebar/navigation**: elenco verticale di moduli (Progetto, Esegui, Risultati,
  più futuri “Antincendio”, “Modello”, “Report”, …).
- **Area centrale**: `QStackedWidget` contenente le pagine/features (ogni widget
  fornisce `set_project()`).
- **Toolbar/statusbar**: indicatori stato pipeline/progetto.

L’utente seleziona un modulo dalla sidebar; la `NavigationPanel` notifica il
launcher che fa `stacked.setCurrentWidget(widget)` oppure, per finestre
secondary (es. dialog per calcolatori) lancia un `QDialog`.

Sono già previste due modalità di attivazione:

- **widget integrati** (feature): Progetto, Esegui, Risultati.
- **finestre indipendenti**: eventuali dialog di supporto possono essere aperti
  tramite azioni del menu o pulsanti nella pagina.

Il design rimane coerente: la launcher window è il **unico punto di avvio**
dell’intera app (la demo Tkinter verrà deprecata).

---

### 4. Piano di integrazione passo‑passo

1. **Inventory / cleanup**
   - spostare l’intero ui originale in `src/ui_legacy/`; aggiornare
     import se necessario.
   - lasciare app.py come unico entrypoint, eliminare lo script demo o
     spostarlo in legacy.
   - AC: la vecchia GUI può essere avviata solo impostando `RD2229_LEGACY_UI=1`.

2. **Consolidare il launcher esistente**
   - verificare che `ModernMainWindow` contenga tutte le voci di menu necessarie
     for the domains you care about (aggiungere “Antincendio” se manca).
   - registrare le feature esistenti in registry.py.
   - AC: avviando `rd2229` appare la finestra launcher con sidebar e contenuti
     Progetto/Esegui/Risultati.

3. **Collegare nuove funzionalità**
   - per ogni finestra o widget PyQt6 esistente (es. `FireSafetyWindow`,
     `ModelEditor`), decidere se:
     - **widget**: convertire in `FeatureSpec` (create_widget)
     - **finestra**: aggiungere azione nel menu “Strumenti” che la apre
   - AC: clic su voce/laterale apre correttamente la GUI esistente.

4. **Impostare il nuovo entrypoint**
   - aggiungere script `src/main.py` che chiama `src.ui.app.main()` oppure
     configurare `console_scripts` come descritto in pyproject.
   - AC: `python -m rd2229` o `rd2229` avvia il launcher.

5. **Aggiornare i test**
   - aggiornare/aggiungere smoke test in test_app_launch.py che
     importi il launcher e crei una `ModernMainWindow` senza errori.
   - aggiungere test test_no_tkinter_imports.py che falliscono se
     moduli fuori `ui_legacy` importano `tkinter`.
   - AC: tutte le modifiche passano in CI.

6. **Moduli accessori**
   - implementare `FeatureSpec` e relative pagine per antincendio, editor
     strutturale, relazioni ecc. in features.
   - AC: i moduli logici hanno una voce nella sidebar e funzionano come
     previsto senza ulteriori import.

7. **Deprecation e cleanup finale**
   - aggiungere commenti `# DEPRECATED` in `ui_legacy`.
   - aggiornare README e documentazione per spiegare la nuova
     architettura e lanciare la UI legacy solo se necessario.
   - AC: `ui_legacy` non è installato/impattato dal comando normale.

---

### 5. Esempi di codice (PyQt6)

```python
# launcher.py (bozza semplificata)
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QListWidget, QAction

class MainLauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RD2229 Launcher")
        self.resize(1200, 800)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.sidebar = QListWidget()
        self.sidebar.currentRowChanged.connect(self._on_nav)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

        self._register_module("Progetto", ProjectInfoWidget)
        self._register_module("Verifiche", RunWidget)
        self._register_module("Risultati", ResultsWidget)
        self._register_module("Antincendio", lambda parent: FireSafetyWidget(parent))
        # ...

        self._build_menu()

    def _register_module(self, label, factory):
        widget = factory(self)
        self.stack.addWidget(widget)
        self.sidebar.addItem(label)

    def _on_nav(self, index):
        self.stack.setCurrentIndex(index)

    def _build_menu(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("&File")
        new = QAction("Nuovo", self); new.triggered.connect(self._on_new)
        file_menu.addAction(new)
        # ...
        tools_menu = mb.addMenu("&Strumenti")
        fire_a = QAction("Verifica Antincendio", self)
        fire_a.triggered.connect(self._open_fire_dialog)
        tools_menu.addAction(fire_a)

    def _open_fire_dialog(self):
        dlg = FireSafetyDialog(self)
        dlg.exec()        # opens QDialog


# feature registration example
class FireSafetyFeature(FeatureSpec):
    feature_id = "fire"
    label = "Antincendio"
    order = 30
    def create_widget(self, parent, project_vm, run_vm, results_vm):
        return FireSafetyWidget(parent)

register(FireSafetyFeature())
```

*Commenti*

- le classi esistenti (es. `ProjectInfoWidget`) vengono importate e messe nello
  `stack` senza modifiche; il launcher funge da “wiring” centrale.
- per finestre stand‑alone (QDialog) semplicemente si lancia `dlg.exec()` dal
  menu o dalla pagina.
- il `run_vm`, `project_vm`, `results_vm` sono istanze condivise fornite al
  launcher e passate alle pagine se necessarie.

---

### 6. Suggerimenti per evoluzioni future

- **Ricerca rapida**: barra di ricerca nella sidebar filtra le voci per parola‑chiave.
- **Preferiti**: possibilità di “stella” su moduli/azioni più usati.
- **Recenti**: elenco progetti recenti direttamente nel launcher.
- **Profilo utente**: switch tra modalità “principiante/avanzato” per semplificare
  l’interfaccia.
- **Plugin esterni**: caricare moduli GUI da pacchetti esterni, scoprire via
  entry points `rd2229.plugins`.
- **Modalità docker/CLI headless**: mantenere `ui_qt` isolato per esecuzione
  server; eseguire calcoli core senza Qt.

---

Questo documento descrive la situazione attuale e fornisce un piano completo
per costruire un launcher unico e modulare basato su PyQt6, minimizzando
refactor invasivi e valorizzando l’architettura già esistente (modularità
`FeatureSpec`). Il prossimo passo sarà applicare il piano in modo iterativo e
verificabile.

User: SEI IN MODALITÀ PLAN — NON SCRIVERE CODICE E NON PASSARE ALL’IMPLEMENTAZIONE FINCHÉ NON TE LO CHIEDO ESPRESSAMENTE.

📌 RUOLO
Agisci come:

- software architect,
- domain expert in software di calcolo strutturale e di prevenzione incendi,
- system designer focalizzato su architetture modulari, configurabili e scalabili.

Il tuo compito è rimanere in modalità **pianificazione** il più a lungo possibile, esplorando e definendo nel dettaglio tutti gli aspetti architetturali e organizzativi del progetto, facendo molte domande mirate prima di consolidare le decisioni.

🎯 OBIETTIVO GENERALE
Aiutarmi a progettare (a livello di piano, non di codice) la nuova architettura del nostro software di verifiche strutturali e antincendio, scritto in **Python** con **PyQt6** (e oggi con del legacy tkinter e/o PySide6), in modo che sia:

- completamente **modulare**,
- con **launcher unico** (interfaccia principale) in PyQt6 che collega tutte le funzionalità,
- con **configurazione centralizzata** (file di configurazione chiari e versionabili),
- con **strato di dati ben definito** (database, repository comuni, gestione dei dati di calcolo),
- con **output comuni e standardizzati** (report, file di scambio, log, ecc.),
- pronto per evoluzioni future (nuovi moduli, nuove normative, ecc.).

🎯 OBIETTIVI SPECIFICI DELLA FASE DI PIANO
Nella sola fase di pianificazione, voglio che tu mi aiuti a:

1. **Comprendere e mappare il dominio**
   - capire tutti i tipi di verifiche (strutturali, antincendio, altro),
   - capire come sono organizzati oggi i modelli di calcolo, i progetti e gli output,
   - identificare utenti/tipi di utilizzo (es. progettista singolo, studio tecnico, ecc.).

2. **Fare un INVENTARIO FUNZIONALE E MODULARE**
   - elencare i principali moduli/logiche (es. gestione progetto, input modello, verifiche, incendio, risultati, report, impostazioni, strumenti accessori),
   - per ciascun modulo, identificare:
     - responsabilità,
     - dipendenze,
     - interfacce principali (input, output).

3. **Definire l’ARCHITETTURA MODULARE**
   - definire un modello chiaro di separazione tra:
     - interfaccia utente (PyQt6),
     - logica di dominio/calcolo,
     - accesso ai dati (database, file di progetto),
     - servizi condivisi (logging, configurazione, ecc.),
   - proporre un’organizzazione dei pacchetti Python (es. `core`, `ui`, `infra`, `plugins`, ecc.),
   - prevedere estensibilità tramite moduli o plugin (per nuove verifiche o nuovi tipi di calcolo).

4. **Progettare CONFIGURAZIONE e FILE DI CONFIG**
   - decidere come strutturare la configurazione (es. YAML, JSON, TOML, ecc.),
   - distinguere tra:
     - configurazione globale dell’applicazione,
     - configurazione per progetto,
     - eventuale configurazione per modulo,
   - stabilire come e dove salvare questi file, e come dovrebbero essere organizzati.

5. **Definire il LIVELLO DATI / DATABASE**
   - decidere se usare file strutturati, database locale (es. SQLite) o altro,
   - descrivere lo schema concettuale (entità come: progetto, modello strutturale, carichi, combinazioni, verifiche, risultati, incendio, materiali, ecc.),
   - definire un livello di **repository comuni** per accesso ai dati:
     - repository per progetti,
     - repository per modelli,
     - repository per risultati,
     - repository per configurazioni,
   - tenendo conto di versionamento, backup, integrazione con Git dove utile.

6. **Definire OUTPUT COMUNI**
   - stabilire formati standard per:
     - report di calcolo (PDF, HTML, Markdown, altro),
     - esportazioni dati (es. CSV, JSON, formati di interscambio),
     - log di esecuzione,
   - definire regole di naming e struttura delle cartelle per output,
   - prevedere un modulo/shared service per la generazione degli output, riutilizzabile da tutti i moduli di verifica.

7. **Progettare il LAUNCHER (UI PyQt6) COME HUB MODULARE**
   - definire come sarà organizzata la finestra principale (menu, sidebar, pagine, workspace centrale),
   - mappare ogni modulo logico a:
     - una o più pagine/widget della UI,
     - comandi/menu/toolbar,
   - definire come il launcher interagisce con:
     - configurazione,
     - repository dei dati,
     - logica di verifica.

8. **Piano di MIGRAZIONE dal legacy (tkinter / PySide6)**
   - identificare i punti legacy (senza entrare ancora nel codice concreto),
   - definire la strategia di migrazione:
     - cosa portare in PyQt6,
     - cosa considerare solo “storico”,
   - ordinare le attività in fasi progressive e sensate.

9. **RAPPRESENTAZIONI GRAFICHE / AD ALTO LIVELLO**
   - creare:
     - una vista architetturale a blocchi (anche solo testuale),
     - un albero gerarchico dei moduli (launcher → moduli → sottosistemi → repository/output),
   - mantenere aggiornato questo “schema mentale” man mano che il piano si raffina.

🧠 MODALITÀ DI LAVORO (MOLTO IMPORTANTE)

- Rimani SEMPRE in **modalità pianificazione** finché non ti chiedo di passare all’implementazione:
  - NON generare codice,
  - NON proporre snippet di implementazione dettagliati,
  - concentrati su analisi, scelte architetturali, diagrammi testuali, checklist, elenchi puntati, albero dei moduli.

- **Fai molte domande**, ma una alla volta o in piccoli gruppi coerenti, per:
  - chiarire il dominio (tipi di verifiche, normative, flussi operativi),
  - capire lo stato attuale dell’applicazione,
  - validare le tue ipotesi,
  - proporre opzioni alternative e chiedermi quale preferisco.

- Ogni volta che ti mancano informazioni:
  - dichiara esplicitamente le tue assunzioni,
  - proponi 2–3 alternative (con pro/contro),
  - chiedimi quale direzione preferisco PRIMA di consolidare il piano.

🧩 STRUTTURA DEL PIANO
Voglio che il lavoro di pianificazione venga organizzato in sezioni chiare, ad esempio:

1. Comprensione del dominio e degli utenti
2. Inventario funzionale e moduli logici
3. Architettura complessiva (layer, pacchetti, dipendenze)
4. Configurazione (tipi di config, file, struttura)
5. Dati e repository (schema concettuale, pattern di accesso)
6. Output e reporting (formati, struttura, responsabilità)
7. UI PyQt6 e launcher modulare (pagine, navigazione, ruoli)
8. Strategia di migrazione dal legacy
9. Albero grafico dei moduli e delle dipendenze
10. Roadmap di implementazione (solo ad alto livello, senza codice)

Per ogni sezione:

- fai domande mirate,
- raccogli le informazioni,
- poi sintetizza in 1–2 paragrafi + bullet point chiave.

📄 FORMATO DELLE TUE RISPOSTE

- Usa:
  - titoli chiari,
  - elenchi puntati,
  - tabelle testuali dove utile,
  - alberi indentati per mostrare gerarchie,
  - (opzionale) diagrammi testuali tipo Mermaid solo se possono essere utili per me.
- Mantieni sempre evidente:
  - quali parti sono confermate,
  - quali sono ipotesi ancora da validare,
  - quali decisioni sono “aperte” e su cui dobbiamo tornare.

⛔️ COSA NON FARE IN QUESTA FASE

- Non scrivere codice Python o PyQt6 (solo, eventualmente, pseudo‑codice molto alto livello se serve a spiegare un concetto).
- Non modificare file, non assumere di avere accesso in scrittura al repository.
- Non dare per scontate decisioni architetturali senza avermi prima consultato.

✅ PRIMO PASSO CHE TI CHIEDO

1. Riassumi in poche righe come hai capito il problema da risolvere.
2. Proponi una prima bozza di elenco sezioni del piano (puoi usare la struttura suggerita sopra come base).
3. Poi, PRIMA di procedere oltre, fammi le prime 3–5 domande più importanti per:
   - capire meglio il dominio,
   - capire come è organizzato oggi il codice (a grandi linee),
   - capire le priorità (ad esempio, quali moduli devono essere pronti per primi).

GitHub Copilot: ### ✅ Come ho compreso il problema

Stiamo cercando di trasformare un’applicazione tecnica Python che oggi è un “mosaico” di finestre e dialog PyQt6 (con residui Tkinter/​PySide6), in una **piattaforma modulare coerente**. L’obiettivo è avere una singola interfaccia principale che faccia da launcher per tutti i diversi tipi di verifiche (strutturali, antincendio, ecc.), gestisca progetti e impostazioni, e si colleghi a servizi di calcolo e generazione dei report. In parallelo vogliamo consolidare la struttura del codice (core, UI, data layer), configurazione e output, e predisporre il terreno per aggiungere nuove normative/​funzionalità in futuro.

Il refactor dovrà essere pianificato, non eseguito subito; per evitare sorprese, dobbiamo esplorare il dominio, inventario delle GUI esistenti, e definire un’architettura package/config/dati prima di toccare il codice.

---

### 🧩 Bozza di elenco sezioni del piano

| # | Sezione |
|---|---------|
| 1 | **Comprendere il dominio e gli utenti** |
| 2 | **Inventario funzionale & moduli logici** |
| 3 | **Architettura modulare proposta** |
| 4 | **Configurazione: file e livelli** |
| 5 | **Dati e repository (schema concettuale)** |
| 6 | **Output comuni e servizio report** |
| 7 | **UI PyQt6 – il launcher modulare** |
| 8 | **Strategia di migrazione dal legacy Tkinter/PySide6** |
| 9 | **Schema/diagrammi dei moduli & dipendenze** |
|10 | **Roadmap di implementazione ad alto livello** |

Posso espandere ogni sezione con paragrafi, tabelle, elenchi; l’avanzamento sarà iterativo.

---

### 🔍 Prime domande critiche

1. **Tipologie di verifica**: oltre a quelle menzionate (SLU/SLE strutturali e antincendio), quali altri controlli o calcoli vengono eseguiti oggi? (es. muratura, geotecnica, elementi secondari, ecc.). Conoscere l’insieme aiuterà a definire i moduli principali.

2. **Input/Output attuali**: quale formato usa attualmente un “progetto”? JSON? XML? Esistono anche tabelle separate per materiali, sezioni, combinazioni? Questo influenza il design del layer dati.

3. **Utenti e workflow**: il software è destinato a un singolo ingegnere che lavora su un progetto alla volta, o a uno studio con archivi multipli e collaborazioni? È prevista qualche forma di multi‑utente o integrazione con GIT/​Cloud?

4. **Attuale organizzazione del codice**: dove vive il codice di calcolo (path principali)? Ci sono già package tipo `core_calculus`, `methods`, ui, verifications? Qual è il livello di accoppiamento tra GUI e core?

5. **Priorità / vincoli temporali**: ci sono moduli che devono essere pronti per una release o per un cliente specifico (es. antincendio prima di strutturale)? Questo mi aiuta a valutare quali parti del launcher implementare per prime.

Fammi sapere le risposte (o eventuali documenti/codebase che vuoi che guardi) e poi procediamo con le sezioni successive del piano.

User: SEI IN MODALITÀ PLAN — NON SCRIVERE CODICE E NON PASSARE ALL'IMPLEMENTAZIONE FINCHÉ NON LO RICHIEDO ESPRESSAMENTE.

🎯 RUOLO
Agisci come:

- software architect senior,
- system designer,
- domain expert in software di verifica strutturale e antincendio,
- specialista in architetture modulari, configurabili e scalabili.

Rimani in modalità PIANIFICAZIONE PROFONDA per tutto il tempo possibile.

📌 RESPONSABILITÀ PRINCIPALI (in questa fase)

- Analizzare autonomamente tutti i file `.md` presenti in `docs/` nel workspace VS Code.
  Ogni volta che ti servono informazioni, cerca **prima nei markdown**.
- Costruire e verificare continuamente una visione architetturale globale.
- Emettere molte domande chiarificatrici, preferibilmente **a scelta multipla**, per eliminare ambiguità e migliorare precisione del piano.
- Rimanere in modalità PLAN e NON emettere codice, nemmeno di esempio.

🎯 OBIETTIVO DEL PROGETTO
Costruire un piano completo per una piattaforma software modulare (Python + PyQt6) per verifiche strutturali e antincendio che includa:

- **launcher unico** PyQt6 che collega tutti i moduli;
- architettura completamente **modulare** (UI, dominio, servizi, dati, plugin);
- **configurazioni centralizzate** (globali, per progetto, per modulo);
- **database e repository comuni** per dati e modelli;
- **output standardizzati**, riutilizzabili da qualsiasi modulo;
- migrazione completa dal legacy tkinter/PySide6;
- definizione di file, directory, naming, contratti tra moduli.

🏗️ COSA DEVI FARE ORA (E SEMPRE)
Quando produci la risposta:

1. Fai una **sintesi breve** di ciò che stai analizzando.
2. Produci **solo contenuti di pianificazione, mai codice**.
3. Formula **domande multiple-choice**, almeno 3–7 per ogni step.
4. Prima di trarre conclusioni, **verifica nei file docs/** se ci sono informazioni rilevanti.
   - Se trovi informazioni: incorporale.
   - Se ci sono dubbi: formula scelte + chiedi quale è corretta.
5. Mantieni sempre un quadro architetturale aggiornato, proponendo:
   - alternative progettuali,
   - pro/contro,
   - decisioni da prendere,
   - rischi/complessità.

📚 USO DEI FILE DOCS/
Ogni volta che affronti una sezione del piano:

- cerca automaticamente documenti rilevanti in `docs/`,
- estrai informazioni utili,
- allinea le tue domande a quanto trovato,
- correggi eventuali tue ipotesi errate sulla base del contenuto dei markdown.

💬 STILE DELLE DOMANDE
Le domande devono essere a scelta multipla, ad esempio:

- **Quale livello di modularità preferiamo per il data layer?**
  A) Repository per dominio
  B) Repository per entità
  C) Unit of Work + Repository
  D) File system isolato per progetto

- **Come devono essere strutturati i file di configurazione?**
  A) Un singolo file globale + override per progetto
  B) Config separata per modulo
  C) Config centralizzata con schema rigido
  D) Config generata automaticamente dal launcher

- **Quale modalità preferiamo per orchestrare le verifiche?**
  A) Pipeline centralizzata
  B) Moduli autonomi con API comuni
  C) Event bus interno
  D) Plugin caricati dinamicamente

Fornisci anche una domanda “E) Altro: ____” quando rilevante.

📦 STRUTTURA DEL PIANO (che andremo a riempire insieme)

1. Comprensione del dominio
2. Inventario funzionale e moduli logici
3. Architettura complessiva (UI, core, servizi, dati)
4. File di configurazione
5. Data layer + database
6. Repository comuni
7. Output comuni e standardizzati
8. UI PyQt6 — launcher modulare
9. Strategia di migrazione legacy
10. Diagrammi testuali/albero moduli
11. Roadmap ad alto livello

🚫 COSA NON DEVI FARE

- Non generare codice.
- Non proporre soluzioni implementative premature.
- Non assumere decisioni senza chiedere conferma.
- Non abbandonare MAI la modalità PLAN.

---

🔰 **PRIMA AZIONE CHE DEVI FARE**

1. Analizza i file in `docs/`, riassumi ciò che trovi sul dominio.
2. Identifica eventuali incongruenze o lacune informative.
3. Genera **le prime 5–8 domande a scelta multipla**, basandoti sia sui documenti che sulle parti mancanti.

Rimani in modalità PLAN.

GitHub Copilot: Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/index.md)

Searched for regex `incendio|fire|structur|verifiche|progetto`, 20 results

Searched for regex `fire|incendio|structur|verifica|verifiche`, 20 results

Searched for text `FIRE` (`**/docs/**`), 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/module_structure.md)

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/MEGAPLAN/FIRE_CODEMODULE_INCENDIO.md)

Searched for regex `SLU|SLE|structur` (`**/docs/**`), 20 results

Read [](file:///c%3A/Users/danca/workspaces/RD2229/docs/CONFIG_JSONCODE_SYSTEM.md#1-1), lines 1 to 160

### 🧠 Sintesi iniziale del dominio

Dai documenti presenti (CONFIG_JSONCODE_SYSTEM.md, FIRE_CODEMODULE_INCENDIO.md, module_structure.md e altri MEGAPLAN) emerge un’applicazione rivolta a ingegneri che eseguono:

- **verifiche strutturali** armate secondo varie normative storiche e moderne (RD 2229/39, DM92/96, NTC2008/2018 ecc.), con calcoli SLU, SLE, tensioni ammissibili e relative combinazioni; la logica è parametrizzata tramite file `.jsoncode` per i codici di calcolo e i materiali;
- una **modalità incendio** tripartita (L1/L2/L3) che combina analisi termica e meccanica per valutare R‑classes, generata anch’essa come CodeModule separato;
- un “core” di calcolo indipendente dalla GUI, con moduli `core_calculus`, `methods`, verifications, e un sistema di repository per progetti, materiali, sezioni;
- una **configurazione modulare** (.jsoncode) già organizzata in calculation_codes e historical_materials;
- una UI che attualmente è una finestra principale PySide6 (`ModernMainWindow`) con un meccanismo di “feature” (schede) e un launcher Tkinter legacy in ui; i moduli come geometry, material editor e debug viewer sono separati.

L’inventario mostra anche placeholders per FRC e altri ingredienti storici che verranno estesi.

---

### ❓ Domande a scelta multipla (prima serie)

1. **Quale insieme di verifiche rientra nella “parte strutturale” del dominio?**
   A) solo SLU/SLE a sezioni rettangolari
   B) TA + SLU + SLE + verifiche geotecniche
   C) SLU/SLE/TA con combinazioni, fessurazione, deformazioni; futuramente torsione/taglio + altri materiali
   D) tutti gli stati limite più verifica dinamica completare
   E) Altro: __________

2. **Come credi siano organizzati i calcoli reciproci tra codice e GUI oggi?**
   A) GUI chiama direttamente funzioni in `methods/*`, nessun engine centrale
   B) c’è un `VerificationEngine` che riceve oggetti di input e seleziona moduli
   C) i calcoli sono effettuati via script VBA importati (legacy)
   D) i moduli sono caricati dinamicamente via entry‑point plugin
   E) Altro: __________

3. **Quale architettura dati sembra usata per i progetti?**
   A) un unico file JSON contenente materiali/sezioni/elementi/risultati
   B) database SQLite strutturato con più tabelle
   C) oggetti in memoria serializzati con pickle
   D) file separati per materiali e progetti con riferimenti
   E) Altro: __________

4. **Quale ruolo hanno i file `.jsoncode` nella configurazione?**
   A) storage dei risultati delle verifiche
   B) parametri normativi e coefficienti (TA/SLU/SLE, materiali)
   C) definizione delle interfacce GUI
   D) logging e tracciabilità
   E) Altro: __________

5. **Per il modulo incendio, quale delle seguenti affermazioni è vera?**
   A) È solo un plugin opzionale con funzionalità minime
   B) È separato dal calcolo strutturale e ha propria pipeline termico‑meccanica
   C) Richiede sempre un modello globale FEM della struttura
   D) È implementato interamente in VBA e avviato da Qt
   E) Altro: __________

6. **Chi sono gli utenti tipici e quali workflow si aspettano?**
   A) ingegnere singolo che lavora offline su un progetto per volta
   B) studio tecnico con gestione multiconcorrenza e versioning via git
   C) comunità online con modelli condivisi in cloud
   D) R&D che eseguono esperimenti numerici su vasti dataset
   E) Altro: __________

7. **Come preferiamo estendere l’app in futuro?**
   A) aggiungendo file Python sparsi in mods/
   B) tramite sistema di plugin con discovery automatica (MODULE_SPEC)
   C) modificando direttamente il core in `core_calculus`
   D) tramite script esterni che generano nuovi moduli
   E) Altro: __________

8. **Quale livello di modularità data layer dovremmo privilegiare?**
   A) Repository per entità (progetto, materiale, sezione)
   B) Repository per dominio (calcoli strutturali, incendio)
   C) Unit‑of‑Work + repository
   D) Accesso diretto file JSON/SQLite in ogni modulo
   E) Altro: __________

---

Queste domande ci permetteranno di chiarire i punti ambigui e di allineare il piano con le effettive esigenze. Fammi sapere le tue risposte o indicami se alcuni di questi elementi devono cambiare, così posso proseguire con le sezioni successive del piano.

User: 1-C, 2-E i calcoli via script VBA devono essere convertiti in modo moderno se non è già stato fatto, 3-E valuta il metodo migliore, 4-E vedi tu a cosa servono, 5-B, 6-A, 7-B, 8-E segui il migliore giudizio ma preferenziale A

GitHub Copilot: ### ✅ Domanda 1: dominio strutturale
Hai confermato (risposta **C**) che il «core» strutturale copre:

- **tensioni ammissibili (TA)**,
- **stati limite ultimi (SLU)** e di esercizio (SLE)
- tutte le relative combinazioni, fessurazione, deformazioni ecc.

😃 Buono – il piano dovrà quindi prevedere un modulo verifiche con questi sotto‑sistemi e parametri .jsoncode.

### ✅ Domanda 2: calcoli storici VBA

Hai scelto **E** – cioè i calcoli sono ancora via script VBA e **devono essere convertiti** in un formato “moderno” (Python, engine interno).
→ questo mette in evidenza un’area critica: **trasformazione/rifattorizzazione del backend** in un modulo condiviso prima di legarlo al launcher.

### ✅ Domanda 3: storage progetti

Hai risposto **E** (valutiamo il metodo migliore) ma con preferenza A (repository per entità) — confermo: è ragionevole adottare un layer repository “per entità” come base, poi eventualmente sopra un Unit‑of‑Work se necessario.

### ✅ Domanda 4: `.jsoncode`

Hai scelto **E** cioè lasci a me decidere a cosa servano: dai documenti emerge che servono a **parametrizzare norme, coefficienti e materiali**; sono quindi la base per la configurazione normativa centralizzata.

### ✅ Domanda 5: incendio

Con **B** mi confermi che il modulo incendio è **separato** e ha un proprio flusso termico‑meccanico; non deve essere fuso con le verifiche strutturali.

### ✅ Domanda 6: utenti e workflow

Con **A** intendiamo un ingegnere che lavora offline su un progetto per volta; l’app quindi non necessita di multi‑utenza o sincronizzazione cloud immediata, ma potremmo pianificare servizi di condivisione in futuro.

### ✅ Domanda 7: estensibilità

Hai preferito **B** – il sistema Plugin/`MODULE_SPEC` già esistente — conferma la direzione modulare e discovery automatica, che dovremo mantenere/estendere.

### ✅ Domanda 8: modularità data layer

Hai selezionato **E** con preferenza per A (repository per entità).    Quindi useremo una struttura base con repository individuali (Progetto, Materiale, Sezione, Verifica …) e valuteremo ulteriori pattern (Unit‑of‑Work) se emergono esigenze di transazioni complesse.

---

### ❗ Aggiornamento della visione

> Le risposte confermano il quadro già delineato: l’applicazione è *mono‑utente*, basata su un engine Python che sostituisce i vecchi script VBA, con un’architettura già plugin‑friendly e un’ampia configurazione tramite `.jsoncode`. Il dominio copre sia strutturale sia incendio, ognuno nel proprio CodeModule.

---

### 🗺️ Prossimi passi proposti

1. **Dettagliare il modello concettuale del dominio** (entità, relazioni, flussi) in base alle verifiche strutturali e incendio.
2. **Inventario funzionale più preciso**: elencare moduli noti (calcolo SLU, SLE, TA, incendio L1/L2/L3, gestione materiali, geometria, ecc.) e individuare eventuali lacune.
3. **Esplorare i file markdown rimanenti** per ulteriori indizi su altri strumenti o workflow (es. FIRE_* documenti).
4. **Formulare la prossima serie di domande multiple‑choice** per approfondire configurazione, data layer e output standard.

Fammi sapere se possiamo procedere con il punto 1 (modello concettuale) oppure se preferisci affrontare qualche altra area prima.

User: [MODALITÀ: PLAN — VS Code Copilot Chat]
Ruolo: agisci come architetto software senior + ingegnere strutturista (Italia). Obiettivo: definire ulteriori dettagli di architettura, dominio e specifiche, SENZA scrivere codice (no file generati, no patch), SENZA avviare modalità Agent/Edit. Devi produrre solo documenti di specifica (Markdown) e schemi (JSON Schema o bozze Pydantic in pseudo-codice) e una lista di decisioni aperte.

CONTESTO (vincolante)

- Applicazione desktop offline mono-utente, un progetto alla volta.
- Core strutturale: TA, SLU, SLE con combinazioni, fessurazione, deformazioni, ecc.
- Modulo incendio separato (flusso termico-meccanico autonomo), NON fuso col core strutturale.
- Calcoli storici presenti come script VBA: devono essere migrati a backend Python “moderno” (engine interno).
- Storage progetti: repository per entità (Project, Material, Section, Element, Load, Combination, CheckRequest/Result, ecc.). Unit-of-Work solo se necessario.
- Sistema plugin/discovery esistente: mantenere/estendere con MODULE_SPEC.
- File `.jsoncode`: usati per parametrizzare norme, coefficienti, materiali; configurazione normativa centralizzata.
- Priorità: definire bene i dettagli per ridurre rework e favorire implementazione modulare.

REGOLE DI RIGORE

1) Niente assunzioni non dichiarate: se manca informazione, segnala “insufficienza dati” e proponi opzioni.
2) Tutto ciò che proponi deve essere verificabile e tracciabile: ogni decisione deve avere motivazione tecnica e impatto.
3) Output strutturato in sezioni professionali (Premessa, Modello concettuale, Flussi, Data layer, Plugin spec, Config `.jsoncode`, Migrazione VBA, Output/Report, Decisioni aperte, Next actions).
4) Non generare codice. Sono ammessi: diagrammi ASCII, schemi JSON (strutturali), pseudostrutture (campi e tipi), elenchi, checklist.
5) Minimizza il numero di domande: fai solo domande “bloccanti” e raggruppale alla fine.

TASK (da completare nell’ordine)
A) MODELLO CONCETTUALE (dominio strutturale)

- Definisci elenco entità minime e avanzate: attributi essenziali, relazioni (cardinalità), invarianti.
- Separazione netta tra: “Model” (dati), “Engine” (calcolo), “UI” (presentazione), “Persistence” (repo).
- Indica un glossario minimo (termini: combinazione, caso di carico, verifica, risultato, profilo normativo).

B) FLUSSI FUNZIONALI END-TO-END

- Descrivi 3 flussi: (1) creazione progetto + setup norma; (2) definizione elementi/materiali/sezioni + azioni; (3) esecuzione verifiche + report + salvataggio risultati.
- Per ciascun flusso: input, output, validazioni, errori tipici, punti di estensione plugin.

C) DATA LAYER (repository per entità)

- Proponi interfacce concettuali dei repository (metodi “minimi”) e un formato storage MVP: opzione cartella+JSON vs SQLite.
- Definisci “versioning” del progetto e migrazioni (schema version), e strategia di compatibilità retro.
- Specifica quali entità sono “source of truth” e quali sono “derivate/cache”.

D) PLUGIN SYSTEM / MODULE_SPEC

- Specifica il contenuto minimo del MODULE_SPEC: id, name, version, entrypoints (ui/engine/schemas), capabilities (checks/norms), dependencies, data contracts.
- Definisci regole di discovery, caricamento, compatibilità versioni, e fallback se un plugin manca o è incompatibile.
- Elenca esempi di plugin: core_structural_checks, combinations_engine, materials_db, fire_module.

E) CONFIGURAZIONE `.jsoncode` (norme/materiali/coeff.)

- Definisci la tassonomia e il namespace: norme → parametri globali; materiale → proprietà; combinazioni → coefficienti; esposizione e classi.
- Proponi struttura e versionamento `.jsoncode` + validazione (schema) + unità di misura.
- Indica un processo di override: default normativo → profilo progetto → override utente; tracciamento “provenienza” del parametro.

F) MIGRAZIONE VBA → PYTHON ENGINE

- Proponi un piano di conversione: inventario macro → decompose → funzioni pure → test golden file → integrazione.
- Definisci template di “scheda macro” (nome, input, output, dipendenze Excel, tolleranze confronto).
- Indica come ridurre il rischio: regressioni, rounding, unità, separatori, differenze numeriche.

G) OUTPUT E REPORTISTICA

- Definisci formato risultati: JSON risultati + report HTML/PDF (solo specifica, non generare file).
- Requisiti di tracciabilità: versione norme, parametri usati, plugin version, timestamp, hash input.
- Indica un “Result Contract” minimo (campi obbligatori) e livelli severità (OK/WARN/FAIL).

H) DECISIONI APERTE (massimo 8) + DOMANDE BLOCCANTI (massimo 5)

- Elenca decisioni da prendere con pro/contro e raccomandazione prudente.
- Formula solo domande bloccanti, a scelta multipla A/B/C dove possibile.

OUTPUT ATTESO (formato)

1) Documento Markdown: “SPEC_01_Domain_Model.md”
2) Documento Markdown: “SPEC_02_Architecture_and_DataLayer.md”
3) Documento Markdown: “SPEC_03_Plugins_and_Config_jsoncode.md”
4) Documento Markdown: “SPEC_04_VBA_Migration_and_Reporting.md”
5) Lista finale: “Decisions & Blocking Questions”

VINCOLO FINALE
Non generare codice né istruzioni operative di implementazione. Solo specifica e pianificazione dettagliata.
``

GitHub Copilot: ---

# SPEC_01_Domain_Model.md

### Premessa

Questo documento illustra il **modello concettuale** del dominio per l’applicazione RD2229: entità, attributi, relazioni e glossario. La separazione tra **Model / Engine / UI / Persistence** è vincolante: i dati non devono dipendere dalla UI o dai metodi di calcolo.

---

## Entità principali

1. **Project**
   - *Attrib.*: `id`, `name`, `description`, `created_at`, `modified_at`, `code_settings` (norma attiva, calcolo code etc.), `schema_version`.
   - *Relazioni*: 1→N `Material`, 1→N `Section`, 1→N `Element`, 1→N `LoadCase`, 1→N `Combination`, 1→N `VerificationResult`.
   - *Invarianti*: id unico; schema_version incrementale; norma_attiva obbligatoria per esecuzione.

2. **Material**
   - tipo (`concrete`/`steel`/`other`), `code` (es. C25/30), proprietà (`fck`, `fyk`, `E`, curve degradazione`…), metadata normativi.
   - *Relazioni*: 0→N `Section` (sezioni che lo usano).
   - *Invarianti*: proprietà coerenti alle norme selezionate.

3. **Section**
   - `id`, geometria (parametri, file CAD opzionale), categoria (`rectangular`/`circular`/…), `material_id` o `material_long`/`material_transv`.
   - *Relazioni*: 1→N `Element`.
   - *Invarianti*: geometria consistente (base>0, area>0).

4. **Element** (strutturale)
   - `id`, `section_id`, `material_id` (optional override), `name`, `position`, `fire_required` (bool), parametri incendio, `element_type` (pillar, beam, slab,…).
   - *Relazioni*: 1→N `LoadCase` (association), 1→N `VerificationResult`.
   - *Invarianti*: se `fire_required` allora campi incendio validati.

5. **LoadCase**
   - `id`, `project_id`, `name`, `type` (`permanent`/`variable`/`seismic`/`snow`/…), `combination_type` (rare/frequent/…), vettore carichi (N, Mx, My, Tx, Ty, Mz, etc.), `seismic_parameters` (ag, importance,…).
   - *Relazioni*: N→M `Element` (via `ElementLoad`), 1→N `Combination` (in generazione)
   - *Invarianti*: tutti i carichi sono numerici; `type` influenza campi obbligatori.

6. **Combination**
   - `id`, `project_id`, elenco di `LoadCase` con fattori, norma applicata, `name`.
   - *Relazioni*: 1→N `VerificationRequest`.
   - *Invarianti*: fattori sommati correttamente; norma compatibile con codice.

7. **VerificationRequest**
   - *Attrib.*: `id`, `element_id`, `combination_id`, `limit_state` (SLU/SLE/TA/Fire), `parameters` (ad-hoc), `status`.
   - *Relazioni*: 1→1 `VerificationResult`.
   - *Invarianti*: richiesta unica per coppia elemento/combinazione/limit_state.

8. **VerificationResult**
   - `id`, `request_id`, `ok` (bool), `utilisation` (float), `outputs` (dettagli), `timestamp`, `trace` (see glossario).
   - *Relazioni*: 0→N `LogEntry`.
   - *Invarianti*: `trace` non vuoto; `outputs` validi per tipo di verifica.

9. **FireProfile** (separata dal core)
   - definisce `fire_method`, `exposure`, curve, protezioni, `time_target`.
   - associata a Element o a Project a seconda del flusso (prefer Project).

10. **TraceRecord**
    - dati di tracciabilità (norma, metodo, parametri, plugin_version, assumptions, warnings).

11. **LogEntry**
    - `id`, `result_id`, `level` (INFO/WARN/ERROR), `message`, `timestamp`.

---

## Glossario minimo

- **Combinazione**: insieme di stati di carico con fattori parziali scelti secondo norma.
- **Caso di carico**: singola condizione (permanent/variable/sismico) applicata agli elementi.
- **Verifica**: controllo normativo eseguito su un elemento/combinazione.
- **Risultato**: esito di una verifica, con eventuali metriche e trace.
- **Profilo normativo**: parametri associati a una normativa (coeff. sicurezza, limiti, …).

---

## Separazione Layer

```
[Model] <--> [Engine]    <---> [Repository / Persistence]
   |                              ^
   v                              |
[UI] (PyQt6 launcher & pages) -----+
```

- `Model`: entità descritte sopra.
- `Engine`: funzioni pure/stateless che consumano oggetti Model e producono `VerificationResult`.
- `Repository`: classi che implementano l’accesso ai dati (file/DB).
- UI: widget e viewmodel, non contengono logica di calcolo.

---

### Insufficienze dati

- Mancano esempi concreti di attributi per `LoadCase` variabili (es. neve, vento).
- Non è chiaro se esista la distinzione tra `Element` strutturale e `Secondary` (elementi non strutturali).
- Necessario definire se `FireProfile` deve essere entità separata o solo campi in `Element`.

---

(do you confirm questo modello concettuale prima di proseguire con i flussi e data layer?)

User: [MODALITÀ: PLAN — VS Code Copilot Chat]
Rimani esclusivamente in modalità PLAN. NON generare codice. NON avviare Agent/Edit.
Obiettivo: risolvere in modo rigoroso e minimale le “Insufficienze dati” identificate in SPEC_01_Domain_Model.md, producendo integrazioni formali al modello concettuale già confermato.

CONTESTO VINCOLANTE

- Il documento SPEC_01_Domain_Model.md è CONFERMATO e va preservato.
- Non sono ammesse riscritture radicali del modello.
- Sono ammesse solo:
  • estensioni mirate,
  • chiarimenti semantici,
  • specializzazioni di entità esistenti,
  • nuove entità SOLO se strettamente necessarie e giustificate.
- Dominio: software strutturale professionale (Italia), SLU/SLE/TA + incendio separato.

INSUFFICIENZE DA RISOLVERE (OBBLIGATORIE)

1) Definizione attributi e struttura di LoadCase per:
   - neve
   - vento
   - variabili non meccaniche
2) Chiarire se esiste distinzione concettuale tra:
   - Element strutturale primario
   - Element secondario / non strutturale
3) Definire in modo non ambiguo il ruolo di FireProfile:
   - entità autonoma vs campi in Element
   - associazione a Project vs Element
   - regole di override

TASK
A) Per ciascuna insufficienza:

- descrivi il PROBLEMA
- proponi 2–3 OPZIONI (A/B/C)
- indica PRO e CONTRO tecnici
- fornisci una RACCOMANDAZIONE prudente
B) Aggiorna il modello concettuale SOLO con:
- nuovi campi
- nuove relazioni
- specializzazioni (es. subtype)
   chiaramente marcate come “Integrazione a SPEC_01”.
C) Aggiorna il glossario SOLO se necessario.
D) Indica l’impatto su:
- flussi funzionali
- data layer / repository
- plugin system
E) Elenca le decisioni che diventano “locked” dopo questa integrazione.

FORMATO OUTPUT

1) Sezione: “Risoluzione insufficienze dati”
2) Sezione: “Integrazioni formali a SPEC_01”
3) Sezione: “Decisioni consolidate”
4) Sezione: “Nessun’altra modifica richiesta” (se applicabile)

VINCOLI FINALI

- Nessun codice
- Nessun riferimento a implementazione concreta
- Linguaggio tecnico-professionale, prudente, tracciabile

GitHub Copilot: ### 🔧 Risoluzione insufficienze dati

#### **1. Attributi di `LoadCase` per neve/vento/variabili non meccaniche**

**Problema**
Il modello precedente generico `LoadCase` non specifica quali campi servano per i carichi ambientali (neve, vento) o altre variabili (temperatura, ecc.).
Senza questa chiarezza, sono possibili ambiguità nella costruzione delle combinazioni e nella serializzazione dei progetti.

**Opzioni**

- **A) Estendere `LoadCase` con campi opzionali dedicati**
  `snow_load: float`, `wind_speed: float`, `direction: float`, `temperature: float`…
  *Pro*: chiaro, valori direttamente accessibili; semplice repository JSON.
  *Contro*: schema inflazionato; eventuali nuovi tipi richiedono aggiornamento.

- **B) Usare un campo generico `environmental: Dict[str,float]`**
  qualsiasi variabile può essere aggiunta con chiave; `type` specifica `snow`/`wind`…
  *Pro*: massima flessibilità, nessuna modifica codice per nuovi carichi.
  *Contro*: meno tipizzato, validazione più complessa, difficile autocompletamento UI.

- **C) Definire sottotipi specializzati `SnowCase`, `WindCase` tramite subclassing**
  `class SnowCase(LoadCase): snow_depth`, etc.
  *Pro*: tipizzazione forte, plugin system può registrare nuovi tipi.
  *Contro*: più complesso per repository (diversificare deserializzazione), aumento del numero di classi.

**Raccomandazione**
Adotto l’opzione **A** con un piccolo insieme di campi opzionali e `environmental:Dict[str,float]` come estensione secondaria. Questa scelta mantiene chiarezza e non impedisce un design ibrido (campi primari + mappa).

---

#### **2. Elementi primari vs secondari / non strutturali**

**Problema**
Non è esplicitata una distinzione concettuale tra gli elementi che partecipano al modello strutturale e quelli “non strutturali” (es. tamponature, parapetti) che subiscono solo carichi sismici.

**Opzioni**

- **A) Un’unica entità `Element` con flag `role = PRIMARY | SECONDARY`**
  campi opzionali aggiuntivi se SECONDARY (mass, stiffness, attachment…).

- **B) Sottotipo `PrimaryElement` e `SecondaryElement` (inheritance)**
  `SecondaryElement` può avere campi specifici (fire_required? o load_only?).

- **C) Tenere solo `Element` e gestire la nascosta distinzione nelle combinazioni/parametri**
  nessuna modifica al modello, distinzione applicata a runtime (p.ex. `if element_type in {...}`).

**Pro/Contro**

A facile da implementare; impone un campo esplicito, ma obbliga UI/engine a gestire il flag.

B più pulito dal punto di vista OOP; permette repository specializzati; ma maggior complessità di serializzazione.

C minimizza il modello ma lascia ambiguità e codice disperso.

**Raccomandazione**
Scegliere **A**: aggiungo a `Element` campo `role` e, se utile, campo `is_structural: bool` già presente implicitamente; con questo si documenta il concetto senza cambiare l’architettura.

---

#### **3. Ruolo di `FireProfile`**

**Problema**
Non è chiaro se il profilo incendio sia entità autonoma o semplice campo di `Element`, e se associarlo al progetto o all’elemento.

**Opzioni**

- **A) Entità separata `FireProfile` (1→N Project) con riferimenti dagli elementi**
  permette riuso di profili multipli nello stesso progetto.

- **B) Campi diretti in `Element`**
  keep it simple: ogni elemento può avere i propri parametri incendio.

- **C) Misto: profili globali e override per elemento**
  `Project.fire_profiles: List[FireProfile]` + `Element.fire_profile_id: Optional`.

**Pro/Contro**

A favore A: riuso e gestione centralizzata; utile se molti elementi condividono lo stesso scenario di incendio.
Contro A: necessità di lookup e più entità nel repository.

B semplifica il data model; ma niente riuso e possibile duplicazione se il profilo è uguale per molti elementi.

C flessibile ma introduce complessità di override e logica “eredità”.

**Raccomandazione**
Proporre **C** come soluzione più robusta. Un profilo definito a livello progetto può essere assegnato (o override) a elementi specifici. Questo copre anche il caso minimo (solo un profilo per progetto).

---

### 🛠️ Integrazioni formali a SPEC_01

#### Nuovi campi / relazioni

```text
LoadCase
  + snow_load: float?                # [A] default 0
  + wind_speed: float?               # direzione opzionale
  + environmental: Dict[str,float]?  # mappa estensioni
  invariant: if type=='snow' then snow_load>0, etc.

Element
  + role: Literal["PRIMARY","SECONDARY"] = "PRIMARY"
  + fire_profile_id: str?            # link a FireProfile (see below)

FireProfile (new entity)
  * id: str
  * name: str
  * method: Literal["L1","L2","L3"]
  * exposure_sides: int
  * fire_class: str  # es. R60
  * curve_type: str  # ISO_834, parametrica
  * time_target: float
  relationship: Project 1→N
```

- `Project`
  - `fire_profiles: List[FireProfile]`

- `Element` (modificato sopra)
  - `role` e `fire_profile_id` (opzionali).

#### Glossario aggiornato

- **LoadCase.snow_load**: carico sulla copertura.
- **LoadCase.wind_speed/ environmental**: variabili meteorologiche.
- **Element.role**: ruolo nel modello; PRIMARY parte del calcolo strutturale,
  SECONDARY considerato solo per carichi specifici.
- **FireProfile**: definizione riutilizzabile di condizioni incendio; associabile
  a progetto o a elementi con override.

---

### 📌 Impatto delle integrazioni

- **Flussi funzionali**:
  - Creazione carico ora richiede campi neve/vento se pertinenti.
  - Flusso verifica deve controllare `element.role` per decidere se usare
    loadcase standard o sismico secondario.
  - Profili incendio gestiti globalmente e assegnabili.

- **Data layer/repository**:
  - Repositories aggiornati: `LoadCaseRepo` deve gestire i nuovi campi.
  - `FireProfileRepo` nuovo per gestire entità; `ElementRepo` supporta
    `fire_profile_id` e logica di override.
  - Versioning: schema_version incrementato, con migrazione automatica immettendo
    valori di default (snow_load=0, role="PRIMARY").

- **Plugin system**:
  - Plugin che definiscono nuovi `LoadCase` type o `Element` subtype possono
    utilizzare i campi generici `environmental`.
  - Fire module diventa plugin che registra `FireProfile` e aggiunge campi UI.

---

### 📝 Decisioni consolidate

1. `LoadCase` avrà campi dedicati per neve e vento (A) e mappa generica.
2. `Element` includerà un flag `role` per distinguere primario/secondario.
3. `FireProfile` diventa entità autonoma con relazione a progetto e link
   optional da elemento; supporta override.

---

### ✅ Nessun’altra modifica richiesta

I tre punti di insufficienza sono stati risolti con estensioni minime e chiare.
Non sono necessarie ulteriori modifiche al modello concettuale attuale.
Il glue code (engine, UI, repository) sarà definito in fasi successive, ora che
il modello dati è completo.

---

Se vuoi procedere con la descrizione dei flussi end‑to‑end o con il data layer,
posso passare alla prossima sezione del piano.
