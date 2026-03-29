
PLAN – INPUT COMUNE
Status: STABILE Ambito: Schema dati e validazione Vincolo: Un solo sistema di input per tutto il software
Scopo
Definire uno schema di input unico, coerente e condiviso da tutti i moduli di calcolo (NTC2018, RD2229/39, DM92, DM96, ECx) e da tutte le GUI, evitando duplicazioni e ambiguità.
Principi non negoziabili

Single Source of Truth: un solo schema dati per tutti i moduli
Separazione dominio/UI: le GUI non introducono campi propri
Validazione preventiva: nessun calcolo parte con input non validi
Retro‑compatibilità: estensioni additive, mai distruttive
Gerarchia concettuale degli schemi
BaseElementSpec (comune a tutto)

Identità: id, name, schema_version
Geometria base: dimensioni principali, riferimenti di sezione
Materiale: material_id (lookup su repository materiali)
Massa / carichi equivalenti
Parametri sismici minimi (se applicabili): quota z, contesto edificio
Vincoli / condizioni di appoggio
Metadati normativi: norma primaria, fallback consentiti
Estensioni di dominio (solo additive)

RCElementSpec: armature, parametri sezionali CA
SecondaryElementSpec: elementi secondari / non strutturali
Steel / Masonry / Geotech Spec: campi specifici di materiale/dominio
Input standardizzati (vocabolario comune)

Geometria: lunghezze, aree, volumi, riferimenti di sezione
Materiale: classe, proprietà meccaniche via material_id
Sismica: ag, categoria suolo, quota z, parametri edificio
Vincoli / ancoraggi: tipo di vincolo, capacità dichiarata
Metadati: norma, stato limite, opzioni di fallback
Regole di utilizzo

Ogni GUI legge e scrive esclusivamente questo schema
Ogni CodeModule consuma esclusivamente questo schema
I campi opzionali diventano obbligatori in base al check (gating)
Le estensioni non rompono i consumer esistenti
Validazione (concettuale)

Controlli di completezza per check richiesto
Controlli di coerenza fisica (valori, unità, range)
Segnalazione NOT_APPLICABLE quando fuori campo normativo
Deliverable del piano

Schema logico consolidato degli input
Regole di obbligatorietà per famiglia di check
Linee guida di estensione futura
Criteri di accettazione

Nessuna GUI introduce campi non presenti nello schema
Nessun CodeModule richiede input esterni allo schema
Migrazioni possibili solo tramite schema_version
