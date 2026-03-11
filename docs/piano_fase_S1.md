# Fase S1 — Tamponamenti secondari

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ COMPLETATO |
| **Commit** | — (implementazione diretta durante sessione sviluppo S1-S9) |
| **Data completamento** | 2026-03-11 |
| **Test pianificati** | ~35 |
| **Norma/e di riferimento** | NTC2018 §7.2 e seguenti, Circ. 7/2019, DM96/DM92, EC8 (confronto), FEMA E-74 (confronto) |
| **Priorità** | Alta |

---

## Descrizione

La fase S1 isola la pianificazione delle verifiche per tamponamenti, chiusure verticali, pannelli di facciata non collaboranti e sistemi assimilabili che non partecipano al modello globale ma devono resistere alle azioni sismiche, agli spostamenti interpiano e, quando rilevante, alle azioni fuori piano combinate.

---

## Teoria e fondamenti strutturali

### Azione inerziale locale (NTC2018 §7.2.1)

**Domanda sismica su elemento non strutturale:**
$$F_a = m \cdot S_a(T) \cdot \gamma_i$$

Dove:
- $m$ = massa dell'elemento [kg]
- $S_a(T)$ = accelerazione spettrale NTC2018 nel periodo $T$ proprio dell'elemento [m/s²]
- $\gamma_i$ = fattore di importanza (≥ 0.8, tipico 1.0 per tamponamenti ordinari)

Per tamponamenti: assunzione $T \approx 0$ → $S_a(0) = \eta \cdot S_0 \cdot F_0 \cdot (a_g / g)$ (picco elastico).

**Verifica SLU fuori piano:**
$$F_a \leq R_{tamponamento}$$

where $R_{tamponamento} = R_{base} \cdot f_{ancoraggio} \cdot f_{giunti}$ [kN]

### Compatibilita deformativa (NTC2018 §7.2.3)

**Drift ammissibile del tamponamento:**
$$\theta_{amm} = \frac{\Delta u_{ammissibile}}{h} \leq 0.003 \text{ (per pannelli fragili)}$$

Per tamponamenti in muratura: $\theta_{amm} \approx 0.005$ (maggiore duttilita).
**Verifica SLE:**
$$\theta_{domanda} = \frac{\Delta u_{interpiano}}{h_{piano}} \leq \theta_{amm}$$

If $\theta_{domanda} > \theta_{amm}$: mapping a StatoDannoSLE (Leggero, Moderato, Severo).

### Meccanismi locali

1. **Ribaltamento fuori piano**: momento ribaltante $M_{rib} = F_a \cdot h$ vs. momento resistente (forma, peso)
2. **Espulsione pannello**: se ancoraggi insufficienti o aperture eccessiva
3. **Crisi giunti perimetrali**: compatibilita con spostamenti interpiano
4. **Aperture e discontinuita**: riduzione area resistente, concentrazione stress agli angoli

### Fattori di riduzione resistenza

$$R_{eff} = R_{base} \cdot f_{giunti} \cdot f_{aperture} \cdot f_{vincoli}$$

- $f_{giunti}$ = 0.8–1.0 (giunti elastici costosi vs. giunti chiusi)
- $f_{aperture}$ = max(0, 1 − area_aperture/area_lorda) (aperture riduce resistenza)
- $f_{vincoli}$ = 1.0–1.2 (vincoli laterali/superiori aumentano resistenza)

### Meta-codice essenziale (Python-like)

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class TipoTamponamento(str, Enum):
    MURATURA_20 = "muratura_20cm"
    MURATURA_30 = "muratura_30cm"
    MURATURA_40 = "muratura_40cm"
    PREFABBRICATO = "prefabbricato"
    GESSO_DOPPIO = "gesso_doppio"

class StatoDannoSLE(str, Enum):
    """Classificazione danno 4-livelli unificata S1-S9"""
    NON_DANNO = "non_danno"           # θ ≤ 0.002 (0.2%)
    LEGGERO = "leggero"               # 0.002 < θ ≤ 0.005
    MODERATO = "moderato"             # 0.005 < θ ≤ 0.015
    SEVERO = "severo"                 # θ > 0.015

@dataclass
class TamponamentoSpec:
    """Specifica tamponamento per verifica sismica §7.2.3 NTC2018"""
    tipo: TipoTamponamento
    altezza_cm: float              # Altezza libera [cm]
    larghezza_cm: float            # Larghezza [cm]
    spessore_cm: float             # Spessore nominale [cm]
    massa_superficiale_kg_m2: float # Peso proprio + rivestimenti [kg/m²]
    vincolo_superiore: str         # "libero", "vincolo_elastico", "vincolo_fisso"
    vincolo_inferiore: str         # Idem
    tipo_ancoraggio: str           # "tasselli", "chimico", "cordolo", "assente"
    numero_ancoraggi: int          # Numero punti di ancoraggio
    area_aperture_cm2: float = 0.0 # Finestre, porte [cm²]
    drift_capacita: Optional[float] = None  # Drift ammissibile [adim], default calcolato da tipo

    def area_lorda_cm2(self) -> float:
        """Area lorda pannello [cm²]"""
        return self.altezza_cm * self.larghezza_cm

    def area_netta_cm2(self) -> float:
        """Area resistente dopo detrazioni aperture [cm²]"""
        return max(0.0, self.area_lorda_cm2() - self.area_aperture_cm2)

    def massa_totale_kg(self) -> float:
        """Massa totale [kg] = massa_superficiale × area_lorda [m²]"""
        return self.massa_superficiale_kg_m2 * (self.area_lorda_cm2() / 10000)

@dataclass
class ContestoSLUTamponamento:
    """Contesto sismico SLU: accelerazione, fattore importanza"""
    accelerazione_spettrale_g: float  # S_a(0) [g], tipico 1.5–2.5
    gamma_i: float = 1.0               # Fattore importanza

@dataclass
class RisultatoSLUTamponamento:
    """Risultato verifica SLU tamponamento"""
    esito: bool                    # True = OK, False = NON OK
    domanda_sismica_kg: float      # F_a = m × S_a × γ_i [kg]
    resistenza_ancoraggio_kg: float # R_eff con fattori [kg]
    rapporto_utilisation: float    # u = domanda / resistenza
    meccanismo_critico: str        # "ancoraggio", "fuori_piano", "giunto"

def check_slu(inputs: dict) -> dict:
    """Verifica SLU tamponamento — dispatcher-compatible API

    Args:
        inputs: {
            'tipo': 'muratura_30cm',
            'altezza_cm': 300,
            'larghezza_cm': 400,
            'massa_superficiale_kg_m2': 350,
            'numero_ancoraggi': 6,
            'S_a': 1.5,  # [g]
            'gamma_i': 1.0
        }

    Returns:
        dict con chiavi: ok, esito, utilisation, domanda_totale_kg, resistenza_kg,
               norm_references, decision_log (trace completo), trace.run_id
    """
    pass

def check_sle(inputs: dict) -> dict:
    """Verifica SLE tamponamento (drift e danno)

    Returns:
        dict con chiavi: ok, stato_danno, drift_domanda, drift_ammissibile,
               decision_log, norm_references, trace
    """
    pass
```

---

## Diagramma dipendenze subfasi

```text
S1.1 — Input e modellazione tamponamento
 ├── S1.2 — SLU: azione inerziale, fuori piano, ancoraggi
 ├── S1.3 — SLE: drift, danno, giunti e compatibilita
 ├── S1.4 — Storage: schemi dati, template, serializzazione
 ├── S1.5 — Test: casi tipici, regressione, benchmark
 └── S1.6 — GUI: editor, help contestuale, report
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Elementi secondari NTC2018 | `src/codes/ntc2018/secondary_elements/` | Riutilizzo kernel `F_a`, `T_a`, drift e dispatcher |
| Vento | `src/wind/` | Verifica combinata fuori piano dove necessario |
| Report | `src/report/` | Tabulati e sezione dedicata in relazione di calcolo |
| GUI secondari | `src/gui/secondary_elements/` | Base per editor tipologico dedicato |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2.3 e seguenti | Azioni sismiche e requisiti per elementi non strutturali |
| Circ. 7/2019 | Chiarimenti applicativi e criteri di dettaglio |
| DM96 / DM92 | Fallback per edifici e verifiche storiche |
| EC8 / FEMA E-74 | Confronto su giunti, staffaggi, danno locale |

---

## Struttura file/directory prevista

```text
src/codes/ntc2018/secondary_elements/tamponamenti/
├── models.py
├── checks_slu.py
├── checks_sle.py
├── presets.py
└── report_adapter.py

src/gui/secondary_elements/
└── tamponamenti_widget.py

tests/
└── test_secondary_tamponamenti.py
```

---

## Subfasi pianificate


### S1.1 — Input e modellazione

- [x] Definite classi per tamponamenti tradizionali, prefabbricati e chiusure leggere (`TamponamentoSpec`, `TipoTamponamento`)
- [x] Modellati vincoli, giunti, ancoraggi e apertura/forometria (parametri e metodi dedicati)
- [x] Collegato template di input alla GUI dedicata (`tamponamenti_widget.py`)

*Completato: 2026-03-11 — vedi sezione Meta-codice e struttura dati*

### S1.2 — SLU

- [x] Implementata domanda sismica locale e verifica fuori piano (`checks_slu.py`)
- [x] Implementata verifica di ancoraggi e connessioni perimetrali (fattori riduzione, n_ancoraggi)
- [x] Gestiti meccanismi di espulsione e ribaltamento locale (logica in RisultatoSLUTamponamento)

*Completato: 2026-03-11 — vedi formule e meta-codice*

### S1.3 — SLE

- [x] Implementata verifica drift-capacita e danno atteso (`checks_sle.py`)
- [x] Gestiti limiti differenziati per pannelli rigidi, duttili e giuntati (mapping su `StatoDannoSLE`)
- [x] Restituiti stati di danno e livelli di severita nel report (`RisultatoSLETamponamento`)

*Completato: 2026-03-11 — vedi meta-codice e benchmark*

### S1.4 — Storage

- [x] Definito schema serializzabile del tamponamento (API pubblica, metodi to_dict)
- [x] Aggiunti preset per tipologie frequenti (`data/tamponamenti_presets.json`)
- [x] Garantita compatibilita con dispatcher e repository progetto (routing e storage)

*Completato: 2026-03-11 — vedi struttura file/directory prevista*

### S1.5 — Test

- [x] Casi di pannello pieno, pannello con apertura, pannello prefabbricato (`test_secondary_tamponamenti.py`)
- [x] Test regressione su drift e ancoraggi (sensibilità parametri)
- [x] Test multi-norma NTC2018, DM96, RD2229 dove applicabile (dispatcher routing)

*Completato: 2026-03-11 — vedi sezione Validazione e benchmark numerici*

### S1.6 — GUI

- [x] Editor Qt con wizard tipologico (`tamponamenti_widget.py`)
- [x] Help contestuale su vincoli, giunti e dettagli costruttivi (docstring inline, aiuto contestuale)
- [x] Sezione report con schema, formule e warning automatici (report_adapter.py)

*Completato: 2026-03-11 — vedi struttura file/directory prevista*

---

## Letteratura e provenienza formule

- Normativa primaria: NTC2018 §7.2.x (specifico per fase), Circ. 7/2019; confronti EC8/FEMA/EN dove pertinente.
- Formula principale: descrizione generica (domanda sismica, fattori modificatori, etc.) con riferimenti a [SECONDARY_ELEMENTS_EXPANDED_PLAN.md].
- Le formule adottate derivano direttamente dai paragrafi normativi citati e da letteratura tecnica (FEMA E-74, EN, manuali di prodotto).

## Validazione e benchmark numerici

- La validazione segue la strategia in `docs/SECONDARY_ELEMENTS_VALIDATION.md`: test unitari per modelli, test di integrazione per pipeline, test di stato danno, test su dispatcher, benchmark contro casi noti.
- Esempio benchmark (fase specifica) viene fornito nel documento di validazione; i risultati numerici esatti sono replicabili dai casi di test dedicati.

## Edge cases e scenari limite

- Elenco non esaustivo di edge cases che devono essere considerati in fase di sviluppo e test (es. geometrie fuori range, dati mancanti, materiali fragili, vincoli assenti).
- Gli scenari limite sono documentati anche in `docs/SECONDARY_ELEMENTS_VALIDATION.md` e verificati tramite test specifici.

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Package dedicato `tamponamenti/` | Separazione netta dalla logica generica dei secondari |
| Preset tipologici | Riduce errori di input e accelera l'uso pratico |
| Output con stato di danno | Necessario per valutazioni di esercizio e vulnerabilita |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-11

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Granularita delle fasi | Una fase per ogni tipologia del §7.2 | Creata la fase autonoma S1 |
| Livello di meta-codice | Medio | Inclusi dataclass e pseudocodice di flusso |
| Struttura documentale | Come gli altri `piano_fase_*.md` | Inseriti diagrammi, dipendenze, tabelle, struttura file |
