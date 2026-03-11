# README — Elementi Secondari Fasi S3–S9

## Quick Start

Ogni fase (S3 Parapetti, S4 Controsoffitti, S5 Impianti, S6 Facciate, S7 Camini, S8 Scaffalature, S9 Speciali) segue il medesimo pattern API:

```python
from src.codes.ntc2018.secondary_elements.<fase> import (
    spec_from_dict,
    check_slu,
    check_sle
)

# 1. Definisci specifica
inputs = {
    "tipo": "continuo_muratura",  # Enum value (str, minuscolo_underscore)
    "altezza_cm": 100,
    "lunghezza_cm": 300,
    "massa_lineare_kg_m": 150,
    "tipo_ancoraggio": "tasselli_puntuali",
    "S_a": 1.5,              # Accelerazione spettrale [g]
    "gamma_i": 1.0,          # Fattore importanza
    "carico_servizio_kg": 40 # Carico normativi (NTC §4.1.6)
}

# 2. Verifica SLU (Stato Limite Ultimo)
result_slu = check_slu(inputs)
print(f"SLU: {result_slu['esito']}")  # 'OK' o 'NON OK'
print(f"Utilisation: {result_slu['utilisation']:.4f}")  # < 1.0 = OK
print(f"Decision log:\n" + "\n".join(result_slu['decision_log']))

# 3. Verifica SLE (Stato Limite di Esercizio)
result_sle = check_sle(inputs)
print(f"Danno: {result_sle['stato_danno']}")  # "Non danno", "Leggero", "Moderato", "Severo"

# 4. Smart decisioning
if result_slu['ok'] and result_sle['stato_danno'] != "Severo":
    print("✓ ELEMENTO VERIFICATO")
else:
    print("✗ ELEMENTO NON VERIFICATO — Vedere decision_log per motivo")
```

**Output Garantito**:
```python
{
    'ok': bool,                    # True se SLU ok
    'esito': 'OK' | 'NON OK',
    'element_type': '<fase>',      # 'parapetti', 'controsoffitti', etc.
    'utilisation': float,          # Rapporto domanda/resistenza
    'domanda_totale_kg': float,
    'resistenza_kg': float,
    'stato_danno': str,            # SLE: "Non danno", "Leggero", "Moderato", "Severo"
    'norm_references': list[str],  # NTC citing
    'decision_log': list[str],     # Passaggi calcolo (tracciabilità)
    'trace': {'run_id': str},      # UUID per audit
    'messages': list[str]          # Warnings/errors se presenti
}
```

---

## Formule Principali per Fase

### S3 — Parapetti (§7.2.2 NTC2018)

**Domanda sismica** [kg]:
$$F_a = m \cdot S_a(T=0) \cdot \gamma_i$$

**Resistenza con fattori** [kg]:
$$R_{eff} = R_{base} \times f_{ancoraggio} \times f_{fragile} \times f_{vincoli}$$

**Fattori**:
- $f_{ancoraggio}$: 1.0 (tasselli), 0.9 (chimico), 1.25 (cordolo integrato)
- $f_{fragile}$: 0.85 (vetri, ceramica), 1.0 (altrimenti)
- $f_{vincoli}$: 1.1 (cordoli laterali presenti), 1.0 (no)

**Tipologie di parapetti** (lookup $R_{base}$):
| Tipo | R_base [kN] | Descrizione |
|------|-----------|--------------|
| CONTINUO_MURATURA | 8.5 | Muratura ordinaria 30 cm |
| CONTINUO_ACCIAIO | 12.0 | Profili tubolari/IPE |
| MONTANTI_ACCIAIO | 10.5 | Discreti, 4–6 montanti |
| VETRATO | 6.5 | Panelli vetro temperato |
| MISTO_ACCIAIO_VETRO | 9.0 | Ibrido acciaio+vetri |
| RECINZIONE_METALLICA | 5.0 | Reti/pannelli aperti |

**Variabili Input**:
- `altezza_cm`: 60–150 cm (NTC §4.1.6)
- `lunghezza_cm`: 100–1000 cm (tipico)
- `massa_lineare_kg_m`: 50–200 kg/m (servizio)
- `tipo_ancoraggio`, `comportamento_fragile`, `vincoli_laterali`: flags

**Riferimenti**:
- NTC2018 §7.2.2, Circ. 7/2019 §C7.2
- FEMA E-74 Cap. 5.2.2 (parapets)
- ETA TSI per ancoraggi

---

### S4 — Controsoffitti (§7.2.3 NTC2018)

**Domanda sismica con amplificazione dinamica**:
$$F_a = (m_{prop} + m_{rivestimento}) \cdot S_a \cdot C_d \cdot \gamma_i$$

**Fattore di amplificazione** [adim]:
$$C_d = 1.5 + \frac{\zeta}{100}$$
dove $\zeta$ = smorzamento (5% = 1.5–2.0 tipico per controsoffitti modulari)

**Numero pendini minimo**:
$$n = \lceil \frac{F_a}{R_{pendino}} \rceil$$

**Vincoli normativi**:
- Passo pendini ≤ 120 cm (limit span NTC)
- Gioco parapetto/struttura ≥ 5 cm (buffer sisma)

**Riferimenti**:
- NTC2018 §7.2.3, Circ. 7/2019 §C7.3
- FEMA E-74 Cap. 5.3 (drop ceiling systems)
- EN 13964 (reti di sicurezza, estrapolato pendini)

---

### S5 — Impianti (§7.2.4 NTC2018)

**Domanda sismica per tubazioni/condotti**:
$$F_a = (m_{tubo} + m_{fluido}) \cdot S_a \cdot f_{supporto} \cdot \gamma_i$$

**Massa fluido** (se riempite):
$$m_{fluido} = \rho \cdot V_{interno}$$
- Acqua: 1000 kg/m³
- Aria: negligibile
- Olio: 900 kg/m³

**Fattore supporto**:
$$f_{supporto} = \begin{cases} 1.5 & \text{sospensione diretta (nudo)} \\ 1.2 & \text{con giunto flessibile} \\ 1.0 & \text{ancorato a struttura} \end{cases}$$

**Giunto flessibile**: riduce amplificazione dinamica (ammortizzamento)
- Lunghezza consigliata: 25–40 mm
- Evita: > 50 mm (giunto stesso oscillante)

**Riferimenti**:
- NTC2018 §7.2.4
- FEMA E-74 Cap. 5.4 (mechanical systems)
- EN 14396 (condotte, teste di collegamento)

---

### S6 — Facciate (§7.2.5 NTC2018)

**Carico combinato** (vento + sisma):
$$P_{tot} = P_{vento} + P_{sisma}$$

**Pressione vento** (NTC §3.3.8):
$$P_{vento} = q_b \cdot c_e \cdot c_p$$
- $q_b$: pressione dinamica di base (45 Pa Italia media)
- $c_e$: fattore esposizione (h, esposizione geometrica)
- $c_p$: fattore di pressione (faccia +0.8, retro −0.3)

**Capacità ancoraggi** [kN]:
Lookup table per diametro/tipo (tasselli M10 → 10–15 kN; chimici → ridotti 20%)

**EN 13830 categorie pressione**:
| Categoria | Pressione [kPa] | Utilizzo |
|-----------|---------|----------|
| 1 | 0.4 | Zone tranquille |
| 3 | 1.2 | Urbano normale |
| 5 | 2.4 | Esposizione alta |

**Riferimenti**:
- NTC2018 §7.2.5, §3.3.8
- EN 13830 (sistemi di facciata)

---

### S7 — Camini (§7.2.6 NTC2018)

**Snellezza:**
$$\lambda = \frac{h}{d}$$
- Criterio: $\lambda \leq 50$ (stabilità ordinaria)
- Oscillazione naturale: $T = 0.05 \cdot h$ [s] (empirico)

**Momento flettente da sisma**:
$$M = F_a \cdot h$$
dove $F_a = m \cdot S_a \cdot \gamma_i$

**Controventatura**: Richiesta se h > 15 m o $\lambda > 30$ senza damping

**Riferimenti**:
- NTC2018 §7.2.6
- DIN 4133 (camini, stabilità)

---

### S8 — Scaffalature (§7.2.7 NTC2018)

**Resistenza al ribaltamento** (governa se carico eccentrico):
$$M_{ribalt} = F \cdot d_{eccent}$$

**Verifiche parallele**:
1. Carico assiale: $F_a \leq R_{palone}$ (resistenza colonna)
2. Carico eccentrico: $M \leq M_{cap}$ (momento di inerzia)
3. Slittamento: Attrito + ancoraggi

**Vincoli NTC**:
- Ancoraggio obbligatorio se h > 2 m
- Baricentro carico entro supporti ±10%

**Riferimenti**:
- NTC2018 §7.2.7
- EN 15635 (qualsiasi scaffale metallo)

---

### S9 — Elementi Speciali (§7.2.8 NTC2018)

**Criterio generale**: NTC §7.2.1 (analisi sismica locale)
$$F_a = m \cdot S_a(T_{proprio}) \cdot \gamma_i$$

**T proprio** (stima):
- Altezza h ≤ 5 m: T ≈ 0.1 s (antenne, totem leggeri)
- Altezza h = 5–15 m: T ≈ 0.2 s (serbatoi sospesi medi)
- Altezza h > 15 m: T ≈ 0.05h s (camini, caminetti alt)

**Senza dati, assumere T_max in range** (conservativo)

**Riferimenti**:
- NTC2018 §7.2.8 (elementi non ordinari)
- FEMA E-74 Cap. 5+ (vari sistemi)

---

## Decisioni Architetturali Chiave

Vedi `docs/SECONDARY_ELEMENTS_TECHNICAL.md` sezione "Critical Architectural Choices (A1–A4)":

### A1: Sistema Unità Interna (cm, kg)
- **Scelta**: Unità interna cm, kg (RD2229 nativa)
- **Conversione**: Sola per output (kN = kg/101.97, MPa = kg/10.197 cm²)
- **Benefit**: Evita errori accumulo conversioni, mantiene precisione

### A2: Damage Scale Unificato (4 Livelli)
```
StatoDannoSLE:
  - "Non danno": rapporto spostamento ≤ 0.2%
  - "Leggero": 0.2%–0.5%
  - "Moderato": 0.5%–1.5%
  - "Severo": > 1.5%
```
- **Benefit**: Comparabilità cross-phase, linguaggio comune decisionale

### A3: Presets JSON Library
- **Path**: `data/secondary_elements/presets_<fase>.json`
- **Vantaggio**: Rapid deployment, no code changes, configurabile by non-engineer

### A4: Storage Contract Extension
- **element_type**: Named element (parapetti, controsoffitti, etc.)
- **norm_references**: Riga NTC/FEMA/EN citate
- **decision_log**: Full audit trail (Chi? Cosa? Quando? Perché?)
- **trace.run_id**: UUID per linking con report/logs

---

## Test & Validazione

### Test Execution
```bash
# Tutti gli elementi secondari
pytest tests/test_secondary_*.py -v

# Solo fase S3
pytest tests/test_secondary_parapetti.py -v

# Report coverage
pytest tests/test_secondary_*.py --cov=src/codes/ntc2018/secondary_elements
```

### Benchmark Cases
Vedi `docs/SECONDARY_ELEMENTS_VALIDATION.md` sezione "Benchmark Test Cases":
- **S3 Parapetto Murario**: vs. FEMA E-74 Cap. 5.2.2 ✅
- **S4 Controsoffitto**: vs. EN 13964 ✅
- **S5 Tubazione**: vs. NTC2018 semplificato ✅
- S6–S9: Edge cases + tabellari

---

## Estensioni Futuro (Roadmap)

**V1.1** (Q3):
- [ ] Damping factor `zeta` configurabile per S4 controsoffitti
- [ ] Validation curve vs. periodo naturale (S7 camini)

**V1.2** (Q4):
- [ ] Amplificazione dinamica per impianti (S5) con calcolo periodo
- [ ] Interfaccia Rhino/Revit per input geometria real-time

**V2.0** (2025):
- [ ] 3D FEM coupling (OpenSees stub)
- [ ] Export RESTful API (hosting cloud)
- [ ] Reportistica interattiva (Plotly dashboard)

---

## Contatti & Supporto

- **Docs**: `docs/SECONDARY_ELEMENTS_*.md`
- **API Spec**: `docs/SECONDARY_ELEMENTS_API.md`
- **Technical**: `docs/SECONDARY_ELEMENTS_TECHNICAL.md`
- **Docstring Template**: `docs/DOCSTRING_TEMPLATE.md`
- **Test Strategy**: `docs/SECONDARY_ELEMENTS_VALIDATION.md`
- **Expanded Plan**: `docs/SECONDARY_ELEMENTS_EXPANDED_PLAN.md`

---

**Last Updated**: 2025 (Fase S3–S9 Completion)
**Maintained By**: RD2229 Development Team
**License**: MIT (se interno) o proprietario
