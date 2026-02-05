# Indicizzazione delle funzionalità di PrincipCA_TA.bas

Questo file elenca e descrive le principali funzionalità, routine e aree di calcolo presenti in visual_basic/PrincipCA_TA.bas, organizzate per tipo di calcolo e forma di sezione.

---

## 1. Tipi di calcolo eseguiti
- Calcolo delle sollecitazioni (momento, taglio, ecc.)
- Verifica di resistenza a flessione e taglio
- Calcolo armature minime e massime
- Verifica di duttilità
- Calcolo delle tensioni nei materiali (calcestruzzo, acciaio)
- Verifica di stati limite (SLE, SLU)
- Calcolo delle deformazioni

## 2. Forme di sezione gestite
- Sezioni rettangolari
- Sezioni a T
- Sezioni a doppio T
- Sezioni circolari
- Sezioni generiche (eventualmente poligonali)
- Sezioni scatolari

## 3. Indicizzazione delle funzioni e riferimenti

| Funzione/Subroutine                | Tipo di calcolo                | Forma sezione         | Riferimento (sezione del file)         |
|------------------------------------|-------------------------------|----------------------|----------------------------------------|
| CalcolaMomentoUltimo               | Momento resistente SLU        | Tutte                | PrincipCA_TA.bas, sezione: CalcolaMomentoUltimo |
| VerificaTaglio                     | Verifica taglio SLU           | Tutte                | PrincipCA_TA.bas, sezione: VerificaTaglio       |
| CalcolaArmatureMinime              | Armatura minima               | Tutte                | PrincipCA_TA.bas, sezione: CalcolaArmatureMinime|
| CalcolaArmatureMassime             | Armatura massima              | Tutte                | PrincipCA_TA.bas, sezione: CalcolaArmatureMassime|
| VerificaDuttilita                  | Duttilità                     | Tutte                | PrincipCA_TA.bas, sezione: VerificaDuttilita    |
| CalcolaTensioniMateriali           | Tensioni materiali            | Tutte                | PrincipCA_TA.bas, sezione: CalcolaTensioniMateriali|
| CalcolaDeformazioni                | Deformazioni                  | Tutte                | PrincipCA_TA.bas, sezione: CalcolaDeformazioni  |
| CalcoloSezioneRettangolare         | Tutti i calcoli               | Rettangolare         | PrincipCA_TA.bas, sezione: CalcoloSezioneRettangolare|
| CalcoloSezioneT                    | Tutti i calcoli               | T                    | PrincipCA_TA.bas, sezione: CalcoloSezioneT      |
| CalcoloSezioneDoppioT              | Tutti i calcoli               | Doppio T             | PrincipCA_TA.bas, sezione: CalcoloSezioneDoppioT|
| CalcoloSezioneCircolare            | Tutti i calcoli               | Circolare            | PrincipCA_TA.bas, sezione: CalcoloSezioneCircolare|
| CalcoloSezioneScatolare            | Tutti i calcoli               | Scatolare            | PrincipCA_TA.bas, sezione: CalcoloSezioneScatolare|
| CalcoloSezioneGenerica             | Tutti i calcoli               | Generica             | PrincipCA_TA.bas, sezione: CalcoloSezioneGenerica|

---

Per dettagli su una specifica funzione, routine o variabile, consultare direttamente il file PrincipCA_TA.bas o richiedere un approfondimento.