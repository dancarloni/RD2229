# D.3 — Traliccio Reticolare Piano (Cordolo Metallico Reticolare)
# Contesto completo per implementazione — aggiornato dopo Q&A Round 2

## Concetto strutturale (VERIFICATO e CONFERMATO)

Il traliccio e' disposto ORIZZONTALMENTE IN PIANTA sulla sommita' del muro.

Assi di riferimento (nel solutore traliccio_2d):
- X = direzione lungo il muro (span del Warren/Pratt)
- Y = spessore del muro = altezza h del traliccio (distanza tra i due correnti)
- Z = verticale (non nel piano del solutore 2D)

La forza sismica F agisce in DIREZIONE Y (fuori piano della parete = direzione forte del Warren).
Il Warren ha inerzia massima rispetto a Z (I_z = A_corrente * (h/2)^2 * 2), quindi
resistenza massima a carichi in Y: e' il comportamento a "trave profonda" nel piano XY.

I correnti corrono lungo X.
Le diagonali collegano corrente superiore (y=h, faccia esterna muro) con
corrente inferiore (y=0, faccia interna muro).

Lo schema statico: CERNIERA a x=0 (collegamento parete trasversale sx),
CARRELLO_X a x=L (collegamento parete trasversale dx). I carichi Fy sono
distribuiti sui nodi del corrente superiore.

Verifica test case:
- Warren 4 campate, L=400 cm, h=30 cm, F_tot=1000 kg (Fy distribuito)
- q_y = 1000/400 = 2.5 kg/cm; a = L/4 = 100 cm; theta = arctan(30/100) = 16.7 deg
- M_max (midspan) = q*L^2/8 = 2.5*160000/8 = 50000 kg*cm
- N_corrente (midspan) = M_max/h = 50000/30 = 1667 kg
- V (primo pannello, vicino appoggio) = F_tot/2 = 500 kg
- N_diagonale = V/sin(theta) = 500/sin(16.7 deg) = 500/0.2873 = 1740 kg

---

## Decisioni Q&A Round 1 (35 domande, 3 round precedenti)

(vedasi versione precedente — tutte le decisioni di architettura sono riportate di seguito)

---

## Decisioni Q&A Round 2 (sessione 2026-03-07)

### A — Sezioni aste (CRITICO)

**Decisione**: Massima flessibilita' e generalita'. Refactoring mirati per riusare moduli esistenti.
Piatti e angolari RICHIESTI (molto usati in pratica).

**Architettura adottata (A1 estesa)**:
- Creare `src/steel/sezione_asta.py` con dataclass `SezioneAsta`:
  - Campi: `A, Ix, Iy, ix, iy, nome, tipo_sezione (enum)`
  - Builder: `SezioneAsta.da_piatto(b, t, orientamento)` — calcolato analiticamente
  - Builder: `SezioneAsta.da_angolare(b, d, t)` (o `da_angolare_pari(b, t)`)
  - Builder: `SezioneAsta.da_profilo(profilo: ProfiloAcciaio)` — wrapper
  - Catalogo piatti: `data/steel/piatti.json` (taglie standard)
  - Catalogo angolari: `data/steel/angolari.json` (L pari: L30..L200, L impari: selezionati)
- Refactoring `verifica_aste_traliccio()` in `traliccio_2d.py`:
  - Accettare `list[SezioneAsta]` al posto di `list[Asta]` per i dati sezione
  - Eliminare l'approssimazione `i_min = sqrt(A/pi)` (SBAGLIATA per piatti)
  - Usare `SezioneAsta.ix` e `SezioneAsta.iy` correttamente
- Adattare `verifica_profilo_ta()` in `verifiche_ta.py`: accettare anche `SezioneAsta`
  (o creare wrapper `verifica_asta_ta(sezione: SezioneAsta, N, L, vincolo, tipo_acciaio)`)

**Formule per piatto b x t (b >= t)**:
- A = b * t
- I_forte (asse lungo b) = t * b^3 / 12  → i_forte = b / sqrt(12)
- I_debole (asse lungo t) = b * t^3 / 12  → i_debole = t / sqrt(12)
- Orientamento: 'verticale' (b = dimensione in Z) o 'orizzontale' (b = dimensione in Y)

**Formule per angolare uguale L b x b x t** (assi centroidali, approssimati):
- A = (2*b - t) * t
- Centroide: y_G = x_G = (b^2 - (b-t)^2) / (2*(2*b-t)) ... calcolo esatto con formule standard
- I_1 = I_2 (assi centroidali paralleli alle ali) — dalla tabella EN 10056 o formula
- I_min (asse debole a 45 deg) = I_1 - I_12 (dove I_12 e' il prod. di inerzia)
  Per angolare pari: i_min ≈ 0.195 * b (approssimazione pratica utile per pre-dimensionamento)
  Per implementazione esatta: calcolo analitico integrando A con centroide
- Catalogo JSON con valori precalcolati (come sagomario)

### B — Molle distribuite nodo-muro

**Decisione**: B2 per ora (solo vincoli rigidi: cerniera/carrello alle estremita').
Se esistono formulazioni robuste per le molle → marcato TODO, predisposto per implementazione futura.

**Implementazione**:
- `CordoloReticolare` avra' campo `rigidezza_collegamento_muro: float | None = None`
  con commento `# TODO: molle distribuite ai nodi — rigidezza per unita' di lunghezza [kg/cm/cm]`
- Nel generatore di nodi: se rigidezza_collegamento_muro e' None → solo vincoli estremi
- TODO futuro: `kx_nodo = k_muro * a` dove `a` e' la lunghezza del pannello (distanza internodo)
  Tipo molla da aggiungere al solutore: `Molla(nodo_id, kx, ky)` → aggiunta a K diagonale

**Nota tecnica molle (per futura implementazione)**:
La molla rappresenta la rigidezza distribuita del collegamento traliccio-muro.
Fisica: il muro sotto il cordolo fornisce un vincolo elastico distribuito.
Modello: molla di Winkler → k_w = k_muro_per_metro [kg/cm/m], distribuita sui nodi.
Rigidezza equivalente per nodo: k_nodo = k_w * a [kg/cm].
La rigidezza k_w dipende dal tipo di collegamento (inghisaggio, tassello, connettore).

### C — Schema anello chiuso

**Decisione**: C1 per ora (4 tralicci piani indipendenti ai nodi d'angolo).
C2 (vincolo cerniera singola per risolvere la labilita') come opzione TODO.

**Implementazione**:
- `CordoloReticolare` avra' campo `schema_chiusura: str = "muro_singolo"`
- Opzioni: "muro_singolo" (default), "anello_c1" (4 tralicci indip.), "anello_c2" (TODO)
- Anello C1: ciascun lato del perimetro e' un traliccio indipendente con i propri vincoli
  Le reazioni ai nodi d'angolo diventano i carichi per la verifica D.3.6
- Anello C2 (TODO): un nodo del perimetro = CERNIERA globale; tutti gli altri liberi in X

### D — Forza F da cinematica -> traliccio

**Decisione**: Implementare ENTRAMBE le formulazioni (D1 + D3):

**D1 — Forza da equilibrio (rigorosa)**:
Dalla cinematica si conosce: M_stabilizzante, M_ribaltante_coeff, alpha_0_attuale
L'equilibrio con ritegno: alpha_0_target = (M_stab + F_rit * h_sommita) / M_rib_coeff
→ F_ritegno = (alpha_0_target * M_rib_coeff - M_stab) / h_sommita
Richiede che RisultatoCinematica esponga M_stab e M_rib_coeff (da aggiungere se mancanti)

**D3 — Approssimazione linearizzata**:
F_ritegno_approx = (alpha_0_target - alpha_0_attuale) * M_ribaltante / h_sommita
dove M_ribaltante = M_rib_coeff * alpha_0_attuale (momento ribaltante allo stato attuale)
Piu' semplice ma meno rigorosa, utile come check rapido

**Implementazione**:
```python
def calcola_F_ritegno(
    risultato_cin: RisultatoCinematica,
    alpha_0_target: float,
    h_sommita: float,
    metodo: str = "D1",  # "D1" o "D3"
) -> float: ...
```
**Nota**: `RisultatoCinematica` deve esporre `forze_stabilizzanti` (gia' presente)
e `forze_ribaltanti` (gia' presente). Ma per D1 serve anche M_rib_coeff (il coefficiente
senza alpha_0). → Aggiungere `M_rib_coeff: float = 0.0` a RisultatoCinematica
o calcolarlo come `M_rib_coeff = forze_ribaltanti / alpha_0` se alpha_0 > 0.

### E — Instabilita' fuori piano aste

**Decisione**: E2 — calcolo entrambe le snellezze, usa la peggiore.

**Implementazione**:
- `SezioneAsta` ha `ix` (asse forte) e `iy` (asse debole)
- Per ogni asta in compressione, calcolare:
  - lambda_in_piano = L0_in_piano / ix  (piano del traliccio = piano XY)
  - lambda_fuori_piano = L0_fuori_piano / iy  (piano verticale XZ)
- L0_in_piano = beta_in_piano * L_asta
- L0_fuori_piano = beta_fuori_piano * L_asta (default beta=1.0 per cerniere ai nodi)
- omega = omega_acciaio(max(lambda_in_piano, lambda_fuori_piano))
- Per piatto con `orientamento = 'verticale'` (b in Z, t in Y/X):
  - i_forte = b/sqrt(12)   (asse verticale = fuori piano del traliccio)
  - i_debole = t/sqrt(12)  (asse orizzontale = nel piano del traliccio)
  → Nota: l'asse debole governa per instabilita' nel piano, il forte per fuori piano
  → In genere governa i_debole = t/sqrt(12) → lambda_in_piano massimo
- Utente specifica: `orientamento: str = 'verticale'` per piatti (default pratico)

### F — Verifica collegamento traliccio-muro

**Decisione**: F3 — trattamento uniforme semplificato.
Verifica: tau = F_nodo / A_totale_ancoraggi <= tau_adm
Dove:
- F_nodo = reazione del nodo al carico sismico (da risultato solutore)
- A_totale_ancoraggi = n_ancoraggi * A_singolo_ancoraggio [cm^2]
- tau_adm = tensione ammissibile a taglio acciaio degli ancoraggi [kg/cm^2]
- n_ancoraggi e phi_ancoraggio: parametri per nodo o globali (tutti uguali per default)

Nota: tasselli chimici → F1 (input F_Rd dall'utente da scheda tecnica) come TODO futuro.
Barre inghisate piu' complete: verifica aderenza tau_adh = F / (pi * phi * L_incr) <= tau_adm_muratura
→ Aggiungere come verifica opzionale (F3 extended, marcata TODO).

### G — Dimensionamento inverso

**Decisione**: G1 — per famiglie piatti e angolari (le preferite in pratica).

**Algoritmo**:
- Input: N_max_compressione [kg], L_diagonale [cm], tipo_acciaio, beta_vincoli
- Famiglie: 'PIATTO' (da piatti.json ordinati per A crescente) e 'ANGOLARE_PARI' (da angolari.json)
- Per ogni profilo nella famiglia (crescente per A):
  1. Calcola SezioneAsta
  2. Calcola lambda = L0 / i_min
  3. Calcola omega = omega_acciaio(lambda)
  4. Verifica: omega * |N| / A <= sigma_adm
  5. Verifica snellezza: lambda <= lambda_max (200)
  - Se entrambe OK → profilo trovato, restituisci
- Per profili standard (IPE, HEA, etc.): stessa logica, itera per Wx crescente

**Taglie standard piatti** (da inserire in data/steel/piatti.json):
b x t [mm]: 50x5, 60x6, 60x8, 80x6, 80x8, 80x10, 100x8, 100x10, 100x12,
120x10, 120x12, 150x12, 150x15, 200x15, 200x20 (+ serie UNI 5679)

**Taglie standard angolari pari L** (da inserire in data/steel/angolari.json):
L30x30x3, L40x40x4, L50x50x5, L60x60x6, L70x70x7, L80x80x8,
L90x90x9, L100x100x10, L120x120x12, L150x150x15 (EN 10056-1)

### H — Verifica nodi traliccio

**Decisione**: H1 — verifica semplificata.
- Trova asta piu' sollecitata al nodo (N_max)
- Verifica saldatura d'angolo equivalente:
  tau_sald = N_max / (a * L_sald * sqrt(2)) <= tau_adm_saldatura
  dove a = gola saldatura [cm], L_sald = lunghezza efficace saldatura [cm]
- L_sald default: larghezza asta (b per piatto, b per ala angolare)
- tau_adm_saldatura: dipende da tipo acciaio e beta_w (da connessioni.py gia' disponibile)
- Usa `verifica_saldatura_angolo()` da `src/steel/connessioni.py` (gia' implementata)

### I — Caso test

**Schema corretto verificato**:
- Warren in piano XY (X = lungo muro, Y = spessore muro = forte del Warren)
- F = Fy distribuito sui nodi corrente superiore (y=h)
- Supporti: CERNIERA a x=0 (blocca ux, uy); CARRELLO_X a x=L (blocca uy)
- Valori analitici per 4 campate, L=400, h=30, F_tot=1000 kg → sopra

---

## File da creare (aggiornato)

| File | Tipo | Contenuto |
|------|------|-----------|
| `src/steel/sezione_asta.py` | NUOVO (D.3.0) | SezioneAsta, builders, enum TipoSezioneAsta |
| `data/steel/piatti.json` | NUOVO (D.3.0) | Taglie standard piatti con A, Ix, Iy, ix, iy |
| `data/steel/angolari.json` | NUOVO (D.3.0) | Angolari pari EN 10056-1 con proprieta' sezione |
| `src/steel/traliccio_generatore.py` | NUOVO (D.3.1) | genera_warren, genera_pratt, pre-dim, anteprima |
| `src/elements/cordolo_reticolare.py` | NUOVO (D.3.3) | CordoloReticolare, da_cinematica, verifica, dimensiona |

## File da modificare (aggiornato)

| File | Modifica | Fase |
|------|----------|------|
| `src/steel/traliccio_2d.py` | verifica_aste: usa SezioneAsta, correggi i_min; aggiungi K_globale output; aggiungi carico distrib su corrente | D.3.0 + D.3.2 |
| `src/steel/verifiche_ta.py` | Aggiungere `verifica_asta_ta(sezione: SezioneAsta, N, L, ...)` wrapper standalone | D.3.0 |
| `src/methods/muratura/cinematica.py` | Aggiungere ritegno_sommitale, M_rib_coeff a RisultatoCinematica, RIBALTAMENTO_CANTONALE | D.3.5 |
| `src/elements/cordolo.py` | Implementare TipoCordolo.METALLICO_RETICOLARE (gia' dichiarato) | D.3.3 |
| `src/report/tabulati_calcolo.py` | Sezione cordolo reticolare | D.3.7 |

---

## Schema dipendenze fasi D.3

```
D.3.0 (SezioneAsta) — prerequisito per tutto
    ↓
D.3.1 (generatore) → usa SezioneAsta per pre-dim
D.3.2 (solutore ext) → usa Asta + aggiunge K_globale, distrib
    ↓
D.3.3 (CordoloReticolare) → usa D.3.1 + D.3.2 + SezioneAsta
    ↓
D.3.4 (verifiche aste) → usa D.3.3 + SezioneAsta + connessioni.py
D.3.5 (integrazione cinematica) → usa D.3.3 + cinematica.py modificato
    ↓
D.3.6 (nodo d'angolo) → usa D.3.4 + connessioni.py
D.3.7 (report) → usa D.3.3..D.3.6
D.3.8 (test) → testa tutto
```

---

## Interfacce chiave tra moduli (aggiornato)

### SezioneAsta → traliccio_2d / verifiche_ta
```python
@dataclass
class SezioneAsta:
    A: float          # area [cm^2]
    Ix: float         # inerzia asse forte [cm^4]
    Iy: float         # inerzia asse debole [cm^4]
    ix: float         # raggio d'inerzia asse forte [cm]
    iy: float         # raggio d'inerzia asse debole [cm]
    nome: str         # es. "Piatto 80x8", "L80x80x8", "IPE 200"
    tipo: TipoSezioneAsta  # PIATTO, ANGOLARE, PROFILO_STANDARD
    # Per piatti: attributi aggiuntivi
    b: float = 0.0   # dimensione grande [cm]
    t: float = 0.0   # dimensione piccola [cm]
    orientamento: str = "verticale"  # "verticale" o "orizzontale"
```

### CordoloReticolare → cinematica.py
```python
@dataclass
class CordoloReticolare:
    schema: SchemaReticolare       # WARREN, PRATT
    n_campate: int
    L: float                       # lunghezza [cm]
    h: float                       # altezza = spessore muro [cm]
    sezione_corrente: SezioneAsta
    sezione_diagonale: SezioneAsta
    tipo_acciaio: str = "Fe430"
    tipo_collegamento_muro: TipoCollegamentoMuro = TipoCollegamentoMuro.INGHISAGGIO
    n_ancoraggi_per_nodo: int = 2
    phi_ancoraggio: float = 1.6    # [cm]
    # TODO D.3.2 molle: rigidezza_collegamento_muro: float | None = None
    schema_chiusura: str = "muro_singolo"  # TODO: "anello_c1", "anello_c2"
```

### calcola_F_ritegno()
```python
def calcola_F_ritegno(
    risultato_cin: RisultatoCinematica,
    alpha_0_target: float,
    h_sommita: float,
    metodo: str = "D1",
) -> float:
    """
    D1: F = (alpha_0_target * M_rib_coeff - M_stab) / h_sommita
    D3: F = (alpha_0_target - alpha_0_att) * forze_ribaltanti / h_sommita
    """
```

---

## Note tecniche importanti (aggiornato)

1. Il solutore traliccio_2d e' gia' generico nel piano XY. Non serve flag orientamento.

2. CordoloReticolare e' classe SEPARATA da CordoloMetallico (D.6).
   Non eredita, ma TipoCordolo.METALLICO_RETICOLARE e' gia' dichiarato in cordolo.py.

3. La fatica ciclica sismica e' TODO placeholder. Predisporre campo
   `verifica_fatica: bool | None = None` nel risultato finale.

4. Il flusso iterativo cinematica <-> traliccio (bidirezionale) e' TODO futuro.

5. La `i_min = sqrt(A/pi)` in verifica_aste_traliccio() e' SBAGLIATA per piatti.
   Deve essere corretta nel refactoring D.3.0 (priorita' alta).

6. Per angolari: i_min e' relativo all'asse debole (a 45 deg per angolari pari).
   Per angolari pari L b x b x t: i_min ≈ 0.195 * b (approssimazione ingegneristica)
   oppure calcolo esatto dal catalogo JSON.

7. Test: usare valori analitici Warren (sopra) come golden test nel primo test D.3.8.
   Poi aggiungere test con valori sintetici per piatti, angolari, e integrazione cinematica.
