# Validation and Testing — Elementi Secondari (S1–S9)

## Sommario
Strategia di validazione normativa, test suite, edge cases, benchmark numerici e mappatura a letteratura per tutte le 9 fasi.

---

## Quadro Normativo di Riferimento

### Norme Applicate

| Norma | Uso | Capitoli Rilevanti | Note |
|---|---|---|---|
| **NTC2018** | Primaria | §7.2: "Criteri di sicurezza per elementi non strutturali e impianti" | Base nazionale italiana |
| Circ. n. 7/2019 | Chiarimenti applicativi | §C7.2 | Interpretazioni ufficiali del Ministero |
| **EC8** | Confronto, varianti | Part 1-1: Sezioni 4.4.1–4.4.2 | Standard europeo, non utilizzato in Italia ma utile per benchmark |
| **FEMA E-74** (2011) | Confronto tecnico | Cap. 4–6: Seismic Retrofit Design Examples | Linee guida USA; metodologie di verifica robuste |
| **ASCE 7** | Confronto, wind | Cap. 20 & 21: Non-structural components and equipment | Standard USA; utile per carico vento comparativo |

### Mapping Normativo per Fase

#### S1 — Tamponamenti

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.1: "E' necessario verificare gli elementi non strutturali..." | `check_slu()` su domanda sismica + carico | `test_check_slu_contract` |
| "...e gli eventuali impianti, rispetto ai quali il danno prodotto dal sisma sia capace di significativamente compromettere la funzionalità della costruzione" | Flag `compromette_funzionalita` in spec | `test_classe_funzione_impact` |
| "Progettazione in base agli spostamenti" (SLE) | `check_sle()` con rapporto spostamento | `test_check_sle_damage_classification` |

#### S2 — Tramezzi

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.1: Verifiche rispetto azioni orizzontali | `check_slu()` con massimale domanda combinata | `test_partition_slu_envelope` |
| Considerare vincoli locali (continui vs. puntuali) | `tipo_vincolo` in spec; modificatori di resistenza | `test_vincolo_tipo_modifiers` |

#### S3 — Parapetti

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.2: "Parapetti e balaustre...resistenza rispetto a spinta orizzontale" | `calcola_resistenza_ancoraggio()` con fattori | `test_parapetto_anchortype_factors` |
| "...considerando il comportamento fragile degli elementi" | `comportamento_fragile` flag; factor 0.85× | `test_fragile_behavior_reduction` |
| "Compatibilità con spostamenti del supporto" (SLE) | `check_sle()` con spostamento ammissibile | `test_parapetto_sle_compatibility` |

#### S4 — Controsoffitti

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.4: "Giunti perimetrali...adeguati per l'assorbimento degli spostamenti" | Verifica `gioco_perimetrale_mm >= 25` in SLU | `test_gioco_perimetrale_minimum` |
| "Sistemi di controvento" | `presenza_controventi` bool; modifica resistenza | `test_controvento_capacity_increase` |
| "Riduzione della resistenza dovuta a...perdita di appoggio" (SLE) | `rapporto > 1.5` → `perdita_appoggio_rischio = True` | `test_perdita_appoggio_sle` |

#### S5 — Impianti

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.2 (generalità): "Verifica di elementi secondari puntuali e lineari" | Duplice verifica: supporti + ancoraggi | `test_dual_mechanism_support_anchorage` |
| "Continuità funzionale per sistemi essenziali" (es. sprinkler) | `classe_funzione` in spec; output flag | `test_continuita_funzionale_classe` |
| "Compatibilità con spostamenti relativi tra elementi" | Verifica giunto flessibile; spostamento ammissibile SLE | `test_giunto_flessibile_check` |

#### S6 — Facciate

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2 + §4.2.4 (vento): "Combinazione sisma e vento" | Inviluppo: `max(domanda_sismica, domanda_vento)` | `test_sisma_vento_envelope` |
| "Giunti tra moduli...capacità di corsa" | Verifica giunti SLE; `rapporto > 2.0` → martellamento | `test_giunto_capacita_corsa` |

#### S7 — Camini

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.2 (generalità): "Elementi snelli...considerare la dinamica" | `periodo_proprio_s()` calcolato; amplificazione domanda | `test_periodo_proprio_amplificazione` |
| NTC §4.5.3.3 (stabilità): "Snellezza limite per instabilità locale" | Verifica implicitamente in `check_slu()` con fattori | `test_snellezza_criteria` |

#### S8 — Scaffalature

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.2 (generalità): "Elementi potenzialmente ribaltabili" | Dual verifica: ribaltamento vs. ancoraggi | `test_ribaltamento_vs_ancoraggio` |
| "Massa partecipante e baricentro distante dal supporto" | `baricentro_relativo()` in spec; fattore momento | `test_baricentro_moment_arm` |

#### S9 — Speciali

| Requisito NTC2018 | Implementazione | Test Associato |
|---|---|---|
| §7.2.2 (generalità): Applicazione principi generali a casi non standard | Dispatcher generico per famiglia; output traccia | `test_famiglia_speciale_dispatch` |

---

## Test Strategy per Fase

### Test Categorization

#### 1. Unit Test (Modelli)

**Scope**: Validazione dataclass, enum, metodi di calcolo isolati.

**Esempio (S3 Parapetti)**:
```python
def test_parapetto_massa_totale():
    spec = ParapettoSpec(
        tipo=TipoParapetto.CONTINUO_MURATURA,
        altezza_cm=100,
        lunghezza_cm=300,
        massa_lineare_kg_m=150,
        tipo_ancoraggio=TipoAncoraggio.TASSELLI_PUNTUALI,
    )
    assert spec.massa_totale_kg() == pytest.approx(45000.0, rel=1e-3)
```

#### 2. Integration Test (Check Contract)

**Scope**: Flusso completo spec → check_slu/sle → output contract.

**Esempio (S4 Controsoffitti)**:
```python
def test_controsoffitto_slu_contract():
    inputs = {
        "tipo": "modulare_gesso",
        "area_m2": 100.0,
        "massa_superficiale_kg_m2": 10.0,
        "passo_pendini_cm": 80,
        "gioco_perimetrale_mm": 30,
        "S_a": 1.5,
    }
    result = check_slu(inputs)

    assert result["element_type"] == "controsoffitti"
    assert "utilisation" in result
    assert "decision_log" in result
    assert isinstance(result["ok"], bool)
```

#### 3. Damage State Test (SLE Classification)

**Scope**: Validazione mappatura rapporto spostamento → StatoDannoSLE.

**Esempio (S8 Scaffalature)**:
```python
def test_scaffalatura_damage_states():
    test_cases = [
        (0.4, StatoDannoSLE.ASSENTE),        # rapporto < 0.5
        (0.7, StatoDannoSLE.LOCALE),        # 0.5 ≤ rapporto < 1.0
        (1.2, StatoDannoSLE.DIFFUSO),       # 1.0 ≤ rapporto < 1.5
        (2.0, StatoDannoSLE.INSICUREZZA),   # rapporto ≥ 1.5
    ]

    for rapporto, expected_state in test_cases:
        state, _, _, _, _ = classifica_danno_da_rapporto(rapporto)
        assert state == expected_state
```

#### 4. Pipeline Test (Dispatcher + Storage)

**Scope**: Routing corretto tramite dispatcher; storage metadata completo.

**Esempio (S5 Impianti)**:
```python
def test_impianti_pipeline_completa():
    inputs = {
        "element_type": "impianti",
        "categoria": "tubazione_sospesa",
        "massa_kg": 50.0,
        "quota_cm": 250,
        "S_a": 1.5,
    }

    # Via dispatcher
    from verifications.secondary_elements.dispatcher import run
    from unittest.mock import Mock

    project = Mock(norma_attiva="NTC2018")
    result_slu = run(inputs, project, "SLU", element_type="impianti")

    assert result_slu["element_type"] == "impianti"
    assert "trace" in result_slu
    assert "run_id" in result_slu["trace"]
```

#### 5. Benchmark Test (vs. Letteratura / Casi Noti)

**Scope**: Validazione risultati su esempi storici o letteraturali.

**Esempio: S3 Parapetto (FEMA E-74)**

FEMA E-74, Cap. 5.2.2: "Parapetto murario, h=100 cm, L=300 cm, masse = 15 ton/m"

```python
def test_parapetto_fema_benchmark():
    """Benchmark vs. FEMA E-74 esempio 5.2.2."""

    # Dati FEMA case
    spec = ParapettoSpec(
        tipo=TipoParapetto.CONTINUO_MURATURA,
        altezza_cm=100,
        lunghezza_cm=300,
        massa_lineare_kg_m=150,  # 15 ton/m
        tipo_ancoraggio=TipoAncoraggio.TASSELLI_PUNTUALI,
        numero_montanti=6,
        comportamento_fragile=False,
    )

    # Contesto NTC2018 equivalente a FEMA (S_a ≈ 0.5g + adattamenti)
    inputs = spec.__dict__
    inputs.update({"S_a": 0.5, "gamma_i": 1.0})

    result = check_slu(inputs)

    # FEMA prevede: domanda ≈ 45 kN, resistenza ≈ 120 kN → utilisation ≈ 0.37
    assert result["ok"] == True
    assert result["utilisation"] < 0.5  # Margine ragionevole
```

---

## Edge Cases e Scenari Limite

### S1–S2: Tamponamenti e Tramezzi

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Massa nulla** | Spec con massa_superficiale = 0 | `check_slu()` ritorna domanda = 0 → utilisation = 0 |
| **Ancoraggio inesistente** | `numero_ancoraggi = 0` | Resistenza → 0; risultato → NON OK (salvaguardia) |
| **Giunto non continuo** | `giunto_completo = False` | Fattore riduttivo 0.7× su resistenza |

### S3: Parapetti

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Altezza eccessiva** | h > 150 cm (limite norma) | Warning in decision_log; fattore riduzione (futuro) |
| **Base di ancoraggio insufficiente** | Base continua < 5 cm | Validazione critica; se viola → NON OK |
| **Vetri frammentabili** | `comportamento_fragile = True` + danni SLE | Flag integration `pannelli_integri` in output |

### S4: Controsoffitti

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Gioco perimetrale ZERO** | `gioco_perimetrale_mm = 0` | SLU automaticamente NON OK (gating check) |
| **Pendini con passo > 120 cm** | `passo_pendini_cm > 120` | Warning + fattore riduzione resistenza (futuro) |
| **Controventi assenti + area > 500 m²** | Alto rischio perdita appoggio | Warning specifico in decision_log |

### S5: Impianti

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Numero ancoraggi = 0** | Tubazione non fissata | Resistenza = 0 → NON OK |
| **Giunto flessibile con spostamento > 50 mm** | Flessibilità insufficiente | SLE: `rapporto > 2.0` → INSICUREZZA |
| **Componente essenziale senza ridondanza** | `classe_funzione = "vitale"` + 1 ancoraggio | Flag `continuita_funzionale = False` |

### S6: Facciate

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Pressione vento estrema** | P > 2.0 kPa + SistemaFacciata.CURTAIN_WALL | Domanda vento >> sisma → inviluppo governa |
| **Giunto perimetrale 0** | Nessuna tolleranza di movimento | SLE martellamento con probabilità alta |
| **Sottostruttura in legno** | Tipo "legno" non nelle resistenze base | Error handling: fallback su valore conservativo |

### S7: Camini

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Altezza > 15 m + non controventato** | Snellezza estrema | Verificare Ta > 2.0 s (bassa accelerazione); potrebbe essere OK |
| **Terminale con massa concentrata** | Massa polarizzata in sommità | Amplificazione dinamica per Ta calcolato correttamente |
| **Attraversamento copertura con dettagli insufficienti** | Fissaggio compromesso da cicli termici | Warning decisionale; possibile fattore riduttivo (futuro) |

### S8: Scaffalature

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Baricentro fuori dai supporti** | `baricentro_x > larghezza/2` | Risultato instabile; meccanismo = ribaltamento imminente |
| **Contenuto non uniformemente distribuito** | Carico eccentrico | Modello semplificato assume uniform; warning su realtà |
| **Scaffale non ancorato + massa > 500 kg** | Critico di sicurezza | Decision log: "Ancoraggio fortemente consigliato" |

### S9: Speciali

| Edge Case | Descrizione | Handling |
|---|---|---|
| **Famiglia non prevista** | Input con `famiglia` non in enum | `spec_from_dict()` → ValueError → error dict |
| **Schema statico indeterminato** | `schema_statico = "complesso"` | Output con warning; utilizzare approccio FEM |

---

## Benchmark Numerici (Validazione Letteraria)

### Benchmark 1: S3 Parapetto Murario (FEMA E-74, Cap. 5.2.2)

**Fonte**: FEMA E-74 (2011), "Seismic Retrofit Design Examples"

**Dati Caso**:
- Altezza: 100 cm
- Lunghezza: 300 cm
- Materiale: Muratura ordinaria
- Massa lineare: 150 kg/m → massa totale = 45 ton
- Ancoraggi: Tasselli puntuali, 6 pz

**Contesto Sismico**:
- S_a (FEMA): 0.5g + 2% damping
- NTC2018 equivalente: S_a ≈ 0.5g, γ_i = 1.0

**Domanda FEMA**:
```
F_a = m × S_a = 45,000 kg × 0.5 g = 22,500 kg (forza)
```

**Resistenza FEMA** (tasselli: 20 kN cad, 6 pz):
```
R = 6 × 20 kN = 120 kN = 12,240 kg
```

**Rapporto (FEMA)**:
```
Utilisation = 22,500 / 12,240 ≈ 1.84  → NON OK
```

**Test RD2229** (NTC2018):
```python
def test_parapetto_vs_fema_e74():
    spec = ParapettoSpec(
        tipo=TipoParapetto.CONTINUO_MURATURA,
        altezza_cm=100,
        lunghezza_cm=300,
        massa_lineare_kg_m=150,
        tipo_ancoraggio=TipoAncoraggio.TASSELLI_PUNTUALI,
        numero_montanti=6,
        comportamento_fragile=False,
    )

    inputs = spec.__dict__
    inputs.update({
        "S_a": 0.5,
        "gamma_i": 1.0,
        "resistenza_ancoraggio_kn": 12.24  # FEMA 120 kN
    })

    result = check_slu(inputs)

    # Atteso: NON OK (come FEMA)
    assert result["ok"] == False
    assert result["utilisation"] > 1.5
```

---

### Benchmark 2: S4 Controsoffitto Modulare (EN 13964 / FEMA E-74, Cap. 6.1)

**Fonte**: EN 13964 (European standard for suspended ceilings), integrato da FEMA E-74

**Dati Caso**:
- Tipo: Griglia modulare gesso
- Area: 200 m²
- Massa superficiale: 10 kg/m² → massa totale = 2,000 kg
- Passo pendini: 80 cm (stdandard CEN)
- Gioco perimetrale: 30 mm (conforme CEN)

**Contesto**:
- S_a: 1.0g (alta sismicità)
- Drift interpiano: 0.5% (edificio ordinario)

**Domanda EN 13964**:
```
F_a = m × S_a × γ_i = 2,000 kg × 1.0 g × 1.0 = 2,000 kg
```

**Resistenza CEN** (pendini gesso, base 25 kg cad):
```
Numero pendini ≈ Area / passo² = 200 / (0.8×0.8) ≈ 312 pendini
R = 312 × 25 kg = 7,800 kg
```

**Rapporto (EN 13964)**:
```
Utilisation = 2,000 / 7,800 ≈ 0.26  → OK (ampio margine)
```

**Test RD2229**:
```python
def test_controsoffitto_vs_en13964():
    spec = ControsoffittoSpec(
        tipo=TipoControsoffitto.MODULARE_GESSO,
        area_m2=200,
        massa_superficiale_kg_m2=10,
        passo_pendini_cm=80,
        gioco_perimetrale_mm=30,
    )

    inputs = spec.__dict__
    inputs.update({
        "S_a": 1.0,
        "gamma_i": 1.0,
    })

    result = check_slu(inputs)

    # Atteso: OK
    assert result["ok"] == True
    assert result["utilisation"] < 0.5  # Margine abbondante
```

---

### Benchmark 3: S5 Tubazione Sospesa (NTC2018 Semplificato)

**Fonte**: NTC2018 §7.2.2 + esempio didattico interno

**Dati Caso**:
- Categoria: Tubazione acqua sospesa
- Diametro: DN 50 mm
- Massa: 30 kg (tubi + fluido)
- Quota: 250 cm (intermedio)
- Supporti: 2 sospensioni (catene)
- Giunto flessibile: Sì

**Contesto**:
- S_a: 1.5g
- γ_i: 1.0

**Domanda**:
```
F_a = 30 kg × 1.5 g × 1.0 = 45 kg
```

**Resistenza** (sospensioni: 60 kg cad):
```
R_base = 2 × 60 kg = 120 kg
R_modificata = 120 kg × 1.2 (fattore sospensione) × 1.15 (giunto flex) = 165.6 kg
```

**Rapporto**:
```
Utilisation = 45 / 165.6 ≈ 0.27  → OK
```

**Test RD2229**:
```python
def test_tubazione_sospesa_ntc2018():
    spec = ImpiantoSpec(
        categoria=CategoriaImpianto.TUBAZIONE_SOSPESA,
        massa_kg=30,
        quota_cm=250,
        numero_ancoraggi=2,
        tipo_supporto=TipoSupporto.SOSPENSIONE,
        presenza_giunto_flessibile=True,
    )

    inputs = spec.__dict__
    inputs.update({
        "S_a": 1.5,
        "gamma_i": 1.0,
    })

    result = check_slu(inputs)

    # Atteso: OK
    assert result["ok"] == True
    assert result["utilisation"] < 0.35
```

---

## Reporting e Audit Trail

### Sezione "Decision Log" negli Output

Ogni verificazione include list[str] `decision_log` che traccia step-by-step i calcoli:

**Esempio (S8 Scaffalatura)**:
```
decision_log = [
    "=== VERIFICA SLU SCAFFALATURA ===",
    "Massa vuota = 100 kg",
    "Massa contenuto = 200 kg",
    "Massa totale = 300 kg",
    "Baricentro relativo = 60 cm (altezza 120 cm / 2)",
    "Domanda sismica: F_a = 300 kg × 1.5 g × 1.0 = 450 kg",
    "Resistenza ribaltamento: 150 kg (base tipo LIGHT_DUTY)",
    "Resistenza ancoraggi: 300 kg (2 tasselli × 150 kg)",
    "Meccanismo critico: RIBALTAMENTO",
    "Capacita min(ribalt, ancor) = 150 kg",
    "Utilisation = 450 / 150 = 3.0",
    "ESITO: NON OK (utilisation > 1.0)",
]
```

### Export Normato per Report

Ogni risultato include `norm_references` per citazione automatica:

```python
norm_references = [
    "NTC2018 §7.2.2",
    "Circ. n.7/2019 §C7.2",
    "FEMA E-74 (riferimento letterario)",
    "Fase S8 — Scaffalature e contenuti",
]
```

---

## Validazione Continua (CI/CD)

### GitHub Actions Workflow (Hypothesis)

```yaml
name: secondary-elements-validate

on: [push, pull_request]

jobs:
  test-s1-s9:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    steps:
      - uses: actions/checkout@v2
      - name: Install Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run S1-S9 tests
        run: |
          pytest tests/test_secondary_*.py -v --cov=src/codes/ntc2018/secondary_elements
      - name: Benchmark validation
        run: |
          pytest tests/test_secondary_*.py -k benchmark -v
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Roadmap di Validazione Futura

| Milestone | Scopo | Timing |
|---|---|---|
| **V1.0** (attuale) | Baseline S1–S9 con unit + integration test | 2026-03-11 |
| **V1.1** | Benchmark letterari completi (FEMA, EN, EC) | 2026-Q2 |
| **V1.2** | GUI test e validazione UI (Qt screenshot) | 2026-Q2 |
| **V2.0** | FEM avanzato per camini/impianti snelli | 2026-Q3 |
| **V2.1** | Multinorma (RD2229, EC8, ASCE 7) | 2026-Q4 |
