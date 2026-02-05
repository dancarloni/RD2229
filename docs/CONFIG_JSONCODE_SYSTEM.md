# Sistema di Configurazione .jsoncode

## Panoramica

Il sistema `.jsoncode` fornisce una configurazione modulare e rigorosa per i parametri normativi e i materiali storici utilizzati nelle verifiche strutturali. Questo documento descrive la struttura, l'utilizzo e il mapping con i file Visual Basic originali.

## Struttura Directory

```
config/
├── calculation_codes/       # Configurazioni codici di calcolo
│   ├── TA.jsoncode         # Tensioni Ammissibili
│   ├── SLU.jsoncode        # Stato Limite Ultimo
│   └── SLE.jsoncode        # Stato Limite Esercizio
├── historical_materials/    # Configurazioni materiali storici
│   ├── RD2229.jsoncode     # Regio Decreto 2229/39 (1939-1972)
│   ├── DM92.jsoncode       # DM 1992-1996
│   ├── NTC2008.jsoncode    # NTC 2008
│   └── NTC2018.jsoncode    # NTC 2018
├── calculation_codes_loader.py      # Loader per codici di calcolo
└── historical_materials_loader.py   # Loader per materiali storici
```

## Codici di Calcolo (.jsoncode)

### TA.jsoncode - Tensioni Ammissibili

Configurazione per il metodo delle tensioni ammissibili, compatibile con:
- RD 2229/39
- DM 92/96
- Circolare LL.PP. 617/2009

**Struttura principale:**
```json
{
  "code_name": "TA",
  "description": "Tensioni Ammissibili - Metodo tradizionale italiano",
  "safety_coefficients": {
    "gamma_c": {"value": 1.0, "description": "..."},
    "gamma_s": {"value": 1.0, "description": "..."}
  },
  "stress_limits": {
    "concrete": {"sigma_c_max_factor": 0.5},
    "shear": {"tau_c0": {...}, "tau_c1": {...}}
  },
  "strain_limits": {...},
  "homogenization": {"n_default": 15.0},
  "verification_types": {...}
}
```

**Mapping con Visual Basic:**
- `PrincipCA_TA.bas` → sezioni `safety_coefficients`, `stress_limits`, `formulas`
- Variabili VB: `Gammac`, `Gammas`, `Sigca`, `TauC0`, `TauC1`, `n`

### SLU.jsoncode - Stato Limite Ultimo

Configurazione per SLU secondo NTC 2008/2018.

**Parametri chiave:**
- `gamma_c`: 1.5 (calcestruzzo)
- `gamma_s`: 1.15 (acciaio)
- `eps_c2`: 0.002 (deformazione max parabola-rettangolo)
- `eps_cu`: 0.0035 (deformazione ultima calcestruzzo)

**Mapping con Visual Basic:**
- `CA_SLU.bas` → sezioni `strain_limits`, `constitutive_models`, `confinement`
- Variabili VB: `Eps_c2`, `Eps_cu`, `Eps_su`, `fcd`, `fyd`

### SLE.jsoncode - Stato Limite Esercizio

Configurazione per verifiche SLE (tensioni, fessurazione, deformazioni).

**Parametri chiave:**
- Limiti tensioni: `0.6 × fck` (combinazione caratteristica)
- Limiti fessurazione: `w_max = 0.2-0.3 mm` (secondo ambiente)
- Coefficienti fessurazione NTC 2008: `k1`, `kt`, `beta1`, `beta2`

**Mapping con Visual Basic:**
- `CA_SLE.bas` → sezioni `stress_limits`, `crack_limits`, `cracking_coefficients`
- Variabili VB: `Perc_cls_c`, `Perc_cls_qp`, `k1`, `kt`, `Beta1`, `Beta2`

## Materiali Storici (.jsoncode)

### RD2229.jsoncode - Regio Decreto 2229/39

**Periodo:** 1939-1972  
**Unità:** Sistema tecnico (kg/cm²)

**Classi calcestruzzo:**
- R120: σ_c,28 = 120 kg/cm², σ_c,adm = 60 kg/cm²
- R160: σ_c,28 = 160 kg/cm², σ_c,adm = 80 kg/cm²
- R225: σ_c,28 = 225 kg/cm², σ_c,adm = 112.5 kg/cm²
- R300: σ_c,28 = 300 kg/cm², σ_c,adm = 150 kg/cm²

**Tipi acciaio:**
- Dolce, Semiduro, Duro (lisci)
- FeB32k, FeB38k, FeB44k (aderenza migliorata)
- AQ42, AQ50 (tipo Tor)

**Tipi cemento:**
- Normale (Portland)
- Presa lenta (pozzolanico)
- Alta resistenza
- Alluminoso (⚠️ degradazione nel tempo)

**Formule principali:**
```
σ_c,adm = 0.5 × σ_c,28
τ_c0 = 0.06 × σ_c,28  (taglio di servizio)
τ_c1 = 0.14 × σ_c,28  (taglio massimo)
E_c = 550000 × σ_c,28 / (σ_c,28 + 200)
n = E_s / E_c
```

### DM92.jsoncode - DM 09/01/1996

**Periodo:** 1992-2008  
**Unità:** Sistema SI (MPa)

Transizione dal sistema tecnico al SI. Classi calcestruzzo: C12/15, C16/20, C20/25, C25/30, C28/35, C30/37, C35/45, C40/50.

Acciai: FeB38k, FeB44k, Feb38ks, Feb44ks (saldabili).

### NTC2008.jsoncode e NTC2018.jsoncode

**Unità:** SI (MPa)

Classi calcestruzzo moderne: da C20/25 a C90/105.  
Acciai: B450C (duttile, classe C), B450A (normale, classe A - deprecato in zona sismica).

**Formule modulo elastico:**
```
E_cm = 22000 × (f_cm / 10)^0.3
```

## Utilizzo dei Loader

### Loader Codici di Calcolo

```python
from config.calculation_codes_loader import (
    load_code, 
    get_safety_coefficients,
    get_stress_limits,
    list_available_codes
)

# Elenco codici disponibili
codes = list_available_codes()  # ['SLE', 'SLU', 'TA']

# Carica configurazione completa
ta_config = load_code('TA')

# Ottieni coefficienti di sicurezza
coeffs = get_safety_coefficients('SLU')
gamma_c = coeffs['gamma_c']['value']  # 1.5
gamma_s = coeffs['gamma_s']['value']  # 1.15

# Ottieni limiti tensionali
limits = get_stress_limits('TA')
tau_c0 = limits['shear']['tau_c0']['value']  # 0.06
```

### Loader Materiali Storici

```python
from config.historical_materials_loader import (
    load_material_source,
    get_concrete_properties,
    get_steel_properties,
    list_available_sources
)

# Elenco sorgenti disponibili
sources = list_available_sources()  # ['DM92', 'NTC2008', 'NTC2018', 'RD2229']

# Ottieni proprietà calcestruzzo RD2229 R160
props = get_concrete_properties('RD2229', 'R160')
# {
#   'sigma_c28': 160,
#   'sigma_c_adm': 80,
#   'tau_c0': 9.6,
#   'tau_c1': 22.4,
#   'Ec': 250000,
#   'n': 8.4,
#   'unit': 'kg/cm²'
# }

# Ottieni proprietà acciaio RD2229 FeB38k
steel = get_steel_properties('RD2229', 'FeB38k')
# {
#   'sigma_sn': 3800,
#   'sigma_s_adm': 1900,
#   'Es': 2100000,
#   'bond': 'aderenza_migliorata',
#   'unit': 'kg/cm²'
# }

# Ottieni calcestruzzo moderno NTC2018 C25/30
modern = get_concrete_properties('NTC2018', 'C25_30')
# {
#   'fck': 25,
#   'fcm': 33,
#   'Ecm': 31000,
#   'fctm': 2.6,
#   ...
# }
```

## Aggiornamenti VerificationInput e VerificationOutput

### VerificationInput - Nuovi Campi Carichi

```python
from verification_table import VerificationInput

v_input = VerificationInput(
    N=1000.0,      # Sforzo normale (kg o kN)
    Mx=5000.0,     # Momento attorno asse x (kg·cm o kN·m)
    My=2000.0,     # Momento attorno asse y (kg·cm o kN·m)
    Mz=500.0,      # Momento torcente (kg·cm o kN·m)
    Tx=300.0,      # Taglio direzione x (kg o kN)
    Ty=400.0,      # Taglio direzione y (kg o kN)
    At=6.0         # Armatura a torsione (cm²)
)

# Compatibilità legacy
v_input.M = 5000.0  # Imposta Mx
v_input.T = 400.0   # Imposta Ty
```

### VerificationOutput - Nuovi Campi Risultati

```python
from verification_table import VerificationOutput

v_output = VerificationOutput(
    sigma_c_max=80.0,
    sigma_c_min=0.0,
    sigma_s_max=1600.0,
    asse_neutro=15.0,              # Legacy: distanza da lembo
    asse_neutro_x=0.0,             # Coordinata x (flessione deviata)
    asse_neutro_y=15.0,            # Coordinata y (flessione deviata)
    inclinazione_asse_neutro=0.0,  # Gradi (0° = orizzontale)
    tipo_verifica="Flessione retta",  # Tipo verifica eseguita
    sigma_c=75.0,                  # Tensione cls bordo compresso
    sigma_s_tesi=1500.0,          # Tensione armature tese
    sigma_s_compressi=100.0,      # Tensione armature compresse
    deformazioni="Regione 2a",
    coeff_sicurezza=1.2,
    esito="VERIFICATO",
    messaggi=["Verifica superata"]
)
```

## Tipi di Verifica Supportati

1. **Flessione retta** (solo Mx o solo My)
2. **Flessione deviata** (Mx e My ≠ 0)
3. **Compressione/Trazione semplice** (N ≠ 0, Mx = My = 0)
4. **Presso/Tensioflessione semplice** (N + Mx oppure N + My)
5. **Presso/Tensioflessione deviata** (N + Mx + My)
6. **Torsione** (Mz ≠ 0)
7. **Taglio** (Tx e/o Ty ≠ 0)
8. **Taglio + Torsione** (Mz + Tx/Ty)

## Conversioni Unità

**Sistema tecnico ↔ SI:**
```
1 kg/cm² = 0.0980665 MPa
1 MPa = 10.197 kg/cm²
```

Fattori disponibili in `RD2229.jsoncode` → `conversion_factors`.

## Estensioni Future

- Grafica dominio di resistenza N-M (matplotlib)
- Asse neutro inclinato per flessione deviata
- Zone tese/compresse su sezioni
- Integrazione metodo Santarella (abachi storici)
- FRP e rinforzi con materiali compositi

## Note Implementazione

- I file `.jsoncode` sono **rigorosamente derivati** dai file `.bas` Visual Basic senza semplificazioni
- La cache interna dei loader migliora le prestazioni
- I parametri sono organizzati per **gruppo omogeneo** (safety, stress, strain, etc.)
- Supporto completo per **normative storiche e moderne**
- **Backward compatibility** garantita tramite property legacy (`M` → `Mx`, `T` → `Ty`)

## Riferimenti

- `visual_basic/PrincipCA_TA.bas`: formule TA
- `visual_basic/CA_SLU.bas`: formule SLU
- `visual_basic/CA_SLE.bas`: formule SLE
- `visual_basic/Impostazioni.bas`: impostazioni generali
- `historical_materials.py`: materiali storici esistenti
- `material_sources.py`: sorgenti materiali
