
IMPLEMENTAZIONE GUI NTC2018 – Archivi Sezioni/Materiali e Pannello Verifiche
Status: SPECIFICA OPERATIVA VINCOLANTE (GUI)
Questo documento estende e completa la GUI definita in IMPLEMENTAZIONE_GUI_NTC2018_WORKFLOW.md, introducendo:

selezione di sezioni e materiali da archivi esistenti;
selezione della normativa di verifica (con attivazione automatica delle verifiche pertinenti);
inserimento delle sollecitazioni (N, Tx, Ty, Mx, My, Mz);
esecuzione delle verifiche tramite il core già sviluppato (CAP_4 / CAP_7).
La GUI resta orchestratore: nessuna formula, nessuna norma applicata in GUI.


1. Archivi (read‑only) e requisiti
1.1 Archivio Materiali

Fonte: archivio già presente (DB/JSON/CSV/ORM esistente).
Contenuti minimi (per materiale):identificativo;
classe (es. C25/30, B450C, S355);
proprietà meccaniche (E, fck/fyk, γ, εlim, ecc.);
riferimenti normativi (NTC2018 / EC / storico se presente).
Regola: selezionando un materiale, tutte le proprietà vengono caricate automaticamente nel ProjectModel (read‑only in GUI).
1.2 Archivio Sezioni

Fonte: archivio già presente.
Contenuti minimi (per sezione):tipologia (rettangolare, T, I, circolare, generica);
geometria completa (A, Ix, Iy, W, coordinate baricentriche);
armature (se c.a.): diametri, posizioni, copriferro;
asse locali.
Regola: la sezione è indipendente dalla normativa; la normativa governa solo le verifiche.


2. View: Sezioni & Materiali (SezioniMaterialiView)

┌──────────── SEZIONI E MATERIALI ────────────┐
│ Materiale                                   │
│  [ Cerca ▼ ]  [ Elenco materiali ]          │
│  Classe: B450C                              │
│  Proprietà: (read‑only)                     │
│                                              │
│ Sezione                                     │
│  [ Cerca ▼ ]  [ Elenco sezioni ]             │
│  Tipo: Rettangolare 30×50                    │
│  A, Ix, Iy, W: (read‑only)                  │
│                                              │
│ [ Assegna a elemento ▶ ]                    │
└─────────────────────────────────────────────┘



Selezione da archivio (no editing manuale delle proprietà).
L’assegnazione aggiorna ProjectModel.sezione e ProjectModel.materiale.


3. View: Normativa e Verifiche (NormativaVerificheView)

┌──────────── NORMATIVA E VERIFICHE ────────────┐
│ Normativa di verifica:                         │
│  (●) NTC2018                                   │
│  (○) Eurocodici (se attivo)                    │
│                                              │
│ Ambito:                                       │
│  ☐ CAP_4 – Statiche (SLU/SLE)                  │
│  ☐ CAP_7 – Sismiche (capacità/gerarchia)       │
│                                              │
│ Verifiche attive (auto):                      │
│  ✔ Flessione / Pressoflessione                │
│  ✔ Taglio / Torsione                          │
│  ✔ SLE (tensioni/fessure/defl.)               │
│  ✔ Gerarchia (se CAP_7)                       │
│                                              │
│ [ Applica ▶ ]                                 │
└──────────────────────────────────────────────┘


Regole hard:

CAP_7 abilitabile solo se il workflow lo consente (vedi STEP precedenti).
Le verifiche si attivano automaticamente in base a normativa + ambito.


4. View: Sollecitazioni (SollecitazioniView)

┌──────────── SOLLECITAZIONI DI PROGETTO ────────────┐
│ Sistema di riferimento: Locale                     │
│                                                    │
│ N   [ kN ]   : [ ______ ]                          │
│ Tx  [ kN ]   : [ ______ ]                          │
│ Ty  [ kN ]   : [ ______ ]                          │
│ Mx  [ kNm ]  : [ ______ ]                          │
│ My  [ kNm ]  : [ ______ ]                          │
│ Mz  [ kNm ]  : [ ______ ]                          │
│                                                    │
│ Combinazione: [ SLE_RARA ▼ ]                       │
│                                                    │
│ [ Valida input ]   [ Esegui verifiche ▶ ]          │
└───────────────────────────────────────────────────┘


Note tecniche:

Le sollecitazioni sono effetti interni (output analisi o input manuale controllato).
La GUI non trasforma le sollecitazioni.


5. Esecuzione verifiche (binding al core)
Alla pressione di Esegui verifiche:

La GUI costruisce il contesto di verifica:sezione + materiale (da archivi);
normativa/ambito;
combinazione selezionata;
sollecitazioni (N, Tx, Ty, Mx, My, Mz).
Invoca i moduli core:VerificationEngine (CAP_4 / CAP_7);
eventuali verifiche di capacità/gerarchia;
aggiornamento ProjectModel.verifiche_*.
Riceve solo VerificationResult.


6. View: Risultati (RisultatiView)

┌──────────── RISULTATI VERIFICHE ────────────┐
│ Verifica                     Esito   Ed/Rd │
│ Flessione SLU (CAP_4)          ✅     0.78  │
│ Taglio SLU (CAP_4)             ✅     0.65  │
│ SLE Fessurazione (CAP_4)       ✅     0.90  │
│ Gerarchia (CAP_7)              ❌     —     │
│                                                │
│ [ Dettagli ]   [ Invia a relazione ▶ ]        │
└──────────────────────────────────────────────┘



Vista tabellare + dettagli per singola verifica.
Colonna Capitolo NTC sempre visibile.


7. Integrazione con la Relazione di Calcolo

La GUI seleziona quali verifiche includere.
Passa i VerificationResult al ReportBuilder.
La relazione usa il template:
RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md.



8. Modello dati – Estensioni

class ProjectModel:
    ...
    self.materiale = None
    self.sezione = None
    self.sollecitazioni = {}
    self.normativa_verifica = None




9. Regole di sicurezza normativa (GUI)

impossibile eseguire verifiche senza sezione e materiale;
impossibile eseguire CAP_7 senza prerequisiti;
impossibile esportare relazione senza risultati validi.


10. Stato
✅ Archivi integrati concettualmente ✅ Pannello verifiche completo ✅ Flusso coerente con NTC2018 ✅ Pronto per implementazione Tkinter reale


Questo file è vincolante per l’implementazione GUI delle verifiche di sezione secondo NTC2018.
