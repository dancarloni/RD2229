# DM 9/1/1996 — Formule Stato Limite di Esercizio (SLE)

**Data ricerca**: 2026-03-29 | **Fonte**: Web search + PDF ufficiali DM96 e Circolare 252/1996

---

## 1. FESSURAZIONE — Larghezza delle fessure (w_k, w_d)

### Formula primaria

$$w_d = 1.7 \cdot \Delta s_m \cdot \varepsilon_{sm}$$

Dove:
- **w_d** = larghezza di progetto della fessura (mm)
- **Δs_m** = distanza media tra le fessure (mm)
- **ε_sm** = deformazione unitaria media dell'acciaio in zone fessurate (‰)

### Parametri correlati

**Distanza media tra fessure (Δs_m)**:
- Calcolata al livello baricentrico dell'armatura entro l'area efficace
- Dipende da: diametro barre, percentuale armatura, tipo calcestruzzo
- Valore tipico: 200-400 mm per sezioni normali

**Deformazione unitaria media (ε_sm)**:
- Differenza tra deformazione acciaio e calcestruzzo: ε_sm - ε_cm
- Calcolata dai momenti flettenti effettivi, considerando fessurazione

### Riferimenti normativi
- **DM 9/1/1996** § Verifiche di esercizio
- **Circolare 15/10/1996 n. 252** — Istruzioni alle DM96 (G.U. 26/11/1996 n. 277)
- **EC2** — EN 1992-1-1 approcci alternative (semi-empiriche)

---

## 2. DEFORMAZIONI — Freccia e spostamenti

### Procedure DM96

DM96 rimanda a procedure iterative per il calcolo della freccia, considerando:

1. **Rigidezza efficace** della sezione fessurata:
   - Momento di inerzia efficace: **I_eff** (compreso tra I_0 non fessurato e I_II fessurato)
   - Coefficiente di distribuzione ξ tra I_0 e I_II

2. **Effetti del tempo** (non reversibili):
   - **Fluage** (creep): φ(t) coefficiente di fluage in funzione del tempo
   - **Ritiro** (shrinkage): ε_cs deformazione da ritiro

### Formulazione semplificata (metodo ξ)

$$I_{eff} = \xi \cdot I_0 + (1 - \xi) \cdot I_{II}$$

Dove:
- **I_0** = momento di inerzia sezione non fessurata (con calcestruzzo)
- **I_II** = momento di inerzia sezione fessurata (solo acciaio + calcestruzzo teso)
- **ξ** = coefficiente di distribuzione (0 ≤ ξ ≤ 1)

### Freccia totale (versione base)

$$f_{tot} = f_{elastica} + f_{fluage} + f_{ritiro}$$

Dove:
- **f_elastica** = freccia da carico elastico (classica formula EI)
- **f_fluage** = φ(t) × f_elastica (contributo fluage)
- **f_ritiro** = contributo ritiro (deformazione libera)

### Formulazione DM96 dettagliata

La procedura iterativa richiede:

1. Calcolo momento flettente M (da combinazione SLE)
2. Determinazione sezione fessurata vs non-fessurata
3. Calcolo I_eff considerando fessurazione progressiva
4. Calcolo freccia elastica: f_e = f(M, I_eff, L, E_s, E_c)
5. Amplificazione per fluage: f_fluage = φ(t) × f_e
6. Aggiunta contributo ritiro

### Coefficienti DM96 tipici
- **Fluage** φ(t): 1.2-2.0 (a lungo termine) vs 0.3-0.6 (a breve termine)
- **Ritiro** ε_cs: -300 a -500 × 10^-6 (dipende da umidità, durata)
- **Modulo elastico** E_s = 200.000 MPa (acciaio), E_c ≈ 290.000-330.000 MPa (calcestruzzo)

### Riferimenti normativi
- **DM 9/1/1996** § Verifiche di esercizio — Deformazioni
- **Circolare 252/1996** — Procedimento iterativo dettagliato
- **CEB-FIP Model Code** — Base storica del procedimento

**Nota**: DM96 consente procedimenti semplificati (tabellari) per casi comuni, ma per precisione è consigliato il metodo iterativo.

---

## 3. TORSIONE — Verifica elementi sottoposti a torsione

### Modello di resistenza (traliccio)

DM96 utilizza il **modello della sezione cava equivalente** (hollow section model):

$$T_d \leq T_{Rd} = 2 \cdot A_\Omega \cdot t \cdot f_{ywd} \cdot \cot\theta$$

Dove:
- **T_d** = momento torcente di progetto
- **A_Ω** = area racchiusa dal perimetro medio p_e (area nucleo)
- **t** = spessore equivalente della parete
- **f_ywd** = resistenza di progetto dell'acciaio trasversale
- **θ** = angolo delle armature trasversali (45° tipico)

### Geometria della sezione

Per sezione rettangolare solida:

$$\Omega = b' \cdot h'$$

$$p_e = 2(b' + h')$$

Dove:
- **b'** = larghezza della sezione meno coprifer (copriferro)
- **h'** = altezza della sezione meno copriferro
- **p_e** = perimetro medio

**Diametro cerchio inscritto**:
$$h = \frac{d_e}{6}$$

Dove d_e è il diametro del maggior cerchio inscrivibile nel poligono dei centri delle barre.

### Concetto "nucleo non reattivo"

- Nel modello DM96, il **nucleo centrale della sezione** è considerato **non fessurato** in condizioni di servizio
- La **resistenza torsionale** risiede nel **profilo periferico** (parete equivalente dello spessore s)
- Validazione sperimentale: sezione solida e sezione cava con **stesso perimetro** hanno medesima risposta torsionale in condizioni fessurate

### Dimensionamento delle armature di torsione

1. **Area armatura longitudinale**:
   $$A_{sl} = \frac{T_d \cdot u}{2 \cdot f_{yd}}$$

   Dove u è il perimetro del nucleo, distribuita lungo la sezione

2. **Armatura trasversale** (staffe):
   - Calcolate dalla formula di resistance di cui sopra
   - Tipicamente: φ6-φ8 mm, passo 100-200 mm

### Interazione taglio-torsione

DM96 richiede verifica di **interazione** tra taglio V e torsione T:

$$\sqrt{\left(\frac{V}{V_{Rd}}\right)^2 + \left(\frac{T}{T_{Rd}}\right)^2} \leq 1.0$$

### Riferimenti normativi
- **DM 9/1/1996** § Verifica a torsione
- **Circolare 252/1996** § Torsione — procedimento di calcolo
- **Giorgio Serino** — Lezioni Tecnica Costruzioni, [Federica e-Learning](http://www.federica.unina.it/ingegneria/tecnica-delle-costruzioni-2/torsione-nel-ca/)
- **BeEngineered** — [Modelli torsione e interazioni](https://www.beengineered.it/torsione-nel-calcestruzzo-armato-modelli-di-calcolo-e-interazione-con-taglio-e-flessione/)

---

## 4. TABELLA RIEPILOGATIVA

| Verifica | Formula Base | Limitazione | Figura di merito |
|----------|--------------|------------|-----------------|
| **Fessurazione** | w_d = 1.7 Δs_m ε_sm | w_d ≤ 0.3 mm (SLE) | Ampiezza fessure |
| **Deformazione** | I_eff = ξI_0 + (1-ξ)I_II | f ≤ L/250 tipico | Freccia |
| **Torsione** | T_d ≤ 2 A_Ω t f_ywd cot θ | Armatura trasversale | Momento torcente |

---

## 5. NOTE DI IMPLEMENTAZIONE

### Semplificazioni accettabili per MVP
1. **Fessurazione**: Usare formula w_d base con parametri tabellari (Δs_m, ε_sm standard)
2. **Deformazione**: Procedimento ξ semplificato con fluage costante φ=1.5
3. **Torsione**: Modello hollow section senza interazione taglio

### Step di completamento
- [ ] Implementare formula w_d in `src/methods/dm96/checks.py:1030-1051`
- [ ] Completare procedimento deformazioni iterativo
- [ ] Implementare verifica torsione con area nucleo
- [ ] Aggiungere test benchmark vs valori noti

### Link al codice
- `src/methods/dm96/checks.py` — Implementazione verifiche DM96
- `tests/test_dm96_sle.py` — Test state limit di esercizio

---

**Documento creato**: Sprint B1 Session 2026-03-29
**Autore**: Claude AI (Web search + PDF analysis)
**Stato**: Reference doc per implementazione — Formule complete
