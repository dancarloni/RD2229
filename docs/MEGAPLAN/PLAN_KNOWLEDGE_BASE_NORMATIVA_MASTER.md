
PLAN KNOWLEDGE BASE NORMATIVA – MASTER
Status: VINCOLO DURO (estendibile solo previa richiesta esplicita dell’utente)

1. Scopo del documento
Questo PLAN definisce la struttura vincolante della Knowledge Base normativa del software di calcolo strutturale.
La Knowledge Base (KB):

è l’unica fonte autorevole di contenuto tecnico‑normativo;
è consumata da GitHub Copilot, dal motore di verifica e dalla generazione della relazione di calcolo;
garantisce difendibilità tecnico‑legale, tracciabilità e coerenza multi‑norma.
Il documento non contiene formule e non sostituisce il contenuto delle singole norme.

1. Principio fondamentale (non negoziabile)

I PLAN definiscono l’architettura.
La Knowledge Base normativa contiene:prescrizioni;
limiti;
ipotesi;
riferimenti normativi.
È vietato:

duplicare contenuti normativi nei PLAN;
introdurre formule o coefficienti normativi nel codice senza riferimento KB;
generare verifiche prive di citazione normativa.

1. Ruolo della Knowledge Base
La Knowledge Base normativa serve a:

supportare l’implementazione dei moduli di verifica;
alimentare automaticamente:messaggi di verifica;
warning;
NOT_APPLICABLE;
generare relazioni di calcolo difendibili;
consentire confronti tra norme a parità di modello di analisi.

1. Struttura obbligatoria della Knowledge Base
La Knowledge Base è suddivisa in file separati e indipendenti, uno per ciascun corpus normativo.
4.1 File normativi principali
Devono esistere almeno i seguenti file:

KB_RD2229_1939.md
KB_DM_1992_TA.md
KB_DM_1996_TA.md
KB_NTC2018.md
KB_EUROCODICI.md
Ogni file rappresenta una norma e una sola norma.

1. Struttura interna obbligatoria di ogni file KB
Ogni file KB deve seguire esattamente questa struttura concettuale:

Identità normativatitolo ufficiale;
riferimento G.U. / EN;
stato (vigente / abrogata / fallback).
Campo di applicazionestrutture ammesse;
materiali;
limiti dimensionali e concettuali.
Ipotesi fondamentalilinearità / non linearità;
comportamento elastico;
semplificazioni ammesse.
Prescrizioni di calcolocosa deve essere verificato;
quali grandezze sono richieste;
quali verifiche sono obbligatorie.
Limiti normativilimiti di resistenza;
limiti di esercizio;
condizioni di esclusione.
Rinvii e integrazionirinvii ad altre norme;
rinvii alla “buona tecnica”;
casi di lacuna normativa.
Citazioni puntualicapitolo;
paragrafo;
eventuale comma.

1. Gestione dei rinvii agli Eurocodici
Gli Eurocodici possono essere utilizzati solo come:

integrazione esplicita;
fallback dichiarato;
supporto a norme italiane carenti.
Ogni uso degli Eurocodici deve:

essere motivato;
citare esplicitamente la norma italiana che rinvia o è carente;
essere riportato nella relazione di calcolo.

1. Relazione di calcolo (integrazione obbligatoria)
La Knowledge Base deve consentire alla relazione di calcolo di:

citare automaticamente:norma;
capitolo;
paragrafo;
distinguere chiaramente:analisi strutturale;
verifica normativa;
evidenziare i casi di:fallback Eurocodice;
confronto tra norme.
La relazione non può contenere affermazioni prive di riferimento KB.

1. Confronto tra norme
Il confronto tra norme è ammesso solo se:

il modello di analisi è identico;
il metodo di calcolo è identico;
le ipotesi sono compatibili.
La Knowledge Base deve consentire:

mappature concettuali tra prescrizioni;
esplicitazione delle differenze.

1. Integrazione con Copilot e sviluppo software
GitHub Copilot deve:

usare i file KB come fonte primaria;
non introdurre coefficienti non presenti in KB;
segnalare TODO se una prescrizione non è presente;
rifiutare implementazioni prive di base normativa.

1. Estensioni future consentite
Sono ammesse solo previa estensione formale del PLAN:

aggiunta di nuove norme;
aggiornamenti normativi;
KB dedicate (es. muratura, ponti, opere speciali).

1. Criteri di accettazione
La Knowledge Base normativa è conforme a questo PLAN se:

ogni verifica richiama almeno una voce KB;
ogni limite è tracciabile a una fonte;
la relazione di calcolo è ricostruibile a posteriori;
non esistono contenuti normativi fuori dalla KB.

Questo PLAN è vincolante per tutta la gestione della Knowledge Base normativa del progetto.
