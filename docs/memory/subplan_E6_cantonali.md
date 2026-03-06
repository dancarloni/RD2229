# E.6 — Cantonali e Aperture
# Contesto completo per implementazione futura

## Scope (3 sotto-problemi, 2 in E.6)

### A) Ribaltamento del cantonale (meccanismo 3D) — PRIORITA' ALTA
Un cuneo di muratura delimitato da fratture diagonali a ~45° nelle due pareti
concorrenti si stacca e ribalta. Tipico di tetti a padiglione con puntoni
spingenti. L'asse di rotazione e' perpendicolare al piano a 45° tra le pareti.

### B) Riduzione resistenza maschi d'angolo per aperture — PRIORITA' ALTA
Apertura (porta/finestra) posizionata vicino all'angolo riduce la sezione
del maschio d'angolo e peggiora l'ammorsamento tra pareti ortogonali.

### C) Apertura nuovi vani in pareti portanti — FASE SEPARATA (Fase R)
Confronto rigidezza/resistenza prima/dopo, telaio cerchiatura. NON in E.6.

## Decisioni Q&A complete (2 round, 16 domande)

### Ribaltamento cantonale
- Modellazione: modello semplificato 2D (proiezione cuneo su piano a 45°),
  come fanno 3Muri e PRO_CineM. Modello 3D completo come TODO futuro.
- Geometria cuneo: selezione 2 pareti dal modello + input diretto (entrambi)
- Angolo asse rotazione: configurabile (default 45°) + auto-calcolabile
  da spessori pareti (arctan(t2/t1))
- Modulo: SEPARATO `src/methods/muratura/cantonale.py` (massima modularita')
- Carichi: tutti configurabili singolarmente (peso cuneo, puntone, solaio,
  catena, cordolo D.3)

### Spinta puntoni copertura
- 2 formulazioni automatiche:
  - Formula A: F_h = q * L / (2 * tan(alpha)) — da carico distribuito al m²
  - Formula B: F_h = V / tan(alpha) — da forza verticale nota
- Input generico: forza F diretta con direzione e punto di applicazione
- Tipologie: padiglione, capanna, generica (tutte supportate)

### Riduzione resistenza aperture vicino angolo
- Diagnostica distanza apertura-angolo con 3 livelli di soglia:
  - Normativa NTC2018 (se presente vincolo esplicito — da verificare)
  - Regola pratica: d_min = max(t_muro, 100 cm)
  - Configurabile dall'utente
- Esito: OK / WARNING / FAIL con messaggio e distanza misurata
- Coefficiente riduzione: lineare k = min(distanza / d_min, 1.0)
- Riduzione agisce su: selezionabile dall'utente (V_Rd, alpha_0, o entrambi)
- Flag maschio cantonale: automatico con override manuale

### Integrazione con altri moduli
- TipoMeccanismo: aggiungere RIBALTAMENTO_CANTONALE in cinematica.py
- Incluso in analisi_tutti_meccanismi() con flag "3D" per distinguerlo
- Collegamento D.3: default = cordolo come ritegno generico (D.3.5);
  evoluzione = nodo angolo D.3.6 fornisce H specifica al cantonale
- Entrambi gli approcci implementati, selezionabili

## Formule chiave

### Peso cuneo d'angolo (proiezione 2D su piano a 45°)
```
# Due pareti concorrenti con distacco diagonale
L1_dist = lunghezza distacco sulla parete 1 [cm]
L2_dist = lunghezza distacco sulla parete 2 [cm]
t1 = spessore parete 1, t2 = spessore parete 2 [cm]
h = altezza cuneo [cm]
gamma = peso specifico muratura [kg/cm³]

# Peso dei due cunei triangolari
W_cuneo_1 = 0.5 * h * L1_dist * t1 * gamma  [kg]
W_cuneo_2 = 0.5 * h * L2_dist * t2 * gamma  [kg]
W_cuneo = W_cuneo_1 + W_cuneo_2

# Angolo asse rotazione
theta = 45° (default) oppure arctan(t2/t1) (auto)
```

### Spinta puntone
```
# Formula A — da carico distribuito
F_h = q_mq * L_puntone / (2 * tan(alpha_pendenza))  [kg]

# Formula B — da forza verticale
F_h = V_puntone / tan(alpha_pendenza)  [kg]
```

### Coefficiente riduzione angolo
```
d = distanza apertura piu' vicina dall'angolo [cm]
d_min = max(t_muro, 100)  [cm]  # default, configurabile
k = min(d / d_min, 1.0)  # 0.0 = apertura sull'angolo, 1.0 = nessuna riduzione

# Applicazione (a scelta utente):
V_Rd_ridotto = V_Rd * k        # riduzione taglio
alpha_0_ridotto = alpha_0 * k  # riduzione ammorsamento
```

### Moltiplicatore di collasso cantonale (schema ReLUIS)
```
# Equilibrio alla rotazione attorno alla cerniera alla base del cuneo
# Asse di rotazione a theta gradi tra le due pareti

# Momento stabilizzante (pesi x bracci orizzontali)
M_stab = W_cuneo * d_baricentro + N_sommita * d_N + F_catena * braccio_catena
         + H_cordolo * braccio_cordolo  # se presente D.3

# Momento ribaltante (forze orizzontali x bracci verticali)
M_rib = W_cuneo * h_baricentro + N_sommita * h + F_puntone * h_puntone

# Moltiplicatore di collasso
alpha_0 = M_stab / M_rib  # (coefficiente per forze sismiche)
```

## File da creare

| File | Contenuto |
|------|-----------|
| `src/methods/muratura/cantonale.py` | InputCantonale, SpintaPuntone, TipoCopertura, ribaltamento_cantonale(), diagnostica_apertura_angolo(), coefficiente_riduzione_angolo(), flag_maschio_cantonale(), RisultatoCantonale |

## File da modificare

| File | Modifica |
|------|----------|
| `src/methods/muratura/cinematica.py` | Aggiungere RIBALTAMENTO_CANTONALE a TipoMeccanismo enum. Aggiungere parametro opzionale `ritegno_sommitale` ai meccanismi. Integrare cantonale in analisi_tutti_meccanismi() con flag 3D. |
| `src/methods/muratura/discretizzazione.py` | Maschi d'angolo: assegnare automaticamente `is_cantonale = True`. Se apertura ravvicinata: calcolare e assegnare `fattore_riduzione_angolo`. |
| `src/methods/muratura/discretizzazione.py` → Maschio dataclass | Aggiungere campi opzionali: `is_cantonale: bool = False`, `fattore_riduzione_angolo: float = 1.0` |
| `src/report/tabulati_calcolo.py` | Sezioni "Meccanismo cantonale" e "Diagnostica aperture d'angolo" |

## File esistenti da riusare

| File | Cosa riusare | Righe chiave |
|------|-------------|-------------|
| `cinematica.py` | RisultatoMeccanismo, ForzaCatena, ParametriSismici, cinematica_lineare(), cinematica_non_lineare() | Ribaltamento composto (235-283) come template per cantonale |
| `cinematica.py` | analisi_tutti_meccanismi() | Riga 620-654: lista meccanismi ordinata per alpha_0 |
| `discretizzazione.py` | Maschio dataclass, discretizza_parete() | Righe 67-140 (Maschio), 262-437 (discretizza) |
| `modello_edificio.py` | Parete, Apertura, Edificio | Righe 150-170 (Apertura), 195-252 (Parete) |
| `verifiche.py` | Verifiche taglio/compressione | Per applicare k di riduzione |

## Riferimenti normativi e letteratura

### Normativa
- Circ. n.7/2019 §C8A.4.1 — cinematica lineare meccanismi locali
- NTC2018 §7.8.2 — resistenza maschi murari nel piano
- NTC2018 §8.4.1 — interventi locali (per Fase R, non E.6)

### Letteratura
- **Schede ReLUIS** — meccanismi di collasso locali (ribaltamento cantonale)
  URL: https://www.geostrutture.eu/images/download/ministero/reluismeccanismi.pdf
  Contengono: geometria cuneo, formule alpha_0, bracci, schemi grafici

- **Casapulla & Maione (2020)** — rocking analysis of corner mechanisms
  Primo studio sperimentale sul meccanismo d'angolo, simulando l'azione
  sismica attraverso la rotazione graduale della base

- **D'Ayala & Speranza (2003)** — mechanisms for historic masonry
  Gia' citato in cinematica.py come riferimento

- **Dolce M.** — schematizzazione e modellazione pareti, altezza efficace maschi
  Riduzione h_eff per aperture vicine, angolo di diffusione sforzi

- **Universita' di Pisa** — dispense meccanismi locali
  URL: https://docenti.ing.unipi.it/~a005843/Costruzioni%20in%20zona%20sismica/12-3G-ANALISI-MECCANISMI-LOCALI.pdf
  L'angolo del cuneo dipende dalla qualita' muraria: aumenta con muratura migliore

### Software di riferimento
- 3Muri: definisce blocchi diagonali + cerniera a 45°
- PRO_CineM (2S.I.): analisi cinematismi con cantonali
- FaTANext: meccanismi locali con analisi lineare/non lineare

## Note tecniche importanti

1. Il ribaltamento composto esistente (cinematica.py righe 235-283) modella
   un cuneo 2D su una SINGOLA parete. Il cantonale e' DIVERSO: coinvolge
   DUE pareti ortogonali con un cuneo che si distacca lungo fratture diagonali.

2. La proiezione 2D del cuneo 3D si fa sul piano a 45° tra le due pareti.
   In questo piano proiettato, il calcolo e' analogo al ribaltamento composto
   ma con peso e geometria derivati dalle due pareti reali.

3. Il flag `is_cantonale` sul Maschio e' INDIPENDENTE dal meccanismo di
   ribaltamento. Serve per la riduzione di resistenza nel piano (E.6.B),
   non per il meccanismo fuori piano (E.6.A).

4. La distanza minima apertura-angolo: NTC2018 NON ha un vincolo esplicito
   numerico. La regola d_min = max(t, 100 cm) viene dalla pratica
   professionale e dalle linee guida regionali.
