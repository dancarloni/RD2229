# Fase M — Solutore FEM beam 2D (Euler-Bernoulli)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | <hash-cloud> |
| **Data completamento** | 2026-03-10 |
| **Test eseguiti** | 2366 |
| **Norma/e di riferimento** | EN 1992, EN 1993, NTC2018 |
| **Priorità** | Alta (dipendenza di K per SolutoreFEM) |

---

## Descrizione

Implementa il solutore FEM per travi e telai piani 2D con elementi beam di Euler-Bernoulli. Completa il `SolutoreFEM` stub lasciato in Fase K (`src/grafici/spostamenti.py`). Usa `scipy.sparse` per la costruzione e il riempimento delle matrici di rigidezza, e `scipy.sparse.linalg.spsolve` per la soluzione efficiente del sistema lineare. Il modulo è riutilizzabile sia per la verifica dei telai (Fase L, metodo Cross-Pozzati) sia per analisi modale (Fase U) e pushover (Fase U).

---

## Teoria e fondamenti strutturali

### Elemento beam Euler-Bernoulli piano

Ogni elemento beam piano ha 6 GDL: traslazione assiale, traslazione trasversale e rotazione ai due nodi (u_1, v_1, θ_1, u_2, v_2, θ_2).

**Matrice di rigidezza locale — contributo assiale:**

```text
k_assiale = (EA/L) · [ 1  -1 ]
                      [-1   1 ]
```

**Matrice di rigidezza locale — contributo flessionale:**

```text
k_fless = (EI/L³) · [  12    6L   -12    6L ]
                     [  6L   4L²   -6L   2L² ]
                     [ -12   -6L    12   -6L ]
                     [  6L   2L²   -6L   4L² ]
```

La matrice locale completa 6×6 viene assemblata combinando i due contributi sui rispettivi GDL.

### Matrice di trasformazione

Per un elemento inclinato di angolo α rispetto all'asse globale X:

```text
T_e = [ cosα  sinα  0   0     0    0  ]
      [-sinα  cosα  0   0     0    0  ]
      [  0     0    1   0     0    0  ]
      [  0     0    0  cosα  sinα  0  ]
      [  0     0    0 -sinα  cosα  0  ]
      [  0     0    0   0     0    1  ]
```

La matrice locale in coordinate globali è: `K_e_glob = T_e^T · k_e · T_e`

### Assemblaggio matrice globale

```text
K_G = Σ T_e^T · k_e · T_e
```

La connettività DOF globali viene costruita da una tabella di connettività: per ogni elemento, i 6 GDL locali corrispondono a 6 indici nel vettore globale.

La matrice viene costruita con `scipy.sparse.lil_matrix` durante il riempimento e convertita a `csr_matrix` prima della soluzione.

### Carichi nodali equivalenti

Per carico distribuito uniforme q su trave orizzontale di luce L:

```text
F_eq = { qL/2,  qL²/12,  qL/2,  -qL²/12 }
```

(traslazioni trasversali e momenti ai nodi)

### Applicazione condizioni al contorno

- Incastro: 3 GDL vincolati (u=0, v=0, θ=0)
- Cerniera: 2 GDL vincolati (u=0, v=0)
- Carrello: 1 GDL vincolato (v=0 o u=0 secondo direzione)

Metodo di eliminazione diretta: le righe e colonne dei GDL vincolati vengono rimosse dalla matrice globale prima della soluzione (alternativa: metodo penalty con valore elevato sulla diagonale).

### Soluzione e post-processing

```text
u = spsolve(K_G_ridotta, F_G_ridotta)
```

Dopo la soluzione, gli spostamenti nodali vengono utilizzati per ricostruire i diagrammi continui M(x), V(x), N(x) tramite interpolazione con polinomi di Hermite:

```text
M(x) = EI · v''(x)    da polinomio di Hermite cubico
V(x) = -EI · v'''(x)
N(x) = EA · u'(x)
```

---

## Diagramma dipendenze subfasi

```text
M.1 — Elemento beam 2D (k_e, T_e, F_eq)
 └── M.2 — Assemblaggio matrice globale sparsa
      └── M.3 — Applicazione condizioni al contorno
           └── M.4 — Soluzione sistema lineare (spsolve)
                └── M.5 — Post-processing M/V/N continui
                     └── M.6 — Completamento SolutoreFEM stub (Fase K)
                          └── M.7 — Test e validazione
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| SolutoreFEM (stub) | `src/grafici/spostamenti.py` | Completamento implementazione NotImplementedError |
| Telaio Fase L | `src/methods/rd2229/telaio/` | Confronto risultati FEM vs Cross-Pozzati |
| scipy.sparse | dipendenza esterna | Costruzione e soluzione matrice sparsa |
| scipy.sparse.linalg | dipendenza esterna | `spsolve` per sistema lineare |
| numpy | dipendenza esterna | Operazioni matriciali elementi locali |
| registro_log | `src/core/registro_log.py` | Log assemblaggio, soluzione, condizionamento |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| EN 1992-1-1 §5.4 | Analisi strutturale lineare elastica |
| EN 1993-1-1 §5.2 | Analisi strutturale per elementi in acciaio |
| NTC2018 §7.3 | Modelli di analisi strutturale |
| Pozzati — Teoria e Tecnica delle Strutture Vol.2 | Formule soluzioni analitiche di confronto |
| Hughes T.J.R. — The Finite Element Method (2000) | Riferimento teorico FEM beam |
| Bathe K.J. — Finite Element Procedures (1996) | Assemblaggio, BC, condizionamento |
| Zienkiewicz O.C. — The Finite Element Method (2000) | Polinomi di Hermite, post-processing |

---

## Struttura file/directory prevista

```text
src/fem/
├── __init__.py               # Export pubblico: ElementoBeam, Assemblatore, SolutoreFEM
├── elemento_beam.py          # (~200 righe) matrice rigidezza locale, T_e, F_eq
├── assemblaggio.py           # (~200 righe) assemblaggio globale scipy.sparse, connettività DOF
├── condizioni_contorno.py    # (~100 righe) eliminazione GDL vincolati, metodo penalty
├── solutore.py               # (~150 righe) spsolve, verifica condizionamento, log
└── postprocessing.py         # (~200 righe) diagrammi M/V/N continui, polinomi Hermite

tests/
├── test_fem_beam.py          # (~80 test) trave appoggiata, incastrata, asolata
└── test_fem_telaio.py        # (~40 test) portale, telaio multipiano, confronto Cross-Pozzati
```

---

## Subfasi pianificate

### M.1 — Elemento beam 2D Euler-Bernoulli

**Stato**: COMPLETATO (2026-03-10, sessione Copilot)

- [x] Implementare dataclass `ElementoBeam` con attributi E, A, I, L, angolo
- [x] Calcolare matrice rigidezza locale 6×6 (assiale + flessionale)
- [x] Implementare matrice di trasformazione T_e per elemento inclinato
- [x] Calcolare vettore carichi nodali equivalenti per carico distribuito uniforme
- [x] Calcolare vettore carichi nodali equivalenti per carico triangolare
- [x] Aggiungere `to_dict()` per serializzazione
- [x] Test unitari: verifica valori k_e per trave nota (L=5m, E=30000 MPa, I=1000 cm⁴)

Implementazione estesa oltre il minimo pianificato:
- supporto a carico concentrato, trapezoidale, triangolare inverso, parabolico e distribuzione generica con fallback numerico
- combinazione di piu carichi sullo stesso elemento
- supporto iniziale a cedimenti nodali e rotazioni impresse tramite carichi equivalenti locali
- export pubblico del nuovo pacchetto `src/fem/`

### M.2 — Assemblaggio matrice globale sparsa

**Stato**: COMPLETATO (2026-03-10, sessione cloud Copilot)

- [x] Definita struttura dati nodi e tabella connettività (DOF globali per elemento)
- [x] Costruita matrice K_G con `scipy.sparse.lil_matrix`
- [x] Conversione `lil_matrix` → `csr_matrix` per efficienza soluzione
- [x] Assemblato vettore carichi globale F_G
- [x] Log dimensioni matrice, sparsità, numero non-zero
- [x] Test: portale 2 campate, verifica dimensioni e simmetria K_G

### M.3 — Applicazione condizioni al contorno

**Stato**: COMPLETATO (2026-03-10, sessione cloud Copilot)

- [x] Implementato enum `TipoVincolo` (INCASTRO, CERNIERA, CARRELLO_V, CARRELLO_U, LIBERO)
- [x] Metodo eliminazione diretta: rimozione righe/colonne GDL vincolati
- [x] Metodo penalty come alternativa configurabile
- [x] Verifica che K_G_ridotta sia non singolare (rango pieno)
- [x] Test: trave appoggiata (2 cerniere), incastro-libera, incastro-cerniera

### M.4 — Soluzione sistema lineare

**Stato**: COMPLETATO (2026-03-10, sessione cloud Copilot)

- [x] Soluzione con `scipy.sparse.linalg.spsolve`
- [x] Calcolo numero di condizionamento (opzionale, costoso — attivabile da flag)
- [x] Reimpostazione GDL vincolati a zero nel vettore soluzione completo
- [x] Log: tempo soluzione, norma residuo `||K·u - F||`
- [x] Gestione errori: matrice singolare, divergenza
- [x] Test: trave appoggiata Q=10 kN/m, L=6m — verifica spostamento massimo analitico

### M.5 — Post-processing spostamenti e sollecitazioni

**Stato**: COMPLETATO (2026-03-10, sessione cloud Copilot)

- [x] Estratti spostamenti nodali per ogni elemento
- [x] Ricostruito profilo spostamenti v(x) con polinomio di Hermite cubico
- [x] Calcolato M(x) = EI·v''(x) da derivata seconda polinomio
- [x] Calcolato V(x) = -EI·v'''(x) da derivata terza
- [x] Calcolato N(x) = EA·u'(x) da derivata prima spostamento assiale
- [x] Output: array numpy di punti (x, M, V, N) per diagrammi
- [x] Aggiunto `passaggi_calcolo: list[str]` con formula utilizzata per ogni grandezza
- [x] Test: trave appoggiata — verifica M_max = qL²/8 al centro

### M.6 — Completamento SolutoreFEM stub (Fase K)

**Stato**: COMPLETATO (2026-03-10, sessione cloud Copilot)

- [x] Letto stub esistente in `src/grafici/spostamenti.py`
- [x] Rimosso `raise NotImplementedError`
- [x] Collegato al nuovo modulo `src/fem/solutore.py`
- [x] Adattata interfaccia input/output al contratto esistente
- [x] Verificata compatibilità con `GraficiSollecitazioni` (K.1) e `GraficiSpostamenti` (K.3)

### M.7 — Test e validazione

**Stato**: COMPLETATO (2026-03-10, sessione cloud Copilot)

- [x] Test trave semplicemente appoggiata: confronto con soluzione analitica Pozzati
- [x] Test trave a sbalzo: spostamento e rotazione estremità libera
- [x] Test portale a un piano: momento di incastro, distribuzione Cross-Pozzati
- [x] Test telaio multipiano (3 piani, 2 campate): confronto con Fase L
- [x] Test con carichi concentrati e distribuiti misti
- [x] Benchmark performance: tempo assemblaggio e soluzione per telaio 100 elementi
- [x] Verifica simmetria risultati per strutture simmetriche caricate simmetricamente

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/fem/__init__.py` | 20 | Export pubblico modulo FEM |
| `src/fem/elemento_beam.py` | 200 | Matrice rigidezza locale, T_e, F_eq |
| `src/fem/assemblaggio.py` | 200 | Assemblaggio globale, connettività DOF, scipy.sparse |
| `src/fem/condizioni_contorno.py` | 100 | Applicazione BC, eliminazione/penalty |
| `src/fem/solutore.py` | 150 | spsolve, condizionamento, log |
| `src/fem/postprocessing.py` | 200 | Diagrammi M/V/N, polinomi Hermite |
| `tests/test_fem_beam.py` | 80 test | Casi noti elementi singoli e travi |
| `tests/test_fem_telaio.py` | 40 test | Telai multipiano, confronto Cross-Pozzati |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| Tipo elemento: solo Euler-Bernoulli o anche Timoshenko? | A) Solo E-B (semplice, adeguato per L/h > 10) / B) Timoshenko opzionale (preciso per travi tozze L/h < 10) |
| Integrazione con Fase L: FEM parallelo o sostituto Cross-Pozzati? | A) Parallelo (confronto, verifica) / B) Sostituto (se convergenza dimostrata) |
| Metodo BC: eliminazione diretta o penalty? | A) Eliminazione diretta (esatto, più complesso) / B) Penalty (semplice, numero condizionamento peggiore) |
| Gestione non-linearità geometrica | A) Non prevista in Fase M / B) Stub per Fase U (pushover) |
| Interfaccia con GUI Qt | A) Nessuna GUI in Fase M (solo backend) / B) Widget debug visualizzazione matrice K_G |

## Decisioni architetturali storicizzate — M.1

- 2026-03-10: per M.1 viene adottato beam 2D di Euler-Bernoulli puro; Timoshenko resta esplicitamente fuori per non contaminare il nucleo locale dell'elemento.
- 2026-03-10: le unita sono fissate e coerenti con il repo (`cm`, `kg/cm²`, `kg·cm`, `kg/cm`), senza conversioni implicite.
- 2026-03-10: l'angolo di input dell'elemento accetta sia gradi sia radianti, con normalizzazione interna in radianti.
- 2026-03-10: `ElementoBeam` include anche `id_nodo_iniziale` e `id_nodo_finale` per preparare la connettivita della M.2.
- 2026-03-10: i carichi sono modellati con architettura modulare a oggetti separati, non come metodi monolitici dell'elemento.
- 2026-03-10: la combinazione di piu carichi sullo stesso elemento e supportata gia in M.1.
- 2026-03-10: cedimenti e rotazioni impresse sono inclusi gia in M.1, ma mantenuti separati logicamente dai carichi meccanici ordinari.
- 2026-03-10: per carichi complessi si usa formula chiusa quando disponibile e fallback numerico Gauss-Legendre negli altri casi.
- 2026-03-10: la convenzione dei segni del modulo FEM locale e esplicita e documentata, derivata dalla classica FEM; l'adattamento alle convenzioni grafiche del repo resta alle subfasi successive.

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Singolarità matrice | K_G singolare se BC insufficienti o struttura sconnessa | Verifica rango prima di spsolve, errore esplicito |
| Numero di condizionamento elevato | Strutture con rigidezze molto diverse (es. pilastri + travi snelle) | Log condizionamento, normalizzazione facoltativa |
| Compatibilità stub Fase K | Interfaccia SolutoreFEM non documentata, solo NotImplementedError | Leggere chiamanti esistenti prima di definire firma |
| Memoria per telai grandi | Matrice densa per telaio con molti elementi | Usare sempre `csr_matrix`, mai array denso |

---

## Note di pianificazione

- La Fase M è prerequisito logico per la Fase U (analisi modale e pushover richiedono assemblaggio [K] e [M]).
- Il modulo `src/fem/` deve essere completamente indipendente dalla norma: le verifiche normative rimangono negli altri moduli.
- Il confronto FEM vs Cross-Pozzati (Fase L) è un test di validazione fondamentale: per telai regolari i risultati devono coincidere entro < 1%.
- La Fase M non include la matrice di massa [M]: questa verrà aggiunta in Fase U per l'analisi modale.

## Storicizzazione

- 2026-03-10 — M.1 completata in `src/fem/elemento_beam.py` e `tests/test_fem_beam.py`.
- 2026-03-10 — Test eseguiti per M.1: 16 passati, 0 falliti.
- 2026-03-10 — Pianificazione interattiva completata prima dell'implementazione, come richiesto dai vincoli operativi permanenti.
- 2026-03-10 — M.2–M.7 completate in `src/fem/assemblaggio.py`, `condizioni_contorno.py`, `solutore.py`, `postprocessing.py`, `src/grafici/spostamenti.py`.
- 2026-03-10 — Test eseguiti per M.2–M.7: 2366 passati, 0 falliti (`tests/test_fem_beam.py`, `tests/test_fem_telaio.py`, `tests/test_grafici_spostamenti.py`).
- 2026-03-10 — Aggiornata checklist subfasi, storicizzazione dettagliata, commit <hash-cloud>.
