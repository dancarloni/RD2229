
NTC2018 — Spectrum Paste Service (EdiLus‑MS) — PLAN‑ONLY


Obiettivo: introdurre nel software un servizio “Spettro NTC2018” che non calcola la pericolosità di base, ma consente di:
1) impostare Classe edificio/uso, Vita Nominale (VN), Periodo di Riferimento (VR);
2) fare paste in blocco della tabella testuale proveniente da EdiLus‑MS;
3) parsare e salvare i parametri Tr, ag/g, F0, Tc\* per gli stati limite. >
EdiLus‑MS espone proprio questi campi e la tabella “Parametri di pericolosità Sismica” con colonne Tr, ag/g, F0, Tc\* e stati limite (Operatività, Danno, Salvaguardia Vita, Prevenzione Collasso), copiabili come testo.




0) Vincoli (non negoziabili)

PLAN‑ONLY: in questa fase si definiscono file, percorsi, contratti, test e UI; nessun calcolo numerico avanzato e nessuna logica di interpolazione per pericolosità.
Input dati esterni: i parametri (ag, F0, Tc\*) sono ottenuti da applicativo esterno (EdiLus‑MS).
Paste robusto: accettare decimali con punto e tollerare anche virgola (dipendenza da locale/browser).
Tracciabilità: salvare anche il testo originale incollato (raw_paste) + timestamp + fonte.


1) Deliverable (cosa creare)
1.1 Nuovo documento di piano (questo file)

Creare: docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_SERVICE_PLAN.md (contenuto = questo canvas).
1.2 Specifica dati (schema)

Creare: docs/MEGAPLAN/SPEC_NTC2018_HAZARD_PASTE.md (spec dei campi e validazioni minime).
1.3 Automazione (checklist di implementazione)

Creare: docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_AUTOMATION.md (lista file target + test + integrazione UI).


2) Scelta architetturale (dove mettere il servizio)
2.1 Perché NON dentro secondary_elements
Il servizio spettro è generale NTC2018 e riusabile anche in altri moduli; non va “incapsulato” nel modulo Secondary Elements. (EdiLus‑MS fornisce parametri generali di pericolosità per sito.)
2.2 Percorsi canonici proposti (TO‑BE)


Scegliere uno (consiglio: A).



A) Service nel dominio NTC2018 (consigliato)src/codes/ntc2018/spectrum_paste_service.py
src/codes/ntc2018/init.py (solo export, se già esistente)
B) Service nel core (solo se hai già un “seismic actions service” comune)src/core/seismic/ntc2018_spectrum_paste_service.py


3) Modello dati (MVP) — Ntc2018HazardProfile
3.1 Entità principale
Creare una struttura dati (dataclass/pydantic/typed dict) chiamata:

Ntc2018HazardProfile
Campi minimi:

source: str = "EDILUS_MS"
class_of_use: str in {I, II, III, IV} (classe edificio/uso)
vita_nominale_years: int
vr_years: int (Periodo di Riferimento per l’azione sismica)
site_label: str | None (indirizzo / comune / note)
raw_paste: str (testo incollato in blocco)
parsed_rows: list[Ntc2018HazardRow]
timestamp_import: str (ISO 8601)
quality: str in {OK, WARNING, ERROR}
messages: list[str]
3.2 Righe tabella
Ntc2018HazardRow:

limit_state_label: str (es. “Operatività”, “Danno”, “Salvaguardia Vita”, “Prevenzione Collasso”)
tr_years: float
ag_g: float
f0: float
tc_star_s: float
3.3 Validazioni minime

Accettare decimali con . e anche , (normalizzazione).
Se mancano una o più righe → quality=WARNING.
Se valori non numerici o <=0 su F0 o Tc* → quality=ERROR.


4) Parser “paste in blocco” (MVP)
4.1 Input atteso
Testo multi‑riga incollato dalla tabella EdiLus‑MS, che contiene:

stati limite (Operatività/Danno/Salvaguardia Vita/Prevenzione Collasso)
colonne Tr[anni], ag/g, F0, Tc*
4.2 Regole di parsing (deterministiche)

Pre‑clean: normalizzare \r\n→\n, rimuovere righe vuote, comprimere spazi ripetuti.
Decimal normalize: sostituire virgola decimale , con punto . SOLO dentro token numerici.
Row detect: identificare righe che contengono una delle etichette note (esatte) degli stati limite.
Number extract: estrarre nell’ordine 4 numeri (Tr, ag, F0, Tc*). Se trovati >4 numeri, prendere i primi 4 e mettere warning.
Map: costruire Ntc2018HazardRow.
4.3 Output parser

Ntc2018HazardProfile con parsed_rows + messages.


5) UI (Thin) — schermata “Parametri sismici NTC2018”
5.1 Dove inserirla

Opzione consigliata: Impostazioni progetto → Azioni sismiche (NTC2018)motivazione: è un input “di progetto” comune, non specifico secondary elements.
5.2 Componenti UI

Dropdown class_of_use (I–IV) con descrizione (come EdiLus‑MS).
Numeric input vita_nominale_years.
Numeric input vr_years.
Text input site_label (facoltativo).
TextArea raw_paste + bottone Analizza.
Preview table (read‑only) di parsed_rows.
Indicator quality + elenco messages.
Pulsante Salva nel progetto.
5.3 UX “paste”

Supportare CTRL+V/CMD+V nel TextArea.
Pre‑validazione immediata (on paste) con badge “Riconosciute N righe”.


6) Persistenza (Project Model)
6.1 Campo nuovo in project model
Aggiungere (additivo):

project.seismic_inputs.ntc2018_hazard_profile (singolo) oppure
project.seismic_inputs.ntc2018_hazard_profiles[] (versionabile, multi‑sito)
Contenuto = Ntc2018HazardProfile.
6.2 Tracciabilità
Salvare sempre raw_paste e timestamp_import.


7) Integrazione con Secondary Elements (solo hook, no calcolo pericolosità)
7.1 Uso in futuro

Il modulo Secondary Elements (checks SLU/SLE) potrà leggere dal profilo:i parametri coerenti con lo stato limite richiesto.
In questa fase NON è richiesto calcolare spettro completo; solo accesso ai parametri.
7.2 Interfaccia prevista

get_hazard_params(limit_state_label) -> (tr_years, ag_g, f0, tc_star_s)


8) Test (contrattuali + parser)
8.1 Test parser (unit)
Creare test che verificano:

paste con decimali a punto → parse OK.
paste con decimali a virgola → parse OK (normalizzazione).
paste con righe mancanti → WARNING.
paste con token non numerici → ERROR.
8.2 Test persistenza

round‑trip: salva profilo → ricarica → identico.
8.3 Test UI (smoke)

incolla testo → analizza → preview popolata.


9) Checklist per chiudere il PLAN (prima di implementare)

Confermare percorso canonico del servizio (2.2 A o B).
Confermare se project deve contenere un profilo o una lista profili.
Confermare etichette esatte da matchare (hai già detto: “contiene esattamente tutte le etichette”).
Scrivere i due file MD:SPEC_NTC2018_HAZARD_PASTE.md
NTC2018_SPECTRUM_PASTE_AUTOMATION.md
Una volta completati questi punti, si può passare all’implementazione (con prompt premium o implementazione manuale controllata).
