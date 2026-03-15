# Fase X — Solai (tutti i tipi, multi-campata, aperture, cerchiature)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | 🟨 IN CORSO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~100 |
| **Norma/e di riferimento** | NTC2018, EN 1992, DM96, DM92, RD2229 |
| **Priorità** | Alta (modulo fondamentale per edifici esistenti e nuovi) |
| **Memoria** | `docs/memory/fase_X_context.md`, `docs/memory/fase_X_history.md` |

---

## Master index documentale (Round 3)

Questo file e il master-index della Fase X. Il contenuto tecnico operativo e stato scomposto in moduli autonomi:

- [docs/piano_fase_X1_tipologie_input.md](docs/piano_fase_X1_tipologie_input.md)
- [docs/piano_fase_X2_carichi_combinazioni.md](docs/piano_fase_X2_carichi_combinazioni.md)
- [docs/piano_fase_X3_verifiche_slu.md](docs/piano_fase_X3_verifiche_slu.md)
- [docs/piano_fase_X4_verifiche_sle_vibrazioni.md](docs/piano_fase_X4_verifiche_sle_vibrazioni.md)
- [docs/piano_fase_X5_aperture_cerchiature.md](docs/piano_fase_X5_aperture_cerchiature.md)
- [docs/piano_fase_X6_report_tracciabilita.md](docs/piano_fase_X6_report_tracciabilita.md)
- [docs/piano_fase_X7_benchmark_validazione.md](docs/piano_fase_X7_benchmark_validazione.md)
- [docs/piano_fase_X8_casi_speciali.md](docs/piano_fase_X8_casi_speciali.md)

Regole operative obbligatorie per ogni modulo Xn:

- sezione Rischi normativi residui
- tabella Formula usata / fallback / motivo selezione

Aggiornamento implementativo 2026-03-15:
- X1 completato
- X2 completato
- X3 completato (check X3 + fallback DM96/DM16 + test mirati e benchmark)
- X4 completato (deformabilita, tensioni/fessurazione, vibrazioni, test unit+benchmark)
- X5 completato (`x5_aperture_classificazione`, `x5_aperture_rigidezza`, `x5_cerchiatura_redistribuzione`; test 31/31 PASS: 17 check + 11 benchmark + 3 e2e)
- X6-X8 da implementare

## Base scientifica e riferimenti strutturali

Nota: la trattazione tecnica esaustiva (formule, esempi numerici, tabelle normative e procedure dettagliate) è stata scomposta e trasferita nei moduli dedicati `docs/piano_fase_X1_tipologie_input.md` … `docs/piano_fase_X8_casi_speciali.md`.

Questo file rimane il master-index operativo: per dettagli implementativi e formule vedere i moduli X1–X8 collegati in alto.

---
| Log | `src/core/registro_log.py` | Log calcolo e warning (VoceLog con formula, fonte, esito) |
| Aree di influenza | `src/aree_influenza.py` ⚠️ **NON DISPONIBILE** | Fallback: input manuale + warning `X-AREA-001` (attende Fase Y; precedente in Fase V con `V-AREA-002`) |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2.6 | Verifica solai esistenti e nuovi |
| EN 1992-1-1 §9.3 | Solai in c.a. |
| DM 9/1/96 | Solai laterocemento |
| DM 16/1/96 | Solai legno |
| RD 2229/1939 | Solai storici |
| Santarella, Giangreco | Formule e metodi storici |
| Cataloghi commerciali | Parametri prodotti |

---

## Base scientifica e riferimenti strutturali

### Riferimenti normativi e bibliografici principali

| Norma/Riferimento         | Utilizzo chiave                                  |
|---------------------------|--------------------------------------------------|
| NTC2018 §7.2.6            | Verifica solai nuovi/esistenti                   |
| EN 1992-1-1 §9.3          | Solai in c.a. (Eurocodice 2)                     |
| DM 9/1/96                 | Solai laterocemento                              |
| DM 16/1/96                | Solai legno                                      |
| RD 2229/1939              | Solai storici                                    |
| Santarella, Giangreco     | Formule storiche, coefficienti di sicurezza      |
| Cataloghi commerciali     | Parametri prodotti prefabbricati                 |

### Tipologie di solaio e parametri principali

| Tipologia         | Parametri geometrici         | Parametri meccanici         | Note                       |
|-------------------|-----------------------------|-----------------------------|----------------------------|
| Laterocemento     | h, b, interasse, spessore    | f_ck, E_cm, γ               | Travetti, pignatte         |
| Predalles         | h, larghezza, armature       | f_ck, E_cm, γ               | Precompresso, prefabbricato|
| Legno             | sezione, interasse, lunghezza| f_mk, E_0, γ                | Massiccio/lamellare        |
| Acciaio           | profilo, interasse           | f_y, E, γ                   | Lamiere, travi IPE/HEA     |
| Getto pieno       | h, larghezza                 | f_ck, E_cm, γ               | Solaio pieno c.a.          |
| Misti             | parametri combinati          | dipende da materiali        | Collaboranti, CLT, ecc.    |

### Formule normative (NTC2018 + fallback EN 1992)

Questa sezione raccoglie le formule chiave da implementare, con:
- **Fonte** (NTC2018, EN 1992, DM, RD2229) e riferimento §/tabella.
- **Unità** di input/output (preferibile: cm, kg, kg/cm²; conversione explicitamente documentata).
- **Range di validità** e warning generati automaticamente quando si supera il campo di applicazione.
- **Esempio numerico** per ogni formula.
- **Fallback**: norma secondaria quando la primaria non è applicabile.

### Convenzioni di unità e conversioni

Per evitare errori dimensionali, il piano distingue fra **unità di archiviazione storiche** e **unità di calcolo normativo**:

- **Unità archivio/interfaccia**: cm, kgf, kgf/cm², kg/m², kg/m³.
- **Unità di calcolo normativo consigliate**: SI locale alla formula quando la costante normativa nasce in EN 1992/NTC2018 e presuppone N, mm, MPa o m.
- **Regola implementativa**: convertire gli input in SI all'ingresso della singola routine normativa; riconvertire gli output in unità storiche per report e tracciabilità.

**Conversioni minime obbligatorie**

| Quantità | Conversione |
| --- | --- |
| Lunghezza | $1\,m = 100\,cm$ |
| Area | $1\,m^2 = 10^4\,cm^2$ |
| Momento d'inerzia | $1\,cm^4 = 10^{-8}\,m^4$ |
| Tensione | $1\,MPa = 10{,}1972\,kgf/cm^2$ |
| Forza | $1\,kN = 101{,}97\,kgf$ |
| Carico superficiale | $q_s[kgf/cm^2] = q_s[kgf/m^2]/10^4$ |
| Carico lineare da solaio | $q_l[kgf/cm] = q_s[kgf/m^2] \cdot i[cm] / 10^4$ |
| Massa lineare | $m[kg/m] = \rho[kg/m^3] \cdot A[m^2]$ |

**Nota operativa**

- Nel documento il simbolo **kg** nelle verifiche statiche va inteso come **kgf**.
- Il simbolo **kg/m³** resta massa volumica fisica per le formule dinamiche e per il calcolo della massa.
- Le formule con coefficienti $0{,}18$, $k_1$, $C_{Rd,c}$ o limiti dinamici EN/NTC vanno preferibilmente valutate in SI locale.

---

#### 1) Verifica a flessione (M_Rd)

- **Fonte primaria**: NTC2018 §4.1.2.4 (verifiche di resistenza) + NTC2018 §2.3 (resistenza calcestruzzo).
- **Fallback**: EN 1992-1-1 §6.2 (resistenza flessione).

**Formula base (c.a. armato rettangolare, sezione semplicemente armata)**

- $f_{cd} = \dfrac{f_{ck}}{\gamma_c}$ con $\gamma_c = 1{,}5$ (NTC2018 Tab. 4.1.I / EN 1992-1-1 §3.1.6)
- $f_{yd} = \dfrac{f_{yk}}{\gamma_s}$ con $\gamma_s = 1{,}15$
- equilibrio semplificato: $x = \dfrac{A_s f_{yd}}{0{,}85\,b\,f_{cd}}$
- braccio interno: $z = d - 0{,}4x$
- resistenza: $M_{Rd} = A_s f_{yd} z$

Questa è la formula di riferimento da implementare per il c.a. armato. La forma elastica $M = W_{el} \cdot \sigma$ va mantenuta **solo** come fallback preliminare per predimensionamento o materiali lineari (acciaio, legno, verifiche elastiche storiche).

**Unità**: $A_s$ [cm²], $b$ [cm], $d$ [cm], $f_{cd}, f_{yd}$ [kgf/cm²] → $M_{Rd}$ [kgf·cm]

**Range di validità**:
- $f_{ck} \in [150, 500]$ kg/cm² (NTC2018 Tab. 2.2.I)
- sezione rettangolare o assimilabile rettangolare
- armatura tesa dominante, senza doppia armatura prevalente
- $x \le x_{lim}$ secondo duttilità di norma

**Warning**:
- `X-RD-001`: $f_{ck}$ fuori range tabellare.
- `X-RD-002`: sezione fuori ipotesi semplificate (serve dominio o doppia armatura).
- `X-RD-003`: $x > x_{lim}$, sezione troppo compressa / duttilità non rispettata.

**Fallback elastico preliminare**

- $M_{Rd,el} = W_{el} \cdot \sigma_{amm}$
- usare solo per predimensionamento o per materiali/modelli storici in tensioni ammissibili.

**Esempio**:
- $b=100\,cm$, $d=18\,cm$, $A_s=5{,}65\,cm^2$, $f_{ck}=255\,kgf/cm^2$, $f_{yk}=4586\,kgf/cm^2$
- $f_{cd}=170\,kgf/cm^2$, $f_{yd}=3988\,kgf/cm^2$
- $x = 5{,}65\cdot 3988 /(0{,}85\cdot 100\cdot 170) \approx 1{,}56\,cm$
- $z = 18 - 0{,}4\cdot 1{,}56 \approx 17{,}38\,cm$
- $M_{Rd} \approx 3{,}92\cdot 10^5\,kgf\cdot cm$ per fascia da 1 m

---

#### 2) Verifica a taglio (V_Rd)

- **Fonte primaria**: NTC2018 §4.1.2.4/§4.1.2.5 (verifica a taglio).
- **Fallback**: EN 1992-1-1 §6.2.2.

**Formula base (sistema semplificato NTC/EN)**:
- **Conversione obbligatoria**: $d_{mm} = 10 \cdot d_{cm}$
- le formule EC2/NTC con $C_{Rd,c}$ e $k$ vanno valutate in SI locale oppure con conversioni coerenti esplicitate
- $k = 1 + \sqrt{\dfrac{200}{d_{mm}}} \leq 2$ (d in mm)
- $\rho_{l}=\dfrac{A_{sl}}{b_w d}$ (armatura longitudinale)
- $V_{Rd,c}=0{,}18\,k\,(100\,\rho_{l}\,f_{ck})^{1/3}\,b_w\,d$
- $V_{Rd}=V_{Rd,c}+V_{Rd,s}$ (se è presente armatura trasversale/staffe)

**Unità**: preferibile calcolo in SI locale; output riconvertito in [kgf]

**Range di validità**:
- $\rho_l \in [0{,}002, 0{,}04]$
- $d \ge 15\,cm$
- $V_{Ed}/V_{Rd,c} \le 0{,}6$ (per non richiedere armatura trasversale)

**Warning**:
- `X-TAG-001`: $\rho_l$ fuori range tabellare.
- `X-TAG-002`: $V_{Ed}/V_{Rd,c} > 0{,}6$ (necessaria armatura trasversale).

**Esempio**:
- $b_w=30\,cm$, $d=35\,cm$, $A_{sl}=2\cdot 1{,}2^2=2{,}88\,cm^2$ → $\rho_l=0{,}0027$
- $d_{mm}=350$, $k=1{,}76$, $f_{ck}\approx 24{,}5\,MPa$ → valutare $V_{Rd,c}$ in SI e riconvertire in kgf per il report

---

#### 3) Deformabilità (freccia)

- **Fonte primaria**: NTC2018 §7.2.6 (limiti deformabilità). 
- **Fallback**: EN 1992-1-1 §7.3 (calcolo freccia).

**Formula analitica (trave semplicemente appoggiata)**:

- input di piano: carico superficiale $q_s$ [kgf/m²]
- trasformazione per fascia collaborante/interasse $i$: $q_l[kgf/cm] = q_s[kgf/m^2] \cdot i[cm] / 10^4$
- freccia: $f_{max}=\dfrac{5q_lL^{4}}{384EI}$

**Limiti normativi (NTC2018 Tab. 7.2.II)**:
- Solai ordinari: $f_{lim}=L/250$
- Solai con tramezzi: $f_{lim}=L/300$
- Solai prefabbricati: $f_{lim}=L/400$

**Unità**: $f$ [cm], $L$ [cm], $q_l$ [kgf/cm], $E$ [kgf/cm²], $I$ [cm⁴]

**Warning**:
- `X-DEF-001`: $f_{max} > f_{lim}$.
- `X-DEF-002`: riduzione $E_{eff}$ >50% senza giustificazione (degrado non documentato).

**Esempio**:
- $q_s=300\,kgf/m^2$, $i=50\,cm$ → $q_l = 300\cdot 50/10^4 = 1{,}50\,kgf/cm$
- $L=500\,cm$, $E=3{,}15\cdot 10^5\,kgf/cm^2$, fascia equivalente $b=50\,cm$, $h=20\,cm$ → $I=3{,}33\cdot 10^4\,cm^4$
- $f_{max}=5\cdot 1{,}50\cdot 500^4 /(384\cdot 3{,}15\cdot 10^5\cdot 3{,}33\cdot 10^4) \approx 0{,}12\,cm$
- confronto: $f_{lim}=500/250=2{,}0\,cm$ → verifica soddisfatta

---

#### 4) Vibrazioni (frequenza fondamentale)

- **Fonte primaria**: NTC2018 §C7.10.5 (comfort vibrazionale) + EN ISO 10137.

**Formula (Dunkerley, elemento monodirezionale)**:
- formulazione primaria in SI: $f_{1}=\dfrac{\pi}{2L^{2}}\sqrt{\dfrac{EI}{m}}$ con $L$ [m], $E$ [Pa], $I$ [m⁴], $m$ [kg/m]
- massa lineare: $m = \rho \cdot A$ con $\rho$ [kg/m³], $A$ [m²]
- formulazione comparativa in unità storiche: convertire prima $A[cm^2]$ in $m^2$ con $A[m^2] = A[cm^2] / 10^4$
- quindi $m[kg/m] = \rho[kg/m^3] \cdot A[cm^2]/10^4$

**Criteri di accettazione**:
- $f_1 \ge 4\,Hz$ (NTC2018 C7.10.5)
- $a_{RMS} \le 0{,}5\,m/s^2$ (EN ISO 10137)

**Unità**: usare SI locale in implementazione; riportare eventualmente anche la massa lineare in [kg/m] nel report

**Warning**:
- `X-VIB-001`: $f_1 < 4$ Hz.
- `X-VIB-002`: $a_{RMS} > 0{,}5$ m/s².

**Esempio**:
- $L=5{,}0\,m$, $E=31\,GPa$, $b=1{,}0\,m$, $h=0{,}20\,m$ → $I=6{,}67\cdot 10^{-4}\,m^4$
- $\rho=2500\,kg/m^3$, $A=0{,}20\,m^2$ → $m=500\,kg/m$
- $f_1 \approx \dfrac{\pi}{2\cdot 5^2}\sqrt{\dfrac{31\cdot 10^9\cdot 6{,}67\cdot 10^{-4}}{500}} \approx 12{,}8\,Hz$

---

#### 5) Aperture (riduzione rigidezza) – modello interno cautelativo

- **Fonte**: NTC2018 §7.2.6.2 (necessità di valutazione locale) + EN 1992-1-1 §7.3.
- **Classificazione**: non è una formula normativa diretta; è un **modello interno cautelativo** da usare in V1 quando non è ancora disponibile il FEM locale.

**Modello parametrico V1**:
- $EI_{eff} = EI\,(1-\alpha_{ap})$
- $\alpha_{ap} = \begin{cases}0{,}05 & \text{area apertura} < 10\%\\0{,}20 & 10\%-25\%\\0{,}40 & >25\%\end{cases}$

**Trigger FEM locale**:

- apertura irregolare o eccentricamente vicina ad appoggio
- apertura > 25% dell'area del pannello
- presenza di cerchiature o trasferimento di taglio bidirezionale significativo

**Unità**: $EI$ [kg·cm²], aree [cm²]

**Warning**:
- `X-APE-001`: $\alpha_{ap} > 0{,}25$ (FEM locale raccomandato).
- `X-APE-002`: $\alpha_{ap} > 0{,}50$ (verifica manuale obbligatoria).

**Fallback (FEM locale)**:
- Analisi di piastra locale con mesh e condizioni di vincolo; considerare campi di sollecitazione locali e ridistribuzione.

---

#### 6) Livelli di conoscenza e fattori di confidenza (LC/FC)

- **Fonte**: NTC2018 §C8.5.4 (edifici esistenti).
- **Principio**: per edifici esistenti si applica un fattore di confidenza (FC) che riduce le resistenze di progetto.

**Modalità di applicazione** (usare `lc_fc_adjustments.py`):
- LC1 → FC = 1,35 (valore di progetto più conservativo)
- LC2 → FC = 1,20 (valore di progetto per livello medio di conoscenza)
- LC3 → FC = 1,00 (valore per elevata conoscenza e controllo)

**Formula**:
- $f_{ck,adj} = f_{ck} / FC$
- $f_{yk,adj} = f_{yk} / FC$

**Warning**:
- `X-LC-001`: LC1 applicato (FC=1,35) — valori di progetto ridotti.

**Esempio**:
- $f_{ck}=250\,kg/cm^2$, LC2 → FC=1,20 → $f_{ck,adj}=208\,kg/cm^2$.

---

#### 7) Punzonamento (taglio perimetrale)

- **Fonte**: NTC2018 §4.1.2.5 (punzonamento) + EN 1992-1-1 §6.4.

**Formula base**:
- $V_{Rd,c} = [C_{Rd,c} k (100\rho_l f_{cd})^{1/3} + k_1 \sigma_{cp}] b_0 d$

Dove:
- $C_{Rd,c} = 0{,}18$ (EN 1992)
- $k = 1 + \sqrt{200/d_{mm}} \le 2$ (d in mm)
- $\rho_l = A_{sl}/(b_0 d)$ (armatura longitudinale equivalente)
- $\sigma_{cp}$ = sforzo di compressione medio nel pilastro/colonna
- $b_0$ = perimetro critico di punzonamento (2(a1+a2) per pilastro rettangolare)

**Unità**: $V_{Rd,c}$ [kg], $b_0$ [cm], $d$ [cm], $f_{cd}$ [kg/cm²]

**Warning**:
- `X-PUNZ-001`: $V_{Ed} > 0{,}8 V_{Rd,c}$ (attenzione nei casi con armatura minima). 

**Esempio**:
- $b_0=120\,cm$, $d=30\,cm$, $f_{cd}=160\,kg/cm^2$, $\rho_l=0{,}0025$, $k=1{,}2$ → $V_{Rd,c}\approx 6{,}4\cdot 10^4\,kg$.

---

#### 8) DM 9/1/96 (laterocemento) — fallback documentale

- **Fonte**: DM 9/1/96 (solai laterocemento) – tabelle di portata e coefficienti.
- **Stato nel piano**: fallback documentale, non ancora trascritto integralmente.
- **Regola**: fino alla trascrizione completa delle tabelle, il piano deve richiedere input manuale dei valori tabellari o usare il modello NTC/EN con warning esplicito.
- **TODO documentale**: riportare in appendice le tabelle esatte per luce, interasse, altezza pignatta e schema statico.

- **Warning**: `X-DM96-001` se il caso non rientra nelle tabelle (luci atipiche, interasse non standard).

---

#### 9) DM 16/1/96 (legno) — fallback documentale

- **Fonte**: DM 16/1/96 (solai in legno) – fattori di sicurezza e tabelle.
- **Stato nel piano**: fallback documentale con valori tabellari da confermare.
- **Formula base**:
  - $M_{Rd} = W_{el} \cdot f_{md}$ con $f_{md} = \dfrac{f_{m,k}}{\gamma_m}$
  - $f_{m,k}$ ricavato da tabelle DM 16/1/96 o, in mancanza, da prove/letteratura con warning esplicito.
- **TODO documentale**: trascrivere classi legno, classe di servizio e coefficienti di modifica.

- **Warning**: `X-DM16-001` se $f_{m,k}$ non disponibile; richiedere prove o letteratura.

---

## Matrice formule per fonte e affidabilità

| ID | Verifica | Tipo formula | Fonte primaria | Fallback | Stato | Validato numericamente |
| --- | --- | --- | --- | --- | --- | --- |
| F-X01 | Flessione c.a. | Normativa diretta / equilibrio di sezione | NTC2018 §4.1.2.4, EN 1992-1-1 §6.1 | elastica preliminare | implementabile | da validare |
| F-X02 | Taglio c.a. | Normativa diretta con conversione SI locale | NTC2018 §4.1.2.4-§4.1.2.5, EN 1992-1-1 §6.2.2 | nessuno | implementabile | da validare |
| F-X03 | Freccia | Derivata normativa + meccanica classica | NTC2018 §7.2.6, EN 1992-1-1 §7.4 | nessuno | implementabile | benchmark BM-X01 |
| F-X04 | Vibrazioni | Derivata normativa + dinamica lineare | NTC2018 §C7.10.5, EN ISO 10137 | formula comparativa storica | implementabile | da validare |
| F-X05 | Aperture | Modello interno cautelativo | NTC2018 §7.2.6.2 (trigger) | FEM locale | cautelativo | da validare |
| F-X06 | LC/FC | Normativa diretta | NTC2018 §C8.5.4 | override manuale FC | implementabile | già coerente con repo |
| F-X07 | Punzonamento | Normativa diretta con conversione SI locale | NTC2018 §4.1.2.5, EN 1992-1-1 §6.4 | nessuno | implementabile | da validare |
| F-X08 | Laterocemento DM96 | Documentale tabellare | DM 9/1/96 | input manuale | incompleto | non ancora |
| F-X09 | Legno DM 16/1/96 | Documentale tabellare | DM 16/1/96 | input manuale / letteratura | incompleto | non ancora |

---

### Tabella limiti deformabilità (NTC2018, EN 1992)

| Destinazione d’uso | Limite freccia $f_{lim}$ |
|--------------------|-------------------------|
| Solai ordinari     | $L/250$                 |
| Solai con tramezzi | $L/300$                 |
| Solai prefabbricati| $L/400$                 |

### Metacodice per verifica solaio (esempio Python-like)

```python
def verifica_solaio(M_Ed, V_Ed, f_max, params):
    # Verifica flessione
    M_Rd = calcola_M_Rd(params)
    ok_fless = M_Ed <= M_Rd

    # Verifica taglio
    V_Rd = calcola_V_Rd(params)
    ok_taglio = V_Ed <= V_Rd

    # Verifica deformabilità
    f_lim = params['L'] / params['limite_freccia']
    ok_freccia = f_max <= f_lim

    return {
        'flessione': ok_fless,
        'taglio': ok_taglio,
        'deformabilità': ok_freccia,
        'dettaglio': {
            'M_Ed': M_Ed, 'M_Rd': M_Rd,
            'V_Ed': V_Ed, 'V_Rd': V_Rd,
            'f_max': f_max, 'f_lim': f_lim
        }
    }
```

### Strategie per aperture e cerchiature

- **Modello semplificato:** riduzione sezione efficace, verifica locale con coefficienti di penalizzazione (NTC2018 §7.2.6.2)
- **Modello avanzato:** analisi FEM locale (opzionale, per aperture grandi o irregolari)

| Tipo apertura | Riduzione sezione (%) |
|---------------|----------------------|
| Piccola (<10% area) | 5–10%           |
| Media (10–25%)      | 15–25%          |
| Grande (>25%)       | 30–50%          |

**Nota metodologica:** i valori sopra sono linee guida interne cautelative per la V1, non valori normativi tabellati da applicare automaticamente senza giudizio ingegneristico.

### Limiti di variazione di rigidezza (NTC2018 §4.1.2.2, §7.2.6)

La NTC2018 prescrive che la rigidezza dei solai esistenti sia valutata considerando:
- Possibile degrado dei materiali (legno, acciaio, c.a.)
- Collaborazione effettiva tra elementi (travetti, soletta, pignatte, ecc.)
- Presenza di aperture, modifiche locali, fessurazioni
- Mancanza di prove sperimentali o documentazione

In assenza di dati certi, la rigidezza flessionale (EI) deve essere ridotta rispetto al valore teorico secondo criteri prudenziali.

| Condizione solaio                        | Riduzione rigidezza EI (%) | Riferimento normativo/tecnico                |
|------------------------------------------|----------------------------|----------------------------------------------|
| Solaio nuovo, collaborazione piena        | 0%                         | NTC2018 §7.2.6, EN 1992-1-1 §9.3             |
| Solaio esistente, collaborazione incerta  | 20–30%                     | NTC2018 §7.2.6, CNR-DT 206/2007              |
| Solaio legno, degrado visibile            | 30–50%                     | NTC2018 §4.1.2.2, CNR-DT 206/2007            |
| Presenza aperture >10% area               | +10–20% (cumulabile)       | NTC2018 §7.2.6.2, letteratura                |
| Degrado/fessurazioni diffuse              | fino a 50%                 | NTC2018 §4.1.2.2, Santarella, Giangreco      |

**Note tecniche:**
- Le riduzioni sono cumulative: in presenza di più condizioni sfavorevoli, applicare la somma delle penalizzazioni.
- La scelta dei coefficienti deve essere motivata e documentata nel report di calcolo.
- In caso di incertezza, adottare sempre il valore più cautelativo.
- Per solai storici, è raccomandato il confronto tra valori attuali (NTC2018) e coefficienti storici (Santarella, Giangreco), riportando entrambi nel report.
- La verifica della rigidezza può essere affinata tramite prove sperimentali (carico, dinamica, endoscopia, ecc.).
- Per solai prefabbricati o con elementi innovativi, fare riferimento anche a manuali tecnici e certificazioni di prodotto.

**Riferimenti normativi:**
- NTC2018 §4.1.2.2: "Per le strutture esistenti... si deve tener conto di eventuali riduzioni di rigidezza dovute a degrado, fessurazioni, modifiche locali..."
- NTC2018 §7.2.6: "La rigidezza dei solai deve essere valutata considerando la reale efficacia collaborante tra gli elementi..."
- EN 1992-1-1 §9.3: "La rigidezza delle membrature deve essere valutata in funzione delle condizioni di vincolo e collaborazione..."
- CNR-DT 206/2007: "Per il legno strutturale esistente, si raccomanda una riduzione cautelativa della rigidezza in assenza di prove."
- Santarella, Giangreco: "Per solai storici, applicare coefficienti di sicurezza e riduzione secondo la letteratura tecnica."

---

## Contratto dati minimo (metacodice interfacce)

Il contratto definisce le interfacce Python minime per V1. Ogni campo ha unità esplicita e sorgente. Nessun override silenzioso.

### SolaiInputSpec

```python
@dataclass
class SolaiInputSpec:
    # ---- Identificazione ----
    tipologia: str             # "laterocemento"|"predalles"|"legno"|"acciaio"|"getto_pieno"|"misto"
    norma: str                 # "NTC2018"|"DM96"|"DM92"|"RD2229"
    edificio_esistente: bool   # True → confronto storico + LC/FC automatico

    # ---- Geometria [cm] ----
    luce: float                # Luce netta [cm]
    interasse: float           # Interasse tra nervature [cm]
    altezza_totale: float      # Altezza totale solaio [cm]
    spessore_soletta: float    # Spessore soletta collaborante [cm]; 0 se assente

    # ---- Materiali ----
    classe_cls: str            # "C25/30" (NTC2018) o "Rck200" (RD2229)
    tipo_acciaio: str          # "B450C" | "FeB44k"
    f_ck: float                # Resistenza caratteristica cilindrica [kg/cm²]
    f_yk: float                # Resistenza caratteristica acciaio [kg/cm²]

    # ---- Carichi [kg/m²] ----
    G1: float                  # Pesi permanenti strutturali [kg/m²]
    G2: float                  # Pesi permanenti non strutturali [kg/m²]
    Q: float                   # Carico variabile [kg/m²]
    cat_uso: str               # Categoria d'uso NTC2018 Tab.3.1.II ("A","B","C3",…)

    # ---- Livello conoscenza (esistenti) ----
    lc: str                    # "LC1"|"LC2"|"LC3" (NTC2018 §C8.5.4)
    fc: float | None           # Override FC; None → automatico da lc (via lc_fc_adjustments.py)

    # ---- Aperture e cerchiature ----
    aperture: list[dict]       # [{"posizione_cm": x, "larghezza_cm": b, "altezza_cm": h}]
    cerchiature: list[dict]    # [{"tipo": "trave_equiv"|"tipologica", "parametri": {...}}]

    # ---- Campate ----
    schema_vincolo: str        # "appoggiato"|"incastro-appoggio"|"doppio_incastro"|"continuo"
    n_campate: int             # Numero campate (≥1)
    luci_campate: list[float]  # Luce di ogni campata [cm]; len == n_campate
```

### SolaiOutputResult

```python
@dataclass
class SolaiOutputResult:
    # ---- Azioni ----
    M_Ed: float                # Momento sollecitante max [kg·cm]
    V_Ed: float                # Taglio sollecitante max [kg]
    combinazione_governante: str

    # ---- SLU ----
    M_Rd: float                # Momento resistente [kg·cm]
    V_Rd: float                # Taglio resistente [kg]
    ok_flessione: bool
    ok_taglio: bool
    UC_flessione: float        # M_Ed / M_Rd
    UC_taglio: float           # V_Ed / V_Rd

    # ---- SLE ----
    f_max: float               # Freccia massima calcolata [cm]
    f_lim: float               # Limite freccia [cm]
    ok_deformabilita: bool
    sigma_c_rara: float        # Tensione cls SLE rara [kg/cm²]
    sigma_c_qp: float          # Tensione cls SLE quasi-permanente [kg/cm²]

    # ---- Vibrazioni ----
    f1_hz: float               # Frequenza fondamentale [Hz]
    acc_rms: float             # Accelerazione RMS [m/s²]
    ok_vibrazioni: bool

    # ---- Tracciabilità ----
    passaggi: list[str]        # Passi di calcolo con formula e §fonte
    warning: list[str]         # Codici warning attivati
    esito_per_norma: dict      # {"NTC2018": True/False, "RD2229": True/False, …}
    fc_applicato: float        # FC effettivamente usato
    lc_applicato: str          # LC effettivamente usato
```

---

## Codici warning

Ogni warning ha codice univoco, gravità e azione raccomandata.

| Codice | Gravità | Descrizione | Azione |
|--------|---------|-------------|--------|
| `X-AREA-001` | INFO | Area di influenza inserita manualmente (`src/aree_influenza.py` non disponibile — attende Fase Y) | Verificare area; aggiornare quando Fase Y è pronta |
| `X-MAT-001` | WARNING | Parametri materiale non trovati in archivio; usati valori di default | Inserire parametri reali |
| `X-LC-001` | WARNING | LC1 applicato (FC=1,35); valori di progetto ridotti | Approfondire indagini per passare a LC2/LC3 |
| `X-APE-001` | WARNING | Apertura grande (>25% area): FEM locale raccomandato; attiva penalizzazione semplificata | Attivare FEM locale se disponibile |
| `X-APE-002` | ERROR | Apertura >50% area: riduzione EI cumulativa >70%; verificare manualmente | Revisione progettuale necessaria |
| `X-DEF-001` | WARNING | Freccia calcolata > limite normativo; SLE deformabilità non soddisfatta | Incrementare altezza solaio o ridurre luci |
| `X-VIB-001` | WARNING | Frequenza fondamentale <4 Hz: solaio potenzialmente sensibile a vibrazioni pedonali | Valutare comfort (NTC2018 §C7.10.5) |
| `X-VIB-002` | WARNING | Accelerazione RMS >0,5 m/s²: livello vibrazioni oltre soglia comfort | Verificare destinazione d'uso |
| `X-STORICO-001` | INFO | Verifica storica (RD2229/39) attivata; coefficienti storici applicati | Report include confronto storico/moderno |
| `X-COMP-001` | WARNING | Combinazione critica con azioni variabili multiple; verificare coerenza categorie d'uso | Confermare categorie NTC2018 Tab.3.1.II |

---

## Decisioni progettuali e storicizzazione

Le decisioni seguenti sono state fissate in sessione (15/03/2026) e costituiscono vincoli non modificabili senza revisione esplicita del piano.

| # | Decisione | Valore fissato | Data |
|---|-----------|----------------|------|
| D1 | Modello strutturale | 2D grigliato/piastra ortotropa | 2026-03-15 |
| D2 | Gestione aperture | Penalizzazione semplificata + FEM locale | 2026-03-15 |
| D3 | Gestione cerchiature | Doppio binario: travi equivalenti + libreria tipologica | 2026-03-15 |
| D4 | Vibrazioni | Risposta dinamica estesa (f₁ + acc. RMS) | 2026-03-15 |
| D5 | LC/FC | Configurabile per norma (automatico da LC; override manuale possibile) | 2026-03-15 |
| D6 | Confronto storico/moderno | Automatico solo per edifici esistenti | 2026-03-15 |
| D7 | Unità interne | cm, kg, kg/cm² (conversioni tracciate in output) | 2026-03-15 |
| D8 | Benchmark obbligatori | 5 casi (definiti nella Matrice test e benchmark) | 2026-03-15 |
| D9 | Soglia errore target | ≤2% sui casi con soluzione nota | 2026-03-15 |
| D10 | Esecuzione agente | Sequenza a step con checkpoint (non single-shot) | 2026-03-15 |

**Note operative:**
- Tutte le tipologie di solaio storico sono supportate (legno massiccio, putrelle e tavelloni, voltine di mattoni, ferro e laterizio, ecc.).
- Si applicano sia i coefficienti di sicurezza storici (Santarella, Giangreco) sia i valori attuali (NTC2018) per confronto — attivo solo per edifici esistenti (D6).
- Per la resistenza del legno storico: tabelle semplificate (CNR, letteratura) + inserimento manuale dei parametri.
- Per le aperture: penalizzazione semplificata e analisi locale avanzata (FEM) — conforme a D2.
- Nei report saranno sempre inclusi riferimenti bibliografici e formule storiche esplicite.
- Tutte le scelte e i parametri saranno tracciati nel log (`registro_log.py`) e motivati nel report.
- Decisione 2026-03-10 (confermata 2026-03-15): la logica delle aree di influenza è centralizzata in `src/aree_influenza.py` (Fase Y), condiviso tra solai, scale e fondazioni. Fino alla consegna di Fase Y: fallback manuale + warning `X-AREA-001` (precedente in Fase V: `V-AREA-002`).

---

## Subfasi pianificate

### X.1 — Analisi e classificazione tipologie di solaio

- [ ] Censimento e classificazione: prefabbricati, armatura lenta, storici, moderni (monodirezionali, bidirezionali, alleggeriti)
- [ ] Definizione parametri geometrici e meccanici per ciascuna tipologia
- [ ] Mappatura delle fonti normative e bibliografiche per ogni classe

### X.2 — Modelli di calcolo e parametri storici

- [ ] Raccolta e formalizzazione delle formule storiche (RD2229/39, Santarella, Giangreco)
- [ ] Tabelle armatura minima, coefficienti di omogeneizzazione, spessori equivalenti
- [ ] Implementazione delle relazioni storiche per verifica flessione, taglio, deformabilità
- [ ] Confronto diretto tra approccio storico e NTC2018 per casi tipici

### X.3 — Modelli di calcolo e parametri moderni

- [ ] Formalizzazione modelli per prefabbricati, monodirezionali, bidirezionali, U-Boot
- [ ] Definizione parametri di input/output e struttura dati
- [ ] Integrazione delle formule di verifica moderne (NTC2018, EN 1992, EN 15037-1, EN 13747)
- [ ] Gestione carichi, combinazioni, limiti deformabilità
- [ ] Calcolo aree di influenza tramite modulo condiviso (vedi Fase Y)

### X.4 — Caratteristiche della sollecitazione nella sezione

- [ ] Calcolo posizione asse neutro per ogni tipologia (metodo storico e moderno)
- [ ] Determinazione campo di rottura (compressione, trazione, crisi fragile/duro)
- [ ] Costruzione dominio di resistenza (M-N, diagrammi interazione)
- [ ] Output grafico e tabellare dei domini di resistenza
- [ ] Confronto tra dominio storico e dominio NTC2018

### X.5 — Gestione aperture, cerchiature e degrado

- [ ] Implementazione penalizzazione semplificata e FEM locale per aperture
- [ ] Algoritmo cumulativo per riduzione rigidezza (aperture, degrado, collaborazione incerta)
- [ ] Tabelle e warning automatici per condizioni critiche

### X.6 — Livelli di conoscenza e fattori di confidenza (NTC2018)

- [ ] Implementazione sistema livelli di conoscenza (LC1, LC2, LC3)
- [ ] Applicazione automatica dei fattori di confidenza (FC) su resistenze e parametri
- [ ] Output chiaro dei valori adottati e motivazione della scelta
- [ ] Integrazione con report e tracciabilità

### X.7 — Output, report e tracciabilità

- [ ] Generazione tabulati dettagliati (HTML/MD), con passaggi intermedi e riferimenti normativi
- [ ] Evidenziazione delle differenze tra verifica storica e moderna
- [ ] TODO: Strutturare template di report HTML/MD

### X.8 — Test, validazione e casi studio

- [ ] Test unitari per ogni tipologia e verifica (storica e moderna)
- [ ] Test di integrazione su casi reali e letteratura
- [ ] TODO: Definire casi studio di validazione e benchmark

---

## Guida operativa e checklist per ogni subfase

### X.1 — Analisi e classificazione tipologie di solaio

- [ ] Elencare e descrivere tutte le tipologie (storici, prefabbricati, moderni, ecc.)
- [ ] Definire per ciascuna: parametri geometrici, meccanici, materiali
- [ ] Collegare ogni tipologia a riferimenti normativi e bibliografici
- [ ] Strutturare classi Python e schema dati per ogni tipologia
- [ ] TODO: Validare la copertura di tutte le varianti note

### X.2 — Modelli di calcolo e parametri storici

- [ ] Implementare formule e tabelle RD2229/39 (flessione, taglio, deformabilità)
- [ ] Inserire coefficienti di omogeneizzazione, armature minime, spessori equivalenti
- [ ] Prevedere confronto automatico con NTC2018 per casi tipici
- [ ] TODO: Annotare ogni formula con fonte e validità

### X.3 — Modelli di calcolo e parametri moderni

- [ ] Implementare modelli secondo NTC2018 (SLU, SLE, combinazioni carico)
- [ ] Definire input/output coerenti con la struttura dati
- [ ] TODO: Integrare riferimenti EN 1992, EN 15037-1, EN 13747 se richiesto

### X.4 — Caratteristiche della sollecitazione nella sezione

- [ ] Calcolare posizione asse neutro, campo di rottura, dominio di resistenza (M-N)
- [ ] Generare grafici di interazione e output numerici
- [ ] TODO: Prevedere funzioni di plotting e confronto storico/moderno

### X.5 — Gestione aperture, cerchiature e degrado

- [ ] Offrire sia penalizzazione semplificata sia FEM locale come opzioni
- [ ] Implementare algoritmo cumulativo per riduzione rigidezza
- [ ] TODO: Warning automatici per condizioni critiche

### X.6 — Livelli di conoscenza e fattori di confidenza (NTC2018)

- [ ] Applicare livelli di conoscenza (LC1, LC2, LC3) e fattori di confidenza (FC) in modo automatico
- [ ] Esplicitare sempre i valori adottati e la motivazione
- [ ] TODO: Prevedere override manuale se richiesto in futuro

### X.7 — Output, report e tracciabilità

- [ ] Generare tabulati dettagliati, passaggi intermedi, riferimenti normativi e grafici
- [ ] Evidenziare differenze tra verifica storica e moderna
- [ ] TODO: Strutturare template di report HTML/MD

### X.8 — Test, validazione e casi studio

- [ ] Test unitari per ogni tipologia e verifica (storica e moderna)
- [ ] Confronto con letteratura tecnica
- [x] Casi studio di validazione e benchmark — definiti nella Matrice test e benchmark

---

## Pipeline a checkpoint (guida agente)

Ogni checkpoint è **bloccante**: l'agente non avanza senza soddisfare i criteri stop/go.
Deliverable minimi per ogni checkpoint: **codice + test + delta docs + delta memoria**.

### Checkpoint X.1 — Dataset tipologie e parametri

**Precondizioni:** nessuna

**Deliverable minimo:**
- `src/solai/tipologie.py` — dataclass per ogni tipologia con campi validati
- `tests/test_solai_tipologie.py` — ≥10 test (costruzione, valori limite, coerenza normativa)
- Delta `docs/memory/fase_X_context.md`: tipologie coperte

**Criteri stop/go:** tutti i test passano; ogni tipologia ha fonte normativa documentata; nessun campo senza unità.

---

### Checkpoint X.2 — Motore carichi e combinazioni

**Precondizioni:** X.1 completato

**Deliverable minimo:**
- `src/solai/carichi.py` — G1, G2, Q, peso proprio, area influenza (fallback manuale + `X-AREA-001`)
- `src/solai/combinazioni.py` — wrapper `ntc2018_combinations.py` per SLU/SLE/qp
- `tests/test_solai_carichi.py` — ≥8 test; `tests/test_solai_combinazioni.py` — ≥8 test

**Criteri stop/go:** combinazioni SLU/SLE coerenti con NTC2018 §2.5; peso proprio ±1% vs manuale; warning `X-AREA-001` attivo quando area inserita manualmente.

---

### Checkpoint X.3 — Verifiche resistenza SLU

**Precondizioni:** X.2 completato

**Deliverable minimo:**
- `src/solai/verifiche_slu.py` — flessione + taglio per tutte le tipologie
- `src/solai/lc_fc.py` — wrapper `lc_fc_adjustments.py` per Fase X
- `tests/test_solai_slu.py` — ≥15 test (≥1 per tipologia; ≥1 per LC1/LC2/LC3)

**Criteri stop/go:** UC_flessione e UC_taglio corretti ±2% per tutti i benchmark a soluzione nota; ogni verifica ha codice formula e §fonte; LC/FC applicato e tracciato.

---

### Checkpoint X.4 — Deformabilità e vibrazioni

**Precondizioni:** X.3 completato

**Deliverable minimo:**
- `src/solai/verifiche_sle.py` — freccia immediata + differita, tensioni SLE rara e qp
- `src/solai/vibrazioni.py` — f₁, acc. RMS, criteri comfort
- `tests/test_solai_sle.py` — ≥10 test; `tests/test_solai_vibrazioni.py` — ≥6 test

**Criteri stop/go:** freccia ±2% vs formula analitica; f₁ ±2% vs Dunkerley; warning `X-DEF-001`, `X-VIB-001`, `X-VIB-002` attivi alle soglie corrette.

---

### Checkpoint X.5 — Aperture e cerchiature *(parallelo a X.4)*

**Precondizioni:** X.3 completato

**Deliverable minimo:**
- `src/solai/aperture.py` — penalizzazione semplificata + interfaccia FEM locale
- `src/solai/cerchiature.py` — travi equivalenti + libreria tipologica base
- `tests/test_solai_aperture.py` — ≥8 test; `tests/test_solai_cerchiature.py` — ≥6 test

**Criteri stop/go:** riduzioni EI cumulative corrette; warning `X-APE-001` e `X-APE-002` attivi alle soglie corrette; benchmark BM-X04 entro ±2%.

---

### Checkpoint X.6 — Report e tracciabilità

**Precondizioni:** X.3 + X.4 + X.5 completati

**Deliverable minimo:**
- `src/solai/report_adapter.py` — HTML/MD con passaggi intermedi, formule, §normativi
- `tests/test_solai_report.py` — ≥6 test (struttura, contenuto minimo, encoding UTF-8)

**Criteri stop/go:** ogni passaggio ha §normativo; confronto storico/moderno presente per edifici esistenti; nessun valore senza unità.

---

### Checkpoint X.8 — Test, validazione e benchmark

**Precondizioni:** tutti i precedenti

**Deliverable minimo:**
- `tests/test_solai_benchmark.py` — 5 casi benchmark (vedi Matrice)
- `docs/memory/fase_X_history.md` aggiornato con risultati e hash commit finale
- `docs/piano_fase_X.md` Stato → COMPLETATO + hash commit

**Criteri stop/go:** tutti e 5 i benchmark ±2% vs riferimento; suite completa verde; nessun warning imprevisto.

---

## Strategia di scomposizione documentale della Fase X

Il file `docs/piano_fase_X.md` resta il master plan della fase. Quando il contenuto supera la soglia di manutenibilità, la documentazione deve essere scomposta in file modulari, uno per ciascun blocco implementativo principale.

### Regola di scomposizione

- Ogni nuovo file figlio deve avere una struttura autonoma analoga a questo piano: stato, obiettivo, dipendenze, fonti normative, contratti dati, formule, warning, benchmark/test, sub-fasi, storicizzazione.
- Il file master mantiene: visione generale, perimetro V1, dipendenze trasversali, roadmap, decisioni globali, matrice benchmark aggregata.
- I file modulo mantengono: dettaglio implementativo del singolo sottosistema.

### Mappatura proposta file → modulo

| Modulo | File proposto | Contenuto principale |
| --- | --- | --- |
| Tipologie + input | `docs/piano_fase_X1_tipologie_input.md` | classi tipologiche, input, unità, validazione campi |
| Carichi + combinazioni | `docs/piano_fase_X2_carichi_combinazioni.md` | G1/G2/Q, conversioni, combinazioni NTC, LC/FC |
| Verifiche SLU | `docs/piano_fase_X3_verifiche_slu.md` | flessione, taglio, punzonamento, domini e warning |
| Verifiche SLE + vibrazioni | `docs/piano_fase_X4_verifiche_sle_vibrazioni.md` | freccia, tensioni, frequenze, comfort |
| Aperture + cerchiature | `docs/piano_fase_X5_aperture_cerchiature.md` | modello cautelativo, trigger FEM, libreria interventi |
| Report + tracciabilità | `docs/piano_fase_X6_report_tracciabilita.md` | passaggi, riferimenti, export HTML/MD, log |
| Benchmark + validazione | `docs/piano_fase_X7_benchmark_validazione.md` | casi numerici, tolleranze, reference values, regressioni |
| Casi speciali | `docs/piano_fase_X8_casi_speciali.md` | predalles, collaboranti, CLT, estensioni V1.1+ |

### Struttura minima obbligatoria di ogni file figlio

```text
1. Stato e metadati
2. Scopo del modulo
3. Dipendenze reali del repo
4. Fonti normative con §/tabella
5. Contratto dati del modulo
6. Formule classificate (diretta / derivata / cautelativa)
7. Warning code del modulo
8. Quick reference testabile
9. Sub-fasi implementative
10. Cronologia e decisioni
```

### Regola per le sub-fasi nei file figli

- Le sub-fasi del file figlio devono essere coerenti con la macro-subfase del piano master.
- Esempio: `X3.1 input sezione`, `X3.2 flessione`, `X3.3 taglio`, `X3.4 punzonamento`, `X3.5 test`.
- Ogni file figlio deve chiudersi con criteri stop/go e deliverable minimi.

---

## Matrice test e benchmark (tolleranza ≤2%)

| ID | Caso | Tipologia | Norma | Grandezza di controllo | Input storici | Input SI | Riferimento analitico | Tolleranza |
|----|------|-----------|-------|----------------------|---------------|----------|-----------------------|------------|
| BM-X01 | Laterocemento appoggiato | Monodir. laterocemento | NTC2018 | M_Ed, V_Ed, f_max | G=300, Q=200 kgf/m²; i=50 cm; L=500 cm | G≈2,94, Q≈1,96 kN/m²; i=0,50 m; L=5,0 m | Trave semplicemente appoggiata; C25/30; B450C; LC2 | ≤2% |
| BM-X02 | Predalles multi-campata | Predalles 3 campate continue | NTC2018 | M_Ed campate neg./pos.; f_max campata centrale | G=250, Q=200 kgf/m²; i=120 cm; L=400 cm×3 | G≈2,45, Q≈1,96 kN/m²; i=1,20 m; L=4,0 m×3 | Linea elastica trave continua | ≤2% |
| BM-X03 | Legno storico | Massiccio monodir. | RD2229 | M_Ed, M_Rd_storico, confronto NTC2018, f_max | b=12 cm; h=20 cm; i=60 cm; L=400 cm; f_mk=250 kgf/cm² | b=0,12 m; h=0,20 m; i=0,60 m; L=4,0 m; f_mk≈24,5 MPa | Tabelle Santarella cap. XII | ≤2% |
| BM-X04 | Bidirezionale con apertura | Getto pieno 2D + apertura | NTC2018 | Riduzione EI, M_Ed zona apertura, warning X-APE-001 | Lx=Ly=600 cm; apertura 120×120 cm; Q=300 kgf/m² | Lx=Ly=6,0 m; apertura 1,20×1,20 m; Q≈2,94 kN/m² | Trigger FEM / modello cautelativo interno; LC2 | ≤2% |
| BM-X05 | Cerchiatura con trave equiv. | Laterocemento + cerchiatura | NTC2018 | M_Ed ridistribuito, UC trave equiv. | Trave equiv. 30×50 cm; input BM-X01 | Trave equiv. 0,30×0,50 m; input SI da BM-X01 | Modello grigliato semplice su BM-X01; B450C | ≤2% |

---

## Diagrammi di flusso (ASCII)

### Flusso generale di calcolo

```text
Input geometria/materiali/carichi
    |
    v
Normalizzazione unità e conversioni
    |
    v
Combinazioni NTC2018 / storico
    |
    +--> LC/FC se edificio esistente
    |
    v
Verifiche SLU (M, V, punzonamento)
    |
    v
Verifiche SLE (freccia, tensioni, vibrazioni)
    |
    +--> Aperture/cerchiature --> trigger FEM locale?
    |                             | yes
    |                             v
    |                        Analisi locale / warning
    v
Aggregazione warning + passaggi + formule
    |
    v
Report HTML/MD + benchmark + storico
```

### Flusso aperture e modello locale

```text
Apertura presente?
   |
   +-- no --> usa pannello pieno
   |
   +-- yes --> calcola rapporto area apertura / area pannello
            |
            +-- <= 10% --> modello cautelativo leggero
            +-- 10%-25% --> riduzione EI + warning
            +-- > 25% --> warning X-APE-001 + trigger FEM locale
            +-- > 50% --> warning X-APE-002 + verifica manuale obbligatoria
```

---

## Quick Reference Testabile

| ID test | Formula | Input minimi | Output atteso | Accettazione |
| --- | --- | --- | --- | --- |
| T-X01 | Flessione c.a. | $b$, $d$, $A_s$, $f_{ck}$, $f_{yk}$ | $M_{Rd}$, $x$, $z$ | $UC_M = M_{Ed}/M_{Rd} \le 1$ |
| T-X02 | Taglio | $b_w$, $d$, $A_{sl}$, $f_{ck}$ | $V_{Rd,c}$ | warning `X-TAG-002` se $V_{Ed}/V_{Rd,c}>0{,}6$ |
| T-X03 | Freccia | $q_s$, $i$, $L$, $E$, $I$ | $q_l$, $f_{max}$, $f_{lim}$ | `X-DEF-001` se $f_{max}>f_{lim}$ |
| T-X04 | Vibrazioni | $L$, $E$, $I$, $\rho$, $A$ | $m$, $f_1$, $a_{RMS}$ | `X-VIB-001` se $f_1<4$ Hz |
| T-X05 | Aperture | area pannello, area apertura, posizione | $\alpha_{ap}$, $EI_{eff}$ | `X-APE-001` / `X-APE-002` alle soglie corrette |
| T-X06 | LC/FC | $f_{ck}$, $f_{yk}$, LC | $f_{ck,adj}$, $f_{yk,adj}$ | FC coerente con NTC2018 §C8.5.4 |
| T-X07 | Punzonamento | $b_0$, $d$, $A_{sl}$, $f_{cd}$, $\sigma_{cp}$ | $V_{Rd,c}$ | `X-PUNZ-001` se $V_{Ed}>0{,}8V_{Rd,c}$ |

---

## Casi speciali da espandere in implementazione

### Predalles

- Richiede separazione tra soletta prefabbricata, getto integrativo e armature collaboranti.
- La verifica a flessione non può essere ridotta a sola sezione rettangolare omogenea senza controllo della fase costruttiva.
- Dipendenze future: EN 13747, cataloghi di prodotto, verifica della collaborazione tra elementi prefabbricati e getto.

### Solai collaboranti acciaio-calcestruzzo

- Da trattare come caso speciale, non incluso nella V1 strutturale minima.
- Richiede modello con scorrimento/interazione e riferimenti compositi dedicati; non assimilare al solaio pieno in c.a.
- Dipendenza futura: normativa compositi e moduli travi composte del repo.

### CLT

- Da gestire con modello anisotropo / ortotropo e non come semplice equivalente isotropo.
- Le verifiche flessione-taglio-vibrazioni richiedono parametri di pannello e connessioni; usare solo come placeholder pianificatorio in V1.
- Dipendenza futura: normative legno avanzate e possibile pacchetto materiali legno/CLT dedicato.

---

## Prompt agente AUTO

Incollare nella sessione di implementazione (modalità agent).

```
MISSIONE: Implementare Fase X — Solai in RD2229 seguendo docs/piano_fase_X.md.

REGOLE OPERATIVE:
1. Eseguire in ordine i checkpoint X.1 → X.2 → X.3 → X.4 (e X.5 in parallelo) → X.6 → X.8.
2. Non avanzare al checkpoint successivo senza soddisfare i criteri stop/go.
3. Leggere i file di dipendenza PRIMA di scrivere codice (percorsi corretti in tabella Dipendenze).
4. Non duplicare logica già presente in ntc2018_combinations.py, lc_fc_adjustments.py, registro_log.py.
5. Ogni formula deve avere: sorgente (§ norma o riferimento), campo di validità, unità.
6. Se una dipendenza non esiste (es. src/aree_influenza.py), applicare fallback documentato
   e attivare il warning codificato (X-AREA-001).
7. Ogni checkpoint produce: codice + test passanti + delta docs + delta memoria.

VINCOLI QUALITÀ:
- Tolleranza benchmark: ≤2% rispetto alla soluzione di riferimento.
- Nessun campo senza unità esplicita.
- Nessun warning senza codice.
- Test coverage ≥80% per i nuovi moduli.
- Unità interne: cm, kg, kg/cm².

DELIVERABLE FINALI:
- src/solai/ (tutti i moduli)
- tests/test_solai_*.py (suite completa)
- docs/memory/fase_X_context.md aggiornato
- docs/memory/fase_X_history.md con entry per ogni checkpoint
- docs/piano_fase_X.md: Stato → COMPLETATO + hash commit

RISORSE DISPONIBILI:
- Piano: docs/piano_fase_X.md
- Contesto: docs/memory/fase_X_context.md
- Storia: docs/memory/fase_X_history.md
- Template fase matura: docs/piano_fase_V.md
- Combinazioni NTC2018: src/core/combinations/ntc2018_combinations.py
- LC/FC: src/core_calculus/lc_fc_adjustments.py
- Log: src/core/registro_log.py
- Pattern report: src/codes/ntc2018/secondary_elements/*/report_adapter.py
```

---

# Sottosezioni tecniche dettagliate

## 1. Solai prefabbricati

### Travetti Varese, pianelle, prefabbricati c.a.p./c.a.v

- Travetti prefabbricati in c.a.p. (precompresso), sezione a T rovescia, appoggio su murature o travi.
- Interposti elementi di alleggerimento (pignatte o pianelle in laterizio).
- Soletta collaborante superiore in c.a. gettata in opera (spessore tipico 4–5 cm).
- Collegamento tra travetto e soletta tramite armature di ripresa e staffe.
- Parametri: altezza totale solaio, larghezza travetto, interasse, altezza pignatta, spessore soletta, resistenza calcestruzzo, armatura pretesa.
- Verifiche: flessione (sezione omogeneizzata), taglio (staffe, collegamento), deformabilità (freccia), collaborazione.
- Normativa: NTC2018 §4.1.2.2, §7.2.6, UNI EN 15037-1, manuali tecnici produttori.
- Tabelle di portata e armatura minime da produttore.

## 2. Solai ad armatura lenta e storici (RD2229/39)

### Solai con/ senza soletta collaborante

- Travetti in c.a. gettati in opera, armatura longitudinale “lenta”
- Pignatte/mattoni di alleggerimento (altezza h_m)
- Soletta superiore: presente o assente
- Armatura minima prescritta in funzione di h_m e larghezza travetto
- Coefficienti di omogeneizzazione γ per soletta collaborante
- Spessore equivalente: $h_{eq} = h_{trave} + \gamma \cdot s_{soletta}$
- Tabelle di portata in funzione di interasse, altezza pignatta, presenza soletta
- Verifiche: flessione (sezione omogeneizzata), taglio, deformabilità
- Normativa: RD2229/39, tabelle e formule storiche, confronto con NTC2018

#### Esempio tabella armatura minima RD2229/39

| Altezza mattone (h_m) | Armatura min. (cm²/m) |
|-----------------------|-----------------------|
| 10 cm                 | 0.30                  |
| 12 cm                 | 0.35                  |
| 15 cm                 | 0.40                  |
| 18 cm                 | 0.45                  |
| 20 cm                 | 0.50                  |

#### Coefficienti di omogeneizzazione tipici

| Materiale soletta | γ (E_cls/E_pignatta) |
|-------------------|----------------------|
| Laterizio         | 5–8                  |
| Cemento alleggerito| 3–5                 |

## 3. Solai moderni

### Monodirezionali

- Travetti paralleli, carico portato in una sola direzione
- Alleggerimento con pignatte o blocchi in EPS
- Soletta collaborante superiore
- Verifiche: come sopra, attenzione a interasse e spessore soletta

### Bidirezionali

- Griglia di travetti ortogonali (grigliato, predalles bidirezionale)
- Alleggerimento con casseri plastici (U-Boot, Iglu, ecc.)
- Carico distribuito su entrambe le direzioni (analisi a piastra)
- Verifiche: flessione/taglio in entrambe le direzioni, punzonamento

### Alleggeriti tipo U-Boot

- Casseri plastici riciclati, getto monolitico in c.a.
- Spessore variabile, altezza totale anche >30 cm
- Analisi con metodo delle piastre (modello di piastra ortotropa)
- Vantaggi: riduzione peso proprio, grandi luci, flessibilità architettonica
- Normativa: NTC2018 §4.1.2.2, §7.2.6, EN 1992-1-1 §9.3, EN 13747

## 4. Tabelle e formule di supporto

### Spessore equivalente

$$
h_{eq} = h_{trave} + \gamma \cdot s_{soletta}
$$

### Esempio metacodice verifica solaio (già presente sopra)

## 5. Note operative e riferimenti normativi

- Tutti i parametri devono essere configurabili e tracciabili
- Per ogni verifica, documentare la scelta dei coefficienti e delle formule
- Estratti normativi e bibliografici sempre inclusi nel report
- Confronto tra verifica storica (RD2229/39) e attuale (NTC2018) per solai esistenti

---
