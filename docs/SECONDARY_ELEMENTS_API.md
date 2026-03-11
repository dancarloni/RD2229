# API Reference — Elementi Secondari (S1–S9)

## Sommario
Documentazione completa delle API pubbliche per tutte le 9 fasi di elementi secondari e non strutturali secondo NTC2018 §7.2.

---

## Principi Comuni

### Contratto di Verifica
Tutte le verifiche (SLU, SLE) seguono il pattern:

```python
def check_slu(inputs: dict) -> dict:
    """
    Esegue verifica SLU per elemento secondario.

    Args:
        inputs (dict): Dizionario con spec elemento e contesto (S_a, P_vento, gamma_i).

    Returns:
        dict: {
            'esito': 'OK' | 'NON OK',
            'ok': bool,
            'element_type': str,
            'norm_references': list[str],
            'decision_log': list[str],
            'domanda_totale_kg': float,
            'resistenza_kg': float,
            'utilisation': float  # ratio demand/resistance
        }
    """
```

### Naming Convention
- **Funzioni di verifica**: `check_slu()`, `check_sle()`
- **Funzioni di trasformazione spec**: `spec_from_dict()`
- **Funzioni di calcolo componenti**: `calcola_<quantità>_<unità>()`
- **Enumerazioni tipologie**: `Tipo<Elemento>` (es. `TipoParapetto`, `TipoScaffalatura`)

### Storage Contract
Tutti i risultati includono:
- `element_type`: Identificativo fase (es. "parapetti", "impianti")
- `norm_references`: Lista norma di riferimento (es. ["NTC2018 §7.2.2", "Fase S3"])
- `decision_log`: Trace dei passaggi di calcolo (list[str])
- `trace.run_id`: UUID univoco per esecuzione

---

## S1 — Tamponamenti Secondari

### Package
```
src/codes/ntc2018/secondary_elements/tamponamenti/
```

### API Entry Points

#### `spec_from_dict(inputs: dict) -> TamponamentoSpec`
Converte dizionario in oggetto specifica tamponamento.

**Input keys** (all optional, default fallback disponibile):
- `tipo`: "muratura_tradizionale" | "cls_prefabbricato" | "vetro" | altri
- `altezza_cm`, `lunghezza_cm`, `massa_superficiale_kg_m2`
- `tipo_ancoraggio`: "base_continua", "tasselli_puntuali", "chimico", etc.
- `numero_ancoraggi`, `giunto_completo` (bool), `comportamento_fragile` (bool)

**Returns**: `TamponamentoSpec`

---

## S2 — Tramezzi Secondari

### Package
```
src/codes/ntc2018/secondary_elements/tramezzi/
```

### API Entry Points

#### `spec_from_dict(inputs: dict) -> TramezzoSpec`
Converte dizionario in oggetto specifica tramezzo.

**Input keys**:
- `tipo`: "muratura_ordinaria", "cls_leggero", "cartongesso", "misto", etc.
- `altezza_cm`, `lunghezza_cm`, `massa_superficiale_kg_m2`
- `tipo_vincolo`: "continuo_su_lastre", "puntuale_montanti", etc.
- `numero_montanti`, `classe_funzione`: "non_portante" | "portante_ridotto"

**Returns**: `TramezzoSpec`

---

## S3 — Parapetti e Balaustre

### Package
```
src/codes/ntc2018/secondary_elements/parapetti/
```

### Enumerazioni

#### `TipoParapetto(str, Enum)`
```python
CONTINUO_MURATURA = "continuo_muratura"
CONTINUO_ACCIAIO = "continuo_acciaio"
MONTANTI_ACCIAIO = "montanti_acciaio"
VETRATO = "vetrato"
MISTO_ACCIAIO_VETRO = "misto_acciaio_vetro"
RECINZIONE_METALLICA = "recinzione_metallica"
```

#### `TipoAncoraggio(str, Enum)`
```python
BASE_CONTINUA = "base_continua"
TASSELLI_PUNTUALI = "tasselli_puntuali"
CHIMICO = "chimico"
CORDOLO_INTEGRATO = "cordolo_integrato"
```

### Models

#### `ParapettoSpec` (dataclass)
```python
@dataclass
class ParapettoSpec:
    tipo: TipoParapetto
    altezza_cm: float                      # 60–150 cm (norma)
    lunghezza_cm: float
    massa_lineare_kg_m: float
    tipo_ancoraggio: TipoAncoraggio
    resistenza_ancoraggio_kn: float | None
    numero_montanti: int = 0
    aperture_presenti: bool = False
    vincoli_laterali: bool = True
    comportamento_fragile: bool = False    # Vetri, ceramica

    def massa_totale_kg(self) -> float:
        """Massa = massa_lineare × lunghezza."""
```

#### `RisultatoSLUParapetto` (dataclass)
```python
@dataclass
class RisultatoSLUParapetto:
    domanda_sismica_kg: float              # Forza da inerzia locale
    domanda_servizio_kg: float             # Carico orizzontale d'uso (es. spinta)
    domanda_combinata_kg: float            # Max(sismica, servizio)
    resistenza_ancoraggio_kg: float        # Capacità verificata
    utilisation: float = 0.0               # domanda_combinata / resistenza
```

#### `RisultatoSLEParapetto` (dataclass)
```python
@dataclass
class RisultatoSLEParapetto:
    spostamento_bordo_cm: float
    spostamento_ammissibile_cm: float
    stato_danno: StatoDannoSLE             # ASSENTE | LOCALE | DIFFUSO | INSICUREZZA
    danno_giunti: bool
    integrita_pannelli: bool
    intervento_necessario: bool
```

### Functions

#### `check_slu(inputs: dict) -> dict`
Verifica SLU parapetto contro domanda sismica + servizio.

**Input keys**:
```python
{
    "tipo": "continuo_muratura",
    "altezza_cm": 100,
    "lunghezza_cm": 300,
    "massa_lineare_kg_m": 150,
    "tipo_ancoraggio": "tasselli_puntuali",
    "numero_montanti": 6,
    "S_a": 1.5,           # Accelerazione spettrale  (g)
    "gamma_i": 1.0,       # Coefficiente importanza
    "P_servizio_kg": 40   # Carico orizzontale d'uso
}
```

**Returns**: `dict` con esito OK/NON OK, utilisation, decision_log

#### `check_sle(inputs: dict) -> dict`
Verifica SLE parapetto per danni e compatibilità.

---

## S4 — Controsoffitti Sospesi

### Package
```
src/codes/ntc2018/secondary_elements/controsoffitti/
```

### Enumerazioni

#### `TipoControsoffitto(str, Enum)`
```python
MODULARE_GESSO = "modulare_gesso"           # Griglie modulari, pannelli gesso
LASTRA_CONTINUA = "lastra_continua"         # Lastre PVC, mdf continue
TECNICO_APERTO = "tecnico_aperto"           # Open ceiling, passerelle, impianti visibili
SISTEMA_MISTO = "sistema_misto"             # Combinazioni
```

### Models

#### `ControsoffittoSpec` (dataclass)
```python
@dataclass
class ControsoffittoSpec:
    tipo: TipoControsoffitto
    area_m2: float
    massa_superficiale_kg_m2: float         # 5–25 kg/m² tipico
    passo_pendini_cm: float                 # 60–120 cm
    presenza_controventi: bool = True
    gioco_perimetrale_mm: float = 30        # Deve essere ≥ 25 mm
    lunghezza_controventi_m: float = 0.0

    def massa_totale_kg(self) -> float:
        """Massa = area × massa_superficiale."""
```

#### `RisultatoSLUControsoffitto` (dataclass)
```python
@dataclass
class RisultatoSLUControsoffitto:
    domanda_totale_kg: float
    resistenza_pendini_kg: float
    resistenza_controventi_kg: float | None
    capacita_gioco_perimetrale: bool        # True se ≥ 25 mm
    eccesso_pendini: bool
    eccesso_bordo: bool
```

#### `RisultatoSLEControsoffitto` (dataclass)
```python
@dataclass
class RisultatoSLEControsoffitto:
    drift_calcolato_perc: float
    drift_ammissibile_perc: float
    perdita_appoggio_rischio: bool          # Se drift_ratio > 1.5
    sags_strutturali: bool
    stato_danno: StatoDannoSLE
```

### Functions

#### `check_slu(inputs: dict) -> dict`
Verifica pendini, controventi e gioco perimetrale.

#### `check_sle(inputs: dict) -> dict`
Verifica drift compatibilità e perdita appoggio.

---

## S5 — Impianti e Componenti Impiantistici

### Package
```
src/codes/ntc2018/secondary_elements/impianti/
```

### Enumerazioni

#### `CategoriaImpianto(str, Enum)`
```python
TUBAZIONE_SOSPESA = "tubazione_sospesa"     # Acqua, riscaldamento, antincendio
CANALE_ARIA = "canale_aria"                 # Condotti ventilazione, condizionamento
APPARECCHIATURA = "apparecchiatura"         # Pompe, boiler, fan-coil
QUADRO_ELETTRICO = "quadro_elettrico"       # Quadri MT/BT, scatole di distribuzione
SISTEMA_SPRINKLER = "sistema_sprinkler"     # Rete antincendio pressurizzata
```

#### `TipoSupporto(str, Enum)`
```python
SOSPENSIONE = "sospensione"                 # Catene, tiranti
APPOGGIO = "appoggio"                       # Basamenti, supporti elastici
STAFFAGGIO = "staffaggio"                   # Staffe metalliche, collari
INCOLLAGGIO = "incollaggio"                 # Adesivi strutturali
```

### Models

#### `ImpiantoSpec` (dataclass)
```python
@dataclass
class ImpiantoSpec:
    categoria: CategoriaImpianto
    mass_kg: float
    quota_cm: float                         # Altezza da solaio
    numero_ancoraggi: int = 1
    tipo_supporto: TipoSupporto = SOSPENSIONE
    presenza_giunto_flessibile: bool = False
    classe_funzione: str | None = None      # "ordinaria", "vitale"

    def massa_totale_kg(self) -> float:
        """Ritorna massa."""
```

#### `RisultatoSLUImpanto` (dataclass)
```python
@dataclass
class RisultatoSLUImpanto:
    domanda_totale_kg: float
    resistenza_supporti_kg: float
    resistenza_ancoraggi_kg: float
    capacita_continuita_funzionale: bool
    meccanismo_critico: str                 # "supporto" | "ancoraggio" | "flessibilita_insufficiente"
```

#### `RisultatoSLEImpanto` (dataclass)
```python
@dataclass
class RisultatoSLEImpanto:
    spostamento_relativo_cm: float
    spostamento_ammissibile_cm: float
    collisione_rischio: bool
    perdita_funzionalita: bool
    stato_danno: StatoDannoSLE
```

### Functions

#### `check_slu(inputs: dict) -> dict`
Verifica supporti, staffaggi e continuità funzionale.

#### `check_sle(inputs: dict) -> dict`
Verifica spostamenti relativi e collisioni.

#### `verifica_impianto_completa(inputs: dict) -> RisultatoComponenteImpanto`
Esecuzione integrata SLU + SLE.

---

## S6 — Facciate e Rivestimenti

### Package
```
src/codes/ntc2018/secondary_elements/facciate/
```

### Enumerazioni

#### `SistemaFacciata(str, Enum)`
```python
CURTAIN_WALL = "curtain_wall"               # Elementi tridimensionali sospesi
VENTILATA = "ventilata"                     # Intercapedine ventilata, sottostruttura
PANNELLO_PREFABBRICATO = "pannello_prefabbricato"
RIVESTIMENTO_PESANTE = "rivestimento_pesante"  # Laterizio, marmo, ceramica
```

### Models

#### `FacciataSpec` (dataclass)
```python
@dataclass
class FacciataSpec:
    sistema: SistemaFacciata
    modulo_luce_cm: float                   # 100–300 cm tra ancoramenti
    massa_superficiale_kg_m2: float         # 50–150 kg/m² tipico
    area_m2: float
    tipo_sottostruttura: str                # "alluminio", "acciaio", "legno"
    tipo_ancoraggio: str                    # "fisso", "regolabile", "scorrevole"
    drift_capacita_perc: float = 2.0        #% drift ammissibile

    def massa_totale_kg(self) -> float:
        """Ritorna area × massa_superficiale."""
```

### Functions

#### `check_slu(inputs: dict) -> dict`
Verifica pannelli contro combinazione sisma + vento.

#### `check_sle(inputs: dict) -> dict`
Verifica danni ai giunti, martellamento, integrita pannelli.

---

## S7 — Camini e Canne Fumarie

### Package
```
src/codes/ntc2018/secondary_elements/camini/
```

### Enumerazioni

#### `TipoCamino(str, Enum)`
```python
MURATURA = "muratura"
ACCIAIO = "acciaio"
PREFABBRICATO = "prefabbricato"
COMPOSITO = "composito"
```

### Models

#### `CaminoSpec` (dataclass)
```python
@dataclass
class CaminoSpec:
    tipo: TipoCamino
    altezza_cm: float                       # Lunghezza libera
    massa_totale_kg: float
    diametro_equivalente_cm: float | None = None
    vincolo_base: str = "incastro"          # "incastro", "cerniera"
    controventato: bool = False             # 1.4x resistenza se True
    rigidezza_flessionale_kg_cm2: float | None = None

    def periodo_proprio_s(self) -> float:
        """Stima Ta = 0.3 × (h_m / 100)^0.5"""
```

### Functions

#### `check_slu(inputs: dict) -> dict`
Verifica stabilità, snellezza, ancoraggi.

#### `check_sle(inputs: dict) -> dict`
Verifica spostamento sommitale, risonanza, danni.

---

## S8 — Scaffalature e Contenuti

### Package
```
src/codes/ntc2018/secondary_elements/scaffalature/
```

### Enumerazioni

#### `TipoScaffalatura(str, Enum)`
```python
HEAVY_DUTY = "heavy_duty"                   # 500+ kg per livello, fissate
LIGHT_DUTY = "light_duty"                   # 100–300 kg, mobili
ARMADIO_TECNICO = "armadio_tecnico"         # Quadri, apparecchiature, chiuso
ARCHIVIO = "archivio"                       # Compattatori, faldoni, altezza > 2 m
```

### Models

#### `ScaffalaturaSpec` (dataclass)
```python
@dataclass
class ScaffalaturaSpec:
    tipo: TipoScaffalatura
    altezza_cm: float
    larghezza_cm: float
    profondita_cm: float
    massa_vuota_kg: float
    massa_contenuto_kg: float
    ancorata: bool
    tipo_ancoraggio: str | None = None

    def massa_totale_kg(self) -> float:
        """massa_vuota + massa_contenuto."""

    def baricentro_relativo(self) -> float:
        """altezza_cm / 2.0 semplificato."""
```

#### `RisultatoSLUScaffalatura` (dataclass)
```python
@dataclass
class RisultatoSLUScaffalatura:
    domanda_totale_kg: float
    capacita_ribaltamento_kg: float
    capacita_ancoraggi_kg: float
    meccanismo_critico: str                 # "ribaltamento" | "ancoraggi"
    esito: bool                             # OK se domanda <= min(ribalt, ancor)
```

#### `RisultatoSLEScaffalatura` (dataclass)
```python
@dataclass
class RisultatoSLEScaffalatura:
    spostamento_relativo_cm: float
    spostamento_ammissibile_cm: float
    perdita_contenuto_rischio: bool
    stato_danno: StatoDannoSLE
```

### Functions

#### `check_slu(inputs: dict) -> dict`
Verifica ribaltamento vs. ancoraggio (mech. critico).

#### `check_sle(inputs: dict) -> dict`
Verifica perdita contenuto, danni strutturali.

---

## S9 — Componenti Speciali (Insegne, Cancelli, Pannelli Sospesi)

### Package
```
src/codes/ntc2018/secondary_elements/speciali/
```

### Enumerazioni

#### `FamigliaSpeciale(str, Enum)`
```python
INSEGNA_BANDIERA = "insegna_bandiera"       # Mensolate, esposte al vento
CANCELLO_SCORREVOLE = "cancello_scorrevole" # Binari, cerniere, massa mobile
PANNELLO_SOSPESO = "pannello_sospeso"       # Elementi sospesi per divisioni
MENSOLA_LEGGERA = "mensola_leggera"         # Non impiantistica, carichi concentrati
CHIUSURA_TECNICA = "chiusura_tecnica"       # Porte, tapparelle, elementi di servizio
```

### Models

#### `ComponenteSpecialeSpec` (dataclass)
```python
@dataclass
class ComponenteSpecialeSpec:
    famiglia: FamigliaSpeciale
    massa_kg: float
    schema_statico: str                     # "mensola", "sospensione", "binario"
    esposizione_esterna: bool
    tipo_supporto: str
    grado_mobilita: str                     # "fisso", "mobile", "semi_mobile"
    supporti_numero: int = 1

    def massa_totale_kg(self) -> float:
        """Ritorna massa_kg."""
```

### Functions

#### `check_slu(inputs: dict) -> dict`
Verifica supporti, staffe, bracci, cerniere.

#### `check_sle(inputs: dict) -> dict`
Verifica mobilità, interferenze, danni.

#### `verifica_speciale_completa(inputs: dict) -> RisultatoComponenteSpeciale`
Esecuzione integrata.

---

## Common Module: `common.py`

### Enumerazioni Shared

#### `StatoDannoSLE(str, Enum)`
Usata da **tutte** le fasi per classificare dan compromesso di servizio:
```python
ASSENTE = "assente"                         # No daño
LOCALE = "locale"                           # Daño en zonas limitadas
DIFFUSO = "diffuso"                         # Daño diffuso, servizio compromesso
INSICUREZZA = "insicurezza"                 # Insicurezza, richiede intervento
```

### Functions

#### `calcola_forza_sismica_locale(massa_kg: float, S_a: float, gamma_i: float) -> float`
```python
"""
Calcola domanda sismica locale (Fa).
Formula NTC2018 §7.2.1:
    Fa = massa × S_a × gamma_i

Args:
    massa_kg: Massa elemento (kg)
    S_a: Accelerazione spettrale (g)
    gamma_i: Coefficiente importanza

Returns:
    Forza sismica locale (kg)
"""
```

#### `classifica_danno_da_rapporto(rapporto: float) -> tuple[StatoDannoSLE, bool, bool, bool, str]`
```python
"""
Classifica stato di danno SLE da rapporto spostamento/ammissibile.

Args:
    rapporto: spostamento_reale / spostamento_ammissibile

Returns:
    (stato_danno, danno_giunti, danno_pannelli, intervento_necessario, note)
"""
```

---

## Dispatcher Routing

### `verifications/secondary_elements/dispatcher.py`

Routing basato su **normalized element_type**:

| Element Type (Input) | Normalized | Routing |
|---|---|---|
| "tamponamento", "tamponamenti", "infill" | tamponamenti | `src.codes.ntc2018.secondary_elements.tamponamenti` |
| "tramezzo", "tramezzi", "partition" | tramezzi | `src.codes.ntc2018.secondary_elements.tramezzi` |
| "parapet", "parapetti", "balustrade" | parapetti | `src.codes.ntc2018.secondary_elements.parapetti` |
| "ceiling", "controsoffitti", "suspended" | controsoffitti | `src.codes.ntc2018.secondary_elements.controsoffitti` |
| "impianto", "impianti", "piping" | impianti | `src.codes.ntc2018.secondary_elements.impianti` |
| "facciata", "facciate", "curtain" | facciate | `src.codes.ntc2018.secondary_elements.facciate` |
| "camino", "camini", "chimney" | camini | `src.codes.ntc2018.secondary_elements.camini` |
| "scaffalatura", "scaffalature", "shelving" | scaffalature | `src.codes.ntc2018.secondary_elements.scaffalature` |
| "speciale", "speciali", "signs" | speciali | `src.codes.ntc2018.secondary_elements.speciali` |

---

## Presets JSON

Ogni fase dispone di libreria di configurazioni standard in `data/<fase>_presets.json`:

**Formato**:
```json
[
  {
    "nome": "identificativo_preset",
    "famiglia|tipo": "enum_value",
    "campo1": value1,
    "campo2": value2,
    ...
  }
]
```

**Utilizzo**:
```python
from src.codes.ntc2018.secondary_elements.<fase> import presets

config = presets.load_preset("identificativo_preset")
spec = spec_from_dict(config)
result = check_slu(config)
```

---

## Storage and Reporting

### Storage Keys (In ProjectModel)

```python
verification_result = {
    "spec": {...},                           # Input specification
    "slu": {...},                            # SLU esito
    "sle": {...},                            # SLE esito
    "element_type": "parapetti",              # Routing key
    "norm_references": ["NTC2018 §7.2.2"],   # Norme applicate
    "decision_log": [...],                   # Trace calcolo
    "trace": {"run_id": "uuid"},             # Metadata
}
```

### Report Exports

Ogni fase implementa `report_adapter.py` per export:
- **Markdown** (`to_markdown()`)
- **Dict** (`to_dict()`)
- **HTML** (via template)

---

## Versioning and Compatibility

- **Schema version**: 1.1.0 (NTC2018)
- **Python**: ≥ 3.11
- **Dipendenze**: numpy, scipy, pyyaml (per presets)
- **No breaking changes**: Backward compatible fino a S1–S9
