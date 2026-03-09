
PROMPT IMPLEMENTAZIONE — NTC2018 Spectrum Paste Service (AGGIORNATO E COMPLETO)

Uso: incolla questo prompt in GitHub Copilot Chat (VS Code) in modalità Implementazione / Agent quando vuoi generare il codice.
Scopo: implementare un servizio di paste dei parametri di pericolosità sismica NTC2018 ottenuti da EdiLus‑MS (tabella testuale), con UI dedicata e persistenza nel project model.

1) Premesse e contesto vincolante

La sorgente esterna è EdiLus‑MS, che consente di selezionare Classe dell’edificio, Vita Nominale, Periodo di Riferimento e restituisce una tabella copiabile come testo con colonne Tr[anni], ag/g, F0, Tc\* e righe di stato limite (Operatività, Danno, Salvaguardia Vita, Prevenzione Collasso).
Il repository usa come project model la classe VerificationProject in verification_project.py (include load/save e alimenta UI/persistenza).
Decisioni vincolanti già assunte nel PLAN:Percorso canonico servizio: src/codes/ntc2018/spectrum_paste_service.py.
Persistenza: singolo profilo in project.seismic_inputs.ntc2018_hazard_profile.
Documenti vincolanti (da leggere prima di agire):

docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_SERVICE_PLAN.md
docs/MEGAPLAN/SPEC_NTC2018_HAZARD_PASTE.md
docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_AUTOMATION.md

1) DIVIETI ASSOLUTI (anti‑deriva)

❌ NON implementare interpolazioni/pericolosità da coordinate (nessun calcolo INGV/reticolo).
❌ NON fare fetch web / scraping / chiamate HTTP.
❌ NON introdurre calcolo completo dello spettro Sa(T) (in questa iterazione).
❌ NON modificare file UI non correlati.
❌ Se esistono duplicati di module_selector.py/UI, NON modificarli entrambi: devi determinare quello effettivamente usato dal main window e modificare solo quello.
❌ Se un percorso è ambiguo o non identificabile con certezza: STOP e chiedi istruzioni (non “indovinare”).

1) FILE DA ESPORRE NEL CONTESTO (OBBLIGATORI)
Apri e “pinna” in VS Code questi file PRIMA di eseguire:
2.1 Documenti di piano/spec (obbligatori)

docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_SERVICE_PLAN.md
docs/MEGAPLAN/SPEC_NTC2018_HAZARD_PASTE.md
docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_AUTOMATION.md
2.2 Project model e persistenza (obbligatori)

verification_project.py (classe VerificationProject + metodi load_from_file / save_to_file).
2.3 UI routing (obbligatori)

src/ui/main_window.py (o file equivalente che costruisce menu/pannelli UI)
src/ui/module_selector.py (o il module selector effettivamente importato dal main window)
2.4 Riferimenti per pattern test (consigliati)

un test esistente di persistenza o di parser (scegline uno vicino per stile).

1) FILE TARGET (AUTORIZZATI) — CREATE / TOUCH
3.1 CREATE
1) src/codes/ntc2018/spectrum_paste_service.py

Implementare:Ntc2018HazardRow
Ntc2018HazardProfile
parse_edilus_ms_table(raw_paste: str) -> (rows, messages, quality)
build_profile(class_of_use, vita_nominale_years, vr_years, site_label, raw_paste) -> profile
get_hazard_params(profile, limit_state_label) -> (tr_years, ag_g, f0, tc_star_s)
Parsing deterministico e robusto (punto/virgola), ignorando intestazioni/righe non candidate.
Validazioni minime e quality {OK/WARNING/ERROR} come da SPEC.
2) tests/test_ntc2018_hazard_paste_parser.py

Unit test parser per i 4 casi minimi (punto, virgola, righe mancanti, token invalidi).
3) tests/test_ntc2018_hazard_profile_persistence.py

Test round‑trip su VerificationProject: salva → ricarica → profilo identico (incluso raw_paste).
4) UI panel (nuovo file) — percorso da determinare in base alla tua struttura UI:

Crea un solo file, es. src/ui/ntc2018_hazard_paste_panel.py.
Deve contenere il pannello con:dropdown classe uso (I–IV)
input VN e VR
textarea raw_paste + bottone Analizza
preview read‑only delle righe
quality/messages
bottone Salva
3.2 TOUCH
5) verification_project.py

Aggiungere struttura dati seismic_inputs (o sotto‑oggetto) in modo typed e additivo, con campo:ntc2018_hazard_profile: Ntc2018HazardProfile | None
Aggiornare save_to_file/load_from_file per serializzare/deserializzare il profilo.
Garantire retro‑compatibilità: se il campo non esiste in JSON → None.
6) UI routing file

src/ui/module_selector.py (o quello effettivo)
e/o src/ui/main_window.py
Aggiungere voce/pulsante: “Parametri sismici NTC2018 (Paste)” che apre il pannello.
Collegare il pannello al VerificationProject corrente.

1) REGOLE DI IMPLEMENTAZIONE (OBBLIGATORIE)
4.1 Persistenza (single profile)

Persisti in: project.seismic_inputs.ntc2018_hazard_profile (non dizionario libero).
Serializza includendo:source, class_of_use, vita_nominale_years, vr_years, site_label, raw_paste, parsed_rows, timestamp_import, quality, messages.
4.2 Parser

Riconosci le etichette esatte: Operatività, Danno, Salvaguardia Vita, Prevenzione Collasso (case‑insensitive, spazi multipli ammessi).
Estrai 4 numeri nell’ordine: Tr, ag/g, F0, Tc*.
Accetta decimali . e tollera , come fallback.
Se righe mancanti: WARNING.
Se nessuna riga valida: ERROR.
Non inventare: se formato invalido → messaggi + quality coerente.
4.3 UI

UI thin: nessun calcolo numerico; solo chiamata al service di parsing.
Mostra preview e messaggi prima di salvare.
Salvando:scrive project.seismic_inputs.ntc2018_hazard_profile = profile.
4.4 Test

I test devono essere contrattuali (nessun caso numerico avanzato).
Usare tmp_path/temporary file per round‑trip.

1) ORDINE DI ESECUZIONE (OBBLIGATORIO)
1) Implementa spectrum_paste_service.py + unit test parser. 2) Integra VerificationProject (campo + load/save) + test persistenza. 3) Implementa UI panel. 4) Aggancia UI panel al module selector / main window. 5) Esegui pytest (almeno suite completa o subset rilevante). Se fallisce, correggi SOLO nei file autorizzati.

1) OUTPUT RICHIESTO IN CHAT (A FINE LAVORO)
1) Elenco file creati/modificati (con percorso) e motivazione 1 riga. 2) Istruzioni manuali di test UI:

apri pannello → incolla tabella → Analizza → Salva → salva progetto → riapri progetto → verifica che la preview sia popolata.
3) Conferma esplicita che:

non è stato implementato alcun fetch web / scraping
non è stata implementata alcuna interpolazione di pericolosità
non è stato implementato calcolo Sa(T)

1) CLAUSOLA DI ARRESTO
Se durante l’implementazione scopri che:

non esiste un unico file UI “module selector” chiaramente usato, oppure
i metodi di persistenza non sono in verification_project.py ma altrove,
allora:

NON procedere per tentativi
scrivi STOP e chiedi esplicitamente quali file toccare.
INIZIA ORA.

📁 Files created / modified
Path Role
spectrum_paste_service.py NEW – domain service, data models (Ntc2018HazardRow/Profile), parser, builder and accessor API (parser honours POINT/COMMA, labels, quality, messages).
test_ntc2018_hazard_paste_parser.py NEW – unit‑tests for parser (decimal point, comma, missing rows, invalid tokens).
test_ntc2018_hazard_profile_persistence.py NEW – round‑trip test via VerificationProject ensuring profile serialisation (incl. raw_paste).
ntc2018_hazard_paste_panel.py NEW – thin Tkinter panel implementing the UI spec (fields, textarea, analyse/preview, save button).
verification_project.py MODIFIED – added SeismicInputs dataclass, seismic_inputs field, load/save logic for ntc2018_hazard_profile with backward compatibility.
module_selector.py MODIFIED – added button “Spettro NTC2018 (Paste)” and_open_hazard_paste() handler.
(plus incidental formatting changes) 
🧪 Manual UI testing steps
Launch the app (start module_selector as usual).
Click “Parametri sismici NTC2018 (Paste)” in the Parametri Normativa section.
In the window that appears:
Choose a Classe uso (I‑IV), enter VN and VR, optional site label.
Paste the entire EdiLus‑MS table into the textarea.
Click Analizza → the preview area should list one row per recognised state‑limite; Quality and Messaggi update accordingly.
Press Salva nel progetto → a confirmation dialog is shown.
Use any existing project‑save mechanism (e.g. via verification table) to write the .jsonp file.
Close and reopen the project file; reopen the hazard‑paste panel and note that the preview is still populated (profile was preserved).
✅ Implementation assurances
🚫 No web fetch / HTTP / scraping was added.
🚫 No interpolation or pericolosità calculation; the service only parses user‑pasted data.
🚫 No Sa(T) spectrum computation has been implemented.
All behaviour strictly follows the PLAN/SPEC/AUTOMATION documents.
The new unit tests (§8 PLAN) pass, and the overall suite remains green.

You're now set for the next development phase or review.
