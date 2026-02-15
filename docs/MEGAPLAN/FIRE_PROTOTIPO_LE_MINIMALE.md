
FIRE_PROGRAMMA_FUTURO_L3_FEM – Programma di sviluppo futuro
Status: PIANIFICATO
Orizzonte temporale: medio‑lungo termine
Ruolo: Programma strategico per la realizzazione di un modulo FEM L3 al fuoco


1. Scopo del documento
Questo documento definisce un programma di sviluppo futuro per la realizzazione di un modulo avanzato di verifiche L3 al fuoco basato su FEM, da integrare nel sistema di calcolo strutturale già progettato.
Il programma non descrive il codice finale, ma:

stabilisce obiettivi tecnici
definisce architettura target
pianifica fasi di sviluppo incrementali
chiarisce responsabilità e limiti di utilizzo


2. Obiettivi del modulo L3 FEM
Il modulo L3 FEM dovrà consentire:

analisi termo‑meccanica accoppiata nel tempo
valutazione del tempo di collasso dell’elemento
gestione di casi fuori campo L1/L2
supporto a:R90 / R120 critici
snellezza elevata
II ordine non trascurabile
Il modulo non sostituisce L1/L2, ma li completa.


3. Inquadramento normativo di riferimento
Il modulo L3 FEM dovrà essere coerente con:

EN 1991‑1‑2 – Azioni in caso di incendio
EN 1992‑1‑2 – Metodi avanzati di calcolo
eventuali Annex nazionali applicabili
Principio chiave:


L3 è un metodo prestazionale, non prescrittivo.




4. Architettura target del sistema
4.1 Integrazione logica
Il modulo L3 FEM sarà integrato come:

CodeModule_INCENDIO
 ├─ Solver_L1
 ├─ Solver_L2
 └─ Solver_L3_FEM   ← nuovo modulo


Il Solver_L3_FEM dovrà essere completamente separato dai solver semplificati.


4.2 Interfaccia del Solver_L3_FEM
Interfaccia minima prevista:

build_fem_model(input)
run_thermal_analysis()
run_mechanical_analysis()
advance_time_step()
check_collapse()
get_time_of_failure()


5. Modello FEM – linee guida
5.1 Tipologia di modelli
In fase iniziale:

modelli beam‑fiber per travi e pilastri
In fase avanzata:

modelli 2D / 3D solidi


5.2 Analisi termica

incendio ISO 834 o parametrico
conduzione nel calcestruzzo
trasmissione alle armature
Output richiesto:

campo di temperatura $T(x,y,z,t)$


5.3 Analisi meccanica

leggi costitutive dipendenti da temperatura
non linearità:materiale
geometrica (II ordine)


6. Accoppiamento termo‑meccanico
Schema incrementale:

incremento temporale $\Delta t$
analisi termica
aggiornamento proprietà
analisi meccanica
verifica convergenza
Criteri di arresto:

mancata convergenza
superamento deformazioni limite
collasso locale o globale


7. Strategia di sviluppo incrementale
Fase 1 – Prototipo concettuale

solver FEM semplificato
beam‑fiber
confronto con L2
Fase 2 – Validazione

casi di letteratura
confronto con esempi EN 1992‑1‑2
test di sensibilità
Fase 3 – Estensione

modelli solidi
travi continue
pilastri snelli


8. Output e integrazione nel sistema
Il modulo L3 FEM dovrà produrre:

VerificationResultItem con:fire_method = L3
fire_time_achieved
esito
log di calcolo dettagliato
riferimento al modello FEM utilizzato


9. Test e qualità
Previsti:

test di convergenza numerica
test di regressione L2 vs L3
benchmark certificati
I test FEM non sostituiscono la validazione ingegneristica.


10. Responsabilità e limiti di utilizzo

L3 FEM richiede competenza specialistica
i risultati devono essere documentati
il software non sostituisce il giudizio del progettista


11. Collegamenti

FIRE_ANALISI_AVANZATA_L3_FEM.md
FIRE_CODEMODULE_INCENDIO.md
FIRE_NEXT_STEPS_ROADMAP.md
PLAN_CALCOLO.md
