
FIRE_ANALISI_AVANZATA_L3_FEM – Analisi avanzata termo‑meccanica (Livello 3)
Status: STABILE
Ruolo: Specifica tecnica per integrazione analisi avanzata L3 (FEM) nel modulo INCENDIO

1. Scopo del documento
Questo documento definisce l’integrazione dell’analisi avanzata L3 per le verifiche di resistenza al fuoco, basata su analisi termo‑meccanica accoppiata mediante modelli FEM.
L’obiettivo è:

estendere il modulo INCENDIO oltre i metodi semplificati (L1/L2)
consentire verifiche per casi fuori campo dei metodi semplificati
mantenere coerenza con l’architettura esistente

1. Inquadramento normativo
L’analisi avanzata L3 è ammessa da:

EN 1991‑1‑2 – Azioni in caso di incendio
EN 1992‑1‑2 – Metodi di calcolo avanzati
Caratteristiche normative:

metodo prestazionale
richiede competenza specialistica
richiede esplicitazione delle ipotesi modellistiche

1. Quando è obbligatorio/consigliato L3
L’uso di L3 è obbligatorio o fortemente consigliato quando:

R90 / R120 con snellezza elevata
effetti del II ordine non trascurabili
sezione efficace prossima a collasso
geometrie non tabellabili
richiesta di ottimizzazione prestazionale
In tali casi:

L2 → NON_AMMESSO
suggerimento automatico → L3

1. Architettura software L3
4.1 Estensione CodeModule_INCENDIO
Il CodeModule_INCENDIO deve supportare un sottosolver:

Solver_L3_FEM
Responsabilità:

generazione del modello FEM
analisi termica transiente
analisi meccanica accoppiata
valutazione del collasso

1. Modello FEM – Struttura
5.1 Dominio

discretizzazione della sezione o dell’elemento
elementi solidi o beam‑fiber
5.2 Analisi termica

incendio ISO 834 o parametrico
conduzione termica nel tempo
output: campo di temperatura $T(x,y,t)$
5.3 Analisi meccanica

leggi costitutive dipendenti da $T$
non linearità:materiale
geometrica (II ordine)

1. Accoppiamento termo‑meccanico
Schema di calcolo:

step termico $t_i → T_i$
aggiornamento proprietà materiali
step meccanico
verifica di convergenza
incremento temporale
Criterio di arresto:

perdita di convergenza
superamento deformazioni limite
collasso globale o locale

1. Criterio di verifica L3
La verifica non è puntuale su una sezione, ma temporale:

determinazione del tempo di collasso $t_{coll}$
Esito:

se $t_{coll} ≥ t_{req}$ → OK
se $t_{coll} < t_{req}$ → NOT_OK

1. Output dell’analisi L3
Il VerificationResultItem deve includere:

fire_method = L3
fire_time_achieved = t_coll
esito (OK / NOT_OK)
warning_note (ipotesi FEM, sensibilità)
riferimento al modello utilizzato
⚠️ I risultati FEM non sostituiscono la relazione tecnica.

1. Requisiti di input aggiuntivi
Per L3 sono richiesti:

parametri FEM (mesh, passo temporale)
scelta del tipo di elemento
criteri di convergenza
Tali parametri:

non sono normativi
devono essere versionati

1. Validazione e responsabilità

L3 richiede validazione specialistica
i risultati devono essere:confrontati con L2 (se possibile)
documentati in modo esteso

1. Test e benchmark L3

test di convergenza
confronto con casi noti di letteratura
confronto L2 vs L3

1. Integrazione nella roadmap
Dopo integrazione L3:

aggiornare FIRE_NEXT_STEPS_ROADMAP.md
stato modulo: L1/L2/L3 completo

1. Limiti di utilizzo
L3 non deve essere usato:

senza documentazione
come sostituto automatico dei metodi semplificati

1. Collegamenti

FIRE_ESTENSIONE_R90_R120.md
FIRE_VERIFICA_TRAVI_A_CALDO.md
FIRE_CODEMODULE_INCENDIO.md
FIRE_NEXT_STEPS_ROADMAP.md
