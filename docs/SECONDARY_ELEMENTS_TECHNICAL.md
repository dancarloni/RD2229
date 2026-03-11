# Technical Architecture — Elementi Secondari (S1–S9)

## Sommario
Documentazione tecnica interna, design patterns, decisioni architetturali e dipendenze di sistema per tutte le 9 fasi.

---

## Architettura Generale

### Principi Fondamentali

1. **Modularità estrema**: Ogni fase (S1–S9) è completamente indipendente; sostituzione di una fase non impatta le altre.
2. **Type Safety**: Dataclass + Enum + Type hints per garantire contratti chiari.
3. **Separation of Concerns**: Modelli (models.py) → Verifiche (checks_slu.py, checks_sle.py) → API pubblica (__init__.py).
4. **Standardizzazione output**: Tutti i risultati includono `element_type`, `norm_references`, `decision_log`.
5. **Tracciabilità**: UUID di esecuzione, step-by-step log dei calcoli.

### Principio di Calcolo (comune a tutte le fasi)

```
Input Spec (dict)
    ↓
spec_from_dict() → TipoSpec(dataclass)
    ↓
Context (S_a, drift, etc.)
    ↓
[SLU] check_slu() → domanda vs. resistenza
    ├─ calcola_forza_sismica_locale() — o calcolo domanda specifico
    ├─ calcola_resistenza_<tipo>() — dipende da tipologia e modificatori
    └─ Ratio utilisation = domanda / resistenza
    ↓
[SLE] check_sle() → spostamenti, danni, stato servizio
    ├─ calcola_spostamento_ammissibile() — limiti normativi
    ├─ classifica_danno_da_rapporto() — 4 livelli StatoDannoSLE
    └─ Stato danno + decision_log
    ↓
[Output] dict con esito OK/NON OK, norm_references, decision_log
```

---

## Struttura Directory

```
src/codes/ntc2018/secondary_elements/
├── __init__.py                    # Package init, imports tutte le fasi
├── common.py                      # Enum, helper, dispatcher contract
├── models.py                      # Dataclass comuni (legacy)
├── checks.py                      # Verifiche fallback (legacy)
├── storage_adapter.py             # Serializzazione/deserializzazione
│
├── tamponamenti/
│   ├── __init__.py               # API pubblica: spec_from_dict, check_slu, check_sle
│   ├── models.py
│   ├── checks_slu.py
│   ├── checks_sle.py
│   ├── presets.py
│   └── report_adapter.py
│
├── tramezzi/
│   ├── ... (stessa struttura)
│
├── parapetti/
│   ├── ... (stessa struttura)
│
├── controsoffitti/
│   ├── ... (stessa struttura)
│
├── impianti/
│   ├── ... (stessa struttura)
│
├── facciate/
│   ├── ... (stessa struttura)
│
├── camini/
│   ├── ... (stessa struttura)
│
├── scaffalature/
│   ├── ... (stessa struttura)
│
└── speciali/
    ├── ... (stessa struttura)

src/gui/secondary_elements/
├── __init__.py                    # Exports widget
├── <fase>_widget.py               # Qt widget per ogni fase (PySide6)
└── ... (7-9 widget)

data/
├── <fase>_presets.json            # Biblioteca config standard (1-4 preset per fase)
└── ... (7-9 file JSON)

tests/
├── test_secondary_<fase>.py       # 4-5 test per fase
└── ... (9 file)

verifications/secondary_elements/
├── dispatcher.py                  # Routing element_type → fase corretta
└── storage_adapter.py             # Contract di storage esteso
```

---

## Design Patterns

### Pattern 1: Factory Method tramite `spec_from_dict()`

**Scopo**: Convertire dizionario generico (da UI, file JSON, API) in oggetto tipizzato.

**Implementazione**:
```python
def spec_from_dict(inputs: dict) -> TipoSpec:
    """Factory method per spec element.

    Validazione implicita tramite type checking;
    fallback su valori di default se chiave mancante.
    """
    return TipoSpec(
        tipo=SistemaEnum(inputs.get("tipo", DEFAULT_TIPO)),
        campo1=float(inputs.get("campo1", DEFAULT_VAL1)),
        # ... altri campi
    )
```

**Perché**: Decoupling da fonte dati (UI vs. JSON vs. file).

### Pattern 2: Strategy per Verifiche Specializzate

**Scopo**: Incapsulare logica di calcolo SLU/SLE per ogni tipologia.

**Implementazione**:
```python
# In checks_slu.py
_RESISTENZE_BASE_KN = {
    TipoParapetto.CONTINUO_MURATURA: 8.5,
    TipoParapetto.CONTINUO_ACCIAIO: 12.0,
    # ...
}

def calcola_resistenza_ancoraggio(spec: ParapettoSpec) -> float:
    """Calcola resistenza con modificatori (snellezza, anchortype, ecc.)"""
    base = _RESISTENZE_BASE_KN[spec.tipo]

    # Modificatori
    if spec.tipo_ancoraggio == TipoAncoraggio.CHIMICO:
        base *= FATTORE_CHIMICO  # 0.9x
    if spec.comportamento_fragile:
        base *= FATTORE_FRAGILE  # 0.85x

    return max(MIN_RESISTENZA, base)
```

**Perché**: Logica di calcolo confinata a un modulo; riutilizzabile e testabile indipendentemente.

### Pattern 3: Composite Result Objects

**Scopo**: Incapsulare tutti gli aspetti di una verifica in un dataclass unico.

```python
@dataclass
class RisultatoCompleto:
    spec: TipoSpec              # Input di riferimento
    risultato_slu: RisultatoSLU
    risultato_sle: RisultatoSLE
    passaggi_calcolo: list[str]

    def to_dict(self) -> dict:
        """Serializzazione per storage/report."""
```

**Perché**: Garantisce tracciabilità completa spec → output; facilita report e diagnostica.

### Pattern 4: Dispatcher con Routing Normalizzato

**Scopo**: Instradare richieste da UI a modulo corretto senza dipendenze circolari.

```python
# In dispatcher.py
def run(inputs: dict, project_model, limit_state: str, element_type: str | None = None):
    normalized_type = element_type.lower().strip()

    if normalized_type in {"parapet", "parapetti", "balustrade"}:
        from src.codes.ntc2018.secondary_elements import parapetti
        if limit_state == "SLU":
            return parapetti.check_slu(inputs)
        # ...
```

**Perché**: Centralizza routing; riduce coupling tra moduli.

---

## Dipendenze Interne

### Grafo Dipendenze (semplificato)

```
common.py (StatoDannoSLE, calcola_forza_sismica_locale)
    ↓
    ├─ [Fase 1-9] checks_sle.py (per classifica_danno_da_rapporto)
    └─ [Fase 1-9] checks_slu.py (per calcola_forza_sismica_locale)

models.py (legacy, dataclass comuni)
    ↓
    └─ [Fase 1-9] models.py (override/estensione se necessario)

storage_adapter.py
    ↓
    └─ All fasi (storage contract)

dispatcher.py
    ↓
    ├─ [Fase 1-9] __init__.py (API pubbliche)
    ├─ [Fase 1-9] checks_slu.py, checks_sle.py
    └─ verifications.py (entry point verifiche)

[Fase N] __init__.py
    ├─ [Fase N] models.py
    ├─ [Fase N] checks_slu.py, checks_sle.py
    └─ [Fase N] presets.py

[Fase N] presets.py
    └─ data/<fase>_presets.json

[Fase N] report_adapter.py
    ├─ [Fase N] models.py
    └─ src/report/ (template, formatting)

src/gui/secondary_elements/<fase>_widget.py
    ├─ [Fase N] __init__.py
    └─ PySide6 widgets (Qt)
```

---

## Scelte Architetturali Critiche

### (A1) Unità di Misura: kg/cm² vs. MPa

**Decisione**: RD2229 usa **kg/cm²** nativo; conversione via `src/materials/adapter.py` solo per output/report.

**Motivazione**:
- Codice RD2229 storico usa kg/cm² internamente
- NTC2018 definisce resistenze in MPa, ma equivalenza: 1 kg/cm² ≈ 9.81 MPa
- Mantenzione di un solo sistema di unità riduce errori arrotondamento

**Implementazione**:
```python
# internal (kg/cm²)
resistenza_base = 8.5  # kg/cm²
domanda = 1.5  # kg/cm²

# Per output (MPa)
from src.materials.adapter import convert_kg_cm2_to_mpa
resistenza_mpa = convert_kg_cm2_to_mpa(resistenza_base)
```

### (A2) Sistema di Danno Comune (4-Livelli)

**Decisione**: Tutte le fasi usano **unico enum `StatoDannoSLE`** con 4 livelli:
- ASSENTE
- LOCALE
- DIFFUSO
- INSICUREZZA

**Motivazione**:
- Coerenza tra fasi diverse (parapetti vs. impianti vs. facciate)
- Mapping diretto a rapporti spostamento/ammissibile
- Facilita report aggregati e comparativi

**Implementazione**:
```python
# common.py
def classifica_danno_da_rapporto(rapporto: float) -> tuple[StatoDannoSLE, ...]:
    """Mapping universale:
    rapporto ≤ 0.5  → ASSENTE
    0.5 < rapporto ≤ 1.0  → LOCALE
    1.0 < rapporto ≤ 1.5  → DIFFUSO
    rapporto > 1.5  → INSICUREZZA
    """
    # ...
```

### (A3) Presets JSON: Configurazioni Standard

**Decisione**: Ogni fase dispone di **libreria di preset** in `data/<fase>_presets.json` (1–4 configurazioni frequenti).

**Motivazione**:
- Accelera utilizzo per casi standard
- Riduce dipendenza da documentazione
- Facilita auditing (config di riferimento storica)

**Struttura**:
```json
[
  {
    "nome": "parapetto_muratura_base",
    "tipo": "continuo_muratura",
    "altezza_cm": 100,
    "lunghezza_cm": 300,
    "massa_lineare_kg_m": 150,
    "tipo_ancoraggio": "tasselli_puntuali",
    // ... altri campi
  }
]
```

**Utilizzo**:
```python
from src.codes.ntc2018.secondary_elements.<fase> import presets

config = presets.get_preset("parapetto_muratura_base")
spec = spec_from_dict(config)
slu_result = check_slu(config)
```

### (A4) Storage Contract Esteso

**Decisione**: Ogni risultato include **metadati di tracing**:
- `element_type`: Identificativo fase (routing key)
- `norm_references`: Lista norme applicate
- `decision_log`: Passaggi calcolo (list[str])
- `trace.run_id`: UUID univoco

**Motivazione**:
- Audit trail completo per verifiche
- Debugging e diagnostica facilitata
- Export report con citazioni normative

**Implementazione**:
```python
def check_slu(inputs: dict) -> dict:
    passaggi: list[str] = []
    # ... calcoli ...
    return {
        "ok": esito,
        "element_type": "parapetti",
        "norm_references": ["NTC2018 §7.2.2", "Fase S3"],
        "decision_log": passaggi,
        "trace": {"run_id": str(uuid.uuid4())},
        # ... altri campi risultato ...
    }
```

---

## Moduli Critici per Fase

### S1–S2 (Tamponamenti e Tramezzi)

**Modelli storici**: RD2229 prevede verifiche in termini di "pressoflessione deviata" per tamponamenti murari.

**Precisazione**: Fase S1–S2 ridotta a verifica "semplificata" (domanda locale vs. resistenza), lasciando modelli complessi come opzione futura.

### S3 (Parapetti)

**Modello critico**: Resistenza ancoraggio dipende da:
1. Tipo ancoraggio (base continua vs. tasselli puntuali vs. chimico)
2. Vincoli laterali
3. Comportamento fragile (vetri, ceramica → riduzione 15%)

**Formula**:
```
R_ancoraggio = R_base × fattore_anchortype × fattore_vincoli × fattore_fragile
```

**Fattori di riduzione** (conservativi per sicurezza):
- Chimico: 0.9
- Fragile: 0.85

### S4 (Controsoffitti)

**Meccanismo critico**: Capacità di gioco perimetrale.

**Requisito normativo**: Gioco ≥ 25 mm per permettere movimento solaio senza collisione bordo controsoffitto.

**Verifica SLU aggiuntiva**:
```python
if spec.gioco_perimetrale_mm < 25:
    esito_slu = False
    decision_log.append("Gioco perimetrale insufficiente (< 25 mm)")
```

### S5 (Impianti)

**Caratteristica**: Numero di ancoraggi influenza resistenza (distribuzione carico).

**Formula**:
```
R = R_base × fattore_supporto × fattore_ancoraggi × fattore_giunto_flessibile

fattore_ancoraggi = {
    1: 0.7   (1 ancoraggio, critico)
    2: 0.9   (2 ancoraggi)
    3+: 1.0  (3+ ancoraggi, distribuzione buona)
    4+: 1.1  (4+ ancoraggi, bonus di affidabilità)
}
```

### S6 (Facciate)

**Domanda combinata**: Max(sisma, vento), non somma (inviluppo).

**Verifica**:
```python
domanda_sismica = calcola_fa_superficiale(...)
domanda_vento = pressione_vento × area × fattore_forma
domanda_totale = max(domanda_sismica, domanda_vento)
```

### S7 (Camini)

**Amplificazione dinamica**: Periodo proprio influisce sulla domanda.

**Formula periodo** (semplificata):
```
Ta = 0.3 × (h_m / 100)^0.5    [h_m in metri]
```

**Moltiplicatore domanda** (da spettro NTC2018):
```
F_a = m × S_a(Ta) × γ_i
```

**Controventatura**: +40% di resistenza se controventato.

### S8 (Scaffalature)

**Doppio meccanismo di crisi**:
1. **Ribaltamento**: M_stabilizzante = (larghezza/2) × massa_totale / h_baricentro
2. **Ancoraggio**: Capacità tasselli/bulloneria

**Esito**: Min(capacità_ribaltamento, capacità_ancoraggio).

**Meccanismo critico**: Quale dei due governa la crisi?

```python
mech_critical = "ribaltamento" if cap_rib < cap_anc else "ancoraggio"
```

### S9 (Speciali)

**Variabilità massima**: Schema statico dipende da famiglia (mensola, sospensione, binario).

**Approccio**: Generic per famiglia specifica; se nuova requisito, estendere FamigliaSpeciale enum.

---

## Modificatori di Resistenza (Comuni)

| Fattore | Simbolo | Valore | Motivazione |
|---|---|---|---|
| Snellezza insufficiente | λ_red | 0.85–0.95 | Instabilità locale |
| Ancoraggio chimico | η_chim | 0.90 | Affidabilità minore |
| Comportamento fragile | η_frag | 0.85 | Vetri, ceramica, laterizio |
| Controventatura | η_ctrl | 1.40 | Stabilità aumentata (camini) |
| Multiancoraggi bonus | η_multi | 1.10 | Affidabilità distribuzione carico |
| Giunto flessibile bonus | η_flex | 1.15 | Assorbimento movimento |
| Esposizione esterna (facciata) | η_ext | 0.90 | Vento + cicli termici |
| Derivaggio (impianti) | η_der | 0.95 | Instabilità tubi snelli |

---

## Gestione Errori e Eccezioni

### Livello di Applicazione (checks_slu.py, checks_sle.py)

**Strategia**: Graceful degradation, mai crash.

```python
def check_slu(inputs: dict) -> dict:
    try:
        spec = spec_from_dict(inputs)
        # ... calcoli ...
        return {"ok": True, ...}
    except (KeyError, ValueError) as e:
        return {
            "ok": False,
            "esito": "ERROR",
            "messages": [f"Input validation failed: {str(e)}"],
            "decision_log": ["Input parsing error"]
        }
```

**Non propagare eccezioni al dispatcher**; tornare risultato di errore con messaggio chiaro.

### Validazione Input

```python
def spec_from_dict(inputs: dict) -> TipoSpec:
    """Validazione implicita tramite type checking.

    Se chiave mancante → fallback su DEFAULT
    Se valore non convertibile → ValueError (catturata in check_slu)
    """
    assert isinstance(inputs, dict), "Input must be dict"

    tipo = inputs.get("tipo", DEFAULT_TIPO)
    try:
        tipo_enum = TipoEnum(tipo)
    except ValueError:
        raise ValueError(f"Tipo non riconosciuto: {tipo}")

    # ... altri campi ...
```

---

## Testing Strategy

### Livelli di Test

1. **Unit test** (models): Dataclass, Enum, metodi di calcolo isolati.
2. **Integration test** (checks_slu, checks_sle): Flusso verifica SLU+SLE da spec a risultato.
3. **Pipeline test**: Dispatcher → check_slu → check_sle → storage.
4. **Benchmark** (vs. literatura): Validazione risultati su casi noti.

### Test Template (per ogni fase)

```python
# tests/test_secondary_<fase>.py

import pytest
from src.codes.ntc2018.secondary_elements.<fase> import (
    spec_from_dict, check_slu, check_sle, TipoEnum, RisultatoSLU
)

class TestModels:
    def test_spec_massa_totale(self):
        spec = <TipoSpec>(...)
        assert spec.massa_totale_kg() == pytest.approx(expected, rel=1e-3)

class TestSLU:
    def test_check_slu_contract(self):
        result = check_slu({...})
        assert result["element_type"] == "<fase>"
        assert "utilisation" in result

class TestSLE:
    def test_check_sle_damage_classification(self):
        result = check_sle({...})
        assert "stato_danno" in result

class TestPipeline:
    def test_pipeline_completa(self):
        risultato = verifica_<fase>_completa({...})
        assert isinstance(risultato, Risultato<Fase>)

class TestStorage:
    def test_storage_element_type(self):
        result = check_slu({...})
        assert result["element_type"] == "<fase>"
```

---

## Performance Considerations

### Complessità Computazionale

- **check_slu**, **check_sle**: O(1) — calcoli deterministici, no loop
- **dispatcher.run()**: O(1) — solo routing, non calcolo
- **spec_from_dict()**: O(n) con n = numero campi (5–15 tipico)

**Totale per verifica**: < 1 ms (Python puro, nessun NumPy).

### Caching (Possibile Futura Ottimizzazione)

```python
# NON implementato attualmente; disponibile se load test lo richiede
from functools import lru_cache

@lru_cache(maxsize=256)
def calcola_resistenza_base(tipo: str) -> float:
    """Cache resistenze base per fase."""
```

---

## Roadmap Possibili Estensioni

| Estensione | Priority | Effort | Note |
|---|---|---|---|
| Modelli dinamici avanzati (camini) | Media | Media | Incorporare FEM beam per Ta più preciso |
| Soggetto sismica 3D | Bassa | Alta | Multidirezionalità, componenti con inerzia significativa |
| Interazione suolo-struttura (impianti sotterranei) | Bassa | Alta | Richiede integrazione geotecnica |
| GUI avanzata (layout reticolare controsoffitti) | Media | Media | Editor 2D/3D dei layout sospesi |
| Multi-material (acciaio + legno ibrido) | Bassa | Media | Estensione enum TipoParapetto, TipoFacciata |
| Varianti storiche (RD2229, EC8, ASCE 7) | Bassa | Alta | Dispatcher multinorma per secondari |
