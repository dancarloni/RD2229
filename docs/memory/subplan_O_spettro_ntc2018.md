# FASE O — Griglia sismica INGV + Spettro NTC2018

**Data analisi**: 2026-03-06
**Origine**: Analisi G.1 SLU forza inerziale F_a (verifica completamento)

---

## Contesto: perche' questa fase e' critica

Durante la verifica di G.1 (check_slu elementi secondari) e' emerso un **gap strutturale**:
tutti i moduli del software che usano l'accelerazione sismica ricevono S_a, alpha_S, S_d
come parametri **esterni gia' calcolati**. Il software non e' in grado di calcolare
autonomamente lo spettro NTC2018 dal sito.

### Moduli affetti (ricevono parametri sismici come input esterno)

| Modulo | File | Parametro esterno | Gap |
|--------|------|-------------------|-----|
| check_slu elementi secondari | `src/codes/ntc2018/secondary_elements/checks.py` | `S_a` | non calcola S_a |
| spectral_acceleration_floor | `src/codes/ntc2018/secondary_elements/ta_models.py` | `alpha_S` | non calcola alpha_S |
| drift Metodo B | `src/codes/ntc2018/secondary_elements/drift_models.py` | `S_d_T1` | non calcola S_d |
| POR spettro edificio | `src/methods/muratura/modello_edificio.py` | `ParametriSismiciEdificio` | input manuale |
| Cinematica fuori piano | `src/methods/muratura/cinematica.py` | `a_g, S, q, FC` | input manuale |

### Stato attuale spectrum_paste_service.py

`src/codes/ntc2018/spectrum_paste_service.py` e' il punto di integrazione esistente:

- Importa ag, F0, TC* da EdiLus-MS (parsing testo incollato)
- Memorizza `class_of_use` e `vita_nominale_years`
- Dataclass `Ntc2018HazardProfile` con `parsed_rows: list[Ntc2018HazardRow]`
- `Ntc2018HazardRow`: limit_state_label, tr_years, ag_g, f0, tc_star_s
- `get_hazard_params(profile, limit_state_label)` -> (tr, ag_g, f0, tc_star)
- **NON calcola** SS, ST, S = SS*ST, alpha_S = (ag/g)*S

---

## Catena di calcolo NTC2018 §3.2.3 (percorso mancante)

```
INPUT SITO:
  lat, lon                           -> griglia INGV -> ag, F0, TC* per TR
  categoria suolo (A, B, C, D, E)    -> SS (Tab. 3.2.V, funzione di ag e F0)
  categoria topografica (T1, T2, T3, T4) -> ST (Tab. 3.2.VI)
  classe d'uso (I, II, III, IV)      -> Cu (Tab. 2.4.II)
  vita nominale VN [anni]            -> VR = VN * Cu

CALCOLO PERIODO DI RITORNO:
  VR + probabilita' eccedenza PVR    -> TR = -VR / ln(1 - PVR)
  SLO: PVR=81%, SLD: PVR=63%, SLV: PVR=10%, SLC: PVR=5%

PARAMETRI SPETTRALI (da interpolazione griglia INGV per TR):
  ag [g], F0 [-], TC* [s]

AMPLIFICAZIONE SITO:
  SS = f(ag, F0, cat_suolo)          <- Tab. 3.2.V, formula o tabella
  ST = f(cat_topografica)            <- Tab. 3.2.VI
  S  = SS * ST
  alpha_S = (ag/g) * S              <- usato da spectral_acceleration_floor

SPETTRO ELASTICO ORIZZONTALE Se(T):
  TB = TC/3,  TC = CC * TC*,  TD = 4*ag/g + 1.6
  CC = f(cat_suolo)
  0 <= T <= TB:  Se = ag*S*F0*(eta*F0-1)*T/TB + ag*S
  TB <= T <= TC: Se = ag*S*F0*eta
  TC <= T <= TD: Se = ag*S*F0*eta*(TC/T)
  TD <= T:       Se = ag*S*F0*eta*(TC*TD/T^2)
  eta = sqrt(10/(5+xi)) >= 0.55  (xi = smorzamento viscoso, default 5%)

SPETTRO DI PROGETTO Sd(T):
  Sd(T) = Se(T) / q  (semplificazione per SLV)

ACCELERAZIONE AL PIANO (NTC2018 eq. 7.2.5):
  S_a = alpha_S * max(3*(1+z/H)/(1+(1-T_a/T_1)^2) - 0.5, 1.0)

SPOSTAMENTO SPETTRALE (per drift Metodo B):
  S_d(T_1) = Sd(T_1) * (T_1/(2*pi))^2  [m]
```

---

## Struttura dati NTC2018 Tab. 3.2.V — Coefficiente SS

| Cat. suolo | Condizione | SS |
|------------|------------|----|
| A | - | 1.00 |
| B | ag*S <= 0.25g | 1.00 + 0.40*(F0*ag/g - 0.22) |
| B | ag*S > 0.25g | 1.00 |
| C | ag*S <= 0.25g | 1.00 + 0.50*(F0*ag/g - 0.22) |
| C | ag*S > 0.25g | 1.50 |
| D | ag*S <= 0.35g | 0.90 + 0.90*(F0*ag/g - 0.22) |
| D | ag*S > 0.35g | 1.80 |
| E | ag*S <= 0.20g | 1.00 + 0.60*(F0*ag/g - 0.22) |
| E | ag*S > 0.20g | 1.60 |

Nota: la formula di SS dipende da ag stessa (calcolo iterativo o approx. con ag*S=ag iniziale).
Approccio standard: prima iterazione SS=1, poi ricalcolo con ag*S = ag*SS_iterazione.

## Struttura dati NTC2018 Tab. 3.2.VI — Coefficiente ST

| Cat. topografica | Descrizione | ST |
|------------------|-------------|-----|
| T1 | Superficie pianeggiante, pendii, rilievi isolati con inclinazione media <= 15° | 1.0 |
| T2 | Pendii con inclinazione media > 15° | 1.2 |
| T3 | Rilievi con larghezza in cresta << base, inclinazione media 15°-30° | 1.2 |
| T4 | Rilievi con larghezza in cresta << base, inclinazione media > 30° | 1.4 |

## Struttura dati NTC2018 Tab. 2.4.II — Coefficiente Cu

| Classe d'uso | Descrizione | Cu |
|--------------|-------------|-----|
| I | Agricole, industriali a bassa presenza umana | 0.7 |
| II | Edifici ordinari (residenziale, commerciale) | 1.0 |
| III | Affollamento significativo (scuole, uffici > 200 pers.) | 1.5 |
| IV | Funzioni pubbliche essenziali (ospedali, vigili del fuoco) | 2.0 |

---

## Architettura modulo `src/codes/ntc2018/spectrum.py`

### Enums

```python
class CategoriaSuolo(Enum):
    A = "A"   # Roccia o terreni molto rigidi
    B = "B"   # Rocce tenere, depositi molto addensati
    C = "C"   # Depositi di sabbie o ghiaie mediamente addensate
    D = "D"   # Depositi di terreni coesivi molli
    E = "E"   # Profilo con strati superficiali alluvionali

class CategoriaTopografica(Enum):
    T1 = "T1"  # ST = 1.0
    T2 = "T2"  # ST = 1.2
    T3 = "T3"  # ST = 1.2
    T4 = "T4"  # ST = 1.4

class ClasseUso(Enum):
    I  = "I"   # Cu = 0.7
    II = "II"  # Cu = 1.0
    III= "III" # Cu = 1.5
    IV = "IV"  # Cu = 2.0
```

### Funzioni principali

```python
# Vita di riferimento
calcola_VR(vita_nominale: int, classe_uso: ClasseUso) -> int
  VR = vita_nominale * Cu[classe_uso]
  min(VR, 35)  # NTC2018: VR >= 35 anni

# Coefficienti sito
calcola_CC(cat_suolo: CategoriaSuolo) -> float
  # CC da Tab. 3.2.V (funzione di cat_suolo)
calcola_SS(ag_g: float, F0: float, cat_suolo: CategoriaSuolo) -> float
  # Tab. 3.2.V, iterazione se necessario
calcola_ST(cat_topografica: CategoriaTopografica) -> float
  # Tab. 3.2.VI

# Spettro
calcola_periodi_spettro(TC_star: float, CC: float) -> tuple[float, float, float]
  # (TB, TC, TD) con TD = 4*ag/g + 1.6
spettro_elastico_orizzontale(ag, F0, TC_star, SS, ST, xi, T) -> float
  # Se(T) [m/s2]
spettro_progetto(ag, F0, TC_star, SS, ST, q, T) -> float
  # Sd(T) [m/s2]
calcola_S_d_T1(T_1, ag, F0, TC_star, SS, ST, q) -> float
  # S_d [m] = Sd(T_1) * (T_1/(2*pi))^2
calcola_alpha_S(ag_g, SS, ST) -> float
  # alpha_S = (ag/g) * SS * ST

# Funzione end-to-end (integrazione con spectrum_paste_service)
spettro_da_hazard_row(
    row: Ntc2018HazardRow,
    cat_suolo: CategoriaSuolo,
    cat_topografica: CategoriaTopografica,
) -> dict  # SS, ST, S, alpha_S, TB, TC, TD, Se_func, Sd_func
```

### Integrazione con spectrum_paste_service.py

`spectrum_paste_service.py` produce `Ntc2018HazardProfile` con i parametri grezzi
(ag, F0, TC* per ogni SdL). Il modulo `spectrum.py` ne e' il "consumer":

```
Ntc2018HazardProfile.get_hazard_params("Salvaguardia Vita")
  -> (tr, ag_g, f0, tc_star)
  + cat_suolo, cat_topografica (input utente)
  -> spettro_da_hazard_row(row, cat_suolo, cat_topografica)
  -> alpha_S, Se(T), Sd(T), S_d(T_1)
```

---

## Integrazione con O.1 (griglia INGV)

La FASE O.1 deve produrre un output compatibile con `Ntc2018HazardRow`:

- Input: lat, lon, VR (o TR)
- Output: ag_g, f0, tc_star (interpolazione griglia 0.05° x 0.05°)
- Alternativa offline: tabella CSV locale della griglia INGV (Allegato B NTC2018)

Con O.1 attivo, il flusso diventa completamente automatico:

```
lat, lon + cat_suolo + cat_topogr + classe_uso + VN
  -> O.1: ag, F0, TC* per SLV
  -> O.2: SS, ST, alpha_S, Se(T), Sd(T)
  -> G.1: S_a piano -> F_a = S_a * W_a * gamma_a / q_a
```

---

## File da creare / modificare

| Azione | File | Note |
|--------|------|------|
| CREA | `src/codes/ntc2018/spectrum.py` | Modulo principale O.2 |
| MODIFICA | `src/codes/ntc2018/spectrum_paste_service.py` | Aggiungere integrazione con spectrum.py |
| MODIFICA | `src/codes/ntc2018/secondary_elements/checks.py` | Opzione calcolo S_a interno (G.1.b) |
| CREA | `src/codes/ntc2018/ingv_hazard.py` | Import da webservice/griglia INGV (O.1) |
| CREA | `data/seismic/griglia_ingv.csv` (o .json) | Griglia offline INGV per fallback |
| CREA | `tests/test_spettro_ntc2018.py` | Test spettro con valori noti da letteratura |

---

## Test da scrivere (valori di riferimento)

Per `spectrum.py`, usare come riferimento:

- Esempio NTC2018 Allegato B: sito Roma (lat 41.9, lon 12.5)
- SLV, VR=50 anni, cat. suolo B, cat. topogr. T1
- ag = 0.168g, F0 = 2.398, TC* = 0.327 s
- SS = f(ag, F0, B) ~ 1.2 (iterativo), ST = 1.0
- alpha_S = 0.168 *1.2* 1.0 = 0.2016
- TB = TC/3, TC = CC*TC*, TD = 4*0.168+1.6 = 2.272 s

---

## Dipendenze inverse (cosa sblocca O.2)

| Fase | Modulo | Beneficio |
|------|--------|-----------|
| G.1.a | check_slu elementi secondari | S_a calcolata internamente |
| G.1.b | spectral_acceleration_floor | alpha_S calcolato da sito |
| G.5 drift | drift_models Metodo B | S_d(T_1) calcolato da sito |
| F.1 POR | modello_edificio ParametriSismiciEdificio | spettro da sito |
| E.3 cinematica | cinematica.py a_g, S automatici | parametri da sito |
| FASE U sismica | da implementare | spettro base per tutto |

---

## Note architetturali

- `spectrum.py` e' PURO calcolo (no I/O, no GUI, no dipendenze esterne)
- `spectrum_paste_service.py` rimane il layer di import EdiLus-MS (non modificare la logica)
- `ingv_hazard.py` e' il layer di accesso ai dati INGV (webservice + fallback offline)
- Separazione netta: dati pericolosita' (O.1) vs calcolo spettrale (O.2) vs verifiche (G.1)
- Unita' interne: ag in [g], Se/Sd in [m/s2], S_d in [m] — convertire in output se necessario
- decision_log obbligatorio per tracciabilita' (SS iterativo, ST scelto, etc.)

---

## Stato implementazione (aggiornato 2026-03-06)

**Stato**: O.2 COMPLETATO; O.1 COMPLETATO (CSV richiede file utente)

### File creati / modificati

| File | Stato | Note |
|------|-------|------|
| `src/codes/ntc2018/spectrum.py` | CREATO | Modulo puro O.2, 47 test |
| `src/codes/ntc2018/ingv_hazard.py` | CREATO | Webservice ESSE1 + CSV fallback |
| `data/seismic/.gitkeep` | CREATO | Placeholder CSV griglia INGV |
| `src/codes/ntc2018/secondary_elements/ta_models.py` | MODIFICATO | +spectral_acceleration_floor_from_site |
| `src/codes/ntc2018/secondary_elements/checks.py` | MODIFICATO | +S_a interna in check_slu |
| `src/methods/muratura/cinematica.py` | MODIFICATO | +factory parametri_sismici_da_sito |
| `tests/test_spettro_ntc2018.py` | CREATO | 47 test (1948 totali, 0 falliti) |

### Valori di riferimento corretti (Roma SLV, cat B/T1)

ag=0.168g, F0=2.398, TC*=0.327s:

- SS = 1.0 + 0.40*(2.398*0.168 - 0.22) = 1.073 (NON 1.2 come indicato in precedenza)
- CC = 1.1 * 0.327^(-0.20) = 1.376
- TC = 1.376 * 0.327 = 0.450s; TB = 0.150s; TD = 2.272s
- alpha_S = 0.168 *1.073* 1.0 = 0.180 (NON 0.2016 come indicato in precedenza)

### Gap residui

- CSV griglia INGV: da fornire dall'utente (NTC2018 Allegato B, ~1.5MB)
- G.5 drift: S_d(T_1) ancora input esterno in drift_models.py
- POR: ParametriSismiciEdificio ancora popolato manualmente
- cinematica S_De_Ts: ancora input esterno
