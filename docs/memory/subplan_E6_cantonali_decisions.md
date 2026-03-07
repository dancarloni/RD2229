# FASE E.6.1 — Ribaltamento Cantonale (Cuneo 3D)

Questo file documenta le decisioni architetturali e i vincoli implementativi per il modulo `cantonale.py`, sviluppato il 08/03/2026.

## Decisioni Architetturali (Cinematica 3D)

1. **Modello e Baricentro (Caso A1):**
   Il cuneo è idealizzato come composto da due prismi a base triangolare in sommità, con vertice di fessurazione verso il basso. Il baricentro delle masse murarie è calcolato analiticamente alla quota fissa: $z_g = \frac{2}{3} h$.
2. **Spinta Copertura (Caso B1 come default):**
   La spinta del puntone ($H, V$) sul cuneo viene applicata per default sullo *spigolo interno*. Questo minimizza il braccio stabilizzante del peso $V$, ponendosi a favore di sicurezza. L'utente può comunque optare per il baricentro dell'impronta o lo spigolo esterno (`PosizioneSpinta` enum).
3. **Direzione Sismica e Proiezioni (Caso C1):**
   L'asse di rotazione orizzontale poggia sullo spigolo esterno ed è ruotato di un angolo $\beta$ (default 45° o ortogonale alla bisettrice). Tutte le forze e i bracci dei pesi in pianta ($x_g, y_g$) vengono proiettati matematicamente lungo la direzione ortogonale a questo asse per trovare il braccio stabilizzante puro.
4. **Catene e Tiranti (Caso D2):**
   Non assumiamo catene semplificate. L'input `InputCatenaCantonale` prevede `quota_z` e `angolo_pianta`. La forza della catena viene ridotta vettorialmente moltiplicandola per $\cos(|\beta - \alpha_{catena}|)$, rendendola efficace solo per la componente che si oppone realmente al ribaltamento.
5. **Cordolo D.3:**
   Il cordolo reticolare contribuisce unicamente come forza di ritegno orizzontale stabilizzante in sommità.

## Regole di Integrazione Future

Il modulo `esegui_verifica_cantonale(input_dati)` è standalone. Quando verrà integrato in `analisi_tutti_meccanismi()` (in Fase R o fine Fase E), dovrà semplicemente mappare i dati dal modello 3D globale dell'edificio agli input semplificati del cantonale. Nessun refactoring di `cantonale.py` è ammesso durante l'integrazione globale.


## FASE E.6.2 � Decisioni Riduzione Maschi
1. Soglie (A2): Normative NTC2018 ({min} = \max(t, 100 	ext{ cm})$) + Parametriche (modello proporzionale a step) + Personalizzate.
2. Indebolimento (B2): Limitazione asintotica (safe lower bound {min} = 0.20$) per evitare singolarita a 0 quando le aperture sfiorano i cantonali.
3. Indipendenza (C1): Completamente standalone tramite InputDiagnosticaAngolo e RisultatoDiagnosticaAngolo nel modulo cantonale.py.
