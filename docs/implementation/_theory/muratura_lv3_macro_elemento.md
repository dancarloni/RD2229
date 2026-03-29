# Macro-Elemento Muratura LV3 — Modello SVD e Accoppiamento Taglio-Flessione

**Data**: 2026-03-29
**Status**: BOZZA RICERCA (in sviluppo)
**Norma Primaria**: NTC2018 §7.8 (edifici esistenti)
**Norme Integrate**: EN 1996-1-1, Circ. 7/2019, ASCE 41-06
**Autore**: RD2229 — Calcolo Strutturale Muratura

---

## Indice

1. [Panoramica del modello](#panoramica)
2. [Equazioni fondamentali accoppiamento σ-τ](#equazioni-fondamentali)
3. [Parametri del modello](#parametri-modello)
4. [Criterio di rottura e legame costitutivo](#criterio-rottura)
5. [Algoritmo SVD iterativo](#algoritmo-svd)
6. [Esempio numerico step-by-step](#esempio-numerico)
7. [Riferimenti normativi](#riferimenti)

---

## 1. Panoramica del modello {#panoramica}

### 1.1 Contesto e necessità

Per edifici in **muratura existenti (LV3)**, la valutazione sismica secondo NTC2018 §7.8 richiede un'analisi non lineare che:

1. **Accoppia taglio e flessione** nel piano della parete (interazione σ-τ in stato biassiale)
2. **Modella l'evoluzione della resistenza** con la compressione preesistente (σ₀)
3. **Gestisce la rotazione degli assi principali di stress** durante il carico laterale (fenomeno cruciale per muratura)

### 1.2 Livelli di conoscenza e valutazione (NTC2018 §8.4)

| Livello | Conoscenza | Analisi Richiesta | Domanda Sismica |
|---------|-----------|-------------------|-----------------|
| **LV1** | Limitata | Meccanismi locali semplici | Spettro elastico (q=1) |
| **LV2** | Media | Analisi equivalente (SAC) o modale | Spettro con q ridotto (2–2.5) |
| **LV3** | Completa | **Modello 3D globale non lineare** | **Analisi pushover o dinamica** |

La **Fase U (Muratura LV3)** implementa il livello più dettagliato, con macro-elementi che simulano il comportamento accoppiato σ-τ mediante:

- Modello **Shear-Flexure Coupled (SFC)** o **Strut-Diagonal Compression (SDC)**
- Tensioni principali **σ₁, σ₂** calcolate iterativamente (SVD = Singular Value Decomposition)
- Rotazione automatica degli assi principali durante applicazione delle azioni

### 1.3 Scala di analisi: macro-elemento

Un **macro-elemento muratura LV3** rappresenta un **maschio murario** o una **fascia di collegamento** con:

- Geometria semplificata: rettangolare, spessore costante (t), altezza (h), lunghezza (L)
- Stato di stress 2D nel piano: σₓ (compressione verticale), σᵧ (compressione orizzontale), τₓᵧ (taglio)
- Rottura per: **fessurazione diagonale**, **scorrimento**, **pressoflessione**, **compressione eccentrica**

---

## 2. Equazioni Fondamentali — Accoppiamento σ-τ {#equazioni-fondamentali}

### 2.1 Stato di stress 2D nel piano della parete

Per un macro-elemento soggetto a:

- **Carico verticale** N [kg] → tensione media verticale σₘ = N / (L×t)
- **Taglio orizzontale** V [kg] → tensione media di taglio τₘ = V / (L×t)
- **Momento flettente** M [kg·cm] → eccentricità e = M/N (se N > 0)

Il **tensore di stress** nel sistema locale (x=orizzontale, y=verticale) è:

$$\boldsymbol{\sigma} = \begin{pmatrix} \sigma_x & \tau_{xy} \\ \tau_{xy} & \sigma_y \end{pmatrix}$$

dove:

- **σₓ** = tensione orizzontale (compressione positiva) [kg/cm²]
- **σᵧ** = tensione verticale media = σₘ [kg/cm²]
- **τₓᵧ** = tensione di taglio media = τₘ [kg/cm²]

### 2.2 Tensioni principali (diagonalizzazione del tensore)

Le tensioni principali σ₁ (massima) e σ₂ (minima) sono calcolate come autovalori:

$$\sigma_1, \sigma_2 = \frac{\sigma_x + \sigma_y}{2} \pm \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}$$

L'**angolo di rotazione** degli assi principali (rispetto a x-y) è:

$$\theta = \frac{1}{2} \arctan\left(\frac{2\tau_{xy}}{\sigma_x - \sigma_y}\right)$$

**Osservazione critica**: Durante il carico laterale, l'angolo θ varia iterativamente. La resistenza a taglio diminuisce se σ₁ passa da compressione a trazione.

### 2.3 Criterio accoppiato (Mohr-Coulomb con compressione preesistente)

La **resistenza a taglio nel piano** dipende dalla **compressione verticale preesistente** σ₀:

$$\tau_{\text{max}} = v_0 + \mu \cdot \sigma_n$$

dove:

- **v₀** = resistenza a taglio senza compressione (coesione) [kg/cm²]
- **μ** = coefficiente d'attrito (0.4–0.8 per muratura)
- **σₙ** = tensione normale media sulla fessura diagonale [kg/cm²]

**Per muratura storicamente costruita**, secondo EN 1996-1-1 e Circ. 7/2019 §C8.7.1.3.1.1:

- **v₀** = 0.15–0.35 kg/cm² (in funzione della malta e del tipo di muratura)
- **μ** = 0.40–0.65 (leggermente inferiore a calcestruzzo: 0.5–0.7)

### 2.4 Interazione σ-τ: Criterio di Drucker-Prager esteso per muratura

Per muratura con comportamento **fragile-duttile**, il criterio combinato è:

$$F = \frac{\tau_{xy}^2}{\tau_0^2} + \alpha \cdot \frac{\sigma_1}{\sigma_{\text{lim}}} - 1 \leq 0$$

dove:

- **τ₀** = resistenza pura a taglio (Mohr-Coulomb: v₀)
- **α** = parametro di accoppiamento (0.3–0.5)
- **σ_lim** = resistenza a compressione uniassiale [kg/cm²]

**Forma estesa (EN 1996-1-1 Cap. 6.3)**:

$$\frac{f_v}{f_{v0} + 0.4 \cdot \sigma_d} \leq 1 \quad \text{(criterio di scorrimento)}$$

$$\frac{\sigma_1}{f_d} + \frac{\tau_{xy}}{f_v} \leq 1 \quad \text{(criterio di rottura combinata)}$$

---

## 3. Parametri del Modello {#parametri-modello}

### 3.1 Parametri di materiale

| Simbolo | Descrizione | Tipica | Fonte |
|---------|-------------|--------|-------|
| **v₀** | Resistenza taglio senza pressione [kg/cm²] | 0.15–0.35 | EN 1996-1-1 Tab. 3.4; DM 20/11/1987 |
| **μ** | Coefficiente attrito interstizi malta | 0.40–0.65 | EN 1996-1-1; Circ. 7/2019 |
| **f_d** | Resistenza compressione [kg/cm²] | 10–50 | NTC2018 §4.5; Tabella 4.5.IV |
| **E_m** | Modulo elastico muratura [kg/cm²] | 500–2000 | NTC2018 Tabella 4.5.III |
| **G_m** | Modulo taglio [kg/cm²] | E_m/(2.6–3.0) | NTC2018 §4.5.7 |

### 3.2 Parametri geometrici del macro-elemento

| Simbolo | Descrizione | Unità |
|---------|-------------|-------|
| **t** | Spessore parete | cm |
| **h** | Altezza lorda del piano | cm |
| **L** | Lunghezza del maschio/fascia | cm |
| **A = L × t** | Area parete nel piano | cm² |
| **I = L × t³ / 12** | Inerzia della sezione (approssimazione rettangolare) | cm⁴ |
| **h₀** | Altezza netta (distanza di taglio) | cm |
| **ψ = h₀ / L** | Rapporto di taglio | — |

### 3.3 Stato iniziale (pre-compressione)

**σ₀ = N₀ / A** — Tensione media verticale iniziale [kg/cm²]

dove N₀ è il **carico permanente** (peso proprio + sovraccarichi) calcolato dall'analisi globale.

**Range tipico** per edifici esistenti in muratura:
- Piani inferiori: σ₀ = 1.5–3.0 kg/cm²
- Piani superiori: σ₀ = 0.5–1.0 kg/cm²

---

## 4. Criterio di Rottura e Legame Costitutivo {#criterio-rottura}

### 4.1 Superfici di rottura per muratura (NTC2018 §7.8.2.2)

#### A. Rottura per **fessurazione diagonale** (Turnšek-Čačovič)

Applicabile quando **σ₀ è moderata** (0.5–2.0 kg/cm²).

$$V_{\text{diag}} = L \cdot t \cdot \frac{1.5 \, v_0 / b}{\sqrt{1 + \sigma_0 / (1.5 \, v_0)}}$$

Riscritta con il **taglio medio**:

$$\tau_{\text{diag}} = 1.5 v_0 \sqrt{\frac{\sigma_0}{1.5 v_0 + \sigma_0}} \cdot b^{-1}$$

dove **b = 1.0÷1.5** è il fattore di distribuzione tensioni (dipende da h/L).

#### B. Rottura per **scorrimento** (attrito Mohr-Coulomb)

Applicabile quando **σ₀ è elevata** (σ₀ > 1.0 kg/cm²).

$$V_{\text{scor}} = L \cdot t \cdot (v_0 + \mu \cdot \sigma_0)$$

o in termini di tensione media:

$$\tau_{\text{scor}} = v_0 + \mu \cdot \sigma_0$$

#### C. Rottura per **pressoflessione**

Quando il **momento è dominante** (h/L < 1.0, pareti snelle):

$$V_{\text{press}} = \frac{2 \cdot f_d \cdot L \cdot t}{h_0} \cdot \left(1 - \frac{M}{f_d \cdot L \cdot t \cdot (t/2)}\right)$$

### 4.2 Superficie di rottura combinata (envelope)

La resistenza a taglio effettiva è il **minimo** tra i tre criteri:

$$V_{Rd} = \min(V_{\text{diag}}, V_{\text{scor}}, V_{\text{press}})$$

**Fattore di sicurezza (NTC2018)**:

$$\gamma_{M} = 3.0 \quad \text{(edifici esistenti, conoscenza LC1)}$$

$$\gamma_{M} = 2.4 \quad \text{(conoscenza LC2)}$$

$$\gamma_{M} = 1.8 \quad \text{(conoscenza LC3)}$$

quindi la **resistenza di calcolo**:

$$\tau_d = \frac{\tau_{Rd}}{\gamma_M}$$

### 4.3 Legame costitutivo con degradazione

Per edifici **non lineari** (pushover LV3):

1. **Fase elastica** (δ < δ_y):
   - Rigidezza iniziale: $k_e = E_m \cdot A / h_0$
   - Tensioni crescono linearmente

2. **Fase plastica** (δ_y ≤ δ < δ_u):
   - Forza rimane plateau a V_Rd (perfettamente plastico semplificato)
   - Oppure degradazione lineare (modello più realistico)

3. **Collasso** (δ ≥ δ_u):
   - Capacità residua: V_res = 0 (fragile) oppure V_res = 0.2 V_Rd (degradazione)

**Spostamento ultimo** (drift di collasso):

$$\delta_u = 0.4 \, \% \text{ (fragile, fessurazione diagonale)} \quad \text{oppure}$$

$$\delta_u = 1.0 \, \% \text{ (duttile, scorrimento con confinamento)}$$

---

## 5. Algoritmo SVD Iterativo {#algoritmo-svd}

### 5.1 Problema da risolvere

Durante un **incremento di carico** (pushover):

- Applichiamo uno **spostamento laterale** Δδ
- Calcoliamo la **forza laterale** V corrente
- Questo genera una **nuova distribuzione di stress** σ_x, σ_y, τ_xy nel macro-elemento
- Gli **assi principali ruotano** di angolo θ
- La **resistenza a taglio cambia** in funzione della nuova compressione principale σ₁

### 5.2 Passo iterativo (Newton-Raphson semplificato)

**Dato**: stato di strain {ε_x, ε_y, γ_xy}, parametri materiale {E_m, G_m, v₀, μ, f_d}

**Iterazione k**:

1. **Calcolo stress elastico** (legame costitutivo lineare):
   $$\sigma_x^k = E_m \cdot \varepsilon_x$$
   $$\sigma_y^k = E_m \cdot \varepsilon_y$$
   $$\tau_{xy}^k = G_m \cdot \gamma_{xy}$$

2. **Diagonalizzazione** (SVD/eigenvalue):
   $$\sigma_1^k, \sigma_2^k = \text{eigenval}\left(\begin{pmatrix} \sigma_x^k & \tau_{xy}^k \\ \tau_{xy}^k & \sigma_y^k \end{pmatrix}\right)$$
   $$\theta^k = \frac{1}{2} \arctan\left(\frac{2\tau_{xy}^k}{\sigma_x^k - \sigma_y^k}\right)$$

3. **Calcolo resistenza** (Mohr-Coulomb aggiornato):
   $$\tau_{\text{max}}^k = v_0 + \mu \cdot \sigma_1^k$$

4. **Controllo plasticità** (criterio di snervamento):
   $$f = \frac{|\tau_{xy}^k|}{\tau_{\text{max}}^k} - 1 \quad \text{(senza scorrimento se } f < 0\text{)}$$

5. **Se snervamento** (f > 0): **correzione anelastica**
   - Ridurre σ_x, σ_y mediante **algoritmo return-mapping** (proiezione sul dominio elastico)
   - Oppure: aumentare la deformazione plastica γ_p e ricalcolare

6. **Convergenza**: ripetere fino a ||σⁱ⁺¹ - σⁱ|| < tol (es. tol = 10⁻³)

### 5.3 Pseudo-codice completo

```python
def calcolo_macro_elemento_lv3(delta, N0, v0, mu, fd, Em, Gm, L, t, h):
    """
    Calcolo iterativo macro-elemento muratura LV3 con SVD.

    Args:
        delta: spostamento laterale applicato [cm]
        N0: carico verticale iniziale [kg]
        v0, mu: parametri Mohr-Coulomb
        fd: resistenza compressione [kg/cm²]
        Em, Gm: moduli elastici
        L, t, h: geometria

    Returns:
        dict con: V, sigma_1, sigma_2, theta, tau_max, criterio_dominante, passaggi
    """

    A = L * t
    sigma_0 = N0 / A  # pre-compressione

    # Strain medio da spostamento (approssimazione)
    gamma_xy = delta / h  # taglio medio

    tolerance = 1e-3
    max_iter = 20
    iter_count = 0

    # Inizializzazione
    tau_xy = Gm * gamma_xy
    sigma_x = 0.0  # orizzontale, inizialmente nulla
    sigma_y = sigma_0  # verticale, dalla pre-compressione

    passaggi = []

    while iter_count < max_iter:
        iter_count += 1

        # 1. Salva stato precedente
        tau_xy_old = tau_xy
        sigma_x_old = sigma_x

        # 2. Diagonalizzazione (SVD semplice)
        sigma_1, sigma_2 = eigenvalue_2x2(sigma_x, sigma_y, tau_xy)
        theta = 0.5 * atan2(2*tau_xy, sigma_x - sigma_y)

        # 3. Resistenza Mohr-Coulomb (su sigma_1, stress normale principale)
        tau_max = v0 + mu * max(sigma_1, 0)  # solo se compressione

        # 4. Criterio di snervamento
        f = abs(tau_xy) / tau_max - 1.0

        passaggi.append(f"Iter {iter_count}: σ₁={sigma_1:.3f}, σ₂={sigma_2:.3f}, "
                       f"τ={abs(tau_xy):.3f}, τ_max={tau_max:.3f}, f={f:.4f}")

        if f <= tolerance:
            # Converso
            break

        if f > 0:
            # Snervamento: ridurre il taglio al dominio elastico
            tau_xy = tau_max * (1 - 0.1 * f)  # riduzione graduale

        # 5. Controllo convergenza
        if abs(tau_xy - tau_xy_old) < tolerance * tau_max:
            break

    # Risultato finale
    V = abs(tau_xy) * A  # Taglio totale
    criterio = "diagonale" if abs(tau_xy) > 0.5 * tau_max else "scorrimento"

    return {
        "V": V,
        "sigma_1": sigma_1,
        "sigma_2": sigma_2,
        "theta_deg": degrees(theta),
        "tau_max": tau_max,
        "tau_effettivo": abs(tau_xy),
        "sfruttamento": abs(tau_xy) / tau_max if tau_max > 0 else inf,
        "criterio": criterio,
        "convergenza": iter_count < max_iter,
        "iterazioni": iter_count,
        "passaggi": passaggi
    }
```

---

## 6. Esempio Numerico Step-by-Step {#esempio-numerico}

### 6.1 Dati del problema

**Maschio murario** (pianterreno edificio in muratura storica):

| Parametro | Valore | Unità |
|-----------|--------|-------|
| **Lunghezza** L | 300 | cm |
| **Spessore** t | 50 | cm |
| **Altezza** h | 350 | cm |
| **Carico verticale (N₀)** | 1500 | kg |

**Materiale** (muratura storica malta debolina):

| Parametro | Valore | Unità |
|-----------|--------|-------|
| **v₀** | 0.25 | kg/cm² |
| **μ** | 0.50 | — |
| **f_d** | 20 | kg/cm² |
| **E_m** | 1000 | kg/cm² |
| **G_m** | 400 | kg/cm² |

**Azione sismica (pushover)**: spostamento laterale incrementale δ = 0, 1, 2, 3 cm

### 6.2 Passo 1: Pre-compressione iniziale

$$A = L \times t = 300 \times 50 = 15000 \text{ cm}^2$$

$$\sigma_0 = \frac{N_0}{A} = \frac{1500}{15000} = 0.10 \text{ kg/cm}^2$$

**Interpretazione**: Compressione molto bassa (edificio spingente, muratura poco caricata). Questo suggerisce prevalenza del criterio **diagonale** (bassa compressione).

### 6.3 Passo 2: δ = 1 cm (primo spostamento)

**Strain di taglio**:
$$\gamma_{xy} = \frac{\delta}{h} = \frac{1}{350} = 0.00286 \text{ rad}$$

**Tensione di taglio elastica**:
$$\tau_{xy} = G_m \times \gamma_{xy} = 400 \times 0.00286 = 1.14 \text{ kg/cm}^2$$

**Tensioni principali** (σₓ ≈ 0, σᵧ = σ₀ = 0.10 kg/cm²):

$$\sigma_1 = \frac{0 + 0.10}{2} + \sqrt{\left(\frac{0-0.10}{2}\right)^2 + 1.14^2} = 0.05 + \sqrt{0.0025 + 1.30} = 0.05 + 1.14 = 1.19 \text{ kg/cm}^2$$

$$\sigma_2 = 0.05 - 1.14 = -1.09 \text{ kg/cm}^2 \quad \text{(trazione)}$$

**Angolo di rotazione**:
$$\theta = \frac{1}{2} \arctan\left(\frac{2 \times 1.14}{0 - 0.10}\right) = \frac{1}{2} \arctan(-22.8) \approx -87° $$

Asse principale quasi verticale (fessura diagonale a ~45°).

**Resistenza Mohr-Coulomb**:
$$\tau_{\text{max}} = v_0 + \mu \cdot \sigma_1 = 0.25 + 0.50 \times 1.19 = 0.25 + 0.595 = 0.845 \text{ kg/cm}^2$$

**Criterio di snervamento**:
$$f = \frac{1.14}{0.845} - 1 = 1.349 - 1 = 0.349 > 0 \quad \Rightarrow \text{SNERVAMENTO}$$

La tensione calcolata supera la resistenza del 35%.

### 6.4 Passo 3: Iterazione di correzione (return-mapping)

Riduciamo il taglio al dominio elastico:

$$\tau_{xy}^{\text{corr}} = \tau_{\text{max}} = 0.845 \text{ kg/cm}^2$$

**Verifica**:
$$f = \frac{0.845}{0.845} - 1 = 0 \quad \Rightarrow \text{OK}$$

**Forza laterale risultante**:
$$V = \tau_{xy} \times A = 0.845 \times 15000 = 12675 \text{ kg}$$

### 6.5 Passo 4: δ = 2 cm (secondo spostamento incrementale)

Ripetendo il calcolo con δ = 2 cm:

$$\gamma_{xy} = \frac{2}{350} = 0.00571 \text{ rad}$$
$$\tau_{xy}^{\text{elastica}} = 400 \times 0.00571 = 2.286 \text{ kg/cm}^2$$

Tensioni principali (σₓ ancora ≈ 0):
$$\sigma_1 \approx 2.29 \text{ kg/cm}^2, \quad \sigma_2 \approx -2.19 \text{ kg/cm}^2$$

$$\tau_{\text{max}} = 0.25 + 0.50 \times 2.29 = 1.395 \text{ kg/cm}^2$$

$$f = \frac{2.286}{1.395} - 1 = 0.638 > 0 \quad \Rightarrow \text{SNERVAMENTO}$$

**Correzione**:
$$\tau_{xy}^{\text{corr}} = 1.395 \text{ kg/cm}^2$$

$$V = 1.395 \times 15000 = 20925 \text{ kg}$$

### 6.6 Riassunto: Curva di capacità (pushover)

| δ [cm] | τ_xy [kg/cm²] | σ₁ [kg/cm²] | τ_max [kg/cm²] | V [kg] | Stato |
|--------|---------------|------------|-----------------|--------|-------|
| 0      | 0.00          | 0.10       | 0.30            | 0      | Elastico |
| 1.0    | 0.84          | 1.19       | 0.85            | 12675  | Snervato |
| 2.0    | 1.40          | 2.29       | 1.40            | 20925  | Snervato |
| 3.0    | 1.40*         | 2.29*      | 1.40*           | 20925* | Plateau |

*Plateau plastico: ulteriori incrementi di spostamento non aumentano la forza (limite di resistenza raggiunto).

### 6.7 Interpretazione fisica

1. **Precompressione bassa** → fessurazione diagonale **molto presto** (δ < 0.5 cm)
2. **Rapido snervamento** → curva bilineare con rigidezza elastica k ≈ 12675 kg / 0.5 cm ≈ 25000 kg/cm, poi plateau
3. **Resistenza dominante** = Mohr-Coulomb (attrito su fessura diagonale a σ₁ moderata)
4. **Assenza di pressoflessione** → h/L = 350/300 ≈ 1.17 > 1.0, quindi maschio non snello

---

## 7. Riferimenti Normativi {#riferimenti}

### 7.1 Normative italiane

| Norma | Articolo/Capitolo | Tema |
|-------|-------------------|------|
| **NTC2018** | §4.5 (muratura nuova); §7.8 (sismica muratura) | Parametri meccanici, verifiche a compressione e taglio |
| **NTC2018** | §7.8.2.2 (edifici esistenti) | Resistenza pannelli murari: diagonale, scorrimento, pressoflessione |
| **Circ. 7/2019** | §C4.5 (muratura); §C8.7.1.3.1.1 | Commenti: parametri LC1/LC2/LC3, coefficienti Φ snellezza, γ_M |
| **DM 20/11/1987** | Capp. 3–5 | Muratura ordinaria: prove, parametri, verifiche (storico) |
| **Circ. 30/07/1981** | n. 21745 | Muratura esistente: limitazioni e criteri (storico) |

### 7.2 Eurocodici

| Norma | Capitolo | Tema |
|-------|----------|------|
| **EN 1996-1-1:2005** | Cap. 3 (materiali); Cap. 6 (calcolo) | Proprietà muratura, resistenza caratteristica f_k, criterio di progetto |
| **EN 1996-1-1** | Tab. 3.4 (f_vk0), 3.6 (moduli) | Resistenza taglio base v₀, moduli elastici per diversi tipi |
| **EN 1998-1:2005 (EC8)** | §5.5 (edifici muratura) | Analisi sismica, q, duttilità, legame shear-compression |

### 7.3 Standard internazionali (benchmark)

| Standard | Applicazione | Tema |
|----------|--------------|------|
| **ASCE 41-06** (USA) | Seismic Rehabilitation of Buildings | Cap. 6–7: modelli non lineari, curve isteretiche, macro-elementi muratura |
| **FEMA 356** | Pre-Standard / Commentary for Seismic Rehabilitation | Tab. 5-6 (modelli di rottura), curva capacità, duttilità |
| **ACI 318** (calcestruzzo USA) | Seismic Design Code | Riferimento per confinamento, duttilità (applicabile a muratura in blocchi CLS) |

### 7.4 Letteratura di ricerca (riferimenti teorici)

1. **Turnšek, V., Čačovič, F.** (1970). "Some experimental results on the strength of brick masonry walls." *Proceedings of the 2nd International Brick Masonry Conference*, Stoke-on-Trent, UK.
   - **Tema**: Criterio diagonale originale; test su pannelli murari isolati.

2. **Magenes, G., Della Fontana, A.** (1998). "Cyclic behaviour of brick masonry under general in-plane loading." *Earthquake Engineering & Structural Dynamics*.
   - **Tema**: Isteresi, degradazione, modelli incrudimento.

3. **Anthoine, A.** (1997). "Homogenisation of periodic masonry: plane stress, generalized plane strain or 3D?" *International Journal of Solids and Structures*.
   - **Tema**: Omogeneizzazione muratura (micro-meso scale), modello continuo equivalente.

4. **EN 1996-1-1:2005 Eurocode 6** — Dettagli normativi, TAB. 3.6 (moduli), Cap. 6.3–6.4 (criteri di rottura).

5. **Circolare n. 7 del 21 gennaio 2019** — Istruzioni per l'applicazione NTC2018: chiarimenti su σ₀, Φ(λ,e/t), γ_M per LC1/LC2/LC3.

---

## 7bis. Approfondimento: Rotazione degli Assi Principali durante Carico Laterale {#rotazione-assi}

### 7bis.1 Fenomeno fisico: cosa succede durante il pushover

In un macro-elemento murario sottoposto a **spinta orizzontale progressiva**:

1. **Stato iniziale** (δ = 0):
   - Stress tensor: σₓ ≈ 0, σᵧ = σ₀ (compressione verticale da peso)
   - Assi principali: verticale (σ₁ = σ₀) e orizzontale (σ₂ = 0)
   - θ = 0° (assi allineati a x-y)

2. **Primo incremento di carico** (δ > 0 piccolo):
   - Spinta laterale → τₓᵧ cresce
   - σₓ rimane modesto (muratura povera di rigidezza orizzontale)
   - Angolo θ aumenta: assi principali **ruotano** di ~45°
   - La **compressione principale σ₁** cambia direzione (da verticale a diagonale)

3. **Effetto sulla resistenza**:
   - La **fessura diagonale** (che segue σ₁) ruota anch'essa
   - La resistenza a taglio Mohr-Coulomb (τ = v₀ + μ·σₙ) dipende ora da σ₁ secondo la **nuova orientazione**
   - Se σ₁ passa da compressione a **trazione** (σ₂ < 0), la resistenza **crolla**

### 7bis.2 Formalismo matematico della rotazione SVD

Data la **matrice di stress** 2D:

$$\boldsymbol{\sigma} = \begin{pmatrix} \sigma_x & \tau_{xy} \\ \tau_{xy} & \sigma_y \end{pmatrix}$$

La **decomposizione ai valori singolari (SVD)** o **diagonalizzazione** produce:

$$\boldsymbol{\sigma} = \mathbf{R}(\theta)^T \cdot \boldsymbol{\sigma}_{\text{principal}} \cdot \mathbf{R}(\theta)$$

dove:

$$\mathbf{R}(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$$

e la **matrice principale**:

$$\boldsymbol{\sigma}_{\text{principal}} = \begin{pmatrix} \sigma_1 & 0 \\ 0 & \sigma_2 \end{pmatrix}$$

**Inversione**: dato σ, calcoriamo λ₁, λ₂ e θ come:

$$\text{det}(\boldsymbol{\sigma} - \lambda \mathbf{I}) = 0 \quad \Rightarrow \quad \lambda_{1,2} = \frac{\sigma_x + \sigma_y}{2} \pm \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}$$

$$\theta = \frac{1}{2} \arctan\left(\frac{2\tau_{xy}}{\sigma_x - \sigma_y}\right) \quad \text{(con attenzione ai quadranti)}$$

### 7bis.3 Conseguenze per la verifica a taglio: il criterio **stress-plane** vs **principal-plane**

Nella norma NTC2018 §7.8.2.2, la resistenza a **scorrimento** è:

$$\tau_v = v_0 + \mu \cdot \sigma_0$$

dove σ₀ è la **compressione media verticale** prima dell'azione sismica.

**Tuttavia**, durante il pushover, σ₀ cambia per due motivi:

1. **Compressione verticale residua**: σᵧ diminuisce se c'è uplift
2. **Compressione principale σ₁**: ruota da verticale a diagonale, cambiando la componente normale sulla fessura diagonale

**Formula corretta (EN 1996-1-1, ASCE 41-06)**:

$$\tau_{\text{max}} = v_0 + \mu \cdot \sigma_n^{*}$$

dove σₙ* è la **compressione effettiva sulla fessura diagonale**, ossia:

$$\sigma_n^{*} = \max(\sigma_1, 0) \quad \text{oppure} \quad \sigma_n^{*} = \frac{\sigma_1 + \sigma_2}{2} \quad \text{(media principale)}$$

Se σ₁ < 0 (trazione), allora σₙ* = 0 e τ_max = v₀ **senza beneficio di attrito**.

### 7bis.4 Algoritmo iterativo per tracking della rotazione

```python
def calcolo_con_rotazione_assi(delta_incrementale, stato_precedente):
    """
    Aggiornamento iterativo con rotazione degli assi durante pushover.
    """
    # Stato precedente
    sigma_x_prec, sigma_y_prec, tau_xy_prec = stato_precedente
    theta_prec = atan2(2*tau_xy_prec, sigma_x_prec - sigma_y_prec) / 2

    # Aggiornamento strain
    gamma_xy_new = delta_incrementale / h
    tau_xy_new = G * gamma_xy_new  # elastico

    # Iterazione: convergenza di sigma_x (orizzontale)
    sigma_x_new = 0.0  # start
    for iter in range(10):
        # Diagonalizzazione
        sigma_1, sigma_2 = eigenvalues(sigma_x_new, sigma_y_prec, tau_xy_new)
        theta_new = atan2(2*tau_xy_new, sigma_x_new - sigma_y_prec) / 2

        # Resistenza sulla fessura diagonale (orientata a σ₁)
        sigma_n_diag = sigma_1 * cos(theta_new)**2 + sigma_2 * sin(theta_new)**2
        tau_max = v0 + mu * max(sigma_n_diag, 0)

        # Controllo snervamento
        if abs(tau_xy_new) > tau_max:
            # Ridurre il taglio
            tau_xy_new = tau_max * (1 - 0.05 * (abs(tau_xy_new)/tau_max - 1))
        else:
            break  # Convergenza

    return sigma_x_new, sigma_y_prec, tau_xy_new, theta_new
```

---

## 8. Note Implementative e TODO

### 8.1 Modellazione numerica

- [ ] Implementare SVD iterativo con **Newton-Raphson** o **return-mapping** (§5.3)
- [ ] Aggiungere **controllo di plasticità** con criterio Mohr-Coulomb adattato
- [ ] Gestire la **rotazione degli assi principali** θ(δ) durante il carico
- [ ] Implementare **degradazione di rigidezza** in fase plastica (modello non-lineare incrudimento)

### 8.2 Validazione

- [ ] Test contro **ASCE 41-06** Tabella 6-28 (maschio murario, curve capacità)
- [ ] Benchmark con **software SAP2000** / **3Muri** (macro-elementi muratura)
- [ ] Validazione su casi di **prova sperimentale** (Turnšek-Čačovič, EUCENTRE)

### 8.3 Estensioni future

- [ ] Modello **tridimensionale** (stress fuori-piano)
- [ ] **Danno cumulativo** (low-cycle fatigue per carico ciclico)
- [ ] **Confinamento da cordolo** (variazione v₀ con armatura)
- [ ] **Accoppiamento con SLE** (stato limite d'esercizio, fessurazione limitata)

---

## 9. Appendice: Formule Sintetiche

### A. Riepilogo equazioni

**Mohr-Coulomb**:
$$\tau = v_0 + \mu \cdot \sigma_n$$

**Turnšek-Čačovič (fessurazione diagonale)**:
$$V_t = L \, t \cdot 1.5 \frac{v_0}{b} \sqrt{1 + \frac{\sigma_0}{1.5 v_0}}$$

**Scorrimento (attrito)**:
$$V_s = L \, t \cdot (v_0 + \mu \sigma_0)$$

**Pressoflessione**:
$$V_p = \frac{2 f_d \, L \, t}{h_0} \left(1 - \frac{M}{f_d \, L \, t \, (t/2)}\right)$$

**Tensioni principali da tensore 2D**:
$$\sigma_{1,2} = \frac{\sigma_x + \sigma_y}{2} \pm \sqrt{\left(\frac{\sigma_x - \sigma_y}{2}\right)^2 + \tau_{xy}^2}$$

**Angolo di rotazione assi principali**:
$$\theta = \frac{1}{2} \arctan\left(\frac{2\tau_{xy}}{\sigma_x - \sigma_y}\right)$$

### B. Simbologia

| Simbolo | Significato |
|---------|------------|
| σₘ, σ₀ | Tensione media verticale (compressione positiva) |
| τₘ, τ_xy | Tensione media di taglio nel piano |
| σ₁, σ₂ | Tensioni principali (σ₁ ≥ σ₂) |
| v₀ | Resistenza a taglio senza compressione (coesione) |
| μ | Coefficiente d'attrito Mohr-Coulomb |
| f_d | Resistenza a compressione |
| V_Rd | Resistenza a taglio di progetto |
| δ | Spostamento laterale |
| γ_xy | Deformazione di taglio medio |
| θ | Angolo di rotazione assi principali |
| ψ = h₀/L | Rapporto di taglio |
| γ_M | Coefficiente parziale di sicurezza materiale |

---

## 10. Tabella Comparativa: Modelli di Macro-Elemento Muratura

### 10.1 Confronto tra approcci (NTC2018 vs EN1996 vs ASCE 41)

| Aspetto | **NTC2018 §7.8** | **EN 1996-1-1** | **ASCE 41-06** |
|---------|------------------|-----------------|-----------------|
| **Scala** | Elemento finito (continuo) + macro | Verifica sezione (elastico lineare) | Macro-elemento non-lineare |
| **Accoppiamento σ-τ** | Turnšek-Čačovič + Mohr-Coulomb | Mohr-Coulomb puro | Drucker-Prager generalizzato |
| **Rotazione assi** | Non esplicito | Assume fessura a ~45° | Tracking iterativo (SVD) |
| **Degradazione rigidezza** | Bilineare semplice | No | Incrudimento/degradazione |
| **Input materiale primario** | v₀ tabellato per tipo | f_vk da prova; f_m | f_v, E_m, ν, fattore degradazione |
| **Coefficiente sicurezza** | γ_M = 1.8÷3.0 | γ_M = 2.5 (muratura nuova) | Implicito in curve ASCE |
| **Applicazione** | Edifici nuovi e esistenti | Progetto muratura nuova | Valutazione retrofit (capacity-demand) |

### 10.2 Dettagli critici per implementazione LV3 in RD2229

#### A. Scelta del criterio di rottura (decisione di design)

**Opzione 1 — Turnšek-Čačovič + Scorrimento** (⭐ **CONSIGLIATO per NTC2018**)
- Vantaggi: allineato a NTC2018 §7.8.2.2.1–.2; storicamente validato su muratura italiana
- Svantaggi: non cattura degradazione fine durante carico ciclico
- Implementazione: diretto da §5.2–5.3 (formule semplici)

**Opzione 2 — Drucker-Prager esteso** (per ricchezza di dettaglio)
- Vantaggi: superficie plastica continua, transizioni smooth tra criteri
- Svantaggi: 2–3 parametri aggiuntivi (α, β); fitting su dati sperimentali
- Implementazione: più complessa (return-mapping con projections)

**Decisione raccomandata per Fase U**: **Opzione 1 + transizione morbida** verso Opzione 2 (flag selezionabile in config).

#### B. Parametri di input per muratura storica italiana

Dalla **Circolare 7/2019 §C8.7.1.3.1.1** e **NTC2018 Tabella 4.5.IV**, i valori tipici sono:

| Tipo Muratura | v₀ [kg/cm²] | μ | f_d [kg/cm²] | E [kg/cm²] | Riferimento |
|---|---|---|---|---|---|
| Mattoni pieni, malta normale | 0.25–0.35 | 0.50–0.65 | 15–25 | 800–1200 | DM87, Circ81 |
| Pietra squadrata, malta buona | 0.35–0.50 | 0.55–0.70 | 20–35 | 1200–1800 | Storica |
| Tufo/blocchi laterizio | 0.15–0.25 | 0.40–0.55 | 10–15 | 600–900 | Debole |
| Blocchi CLS, malta cementizia | 0.30–0.45 | 0.60–0.75 | 25–40 | 1500–2500 | Moderna |

**Livello di conoscenza (LC)**:
- **LC1** (limitata): usare minimi della tabella + γ_M = 3.0
- **LC2** (media): medi della tabella + γ_M = 2.4
- **LC3** (completa): dati da prove + γ_M = 1.8

#### C. Modellazione della curva di capacità (bilineare vs tri-lineare)

**Modello Bilineare** (semplice, attuale in RD2229):
- k_e = rigidezza elastica fino a V_Rd
- Plateau plastico perfetto (V = V_Rd costante)
- Collasso fragile a δ_u

```
  V
  |      ___________
  |     /|
  |    / | k_e
  |   /  |
  |  /   |_____ δ_u (collasso)
  | /
  |_______________  δ
```

**Modello Tri-Lineare** (realistico, con degradazione):
- Fase elastica (k_e)
- Fase plastica incrudimento (k_s < k_e)
- Fase post-picco degradazione (k_d < 0)

```
  V
  |      _______
  |     /|     /\
  |    / | k_e/  \ k_d
  |   /  |    / k_s\
  |  /   |   /_____  \___
  | /    |        δ_y δ_u  δ
  |_______________
```

**Per Fase U (LV3)**: implementare **tri-lineare con degradazione**, con opzione user di "semplificare a bilineare" se necessario.

#### D. Interazione con il modulo NTC2018 (probabilistic demand-capacity)

La **Fase U** si interfaccia con **Fase O** (spettro sismico NTC2018):

```
Fase O → Spettro Sa(T) per 84° percentile
    ↓
Fase U.5 → Analisi modale, calcolo T₁, T₂, ...
    ↓
Fase R.4 (LV3) → Demand: F_sism = m · Sa(T₁) / q
    ↓
Fase U.6 → Pushover: calcolo curva capacità V(δ)
    ↓
Confronto: max |δ_demand| vs δ_u (capacità ultima)
    ↓
Vulnerabilità: V = (δ_demand / δ_u)^(α) con α=1.0÷2.0
```

### 10.3 Confronto numerico: Caso test ASCE 41

**ASCE 41-06 Table 6-28** fornisce **curve di capacità tipiche** per maschi murari.

Esempio: Pannello muratura storica (mattoni pieni, malta debolina)
- L = 300 cm, t = 50 cm, h = 360 cm, σ₀ = 0.5 kg/cm²

**ASCE 41 predice**:
| Drift [%] | Force [kN] | Note |
|---|---|---|
| 0.10 | 45 | Limite fessurazione (SLE) |
| 0.50 | 65 | Inizio plasticità |
| 1.50 | 68 | Picco (pushover) |
| 3.00 | 40 | Post-picco (degradazione) |

**Previsione con modello NTC2018** (Turnšek + Mohr-Coulomb):
- Dovrebbe dare **picco simile** (65–75 kN) con **drift leggermente minore** (0.8–1.2%)
- Degradazione post-picco **meno marcata** (modello bilineare tende a conservare V = V_Rd)

**Validazione**: implementare test case ASCE per benchmark.

---

## 11. Connessione al Codice RD2229

### 11.1 Struttura moduli proposti

```
src/methods/muratura/
├── ...
├── macro_elemento_lv3.py          # NUOVO: classe MacroElementoLV3, calc SVD
├── verifica_lv3.py                # NUOVO: verifiche LV3 (capacità, domanda, vulnerabilità)
├── curve_capacita.py              # NUOVO: pushover, curve bilineare/tri-lineare
└── ...

tests/
├── ...
├── test_macro_elemento_lv3.py     # Test SVD, rotazione assi, convergenza
├── test_curve_capacita.py         # Test curve pushover vs benchmark ASCE
└── ...
```

### 11.2 Pseudo-interfaccia Python (scheletro)

```python
# src/methods/muratura/macro_elemento_lv3.py

from dataclasses import dataclass
from enum import Enum

class CriterioRottura(str, Enum):
    TURNSEKALACOVIC = "turnsekalacovic"
    MOHR_COULOMB = "mohr_coulomb"
    DRUCKER_PRAGER = "drucker_prager"

@dataclass
class ParamMuratura:
    """Parametri meccanici muratura LV3."""
    v0: float          # Resistenza taglio senza pressione [kg/cm²]
    mu: float          # Coefficiente attrito
    fd: float          # Resistenza compressione [kg/cm²]
    Em: float          # Modulo elastico [kg/cm²]
    Gm: float          # Modulo taglio [kg/cm²]
    gamma_M: float = 2.4  # Coefficiente sicurezza (LC2)
    livello_conoscenza: str = "LC2"  # LC1, LC2, LC3

@dataclass
class GeometriaMacroElemento:
    """Geometria macro-elemento."""
    L: float   # Lunghezza [cm]
    t: float   # Spessore [cm]
    h: float   # Altezza [cm]

class MacroElementoLV3:
    """Macro-elemento muratura con SVD iterativo."""

    def __init__(self, id_elem: int, geom: GeometriaMacroElemento,
                 param: ParamMuratura, N0: float):
        self.id = id_elem
        self.geom = geom
        self.param = param
        self.N0 = N0  # Carico verticale iniziale

        self.sigma_0 = N0 / (geom.L * geom.t)  # Pre-compressione

    def calcolo_step_pushover(self, delta: float) -> dict:
        """
        Calcolo iterativo per spostamento laterale δ.

        Returns:
            {
                'V': float,           # Forza laterale [kg]
                'sigma_1': float,     # Tensione principale max
                'sigma_2': float,     # Tensione principale min
                'theta_deg': float,   # Angolo assi principali [°]
                'tau_max': float,     # Resistenza a taglio [kg/cm²]
                'sfruttamento': float,  # tau / tau_max
                'criterio': str,      # "diagonale" / "scorrimento" / "pressoflessione"
                'convergenza': bool,
                'iterazioni': int,
                'passaggi': list[str]
            }
        """
        ...

    def pushover_completo(self, delta_max: float, num_step: int) -> dict:
        """
        Pushover incrementale: curva di capacità.

        Returns:
            {
                'delta': [float],     # Spostamenti [cm]
                'V': [float],         # Forze [kg]
                'delta_y': float,     # Spostamento snervamento
                'delta_u': float,     # Spostamento collasso
                'V_Rd': float,        # Resistenza di picco
                'k_elastica': float,  # Rigidezza elastica
                'criterio_dominante': str,
                'curve': [...]        # Dati per grafico
            }
        ```

# src/methods/muratura/verifica_lv3.py

def verifica_lv3_edificio(edificio, spettro, q_user=None) -> dict:
    """
    Verifica sismica completa LV3 per edificio muratura.

    Flusso:
    1. Analisi modale (Fase U.5) → T₁, φ₁
    2. Domanda: Sa(T₁) da spettro, F_demand = m·Sa / q
    3. Per ogni maschio:
       a. Calcolo curva di capacità (pushover)
       b. Conversione in ADRS (acceleration-displacement)
       c. Intersezione con domanda (capacity-demand)
    4. Calcolo vulnerabilità V = (δ_dem / δ_u)^α

    Returns:
        {
            'T1': float,
            'q_usato': float,
            'Sa_T1': float,
            'F_demand': float,
            'maschi': [
                {
                    'id': int,
                    'delta_demand': float,
                    'delta_u': float,
                    'vulnerabilita': float,
                    'stato': 'SICURO' | 'CRITICO' | 'COLLASSO'
                }
            ],
            'stato_globale': str,
            'report_html': str
        }
```

### 11.3 Unit test proposti

```python
# tests/test_macro_elemento_lv3.py

import pytest
from src.methods.muratura.macro_elemento_lv3 import (
    MacroElementoLV3, ParamMuratura, GeometriaMacroElemento
)

def test_pre_compressione():
    """Test calcolo σ₀ iniziale."""
    geom = GeometriaMacroElemento(L=300, t=50, h=350)
    param = ParamMuratura(v0=0.25, mu=0.50, fd=20, Em=1000, Gm=400)
    elem = MacroElementoLV3(1, geom, param, N0=1500)

    assert elem.sigma_0 == pytest.approx(0.10, rel=1e-2)

def test_tensioni_principali():
    """Test diagonalizzazione SVD."""
    sigma_x, sigma_y, tau_xy = 0.0, 0.10, 1.14

    # Calcolo manual
    sigma_1_expected = 1.19
    sigma_2_expected = -1.09

    sigma_1, sigma_2 = calcolo_tensioni_principali(sigma_x, sigma_y, tau_xy)
    assert sigma_1 == pytest.approx(sigma_1_expected, rel=1e-2)
    assert sigma_2 == pytest.approx(sigma_2_expected, rel=1e-2)

def test_pushover_curva_capacita():
    """Test curve di capacità vs ASCE 41 benchmark."""
    geom = GeometriaMacroElemento(L=300, t=50, h=360)
    param = ParamMuratura(v0=0.25, mu=0.50, fd=15, Em=1000, Gm=400)
    elem = MacroElementoLV3(1, geom, param, N0=7500)  # σ₀ ≈ 0.5 kg/cm²

    # ASCE 41-06 predice picco ~65 kN a ~0.5% drift
    capacita = elem.pushover_completo(delta_max=3.0, num_step=30)

    # Controlli ragionevoli
    assert capacita['V_Rd'] > 50 * 1000  # > 50 kN
    assert capacita['V_Rd'] < 100 * 1000  # < 100 kN (realistico)
    assert capacita['delta_u'] > 0.5  # Almeno 0.5 cm
    assert capacita['k_elastica'] > 10000  # k > 10 kN/cm
```

---

## 12. Cronologia implementazione (Planning Fase U)

| Fase | Task | Durata | Dipendenze | Status |
|------|------|--------|------------|--------|
| **U.5** | Analisi modale (autovalori/autovettori) | 1.5 w | M (FEM) | ✅ Completato |
| **U.6a** | Macro-elemento SVD (teoria + pseudo-codice) | **2–3 gg** | **U.5, Theory** | 🔄 IN PROGRESS |
| **U.6b** | Implementazione `macro_elemento_lv3.py` | 1 w | U.6a | ⏳ PENDING |
| **U.6c** | Unit test + benchmark ASCE 41 | 1 w | U.6b | ⏳ PENDING |
| **R.4** | Integrazione LV3 in report vulnerabilità | 1 w | U.6c | ⏳ PENDING |

---

**Documento a cura di**: RD2229 — Progetto Calcolo Strutturale Muratura
**Versione**: 1.0-BOZZA-TEORIA
**Data ultimo aggiornamento**: 2026-03-29 (completamento ricerca online)
**Status**: RICERCA COMPLETATA — Pronto per implementazione codice (Fase U.6b)
**Prossimi step**: Validazione numerica vs ASCE 41-06 Table 6-28; implementazione SVD iterativo
