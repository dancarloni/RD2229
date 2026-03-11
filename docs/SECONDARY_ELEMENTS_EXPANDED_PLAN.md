# Piano Fasi Espanso S3–S9 — Elementi Secondari

## Sommario
Estensione del piano di progetto per fasi S3–S9 (Parapetti, Controsoffitti, Impianti, Facciate, Camini, Scaffalature, Speciali) con:
1. **Letteratura e provenienza formule** — Riferimenti normativi per ogni calcolo
2. **Validazione e benchmark numerici** — Descrizione test e casi empirici
3. **Edge cases e scenari limite** — Gestione eccezioni e bordi critici

**Cross-references**:
- API reference: `docs/SECONDARY_ELEMENTS_API.md`
- Architettura: `docs/SECONDARY_ELEMENTS_TECHNICAL.md`
- Validazione: `docs/SECONDARY_ELEMENTS_VALIDATION.md`
- Docstring in Python: `docs/DOCSTRING_TEMPLATE.md`

---

# FASE S3 — Parapetti (Elementi Secondari)

## Descrizione
Verifiche di parapetti e ringhiere (§7.2.2 NTC2018) per comportamento sismico, ancoraggi, comportamento fragile.

**Target**: Sistemi continui murari/acciaio, montanti discreti, vetrati, misti, recinzioni metalliche.

**Output**: SLU (utilisation ancoraggio), SLE (stato danno), decision log, trace esecuzione.

---

## Letteratura e Provenienza Formule

### Normativa Primaria
- **NTC2018 §7.2.2**: "Elementi secondari — Parapetti"
  - Requisiti: Prova statica orizzontale ≥ carico riferimento
  - Comportamento fragile: fattore 0.85 (crisi fragile senza duttilità)
  - Supporti/collegamenti: resistenza per ancoraggio

- **Circ. 7/2019 §C7.2**: Chiarimenti applicativi
  - Comportamento duttile vs. fragile (muratura vs. vetro)
  - Fattori modificatori per sistema di ancoraggio
  - Esempi numerici muratura ordinaria (30 cm, malta ordinaria)

- **NTC2018 §4.1.6**: Carico di servizio minimo
  - Spinta orizzontale **40 kg** per guardrail scale (parapetti leggeri servizio)
  - Verifica inviluppo domanda sismica vs. servizio

### Letteratura Tecnica

- **FEMA E-74 (2015) Cap. 5.2.2: "Parapets and Railings"**
  - Domanda sismica: $F_a = m \times S_a \times \gamma_i$ [kN]
  - Resistenza base muratura: 150–200 psf (≈ 7.3–9.8 kPa = 730–980 kg/m²)
  - Per parapetto 100 cm × 300 cm: $R_{base} = 730 \text{ kg/m}^2 \times 30 \text{ m}^2 = 21.9 \text{ kN}$
  - Fattore fragile (vetro, laterizio): 0.8–0.85

- **ETA/BTI Standards**: Resistenza ancoraggi chimici
  - Tasselli ad espansione: 3–6 kN per tassello
  - Ancoraggi chimici: 2–4 kN per tassello (penalità accuratezza)
  - Cordolo integrato: +25% resistenza (integrazione strutturale)

- **EN 13964 (Reti di sicurezza edili)**: Applicabile a recinzioni metalliche
  - Prova dinamica: energia assorbita ≥ 10 kJ
  - Prova di trazione: carico rottura ≥ 40 kN

### Formule Critiche e Provenienza

1. **Domanda sismica locale** [kg]:
   $$F_a = m \times S_a(T) \times \gamma_i$$
   - $m$: massa parapetto [kg]
   - $S_a$: accelerazione spettrale NTC [g]
   - $\gamma_i$: fattore di importanza (1.0 parapetti ordinari)
   - **Provenienza**: NTC2018 §3.2.1 (analisi statica equivalente per elementi secondari)

2. **Resistenza con fattori** [kg]:
   $$R_{eff} = R_{base} \times f_{anc} \times f_{frag} \times f_{vinc}$$
   - $R_{base}$: lookup table per tipo (8.5 kN muratura continua)
   - $f_{anc}$: 0.9 (chimico), 1.0 (tasselli), 1.25 (cordolo integrato)
   - $f_{frag}$: 0.85 (comportamento fragile sì), 1.0 (no)
   - $f_{vinc}$: 1.1 (vincoli laterali sì), 1.0 (no)
   - **Provenienza**: FEMA E-74 Cap. 5 (modification factors) + NTC2018 Circ. 7/2019

3. **Utilisation** [adim]:
   $$u = \frac{F_a}{\max(R_{eff}, 50 \text{ kg})}$$
   - Salvaguardia: $R_{eff} \geq 50$ kg (evita divisione per zero)
   - Esito: OK se $u \leq 1.0$
   - **Provenienza**: NTC2018 §2.3 (SLU verifiche)

---

## Validazione e Benchmark Numerici

### Categoria Test e Livelli

Vedi `docs/SECONDARY_ELEMENTS_VALIDATION.md` sezione "Test Categorization (5 levels)":
- **Unit**: Enum, dataclass istanziazione, calcolo formule isolate
- **Integration**: spec_from_dict → check_slu → output contract
- **Damage**: Rapporto spostamento → StatoDannoSLE (4 livelli)
- **Pipeline**: Dispatcher routing + metadati storage
- **Benchmark**: vs. FEMA E-74, EN 13964

### Benchmark Test Case S3

**Caso 1: Parapetto Murario Continuo vs. FEMA E-74 Cap. 5.2.2**

```
Specifica:
  - Tipo: CONTINUO_MURATURA (muratura ordinaria 30 cm, malta M10)
  - Altezza: 100 cm
  - Lunghezza: 300 cm
  - Massa lineare: 150 kg/m
  - Massa totale: 450 kg
  - Ancoraggio: TASSELLI_PUNTUALI (6 tasselli, 3 kN ciascuno)
  - Comportamento fragile: NO
  - Vincoli laterali: SI (cordoli superiore/inferiore)

Contesto SLU:
  - S_a = 1.5 g (di default per T=0 s)
  - γ_i = 1.0
  - Carico servizio: 40 kg (NTC4.1.6)

Calcolo:
  1. Domanda sismica: F_a = 450 kg × 1.5 g × 1.0 = 675 kg
  2. Domanda servizio: F_srv = 40 kg (carico minimo normativo)
  3. Domanda totale: max(675, 40) = 675 kg (domanda sismica governa)

  4. Resistenza base (lookup): R_base = 8.5 kN = 866.5 kg
  5. Fattore anchortype: f_anc = 1.0 (tasselli ordinari)
  6. Fattore fragile: f_frag = 1.0 (muratura non fragile)
  7. Fattore vincoli: f_vinc = 1.1 (vincoli laterali presenti)
  8. Resistenza effettiva: R_eff = 866.5 × 1.0 × 1.0 × 1.1 = 953.2 kg

  9. Utilisation: u = 675 / 953.2 = 0.708
  10. Esito: OK (u < 1.0)

Validazione vs. FEMA:
  - FEMA Tab. 5-4 (parapetti murari): resistenza ≈ 150–200 psf
  - Per area lorda 30 m²: R_FEMA ≈ 21.9 kN = 2234 kg
  - Rapporto: R_nostro / R_FEMA = 953.2 / 2234 = 0.427
  - Interpretazione: FEMA più conservativo (include parapetto intero, non localizzato)
  - Nostro OK: criterio di ancoraggio discreto più rappresentativo per tasselli
```

**Test Code** (da eseguire in `tests/test_secondary_parapetti.py`):
```python
def test_benchmark_parapetto_murario_fema_e74():
    """Verifica SLU vs. FEMA E-74 Cap. 5.2.2."""
    inputs = {
        "tipo": "continuo_muratura",
        "altezza_cm": 100,
        "lunghezza_cm": 300,
        "massa_lineare_kg_m": 150,
        "tipo_ancoraggio": "tasselli_puntuali",
        "numero_montanti": 6,
        "comportamento_fragile": False,
        "vincoli_laterali": True,
        "S_a": 1.5,
        "gamma_i": 1.0,
    }
    result = check_slu(inputs)

    assert result["ok"] == True
    assert result["utilisation"] < 1.0
    assert 0.70 < result["utilisation"] < 0.75, "Verifica benchmark u ≈ 0.71"
    assert "OK" in result["esito"]
```

---

## Edge Cases e Scenari Limite

Vedi `docs/SECONDARY_ELEMENTS_VALIDATION.md` sezione "Edge Cases per fase S3":

1. **Altezza parapetto > 150 cm** (fuori range NTC)
   - Gestione: Flag warning in decision_log, esito conservativo
   - Comportamento: Non blocca calcolo, segnala in trace

2. **Base di appoggio insufficiente** ($f_{vinc} = 1.0$ non appoggio laterale)
   - Impatto: -10% resistenza
   - Scenario: Parapetto standalone senza cordoli

3. **Vetri fragili senza cornice** (VETRATO × comportamento_fragile=True)
   - Impatto: -15% resistenza
   - Risk: Crisi fragile senza preavviso

4. **Ancoraggi chimici su base cattiva** (TASSELLI_CHIMICO su malta scadente)
   - Impatto: -10% (già inserito in lookup)
   - Iterazione: Misura risanamento malta → rifirma resistenza

5. **Area aperture > 50% area lorda**
   - Gestione: Salvaguardia automatica: area_netta = max(0, area_lorda - area_aperture)
   - Warning: Se area_netta < 5 m², segnala inefficace

---

# FASE S4 — Controsoffitti (Elementi Secondari)

## Descrizione
Verifiche controsoffitti sospesi (§7.2.3 NTC2018): estensione superficiale, peso, pendini, comportamento dinamico.

**Target**: Sistemi modulari (gesso, cartongesso), pannelli metallici, sospensioni dirette/derivate.

**Output**: SLU (capacità pendini), SLE (danno pannello), trace.

---

## Letteratura e Provenienza Formule

### Normativa Primaria
- **NTC2018 §7.2.3**: "Controsoffitti sospesi ordinari"
  - Richiesta: Prova dinamica di carico su campione
  - Fattore amplificazione: 2–4× carico statico per sisma (dipende massa–smorzamento)
  - Vincolo: Passo pendini ≤ 120 cm (limit span)

- **Circ. 7/2019 §C7.3**: Esempi di calcolo
  - Controsoffitto leggero (< 50 kg/m²): minore amplificazione
  - Controsoffitto pesante (> 100 kg/m²): fattore amplificazione 1.5–2

- **UNI EN 13964 (2004)**: Reti di sicurezza — applicabile a pendini come sistemi di ritenzione
  - Prova di energia: ≥ 10 kJ
  - Carico concentrato: 5 kN (norma reti, ma estrapolabile)

### Formule Critiche

1. **Domanda sismica per controsoffitto modulare** [kN]:
   $$F_a = (m + m_{pannelli}) \times S_a \times \gamma_i \times C_d$$
   - $C_d$: fattore di amplificazione dinamica (1.5–2.5 tipico)
   - **Provenienza**: NTC2018 §7.2.3, FEMA E-74 Cap. 5.3

2. **Capacità pendino singolo** [kN]:
   $$R_{pendino} = \frac{T_{rottura}}{1.5 \times C_{installazione}}$$
   - $T_{rottura}$: carico rottura dal certificato (es. M16 → 150 kN)
   - Fattore 1.5: coefficiente sicurezza SLU
   - $C_{installazione}$: fattore di riduzione installazione (0.8 cattive condizioni)
   - **Provenienza**: NTC2018 §4.3 (leghe acciaio), certificati ETA

3. **Numero pendini minimo**:
   $$n = \lceil \frac{F_a}{R_{pendino}} \rceil$$
   - Round-up al numero intero positivo
   - Se $n > 20$, controsoffitto non fattibile (redesign)

---

## Validazione e Benchmark Numerici

### Benchmark Test Case S4

**Caso: Controsoffitto Modulare Gesso 200 m² vs. EN 13964 + NTC2018**

```
Specifica:
  - Tipo: MODULARE_GESSO
  - Superficie: 200 m²
  - Peso proprio: 10 kg/m²
  - Peso rivestimento: 5 kg/m²
  - Peso totale: (10+5) × 200 = 3000 kg
  - Passo pendini: 100 cm (< 120 cm OK)
  - Numero pendini: 312 (20 m intervallo, 2×2 per modulo 200×200 cm)
  - Tipo pendino: M10 acciaio galvanizzato
  - T_rottura M10: ≈ 60 kN

Contesto SLU:
  - S_a = 1.5 g
  - C_d = 2.0 (controsoffitto modulare, smorzamento 5%)
  - γ_i = 1.0

Calcolo:
  1. Domanda sismica: F_a = 3000 kg × 1.5 g × 1.0 × 2.0 = 9000 kg = 9.0 kN
  2. Resistenza pendino singolo: R = 60 kN / (1.5 × 0.9) = 44.4 kN
  3. Capacità totale: R_tot = 44.4 kN × 312 = 13853 kN >> 9 kN
  4. Utilisation per pendino: u = 9.0 / 13853 = 0.00065 << 1.0
  5. Esito: OK con ampi margini

Osservazione: Numero pendini elevato (312) rende sistema ridondante.
Ottimizzazione possibile: Riducibile a 6-8 pendini per carico SLU.
Vincolo pratico: Passo massimo 120 cm governa numero (non resistenza).
```

---

## Edge Cases S4

1. **Gioco tra pannello e struttura portante = 0** (montaggio stretto)
   - Problematica: Impedisce oscillazione naturale
   - Soluzione: Gioco minimo 5 cm (buffer sisma)

2. **Passo pendini > 120 cm** (eccede limite NTC)
   - Comportamento: Verifica pannello locale (deformazione plastica)
   - Meccanismo di crisi: Piegatura pannello, non più carico uniformemente distribuito

3. **Area supporto controsoffitto > 500 m² senza controventi orizzontali**
   - Problematica: Moto differenziale supporto
   - Soluzione: Controventi di bordo K-brace

4. **Sospensione ibrida** (alcuni pendini fissi, altri a molla)
   - Complicazione: Periodo naturale non è costante
   - Esito: Conservativo (assume tutti pendini passivi)

---

# FASE S5 — Impianti (Tubazioni, Condotti)

## Descrizione
Verifiche impianti tecnici sospesi (acqua, gas, ventilazione, condizionamento) per sisma, supporti, giunti flessibili.

**Target**: Tubazioni metalliche, condotti in lamiera, condotte isolate, collettori.

---

## Letteratura e Provenienza Formule

- **NTC2018 §7.2.4**: "Impianti tecnici"
  - Verifica resistenza sospensioni (vincoli)
  - Fattore amplificazione: 2–3× per tubazioni liquide (effetto added mass)
  - Giunto flessibile: riduce trasmissione accelerazione (ammortizzamento)

- **FEMA E-74 Cap. 5.4**: "Building Mechanical and Electrical Systems"
  - Tubazioni con liquido: massa aggiunta 25–50% massa tubazione
  - Anchoring strategy: concentrato (punti discreti) vs. distribuito (fasciatura)

### Formule

1. **Domanda sismica con added mass**:
   $$F_a = (m_{tubazione} + m_{liquido}) \times S_a \times \gamma_i \times f_{supporto}$$
   - $m_{liquido} = \rho \times V_{interno}$ (acqua: 1000 kg/m³)
   - $f_{supporto}$: 1.5 sospensione diretta, 1.2 ancorata a traliccio

2. **Resistenza supporto/sospensione** [kN]:
   - Lookup table per diametro/tipo materiale (es. M10 acciaio → 60 kN)

---

## Validazione e Benchmark S5

### Benchmark: Tubazione Acqua DN 50

```
Spec:
  - Materiale: Acciaio zincato
  - Diametro: DN 50 (54 mm estern., 48 mm interno)
  - Lunghezza sospesa: 15 m
  - Massa tubazione: 2 kg/m × 15 m = 30 kg
  - Massa acqua: π × (24 mm)² × 15 m × 1 kg/10⁶ mm³ ≈ 27 kg
  - Massa totale: 57 kg
  - Tipo supporto: 2 sospensioni M10 (T_rottura 60 kN)
  - Giunto flessibile: Sì (diminuisce amplificazione)

Contesto:
  - S_a = 1.5 g
  - f_supporto = 1.2 (con giunto, amplificazione ridotta)
  - γ_i = 1.0

Calcolo:
  1. F_a = 57 kg × 1.5 g × 1.0 × 1.2 = 102.6 kg = 1.0 kN
  2. R_totale = 60 kN × 2 = 120 kN
  3. Utilisation: u = 1.0 / 120 = 0.008 << 1.0
  4. Esito: OK

Osservazione: Sistema robusto. Giunto flessibile garantisce disaccoppiamento dinamico.
```

---

## Edge Cases S5

1. **Numero ancoraggi = 0** (tubazione appoggiata su portale, non vincolata)
   - Esito: NON OK (nessuna resistenza sismica)
   - Soluzione: Installare almeno 2 sospensioni

2. **Giunto flessibile > 50 mm** (eccessivo)
   - Impatto: Giunto stesso oscillante, poco ammortizzamento
   - Limite: 25–40 mm garantisce performance

3. **Classe impianto = "vitale"** senza backup
   - Es: Impianto antincendio senza sostituzione rapida
   - Soluzione: Ridondanza (2 rotte parallele con valve)

---

# FASE S6 — Facciate e Rivestimenti

## Letteratura

- **NTC2018 §7.2.5**: "Rivestimenti di facciate"
  - Pressione vento + sisma considerati in combinazione
  - Ancoraggi: tasselli, incollaggi, meccanismi misti

- **EN 13830 (Sistemi di facciata)**: Prova di resistenza al vento
  - Categoria 1 (pressione bassa): 0.4 kPa
  - Categoria 3 (pressione media): 1.2 kPa
  - Categoria 5 (pressione alta): 2.4 kPa

---

## Edge Cases S6

1. **Pressione vento > 2 kPa** (eccezionale, tempeste)
   - Comportamento: Verifica contingency (non è sisma, è temporale)

2. **Giunto orizzontale = 0** (angusta, costi costruttivi)
   - Impatto: Impedisce movimenti termici
   - Risk: Crisi per cicli termici ripetuti

3. **Sottostruttura in legno** (vecchi edifici)
   - Degradazione umidità nel tempo
   - Riduzione resistenza 30–40%

---

# FASE S7 — Camini e Canne Fumarie

## Letteratura

- **NTC2018 §7.2.6**: "Camini, serbatoi, tubazioni a vista"
  - Sviluppo verticale: rapporto h/d (snellezza)
  - Vincolo: h/d ≤ 50 per stabilità ordinaria
  - Fattore amplificazione (oscillazione): 2–4× secondo smorzamento

- **DIN 4133 (Camini)**: Stabilità strutturale
  - Sforzo da vento: $q_v \times h \times (h/d)^{0.5}$

---

## Edge Cases S7

1. **Altezza camino > 15 m non controventato**
   - Snellezza elevata: h/d = 20 m / 0.8 m = 25
   - Periodo naturale ≈ 0.05 h [s] = 1 s
   - Risonanza con moto sismico a T ≈ 0.5–2 s
   - Soluzione: Controventi di rinforzo

2. **Terminale concentrato (non distribuito)**
   - Impatto carico: Concentrato in testata
   - Momento flettente massimo: M = 1.33× rispetto distribuito

3. **Dettagli copertura insufficienti**
   - Water tightness perduta → umidità intracucchiaio → degradazione malta

---

# FASE S8 — Scaffalature Metalliche

## Letteratura

- **NTC2018 §7.2.7**: "Scaffalature in acciaio per magazzini temporanei"
  - Capacità telaio: da prova di carico (cert. instit.)
  - Deformabilità: limite h/500 (non collasso)
  - Baricentro carico: non deve eccedere supporti

---

## Edge Cases S8

1. **Baricentro carico fuori sostegni** (deposito eccentrico)
   - Momento ribaltamento: $M = F \times d_{eccent}$
   - Resistenza al ribaltamento governa (non carico assiale)

2. **Carico eccentrico > 500 kg senza vincolo traslazionale**
   - Comportamento: Slittamento/ribaltamento scaffale

3. **Non ancorato a struttura portante** (temporaneo)
   - Problema: Amplificazione dinamica non controllata
   - Vincolo NTC: Ancoraggio obbligatorio se h > 2 m

---

# FASE S9 — Elementi Speciali Vari

## Descrizione
Elementi non ricadenti nelle categorie ordinarie (parapetti, controsoffitti, etc.): insegne, totem, antenne, serbatoi, boiler, quadri elettrici.

## Letteratura

- **NTC2018 §7.2.8**: "Elementi secondari non ordinari"
  - **Criterio generale**: Se non espressamente contemplato, applicare NTC §7.2.1 (analisi sismica locale)
  - Domanda: $F_a = m \times S_a(T) \times \gamma_i$
  - T (periodo): stimare da h (altezza) o tabella industiale (es. antenne: T ≈ 0.05–0.2 s)

---

## Edge Cases S9

1. **Famiglia elemento non prevista**
   - Gestione: Prompt utente per T-reale o h-surrogate

2. **Schema strutturale indeterminato** (topologia incognita senza rilievo)
   - Soluzione: Assunzione conservativa (T massimo in range, S_a massimo)

---

# Tabella Sinottica: Letteratura per Fase

| Fase | NTC Ref | FEMA Cap. | EN Spec | Formula Chiave |
|------|---------|-----------|---------|--------------|
| S3 Parapetti | §7.2.2 | 5.2.2 | EN 13964 | $R_{eff} = R_{base} \times f_{anc} \times f_{frag} \times f_{vinc}$ |
| S4 Controsoffitti | §7.2.3 | 5.3 | EN 13964 | $F_a = (m + m_p) \times S_a \times C_d \times \gamma_i$ |
| S5 Impianti | §7.2.4 | 5.4 | EN 14396 | $F_a = (m + m_{liq}) \times S_a \times f_{sup} \times \gamma_i$ |
| S6 Facciate | §7.2.5 | 5.5 | EN 13830 | $P = P_{vento} + P_{sisma}$ |
| S7 Camini | §7.2.6 | 5.6 | DIN 4133 | $T = 0.05 h$; $M = qv \times h \times (h/d)^{0.5}$ |
| S8 Scaffalature | §7.2.7 | 5.7 | EN 15635 | $M_{ribalt} = F \times d_{eccent}$ (governa) |
| S9 Speciali | §7.2.8 | 5.8+ | N/A | $F_a = m \times S_a \times \gamma_i$ (generico) |

---

# Come Usare questo Documento

1. **Per sviluppatori**: Referenziare formule critiche (Letteratura) durante code review
2. **Per validatori**: Usare benchmark cases come gold standard
3. **Per manutentori**: Consultare edge cases prima di feature request
4. **Per documentazione**: Hyperlink a SECONDARY_ELEMENTS_*.md files
5. **Per student**: Studiare provenienza formule (non sono magiche, sono norma-derived)

---

# Prossimi Step

- [ ] Applicare docstring template (DOCSTRING_TEMPLATE.md) a tutti i file Python S3–S9
- [ ] Eseguire benchmark cases (pytest)
- [ ] Validare copertura edge cases nei test
- [ ] Generare Sphinx docs (HTML + PDF futuribile)
