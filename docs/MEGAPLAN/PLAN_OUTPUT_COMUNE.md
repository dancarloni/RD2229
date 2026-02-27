
PLAN – OUTPUT COMUNE
Status: STABILE Ambito: Risultati, post‑processing, export Vincolo: Un solo schema di output per tutte le norme e tutti i moduli
Scopo
Definire uno schema di output unico, coerente e tracciabile che rappresenti l’unica fonte di verità per:

post‑processing
visualizzazione grafica
confronti tra norme
export e reporting tecnico‑legale
Il post‑processing non ricalcola: interpreta esclusivamente l’output.


Principi non negoziabili

Single Output Schema: tutti i moduli producono lo stesso tipo di risultato
Read‑only: la GUI risultati non modifica i dati
Tracciabilità normativa: ogni risultato cita norme e paragrafi
Riproducibilità: grafici e report rigenerabili dall’output salvato


Struttura concettuale unica
VerificationResultItem

check_id
element_id
norma (NTC2018, RD2229/39, DM92, DM96, ECx)
stato_limite (SLU, SLE, SLV, ecc.)
esito (OK / NOT_OK / NOT_APPLICABLE / ERROR)
utilisation (domanda/capacità)
combinazione_critica
domanda (mappa valori significativi)
capacità (mappa valori resistenti)
norm_references (norma, capitolo, paragrafo)
warning_note
metadata (data, versione solver, progetto)
Tutti i risultati del progetto sono una collezione di VerificationResultItem.


Proprietà chiave

Confronto diretto tra norme diverse sullo stesso elemento
Ordinamento per criticità (utilisation)
Aggregazione per elemento, verifica, stato limite


Post‑processing consentito
Tabelle

una riga = una verifica
colonne minime:elemento
check
norma
stato limite
utilisation
esito
Grafica (derivata dall’output)

sezione in scala reale
distribuzione delle tensioni
asse neutro (posizione numerica + rappresentazione)
Regola: nessun valore grafico non presente nell’output.


Output testuale e report
Contenuto minimo

intestazione progetto
norma applicata
input sintetici
risultati (SLU/SLE/SLV)
campo di validità
riferimenti normativi
Base teorica

ipotesi di calcolo
formule in forma simbolica
riferimenti normativi puntuali


Export
Formati ammessi

CSV (batch, confronti)
TXT strutturato
estensibile a PDF / Markdown
Regole di export

esporta solo dati visibili
includi sempre: norma, versione solver, data


Regole di integrazione

Tutte le GUI risultati leggono solo VerificationResultItem
Nessun modulo accede direttamente ai dati interni di altri moduli
L’output è l’unica base per confronti e report


Criteri di accettazione

Tutti i CodeModule producono output conforme
Nessuna GUI richiede dati esterni allo schema
NOT_APPLICABLE sempre esplicito e visibile
Export identico a parità di output
