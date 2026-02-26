
SPEC — NTC2018 Hazard Paste (EdiLus‑MS) — PLAN‑ONLY


Scopo: specificare in modo vincolante lo schema dati, le validazioni minime e le regole di parsing del testo incollato dalla tabella EdiLus‑MS (parametri di pericolosità sismica) per uso NTC2018.


0. Contesto e fonti

La sorgente esterna è EdiLus‑MS (ACCA), che restituisce una tabella copiabile come testo con colonne Tr[anni], ag/g, F0, Tc\* e righe per gli stati limite (Operatività, Danno, Salvaguardia Vita, Prevenzione Collasso).
Questo modulo non calcola l’interpolazione della pericolosità di base; importa e normalizza dati forniti dall’applicativo esterno.
1. Decisioni vincolanti (Fase PLAN)

Percorso canonico servizio: src/codes/ntc2018/spectrum_paste_service.py (VINCOLANTE).
Persistenza progetto: singolo profilo project.seismic_inputs.ntc2018_hazard_profile (VINCOLANTE).
2. Schema dati (MVP)
2.1 Entità Ntc2018HazardProfile
Campi obbligatori:

source: str = "EDILUS_MS"
class_of_use: str ∈ {"I", "II", "III", "IV"} (classe edificio/uso)
vita_nominale_years: int (VN)
vr_years: int (Periodo di Riferimento VR)
site_label: str | null (indirizzo/località/note; facoltativo)
raw_paste: str (testo incollato in blocco; sempre salvato)
parsed_rows: list[Ntc2018HazardRow] (righe parsate)
timestamp_import: str (ISO 8601)
quality: str ∈ {"OK", "WARNING", "ERROR"}
messages: list[str] (messaggi utente/audit)
2.2 Entità Ntc2018HazardRow
Campi obbligatori:

limit_state_label: str (etichetta riga; vedi §3)
tr_years: float
ag_g: float
f0: float
tc_star_s: float
3. Etichette Stati Limite (match esatto)
Il parser deve riconoscere (case‑insensitive, spazi multipli ammessi) le seguenti etichette:

Operatività
Danno
Salvaguardia Vita
Prevenzione Collasso


Nota: l’input utente dichiara che la tabella incollata contiene esattamente tutte le etichette; il parser non deve inventare mapping alternativi.


4. Regole di parsing (deterministiche)
4.1 Pre‑clean

Normalizzare fine riga \r\n → \n.
Rimuovere righe vuote.
Comprimere sequenze di spazi multipli a singolo spazio.
4.2 Normalizzazione decimali

Accettare decimali con ..
Tollerare decimali con , (dipende da locale/browser): sostituire , → . solo nei token numerici (regex/heuristica), senza alterare testo non numerico.
4.3 Individuazione righe tabella

Una riga è candidata se contiene una delle etichette §3.
Il parser deve ignorare intestazioni/righe non candidate (es. titoli colonna).
4.4 Estrazione numeri

Da ogni riga candidata estrarre nell’ordine i primi 4 numeri:
1) Tr (anni)  2) ag/g  3) F0  4) Tc* (s)

Se una riga contiene più di 4 numeri: usare i primi 4 e aggiungere messaggio WARNING.
Se una riga contiene meno di 4 numeri: la riga è ERROR e viene esclusa da parsed_rows (ma segnalata in messages).
5. Validazioni minime (MVP)
5.1 Validazioni per riga

f0 > 0 altrimenti ERROR.
tc_star_s > 0 altrimenti ERROR.
ag_g > 0 altrimenti ERROR.
5.2 Validazioni di completezza

Se mancano una o più etichette §3 in parsed_rows: quality = WARNING e messaggio specifico per etichetta mancante.
Se zero righe valide: quality = ERROR.
5.3 Tracciabilità

raw_paste deve essere sempre salvato integralmente per audit.
timestamp_import sempre valorizzato.
6. Output del servizio (API contrattuale)
6.1 Funzioni minime

parse_edilus_ms_table(raw_paste: str) -> (parsed_rows, messages, quality)
build_profile(class_of_use, vita_nominale_years, vr_years, site_label, raw_paste) -> Ntc2018HazardProfile
get_hazard_params(profile, limit_state_label) -> (tr_years, ag_g, f0, tc_star_s)


In questa fase non è richiesto generare lo spettro Sa(T). Si prepara solo la base dati coerente con NTC2018 per integrazioni future.


7. Criteri di accettazione (SPEC)

Il parser riconosce correttamente le 4 etichette §3 e produce 4 righe valide quando presenti.
Il parser accetta sia . che , come separatore decimale senza perdita informativa.
Il profilo salvato contiene sempre raw_paste + timestamp_import + source.
