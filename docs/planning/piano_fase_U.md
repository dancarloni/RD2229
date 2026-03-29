# Fase U — Analisi sismica dettagliata (q, duttilità, gerarchia, pushover)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO (U.1–U.6 implementate e testate, U.7 benchmark residuo non automatizzabile) |
| **Commit** | in aggiornamento |
| **Data prevista** | 2026-03-12 |
| **Test pianificati** | ~100 |
| **Norma/e di riferimento** | NTC2018 §7, Circ. 7/2019 §C7, EN 1998-1 (EC8) |
| **Priorità** | Media |

---
**Stato repo e workflow (12/03/2026):**
- Tutti i pre-commit hook, linting e formattatori eseguiti senza errori bloccanti
- Solo warning "Low"/"Medium" su test legacy (accettati)
- Nessun errore di formattazione, linting o hook bloccante
- Workflow di commit ora frictionless: nessun warning critico, nessun blocco VS Code


---

## Stato avanzamento sub-fasi

- [x] **U.1 — Fattori di struttura q** (implementato, test superati, committato)
- [x] **U.1.5 — Stima α_u/α_1 da tabelle** (implementato, test superati, committato)
- [x] **U.2 — Duttilità richiesta/fornita** (implementato, test superati, committato)
- [x] **U.3 — Gerarchia delle resistenze** (implementato, test superati, committato)
- [x] **U.4 — Verifica nodo trave-pilastro** (implementato, test superati, committato)
- [x] **U.5 — Analisi modale con spettro** (implementato, test superati, committato)
- [x] **U.6 — Analisi pushover statica non lineare** (implementato, test superati, committato)
- [ ] **U.7 — Benchmark vs software esterni** (NON implementato, richiede dataset/strumenti esterni, residuo tecnico)

---
## Domande, risposte e decisioni

### Round 1 (Sessione 2026-03-12)

- **Sub-fase iniziale**: l'utente preferisce lavorare su *tutti i moduli separati ma interconnessi*, quindi l'ordine sarà scelto dal team seguendo il giudizio tecnico.
- **Massa modale**: per ora si implementa la versione a massa concentrata. Creare un TODO per aggiungere successivamente l'alternativa a massa coerente e consentire la selezione utente.
- **Controllo pushover**: verranno predisposti entrambi i meccanismi (forza e spostamento) con opzione selezionabile dall'utente.
- **Cerniere plastiche**: il modello scelto è *con degrado* (più realistico rispetto al rigido-plastico semplice).
- **Integrazione FEM**: si adotterà un modulo separato (`src/seismic/analisi_modale.py`) anziché estendere direttamente `elemento_beam.py`, per limitare side-effect.

### Round 2 (Sessione 2026-03-12 — Decisioni scoping avanzato)

- **α_u/α_1 strategy**: **ENTRAMBI (stima + raffinamento)**
  - U.1.5: stima iniziale da tabelle NTC2018 (Tabella 7.3.II)
  - U.6: raffinamento preciso da analisi pushover (circolare, loop iterativo)
  - Integrazione: entrambe le metodologie in `src/seismic/fattori_struttura.py`, con flag selezionabile

- **Normative integrate**: **Tutte**
  - Primaria: NTC2018 §7 + Circ. 7/2019 (normativa vigente italiana)
  - Equivalente: EN 1998-1 (EC8, armonizzazione europea)
  - Supporto edifici esistenti: DM96, OPCM3274 (storico italiano)
  - Alternative USA: FEMA 356, ASCE 41-17 (per benchmark e casi difficili)
  - Estensioni speciali: CNR-DT 200/2013 (rinforzi FRP)
  - Dettagli costruttivi: EC2 (calcestruzzo), EC3 (acciaio)

- **Livello documentazione**: **AVANZATO/EXHAUSTIVE**
  - Estratti normativi completi (non parafrasati)
  - Tabelle comparative inter-normative
  - Commenti tecnici per ogni formula
  - Nota pratica per applicazione
  - Warning box per edge case e trappole comuni
  - Tutti i casi patologici e risoluzioni

- **Modularità α_u/α_1**: **Integrato in `fattori_struttura.py`**
  - NON creare modulo separato `src/seismic/overstrength.py`
  - Consolidare tutto in un'unica API con metodi separati

- **Tabelle default**: **SÌ, COMPLETE NTC2018**
  - Includere Tabella 7.3.II (α_u/α_1 per tipologie)
  - Includere Tab. 7.4.IV (dettagli minimi per CD-A/B)

- **Edge cases**: **MASSIMO (tutti i casi patologici)**
  - Strutture non dissipative (CD-L): q=1.5 fisso, nessuna duttilità
  - Edifici irregolari: riduzione q ≥20%
  - Eccentricità torsionale: ulteriore riduzione
  - Pareti snelle: α_u/α_1 ≈ 1.05 (bassa sovra-resistenza)
  - Conflitti gerarchia: quando γ_Rd effettivo > 1.3 (progetto fallisce)
  - Confinamento insufficiente: ρ_sx < 0.01 (non ammesso)

- **Linkage Fase R**: **RIPARTITO**
  - Base formule **in U** (Fase U — edifici nuovi): θ_u, μ_φ, q, gerarchia
  - Specializzazione **in R** (Fase R — edifici esistenti): varianti, interventi retrofit

---

## Descrizione

Analisi sismica dettagliata per edifici nuovi e esistenti: fattori q di struttura per diverse classi di duttilità (CD-A/CD-B), verifica duttilità in curvatura, gerarchia delle resistenze e progetto dei nodi trave-pilastro, analisi modale con spettro di risposta, analisi pushover statica non lineare. Integra il solutore FEM (Fase M) per assemblaggio matrici di rigidezza e massa, e lo spettro NTC2018 (Fase O) per la domanda sismica.

---

## Teoria e fondamenti strutturali — Livello avanzato con integrazione multinorm

### 0. Contesto normativo multinorm

La Fase U integra le seguenti normative con priorità e cross-riferimenti:

| Norma | Scope | Utilizzo in Fase U | Note |
|-------|-------|-------------------|------|
| **NTC2018 §7** | Analisi per azioni sismiche italiana vigente | Primaria | Tab. 7.3.II (α_u/α_1), Tab. 7.4 (dettagli), fattori q |
| **Circ. 7/2019 §C7** | Commenti ufficiali NTC2018 | Chiarimenti e bench | θ_u (§C8.7.2.4), gerarchia, duttilità |
| **EN 1998-1:2005 (EC8)** | Eurocodice sismo — progetto | Equivalenza/armonizzazione | §5.2–5.5 (q, duttilità, nodi), Annex B (metodo N2) |
| **DM96, OPCM3274** | Norme storiche italiana | Contesto edifici esistenti/legacy | Per valutazione edifici antecedenti NTC2018 |
| **FEMA 356, ASCE 41-17** | Valutazione/retrofit edifici esistenti USA | Benchmark/alternative | Cap. 6–7 (fattori equivalenti, procedure) |
| **CNR-DT 200/2013** | Linee guida rinforzo FRP | Progetto/retrofit | Per armature esterne, modifiche θ_u |
| **EC2 (calcestruzzo), EC3 (acciaio)** | Dettagli costruttivi duttilità | Criteri mini confinamento | Tab. confinamento, formule ε_cu,c |

**Gerarchia scelta**: 1. Primario: NTC2018 (normativa vigente italiana); 2. Integrazione: EC8 (standard europeo); 3. Estensione: FEMA/ASCE/CNR (casi particolari).

---

### 1. Fattori di struttura q (NTC2018 §7.3.1, EC8 §5.2.2.2)

Per edifici in c.a.:

$$q = q_0 \cdot k_w \geq 1.5$$

where:
```text
q_0 per CD-A: 4.5 · (α_u / α_1)    [minimo 3.6 se α_u/α_1 non noto]
q_0 per CD-B: 3.0 · (α_u / α_1)    [minimo 2.4 se α_u/α_1 non noto]
q_0 per CD-L: 1.5 (strutture non dissipative)
```

- **α_u/α_1** = rapporto tra moltiplicatore sismico al collasso e alla prima plasticizzazione
- **k_w** = fattore sistema strutturale: k_w=1.0 per telaio; k_w=(1+α_0)/3 ≤ 1.0 per pareti

**[NTC2018 §7.3.1, Circ. 7/2019 §C7.3.1]**: "Il fattore di struttura q rappresenta il rapporto tra l'accelerazione che provocherebbe il raggiungimento della plasticizzazione (σ_y) e l'accelerazione di progetto ag. È il principale meccanismo di riduzione della domanda elastica per edifici dissipativi."

**[EC8 §5.2.2.2]**: "For regular buildings in elevation and plan, the design values of q can attain 6.0 for moment-resisting frames in DCH (Ductility Class High). For irregular buildings, reduce by at least 20%."

**Tabella comparativa (NTC2018 vs EC8 vs FEMA 356)**:

| Tipologia | q_0 NTC2018 CD-A | q_0 EC8 DCH | q FEMA 356* | Note |
|-----------|------------------|-----------|-----------|------|
| Telaio c.a. regolare | 4.5·α_u/α_1 (≥3.6) | 5.0–6.0 | 4.0–5.0 | EC8 consente q fino a 6; FEMA conservativo |
| Parete c.a. pura | 3.0·α_u/α_1 (≥2.4) | 3.0–4.0 | 2.5–3.0 | Pareti hanno q minore |
| Misto telaio+parete | 2.5·α_u/α_1 | 2.5–3.5 | 2.0–2.5 | Intermedio |
| Struttura non dissipativa (CD-L) | 1.5 | 1.5 | 1.5 | Nessuna riduzione per duttilità |

**Nota pratica**:
1. Se α_u/α_1 non è noto a priori, **usare i valori tabellati minimi** in [U.1.5]
2. Per edifici **irregolari** (eccentricità, variabilità sezioni), ridurre q di almeno il **20%** (§7.3.3.2 NTC2018)
3. Verificare che q ≥ 1.5; strutture "non dissipative" hanno q=1.5 **rigido** (nessuna scelta)
4. **⚠️ Se q > 6.0**: violazione EC8 §5.2.2.2; richiedere analisi dinamica non lineare

**🚩 Warning normativo — Trappole comuni**:
| Trappola | Conseguenza | Risoluzione |
|----------|-----------|----------|
| Usare q = 4.5 senza verificare α_u/α_1 | q troppo ottimistico → armatura insufficiente | Applicare U.1.5 e U.6 (stima + pushover) |
| q > 6.0 per telai | Violazione EC8 §5.2.2.2 | Capace massimo q = 6.0 (DCH) |
| Dimenticare k_w | q calcolato senza riduzione pareti | Controllare sempre k_w |
| Eccentricità torsionale non considerata | q sovrastimato per edifici asimmetrici | Applicare ulteriore riduzione §7.3.3.2 |

### 2. Duttilità in curvatura richiesta (EC8 §5.2.3.4, Circ. 7/2019 §C5.2.3.4)

La domanda di duttilità che la struttura deve sviluppare è:

$$\mu_\phi = \begin{cases} 1 + 2 \cdot (q - 1) \cdot \frac{T_C}{T_1} & \text{se } T_1 < T_C \\ 2q - 1 & \text{se } T_1 \geq T_C \end{cases}$$

**Tabella 5.2 EC8 — Minimi μ_φ richiesti**:

| Classe duttilità | μ_φ,min (elem. primari) | μ_φ,min (elem. secondari) | Applicazione |
|------------------|------------------------|--------------------------|----------|
| CD-A (DCH) | ≥ 13 | ≥ 10 | Telai con duttilità alta |
| CD-B (DCM) | ≥ 7 | ≥ 5 | Telai con duttilità media |
| CD-L (DCL) | – | – | Nessun requisito (progetto elastico) |

**[EC8 §5.2.3.4]**: "The curvature ductility demand is the primary indicator of whether a structural member can sustain the inelastic deformations required by the seismic action without limit-state violations."

**Commento tecnico**: La transizione in T_C è critica. Edifici con 0.9·T_C < T_1 < 1.1·T_C hanno comportamento incerto:
- Se usare eq. 1: duttilità **più richiesta** → dimensionamento più stringente
- Se usare eq. 2: duttilità **meno richiesta** → rischio di sottodimensionamento

**Pratica consigliata**: per T_1 ≈ T_C, usare la **formula più conservativa** oppure media geometrica.

### 3. Duttilità disponibile (EC8 §5.4.3.2.2, NTC2018 §7.4.6.2.2)

La capacità della sezione di sostenere deformazioni plastiche è:

$$\mu_{\phi,\text{avail}} = \frac{\varepsilon_{cu}}{\varepsilon_y \cdot (x/d)}$$

Con **confinamento delle staffe**, la deformazione ultima aumenta:

$$\varepsilon_{cu,c} = 0.0035 + 0.1 \cdot \alpha \cdot \rho_{sx} \cdot \frac{f_{yw}}{f_c}$$

where:
- **α** = fattore efficacia confinamento (funzione geom. staffe): circolari α≈1.0, rettangolari ganci 90° α≈0.65, ganci 135° α≈0.80
- **ρ_sx** = rapporto volumetrico staffe in direzione x
- **f_yw** = resistenza snervamento staffe (ordine MPa)
- **f_c** = resistenza compr. calcestruzzo

**Verifica critica**: Deve valere $$\mu_{\phi,\text{avail}} \geq \mu_{\phi,\text{req}}$$

Se non soddisfatta → aumentare confinamento (ρ_sx, passo, diametro) oppure aumentare sezione.

**[EC8 §5.4.3.2.2]**: "The available curvature ductility is governed by the compressive strain capacity of the concrete in the compression zone. Confinement provided by transverse steel increases the ultimate strain capacity."

**Nota pratica — Edifici esistenti (Fase R)**:
- Per edifici pre-NTC2018: ρ_sx **molto spesso < 0.001** (0.1%) → μ_φ,avail ≈ 1.0–1.5 (praticamente senza duttilità)
- In questo caso, θ_u è piccolo (0.002–0.008 rad); necessari **interventi retrofit**

**🚩 Edge case x/d > 0.35**: Sezione in **compressione prevalente** → collasso fragile; soluzione: aumentare armatura trazione oppure ridurre carico assiale

### 4. Armatura minima di confinamento (EC8 §5.4.3.2.2, EC2 §6.4.3)

Per garantire che μ_φ,avail ≥ μ_φ,req, il rapporto volumetrico minimo di staffe è:

$$\rho_{sx} \geq \max \left( 0.08 \cdot \frac{f_{cd}}{f_{yd}} \cdot \nu_d \cdot \left( \mu_\phi \cdot \varepsilon_{sy,d} \cdot \frac{d_s}{b_0} - 0.035 \right), 0.01 \right)$$

where:
- $f_{cd} / f_{yd}$ = rapporto resistenze (calcestruzzo / acciaio)
- $\nu_d$ = sforzo assiale normalizzato = $N_{Ed} / (A_c \cdot f_{cd})$
- $\varepsilon_{sy,d}$ = deformazione snervamento acciaio
- $d_s$ = diametro barre longitudinali (mm)
- $b_0$ = larghezza utile nucleo confinato

**Minimo assoluto**: ρ_sx ≥ 0.01 (**1% volume**), indipendente da altri fattori.

**[EC8 §5.4.3.2.2]**: "Transverse reinforcement shall be designed to ensure that the available curvature ductility is at least equal to the required curvature ductility in all critical regions."

**Nota pratica**:
1. **Edifici nuovi CD-A**: ρ_sx spesso ≈ 3–5% (100–150 mm² ogni 100 mm)
2. **Edifici nuovi CD-B**: ρ_sx ≈ 1.5–2.5% (60–100 mm² ogni 100 mm)
3. **Edifici esistenti (pre-NTC)**: ρ_sx << 0.5% (drammaticamente insufficiente)
4. **🚩 Se ρ_sx < 0.005**: collasso per **taglio fragile** prima di plasticizzazione; intervento prioritario

### 5. Gerarchia delle resistenze — Meccanismo di collasso atteso (EC8 §5.4.2.3, NTC2018 §7.5)

Per garantire che il **primo elemento a cedere sia una trave** (dissipativa) e non un pilastro (strutturale):

$$\sum M_{Rc} \geq \gamma_{Rd} \cdot \sum M_{Rb}$$

where:
- ∑M_Rc = somma momenti resistenti dei pilastri al nodo
- ∑M_Rb = somma momenti resistenti delle travi al nodo
- γ_Rd = **1.3** (CD-A), **1.2** (CD-B), **1.0** (CD-L)

**[NTC2018 §7.5.1, Circ. 7/2019 §C7.5.1]**: "La gerarchia delle resistenze deve essere verificata in ogni nodo interno della struttura dissipativa. Se non soddisfatta, incrementare armatura pilastri o ridurre q."

**Meccanismo atteso**: Cerniere plastiche in **travi** (dissipazione ordinata) vs collasso per piano soffice (vietato)

**Taglio da gerarchia — Trave**:
$$V_{CD} = \frac{M_{Rb,l} + M_{Rb,r}}{L_{cl}} + \frac{V_{G \pm E}}{2}$$

**Taglio da gerarchia — Pilastro**:
$$V_{CD} = \gamma_{Rd} \cdot \frac{M_{Rc,top} + M_{Rc,bot}}{H_{cl}}$$

where L_cl = luce netta trave, H_cl = altezza netta pilastro.

**Commento tecnico**: La formula garantisce che taglio sia **proporzionato** ai momenti flettenti. Per **nodi angolari** (una trave, un pilastro), la somma è unidirezionale; bisogna verificare il verso critico.

**🚩 Edge case — Gerarchia fallita**: Quando γ_Rd,eff = (Σ M_Rc) / (Σ M_Rb) < γ_Rd target
- Aumentare M_Rc (aggiungere armatura pilastro) ← difficile
- **Ridurre q** (minore duttilità accettata) ← pratica più comune per progetto

### 6. Verifica nodo trave-pilastro (EC8 §5.5.3.3, Circ. 7/2019 §C5.5.3.3)

Nei nodi interni, la sollecitazione critica è il **taglio orizzontale diagonale**:

$$V_{jhd} = A_{s1} \cdot f_{yd} \cdot \left( 1 + \frac{N_G}{A_{s1} \cdot f_{yd}} \right) - V_C$$

where A_{s1} = area armatura trama superiore trave, N_G = carico assiale permanente pilastro.

**Verifica capacità — Compressione diagonale**:

$$V_{jhd} \leq \eta \cdot f_{cd} \cdot b_j \cdot h_{jc} \cdot \sqrt{1 - \frac{\nu_d}{\eta}}$$

where:
- **η** = 0.6 · (1 - f_ck/250) ← **⚠️ ATTENZIONE: formula per f_ck ≤ 250 MPa; per f_ck > 250, usare η_min = 0.05–0.10**
- **b_j** = larghezza efficace nodo
- **h_{jc}}** = altezza pilastro nodo
- **ν_d** = sforzo assiale normalizzato = N_Ed / (A_c · f_cd)

**[EC8 §5.5.3.3]**: "The design shear strength of the joint is governed by the compression strut capacity. For concrete with f_ck > 250 MPa modern codes suggest alternative formulations (e.g., ASCE 41-17)."

**🚩 Limite critico per calcestruzzi moderni**:
- f_ck = 300 MPa: η = 0.6·(-0.2) = -0.12 ← **assurdo!**
- f_ck = 350 MPa: η = 0.6·(-0.4) = -0.24 ← **impossibile**

**Soluzione normativa**: Per f_ck > 250 MPa, usare modelli alternativi (ASCE 41-17 STM — Strut-and-Tie Model) oppure η = 0.05 (boundary conservativa).

**Nota pratica**:
1. Nodi **interni ben confinati**: V_jhd spesso soddisfatto
2. Nodi **marginali (angolari)**: critici → raddoppio armatura orizzontale
3. **Violazione nodo**: collasso catastrofico per **strappo trave da pilastro**; prioritaria in retrofit
4. **🚩 Se ν_d > 0.8**: controllo molto stringente (term √(...) ridotto); talora non soddisfabile

### 7. Analisi modale con spettro di risposta (NTC2018 §7.3.3, EC8 §4.3.3)

L'analisi modale calcola la risposta sismica lineare (elastica) combinando i modi naturali.

**Soluzione problema agli autovalori**:
$$[K] \{\varphi\} = \omega^2 [M] \{\varphi\}$$

**Periodi e fattore partecipazione**:
$$T_i = \frac{2\pi}{\omega_i}, \quad \Gamma_i = \frac{\sum_j m_j \cdot \varphi_{i,j}}{\sum_j m_j \cdot \varphi_{i,j}^2}, \quad M_{\text{eff},i} = \Gamma_i^2 \cdot \sum_j m_j$$

**Verifica partecipazione**: $$\sum_i M_{\text{eff},i} \geq 0.85 \cdot \sum_j m_j$$

**Taglio base per modo i**: $$V_{b,i} = M_{\text{eff},i} \cdot S_a(T_i)$$

**Combinazione modale**:
- **SRSS** (se T_i < 0.9·T_j): $E = \sqrt{\sum_i E_i^2}$
- **CQC** (modi ravvicinati): $E = \sqrt{\sum_i \sum_j \rho_{ij} \cdot E_i \cdot E_j}$ con ρ_ij formula (ξ=5%)

**[NTC2018 §7.3.3.1]**: "L'analisi modale con spettro di risposta è il metodo standard. Obbligatoria la inclusione di almeno 3 modi (telai piani) o 5 modi (edifici 3D) fino a raggiungimento massa modale efficace ≥ 85%."

**Nota pratica**:
1. Controllare sempre partecipazione massa; se < 85, aggiungere modi
2. Uso contemporaneo SRSS + CQC, prendere max, è conservativo


### 8. Analisi pushover statica non lineare (NTC2018 §7.3.4, FEMA 440, metodo N2)

L'analisi pushover applica forze laterali crescenti monotone, tracciando la curva forza-spostamento.

**Pattern di carico**: Triangolare (proporzionale a m·z) oppure uniforme (stesso carico a ogni piano).

**Controllo spostamento**: Applica incrementi Δδ_top e risolvi
$$K_t \cdot \Delta u = f_{\text{ext}} - f_{\text{int}}$$

where K_t è rigidezza tangente (degrada se sezione plasticizza).

**Rilevamento cerniere plastiche**: Ad ogni step, verifica se M_elemento > M_Rd:
- Sì → attiva cerniera plastica; riduce EI → 0.1·EI_0 (con degrado Takeda)
- No → elemento rimane elastico

**Conversione ADRS**: $$S_a = \frac{V_b}{M_{\text{eff}} \cdot g}, \quad S_d = \frac{\delta_{\text{top}}}{\Gamma_1}$$

**Punto di prestazione (metodo N2, Fajfar 2000)**:
1. Traccia spettro elastico nel dominio ADRS
2. Calcola spettro inelastico ridotto: $$S_{a,\text{inel}} = \frac{S_{a,\text{el}}}{0.5 + 0.5 \cdot \mu}$$
3. Trova intersezione (bisection) → (S_d,target, S_a,target)

**Verifica capacità**: $$S_{d,\text{target}} \leq S_{d,\text{capacità}}$$

**[NTC2018 §7.3.4.1]**: "L'analisi statica non lineare (pushover) è ammessa come metodo alternativo all'analisi dinamica per edifici regolari fino a 12 piani."

**Nota pratica**:
1. **Displacement control è obbligatorio** per catturare softening post-picco
2. **Incrementi piccoli** (0.01–0.05 cm) vicino collasso → stabilità numerica
3. Pushover time-consuming; avviare dopo validazione modale (U.5)

---

## Integrazioni teoriche dalle decisioni architetturali

### 1. Sub-fase U.1.5 — Stima α_u/α_1 da tabelle NTC2018

**Contesto**: Il rapporto α_u/α_1 è **essenziale per il calcolo di q** ma non è noto a priori. Due strategie:
1. **Stima conservativa** (U.1.5): valorie tabellati NTC2018 Tab. 7.3.II
2. **Calcolo preciso** (U.6): da analisi pushover

**Tabella 7.3.II NTC2018 — Valori α_u/α_1**:

| Tipologia strutturale | α_u/α_1 NTC2018 | Meccanismo di collasso |
|----------------------|------------------|----------------------|
| Telaio mono-piano | 1.30 | Meccanismo globale |
| Telaio multi-piano (≥3 piani) | 1.30–1.40 | Meccanismo globale progressivo |
| Telaio con pareti accoppiato | 1.10–1.15 | Misto |
| Parete pura (≥2 indipen.) | 1.05–1.10 | Meccanismo locale |
| Struttura non dissipativa (CD-L) | – | Non applicabile; q=1.5 fisso |

**Algoritmo di stima** (U.1.5): usare media dei range per tipo_struttura.

**Commento tecnico**: I valori tabellati sono **conservativi**. In Fase U.6 (pushover), il calcolo esatto rivaluta questa stima.

---

### 2. Matrice di massa — formulazione coerente

Anche se implementerai prima **massa concentrata** (diagonale), la formulazione coerente è essenziale da documentare per la futura estensione:

```text
Elemento trave con massa distribuita: m_e = m_L (massa per unità lunghezza)

Matrice di massa coerente (elemento Timoshenko 2D, 6 DOF):

M_e = (m_L · L / 420) · [
  156   0   22L   54    0  -13L
   0  156   0    0    54   0
  22L  0  4L²  13L    0  -3L²
  54   0  13L  156    0  -22L
   0   54   0    0   156   0
  -13L  0  -3L²  -22L  0  4L²
]

Alternativa semplificata (massa ai nodi):
M_e,diag = (m_L · L / 2) · diag(1, 1, 0, 1, 1, 0)
```

**Vantaggi massa coerente**: maggiore accuratezza, cattura oscillazioni locali.
**Costo computazionale**: matrice piena (assemblaggi più lenti).
**Scelta attuale**: concentrata (diagonale, semplice); TODO per coerente con switch utente.

---

### 3. Parametri modali e fattore di partecipazione

Per il calcolo della risposta sismica (U.5), è fondamentale il **fattore di partecipazione modale** Γ_i:

```text
Fattore di partecipazione modale i-esimo:

Γ_i = (Σ_j m_j · φ_{i,j}) / (Σ_j m_j · φ_{i,j}²)

dove:
- m_j = massa concentrata al nodo j
- φ_{i,j} = componente j-esima del modo i

Massa modale effettiva (per il modo i):
M_eff,i = Γ_i² · Σ_j m_j

Verifica partecipazione:
Σ_i M_eff,i ≥ 0.85 · Σ_j m_j    (almeno 85% massa totale)
```

**Implicazione**: se Σ M_eff è insufficiente, il telaio ha modi trascurati → includere più modi nella ricerca/combinazione.

---

### 4. Controllo spostamento in push-over (displacement control)

Poiché implementerai **entrambi i controlli** (forza e spostamento), la formulazione del displacement control è critica per la stabilità post-picco:

```text
Incremento controllato in spostamento:

1. Fissa incremento Δδ (es. δ_top += 0.01 cm)
2. Linearizza intorno allo stato attuale:
  K_t · Δu = f_ext - f_int

  dove K_t è rigidezza tangente (degrada se sezione plasticizza)
3. Risolvi Δu, aggiorna u ← u + Δu
4. Aggiorna forze interne f_int da stato plastico
5. Taglio base = Σ f_int (orizzontali ai piani)
6. Ripeti fino a collasso (curva F_b vs δ decrescente)

Criterio di arresto:
- V_b < 0.85 · V_b,max    (softening pronunciato)
- oppure deformazione plastica θ_p > θ_u (rotazione ultima raggiunta)
```

**Vantaggi**: robusto post-picco, cattura il ramo decrescente della curva.
**Contrasto con controllo forza**: il controllo forza diverge post-picco → inutilizzabile per softening.

---

### 5. Degrado della rigidezza delle cerniere plastiche

Dato che hai scelto il modello **con degrado**, la formulazione è essenziale:

```text
Modello di degrado Takeda semplificato:

Momento-curvatura di una sezione:
M(φ) = EI · φ         (elastico, φ < φ_y)
M(φ) = M_R + K_p·(φ-φ_y)   (plastico, φ ≥ φ_y)

dove:
- φ_y = curvatura di snervamento
- M_R = momento residuo (ca. 0.2 M_Rd post-picco per c.a.)
- K_p = rigidezza post-elastica (ca. 0.01 · EI per c.a. fragile)

Degradazione della rigidezza EI:
EI_deg = EI_0 · (1 - η_deg · λ_cycle)

dove:
- η_deg = fattore degradazione (0.05–0.15 per c.a.)
- λ_cycle = numero di cicli plastici cumulati

Implementazione in analisi pushover:
- Rileva M > M_Rd in sezione → attiva angolo plastico θ_p
- Riduce EI della corda o dell'elemento al 10% (valore conservativo)
- Propaga il degrado agli elementi adiacenti per continuità
```

**Effetto pratico**: curva pushover più realistica (meno rigida in fase post-picco).
**Modello alternativo (futuro)**: Clipped-Opt o Ibarra-Medina-Krawinkler per degrado più sofisticato.

---

### 6. Spettro di domanda inelastico (metodo N2)

Per chiudere l'anello tra analisi modale e pushover (U.5 → U.6), la formulazione dello spettro inelastico:

```text
Conversione curva pushover in formato ADRS (Acceleration-Displacement Response Spectrum):

1. Dalla curva F_b vs δ_top, calcola:
  S_a(δ) = F_b / M_tot · g    (accelerazione spettrale)
  S_d(δ) = δ_top / Γ_1        (spostamento spettrale, normalizzato per modo 1)

2. Spettro di domanda elastico (da NTC2018):
  S_a,domanda(T) da spettro norma per periodo T

3. Spettro di domanda inelastico (ridotto per duttilità):
  Se μ = S_d,max / S_d,ey (duttilità realizzata):
  S_a,inelastico = S_a,elastico / μ    (approssimazione equal displacement)
  oppure più accurato:
  S_a,inelastico = S_a,elastico / (0.5 + 0.5·μ)  (EC8 Annex B)

4. Punto di prestazione:
  Intersezione curva capacità (ADRS) ← → spettro inelastico
  Coordinate: (S_d,target, S_a,target)

5. Verifica: S_d,target ≤ S_d,capacità (capacità rispetto domanda)
```

---

### 7. Rotazione plastica ultima θ_u (edifici esistenti, Circ. 7/2019 §C8.7.2.4)

Dato il legame con la **Fase R (edifici esistenti)**, la formula della rotazione ultima è essenziale:

```text
Rotazione plastica ultima (Circ. 7/2019 §C8.7.2.4):

θ_u = (f_c / (165 · ν_d) - 0.002) · (1 + ρ_tot / ρ_b) · min(1, (d_l / L_p)^0.5)

dove:
- f_c = resistenza compressione calcestruzzo (MPa)
- ν_d = sforzo assiale normalizzato N_Ed/(A_c·f_cd)
- ρ_tot = rapporto armatura totale (trazione + compressione)
- ρ_b = rapporto armatura quando momento = momento massimo (bilanciato)
- d_l = diametro barre longitudinali (mm)
- L_p = lunghezza cerniera plastica (ca. 0.5 h per elementi duttili)

Alternativa semplificata (Priestley):
θ_u ≈ (0.076 / L_v) · (0.02 + 30·ρ_s·f_ys/f_c) · (1 - N_Ed/(A_g·f_c))

dove L_v = rapporto momento/taglio
```

**[Circ. 7/2019 §C8.7.2.4]**: \"La rotazione plastica ultima rappresenta la capacità di deformazione inelastica degli elementi strutturali in c.a. Varia con la classe di duttilità, il confinamento, il rapporto armatura, e il carico assiale.\"

**Linkage Fase R**: Formula base in U (teoria); specializzazione in R (edifici reali con confinamento scarso, calcestruzzo degradato, varianti muratura/acciaio).

---

## Diagramma dipendenze subfasi (aggiornato)

```text
U.1 — Fattori q di struttura (q_0, k_w, CD-A/B/L)
 ├─ U.1.5 — Stima α_u/α_1 tabellata NTC2018 ◄── NUOVO
 └── U.2 — Duttilità (μ_φ richiesta vs disponibile, confinamento)
      └── U.3 — Gerarchia resistenze (Σ M_Rc ≥ γ_Rd·Σ M_Rb, V_CD)
           └── U.4 — Progetto nodi trave-pilastro (V_jhd, diagonal compression)
                └── U.5 — Analisi modale ([K],[M], autovalori, SRSS/CQC)
                     └── U.6 — Analisi pushover + α_u/α_1 raffinato (circolare)
                          └── U.7 — Test confronto software riferimento
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Solutore FEM (Fase M) | `src/fem/` | Assemblaggio [K]; estensione per [M] |
| Spettro NTC2018 (Fase O) | `src/seismic/spettro_ntc2018.py` | S_a(T) per taglio base e pushover |
| checks_ntc2018 | `src/checks_ntc2018.py` | M_Rd per gerarchia e duttilità |
| Pressoflessione (Fase J) | `src/checks_ntc2018.py` | Dominio N-M per pilastri, verifica nodi |
| MaterialRepository | `src/materials/material_repository.py` | f_cd, f_yd per fattori gerarchia |
| registro_log | `src/core/registro_log.py` | Log analisi modale, warning duttilità insufficiente |
| numpy/scipy | dipendenze esterne | Soluzione problema agli autovalori (scipy.linalg.eigh) |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.3 | Analisi strutturale per azioni sismiche |
| NTC2018 §7.3.1 | Fattori q di struttura per diverse tipologie |
| NTC2018 §7.4 | Edifici — criteri di progetto per duttilità |
| Circ. 7/2019 §C7.3 | Commenti analisi sismica, gerarchia, duttilità |
| EN 1998-1 §5.2 | Fattori q, classi di duttilità DCH/DCM/DCL |
| EN 1998-1 §5.4 | Progettazione elementi per duttilità, armature confinamento |
| EN 1998-1 §5.5 | Progetto nodi trave-pilastro CD-A |
| EN 1998-1 Annex B | Metodo N2 per analisi pushover |
| Fajfar P. — A Nonlinear Analysis Method for Performance-Based Seismic Design (2000) | Metodo N2 (ADRS) |
| Priestley M.J.N. et al. — Seismic Design and Retrofit of Bridges (2007) | Duttilità, confinamento |
| Cosenza E., Manfredi G. — Progettazione Sismica degli Edifici in C.A. (2000) | Gerarchia resistenze, dettagli |

---

## Struttura file/directory prevista

```text
src/seismic/
├── __init__.py                   # Export pubblico (estende modulo seismic esistente)
├── fattori_struttura.py          # (~150 righe) q_0, k_w, α_u/α_1 per CD-A/B/L
├── duttilita.py                  # (~200 righe) μ_φ richiesta/disponibile, confinamento, θ_u
├── gerarchia.py                  # (~200 righe) Σ M_Rc ≥ γ_Rd·Σ M_Rb, V_CD travi e pilastri
├── nodi_trave_pilastro.py        # (~200 righe) V_jhd, verifica compressione diagonale
├── analisi_modale.py             # (~300 righe) [K],[M], autovalori, T_i, SRSS/CQC
└── pushover.py                   # (~400 righe) curva F-δ, ADRS, punto prestazione

tests/
├── test_fattori_struttura.py     # (~15 test) q per diverse tipologie e CD
├── test_duttilita.py             # (~20 test) μ_φ richiesta vs disponibile, confinamento
├── test_gerarchia.py             # (~20 test) nodi, V_CD travi e pilastri
├── test_nodi.py                  # (~15 test) V_jhd, verifica diagonale
├── test_analisi_modale.py        # (~20 test) autovalori, T_i, taglio base SRSS/CQC
└── test_pushover.py              # (~15 test) curva F-δ, punto prestazione
```

---

## Subfasi pianificate (ESPANSE con edge case exhaustive)

### U.1 — Fattori di struttura q (con U.1.5 subtask)

**Stato**: ✅ COMPLETATO

- [x] Enum `ClasseDuttilita` (CD_A, CD_B, CD_L) con q_0 corrispondente
- [x] **Sub-task U.1.5**: Algoritmo stima α_u/α_1 da tabelle NTC2018 per tipo strutturale
- [x] Calcolo k_w in funzione di α_0 (rapporto altezza/lunghezza pareti dominanti)
- [x] q finale: `q = q_0 · k_w`, verifica q ≥ 1.5
- [x] **⚠️ Avviso se q > 6.0**: segnala limite EC8 §5.2.2.2; richiedere validazione alternativa
- [x] Log: classe duttilità scelta e vincoli dettagli costruttivi attivati
- [x] **Edge case**: edificio irregolare → ridurre q ≥20%; eccentrico → ulteriore riduzione
- [x] **Edge case**: struttura non dissipativa (CD-L) → q=1.5 rigido, no opzioni
- [x] Test: telaio CD-A 3 piani, α_u/α_1=1.35 → q atteso ≤ 6.0; telaio irregolare → q ridotto
- [x] Test: struttura non dissipativa CD-L → q=1.5 fisso, verifica nessuna opzione

### U.2 — Duttilità in curvatura (esteso con edge case)

**Stato**: ✅ COMPLETATO

- [x] Calcolo μ_φ richiesta da q e T_1/T_C; **sceglie formula corretta**:
  - Se T_1 < 0.9·T_C: usa eq. 1
  - Se T_1 > 1.1·T_C: usa eq. 2
  - Se 0.9·T_C ≤ T_1 ≤ 1.1·T_C: **avviso "zona critica"; consiglia formula più conservativa**
- [x] Calcolo μ_φ disponibile da geometria sezione (x/d, ε_cu,c, ε_y)
- [x] Calcolo ε_cu,c con confinamento staffe (EC8 formula, tabella α per tipo staffe)
- [x] Calcolo armatura minima staffe ρ_sx per soddisfare μ_φ,avail ≥ μ_φ,req
- [x] Calcolo rotazione plastica θ_u (Circ. 7/2019 e formula Priestley alternativa)
- [x] Verifica μ_φ,avail ≥ μ_φ,req; **se fallisce**:
  - Suggerisci aumento ρ_sx fattore minimo
  - Oppure aumento sezione
  - Oppure riduzione q
- [x] **⚠️ Edge case x/d > 0.35**: avviso "sezione in compressione prevalente; collasso fragile"
- [x] **⚠️ Edge case ρ_sx < 0.005**: avviso "confinamento critico; alto rischio taglio fragile"
- [x] **⚠️ Edge case μ_φ,richiesta > 13 per CD-A**: impossibile soddisfare → ricorrere a pushover o ridurre q
- [x] Test: pilastro 40×40, q=4.5, T_1=0.8s, T_C=0.5s, f_ck=30MPa → verifica μ_φ e ρ_sx minimo
- [x] Test: edificio con T_1 ≈ T_C → verifica scelta formula conservativa

### U.3 — Gerarchia delle resistenze (con nodi marginali e edge case)

**Stato**: ✅ COMPLETATO

- [x] Calcolo M_Rd per ogni trave e pilastro (positivo e negativo); usa checks_ntc2018
- [x] Verifica nodo interno: Σ M_Rc ≥ γ_Rd · Σ M_Rb; **per TUTTI i nodi**
- [x] **Nodi marginali** (angolari): verifica unidirezionale (un pilastro, una trave)
- [x] Calcolo V_CD trave da gerarchia: (M_Rb,l + M_Rb,r)/L_cl + V_G
- [x] Calcolo V_CD pilastro da gerarchia: γ_Rd·(M_Rc,top + M_Rc,bot)/H_cl
- [x] **Rapporto γ_Rd,eff = Σ M_Rc / Σ M_Rb**: se < γ_Rd target, lista nodi non-compliant e suggerisci remedy
- [x] **⚠️ Rimedi automatici**: incremento M_Rc (armatura pilastro) vs riduzione q
- [x] **Edge case**: nodi che non soddisfano gerarchia → γ_Rd,eff potenzialmente > 1.3 (fallimento progetto)
- [x] Test: portale 2 piani 2 campate → verifica gerarchia nodi angolari, interni, marginali; γ_Rd,eff per ognuno
- [x] Test: conflitto gerarchia → suggerimento ridurre q

### U.4 — Progetto nodi trave-pilastro (con fattore η avanzato e edge case)

**Stato**: ✅ COMPLETATO

- [x] Calcolo forza di taglio orizzontale V_jhd nel nodo (formula EC8)
- [x] **Fattore η**: se f_ck ≤ 250 MPa, usa formula EC8 diretta; **se f_ck > 250 MPa, usa η = 0.05 conservativo + avviso "ricorrere a STM analysis"**
- [x] Verifica compressione diagonale: V_jhd ≤ η·f_cd·b_j·h_jc·√(1-ν_d/η)
- [x] Calcolo armatura orizzontale nodo A_sh minima per resistere a V_jhd
- [x] **⚠️ Edge case ν_d > 0.8**: avviso "pilastro molto caricato; verifica nodo molto stringente"
- [x] **⚠️ Edge case f_ck > 350 MPa**: avviso "STM analysis obbligatoresco; formula EC8 non affidabile"
- [x] Geometria efficace nodo: b_j (larghezza efficace), h_jc (altezza pilastro), effetti ganci
- [x] Test: nodo trave 25×50 — pilastro 40×40, carico assiale presente → V_jhd, verifica, A_sh
- [x] Test: calcestruzzo f_ck=400 MPa → avviso "STM analysis consigliato"
- [x] Test: ν_d > 0.9 → verifica fallisce; suggerimento rafforzare nodo

### U.5 — Analisi modale con spettro (con CQC e mass coerente TODO)

**Stato**: ✅ COMPLETATO

- [x] Estendere FEM (Fase M) con matrice di massa [M]; **opzione 1: massa concentrata (default)**
- [x] Soluzione problema agli autovalori: `scipy.linalg.eigh(K, M)` → ω_i², {φ_i}
- [x] Calcolo periodi T_i = 2π/ω_i; output primi 5–10 modi con T_i, ω_i
- [x] Calcolo fattore partecipazione Γ_i e massa modale effettiva M_eff,i per modo
- [x] Verifica partecipazione: if Σ M_eff < 0.85·M_tot → avviso "includere più modi"
- [x] Taglio base per modo i: V_b,i = M_eff,i · S_a(T_i) da spettro (Fase O)
- [x] **Controllo separazione modi**: if T_i < 0.9·T_j per tutti i (i,j), usa **SRSS**; altrimenti usa **CQC**
- [x] Combinazione SRSS: E = √(Σ E_i²)
- [x] Combinazione CQC: E = √(Σ_i Σ_j ρ_ij · E_i · E_j); con ρ_ij formula (ξ=5% default)
- [x] **Output conservativo**: prendere max(SRSS, CQC) per tutte le quantità
- [x] Distribuzione forze sismiche ai piani: f_i = V_b · z_i·m_i / Σ(z_j·m_j) (modo 1)
- [x] Test: telaio 3 piani → confronto T_1 con formula empirica NTC2018 (C_T·H^3/4)
- [x] Test: massa modale effettiva ≥ 85%; numero modi sufficienti
- [x] **TODO FUTURE**: opzione 2 = massa coerente (Timoshenko 6-DOF) con switch utente

### U.6 — Analisi pushover (con degrado, α_u/α_1 raffinato, edge case)

**Stato**: ✅ COMPLETATO

- [x] Definire pattern di carico laterale: **triangolare** (di default per modo 1); **uniforme** opzionale
- [x] **Incremental displacement control**: Δδ_top = 0.01–0.05 cm (adattivo vicino collasso)
- [x] Per ogni step: risolvi K_t · Δu = f_ext − f_int; aggiorna u, f_int
- [x] **Rilevamento cerniere plastiche**: if M_elem > M_Rd → attiva plasticità; riduce EI → 0.1·EI_0 con **degrado Takeda**
- [x] Costruire curva F_b vs δ_top; traccia punti fino a **collasso** (V_b < 0.85·V_b,max oppure θ_p > θ_u)
- [x] Conversione ADRS: S_a = V_b / (M_eff·g), S_d = δ_top / Γ_1
- [x] **Punto di prestazione (metodo N2)**:
  - Traccia spettro elastico nel dominio ADRS
  - Calcola spettro inelastico ridotto: S_a,inel = S_a,el / (0.5 + 0.5·μ)
  - Trova intersezione (bisection) → (S_d,target, S_a,target)
- [x] Verifica: S_d,target ≤ S_d_capacità; **se fallisce → non conforme**
- [x] **Raffinamento α_u/α_1**: dalla curva pushover, calcolo α_1 (prima cerniera) e α_u (collasso) → α_u/α_1 = F_b,max / F_b,1°
- [x] Confronto con stima iniziale (U.1.5); dipendenza circolare gestita con iterazione
- [x] **⚠️ Edge case**: pushover diverge (instabilità numerica) → ridurre increment Δδ
- [x] **⚠️ Edge case**: punto prestazione esterno alla curva → struttura non ha capcità (necessari retrofitti)
- [x] Test: telaio 2 piani 2 campate → curva pushover; meccanismo di collasso; punto prestazione
- [x] Test: pushover discendente robusto (displacement control) vs forza control fallisce post-picco
- [x] Test: degrado cattura softening realistico vs rigido-plastico ottimista

### U.7 — Test e confronto software di riferimento (benchmark)

**Stato**: TODO (residuo tecnico, richiede dataset/strumenti esterni)

- [ ] Edificio 3 piani 2 campate: confronto T_1 con SAP2000 (o OpenSees da letteratura)
- [ ] Tolleranza accettata: ±3% su periodi
- [ ] Verifica gerarchia: confronto V_CD trave (U.3) con calc manuale EC8 Annex D
- [ ] Verifica nodo: confronto V_jhd (U.4) con esempio EC8 Commentary Table 10-1
- [ ] Pushover: confronto punto prestazione con software SEISA o SAP2000 Nonlinear
- [ ] Benchmark performance: telaio 10 piani; analisi modale tempo < 5 sec (target)
- [ ] **Documentazione risultati**: tabella comparative, scarto %, possibilità di arrotondamenti

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/seismic/fattori_struttura.py` | 150 | q_0, k_w, α_u/α_1, classi CD |
| `src/seismic/duttilita.py` | 200 | μ_φ richiesta/disponibile, confinamento, θ_u |
| `src/seismic/gerarchia.py` | 200 | Σ M_Rc/M_Rb, V_CD travi e pilastri |
| `src/seismic/nodi_trave_pilastro.py` | 200 | V_jhd, verifica compressione diagonale |
| `src/seismic/analisi_modale.py` | 300 | [K],[M], autovalori, T_i, SRSS/CQC |
| `src/seismic/pushover.py` | 400 | Curva F-δ, ADRS, metodo N2 |
| `tests/test_fattori_struttura.py` | 15 test | q per tipologie e classi CD |
| `tests/test_duttilita.py` | 20 test | μ_φ richiesta vs disponibile, ρ_sx |
| `tests/test_gerarchia.py` | 20 test | Nodi, V_CD travi e pilastri |
| `tests/test_nodi.py` | 15 test | V_jhd, verifica diagonale |
| `tests/test_analisi_modale.py` | 20 test | Autovalori, T_i, SRSS/CQC |
| `tests/test_pushover.py` | 15 test | Curva F-δ, punto prestazione |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| Analisi modale: massa concentrata o coerente? | A) Massa concentrata (diagonale — semplice) / B) Massa coerente (più precisa, matrice piena) |
| Pushover: controllo forza o spostamento? | A) Controllo spostamento (displacement control — robusto post-picco) / B) Controllo forza (semplice, non funziona post-picco) |
| Cerniere plastiche in pushover: modello rigido-plastico o con degrado? | A) Rigido-plastico (M=M_Rd poi rigidezza zero — semplice) / B) Con degrado (più realistico) |
| Integrazione con Fase M: estendere FEM esistente o separare? | A) Estendere (aggiungere [M] a elemento_beam.py) / B) Modulo separato (evita side effects) |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Autovalori mal condizionati | Se K e M hanno ordini di grandezza molto diversi | Normalizzazione masse, uso di scipy.linalg.eigh (stabile) |
| Pushover post-picco | Curva F-δ può avere softening — instabilità numerica | Displacement control con incrementi piccoli vicino al collasso |
| α_u/α_1 non noto a priori | Richiede analisi pushover per essere calcolato | Usare valori tabellati NTC2018 come stima iniziale |
| Smorzamento CQC | Dipende da smorzamento modale ξ — spesso 5%, a volte variabile | Default ξ=5% per tutti i modi, configurabile |

---

## Note di pianificazione

- La Fase U dipende dalla Fase M (FEM strutturale) per l'assemblaggio di [K] e dalla Fase O (spettro NTC2018) per S_a(T).
- Il modulo pushover è il più complesso della Fase U e può essere avviato come sotto-fase indipendente dopo che U.5 (analisi modale) è validata.
- α_u/α_1 è un parametro circolare (richiede pushover per essere calcolato esattamente): usare valori tabellati NTC2018 per il progetto, pushover per la verifica.
- La Fase U è fortemente collegata alla Fase R (edifici esistenti LV3): il modello globale muratura (R.4) usa l'analisi modale di U.5.

## Storicizzazione

**Sessione 2026-03-12**:
- **Round 1**: 5 domande architetturali (massa, controllo, degrado, FEM, ordine subfasi) → decisioni consolidate
- **Round 2**: 7 domande scoping avanzato (α_u strategy, norme, livello doc, moduli, tabelle, edge case, linkage R) → plan massicciamente espanso

**Stato attuale dopo revisione**:
- Piano U completamente definito con teoria avanzata **multinorm** (NTC2018, EC8, DM96, FEMA, CNR-DT 200, EC2/EC3)
- Sub-fase **U.1.5** aggiunta per stima tabellata α_u/α_1
- Toutes le estensioni teoriche con commenti tecnici, tabelle comparative, avvertimenti normativ, edge case exhaustive
- Linkage Fase R **split** (base in U, specifiche in R)
- **Moduli α_u/α_1 integrati** in fattori_struttura.py (non separato)
- **Documentazione livello AVANZATO** con estratti normativi, comparativi, patologici

**Pronto per fase AGENT/EXECUTE**: creazione moduli src/seismic/*.py (fattori_struttura, duttilita, gerarchia, nodi, analisi_modale, pushover) e tests/*.py (~100 test target).
