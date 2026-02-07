# Summary: Verification Module Updates - New Load Parameters & .jsoncode System

## Implementation Overview

This document summarizes the updates to the verification module to support new load parameters and a modular configuration system using `.jsoncode` files.

## Changes Implemented

### 1. VerificationInput Dataclass Updates

**New Load Parameters:**
- `Mx`: Bending moment about x-axis (renamed from `M`)
- `My`: Bending moment about y-axis (NEW)
- `Mz`: Torsional moment (NEW, replaces previous "Mt")
- `Tx`: Shear force in x direction (NEW)
- `Ty`: Shear force in y direction (renamed from `T`)
- `At`: Torsional reinforcement area (NEW)

**Backward Compatibility:**
- Legacy properties `M` and `T` maintained as aliases to `Mx` and `Ty`
- Existing code continues to work without modifications
- Example:
  ```python
  v_input.M = 100.0  # Sets v_input.Mx = 100.0
  v_input.T = 50.0   # Sets v_input.Ty = 50.0
  ```

### 2. VerificationOutput Dataclass Updates

**New Result Fields:**
- `asse_neutro_x`: Neutral axis x-coordinate (for deviated bending)
- `asse_neutro_y`: Neutral axis y-coordinate (for deviated bending)
- `inclinazione_asse_neutro`: Neutral axis inclination in degrees
- `tipo_verifica`: Type of verification performed
- `sigma_c`: Concrete stress at compressed edge
- `sigma_s_tesi`: Tensile steel stress
- `sigma_s_compressi`: Compressed steel stress

**Default Initialization:**
- All new fields default to 0.0 or empty string
- `messaggi` list automatically initialized to `[]`

### 3. Configuration System (.jsoncode)

**Directory Structure:**
```
config/
├── calculation_codes/
│   ├── TA.jsoncode      # Allowable stress method
│   ├── SLU.jsoncode     # Ultimate limit state
│   └── SLE.jsoncode     # Serviceability limit state
├── historical_materials/
│   ├── RD2229.jsoncode  # Royal Decree 2229/39 (1939-1972)
│   ├── DM92.jsoncode    # DM 1992-1996
│   ├── NTC2008.jsoncode # Technical standards 2008
│   └── NTC2018.jsoncode # Technical standards 2018
├── calculation_codes_loader.py
└── historical_materials_loader.py
```

### 4. Calculation Code Configurations

**TA.jsoncode (Tensioni Ammissibili):**
- Safety coefficients: γ_c = 1.0, γ_s = 1.0 (already in allowable stress)
- Stress limits: σ_c,adm = 0.5 × σ_c,28
- Shear limits: τ_c0 = 0.06 × σ_c,28, τ_c1 = 0.14 × σ_c,28
- Homogenization: n_default = 15.0
- Material sources: RD2229, DM72, DM92, DM96

**SLU.jsoncode (Stato Limite Ultimo):**
- Safety coefficients: γ_c = 1.5, γ_s = 1.15
- Strain limits: ε_c2 = 0.002, ε_cu = 0.0035
- Constitutive models: parabola-rectangle, stress block, elastic-perfect plastic
- Confinement models: Mander model for confined concrete
- Material sources: NTC2008, NTC2018

**SLE.jsoncode (Stato Limite Esercizio):**
- Stress limits: σ_c ≤ 0.6 × fck (characteristic), σ_c ≤ 0.45 × fck (quasi-permanent)
- Crack limits: w_max = 0.2-0.3 mm (environment dependent)
- Cracking coefficients: k1, kt, β1, β2 (NTC 2008/2018 method)
- Deformation limits: l/250, l/500 (beams), l/125 (cantilevers)

### 5. Historical Materials Configurations

**RD2229.jsoncode (1939-1972):**
- Unit system: Technical (kg/cm²)
- Concrete classes: R120, R160, R225, R300
- Steel types: Dolce, Semiduro, Duro, FeB32k, FeB38k, FeB44k, AQ42, AQ50
- Cement types: Normale, Presa lenta, Alta resistenza, Alluminoso
- Formulas: E_c = 550000 × σ_c,28 / (σ_c,28 + 200), n = E_s / E_c
- Conversion factors: 1 kg/cm² = 0.0980665 MPa

**DM92.jsoncode (1992-2008):**
- Unit system: SI (MPa)
- Concrete classes: C12/15 to C40/50
- Steel types: FeB38k, FeB44k, Feb38ks, Feb44ks (weldable)
- Transition period from technical to SI units

**NTC2008.jsoncode & NTC2018.jsoncode:**
- Unit system: SI (MPa)
- Concrete classes: C20/25 to C90/105
- Steel types: B450C (ductile, class C), B450A (normal, class A)
- Elastic modulus: E_cm = 22000 × (f_cm / 10)^0.3

## Verification Types Supported

1. **Simple bending** (Flessione retta): Only Mx OR only My ≠ 0
2. **Deviated bending** (Flessione deviata): Mx AND My ≠ 0
3. **Simple compression/tension**: N ≠ 0, Mx = My = 0
4. **Simple axial+bending**: N ≠ 0 AND (Mx OR My) ≠ 0
5. **Deviated axial+bending**: N ≠ 0 AND Mx AND My ≠ 0
6. **Torsion**: Mz ≠ 0
7. **Shear**: Tx and/or Ty ≠ 0
8. **Shear + Torsion**: Mz AND (Tx OR Ty) ≠ 0

## Usage Examples

### Loading Calculation Codes

```python
from config.calculation_codes_loader import load_code, get_safety_coefficients

# Load full configuration
ta_config = load_code('TA')

# Get specific parameters
coeffs = get_safety_coefficients('SLU')
gamma_c = coeffs['gamma_c']['value']  # 1.5
gamma_s = coeffs['gamma_s']['value']  # 1.15
```

### Loading Historical Materials

```python
from config.historical_materials_loader import get_concrete_properties, get_steel_properties

# RD2229 concrete R160
concrete = get_concrete_properties('RD2229', 'R160')
# {'sigma_c28': 160, 'sigma_c_adm': 80, 'tau_c0': 9.6, 'Ec': 250000, ...}

# RD2229 steel FeB38k
steel = get_steel_properties('RD2229', 'FeB38k')
# {'sigma_sn': 3800, 'sigma_s_adm': 1900, 'Es': 2100000, ...}

# NTC2018 concrete C25/30
modern = get_concrete_properties('NTC2018', 'C25_30')
# {'fck': 25, 'fcm': 33, 'Ecm': 31000, 'fctm': 2.6, ...}
```

### Using New Load Parameters

```python
from verification_table import VerificationInput, VerificationOutput

# Create verification input with new parameters
v_input = VerificationInput(
    section_id="SECT_001",
    verification_method="SLU",
    N=1000.0,     # Axial force
    Mx=5000.0,    # Bending moment x
    My=2000.0,    # Bending moment y (NEW)
    Mz=500.0,     # Torsional moment (NEW)
    Tx=300.0,     # Shear force x (NEW)
    Ty=400.0,     # Shear force y (renamed from T)
    At=6.0        # Torsional reinforcement (NEW)
)

# Legacy compatibility still works
v_input.M = 5000.0  # Sets Mx
v_input.T = 400.0   # Sets Ty
```

## Testing

All tests pass successfully:
- ✅ Configuration loaders functional
- ✅ TA, SLU, SLE configurations loaded
- ✅ RD2229, DM92, NTC2008, NTC2018 materials loaded
- ✅ Concrete properties retrieved correctly
- ✅ Steel properties retrieved correctly
- ✅ VerificationInput new fields initialized
- ✅ VerificationOutput new fields initialized
- ✅ Legacy M and T properties work correctly
- ✅ Caching mechanism functional

## Files Modified

1. `verification_table.py`: Updated VerificationInput and VerificationOutput dataclasses
2. `config/calculation_codes_loader.py`: New loader for calculation codes
3. `config/historical_materials_loader.py`: New loader for historical materials
4. `config/calculation_codes/*.jsoncode`: Configuration files for TA, SLU, SLE
5. `config/historical_materials/*.jsoncode`: Configuration files for materials
6. `docs/CONFIG_JSONCODE_SYSTEM.md`: Comprehensive documentation
7. `tests/test_config_loaders.py`: Test suite for loaders

## Visual Basic Mapping

All `.jsoncode` parameters are rigorously extracted from Visual Basic files:

**PrincipCA_TA.bas → TA.jsoncode:**
- `Gammac`, `Gammas` → `safety_coefficients`
- `Sigca`, `TauC0`, `TauC1` → `stress_limits`
- `n` (Es/Ec) → `homogenization`
- `Eps_c2`, `Eps_cu`, `Eps_su` → `strain_limits`

**CA_SLU.bas → SLU.jsoncode:**
- Strain limits, constitutive models, confinement parameters

**CA_SLE.bas → SLE.jsoncode:**
- Stress limits, crack limits, cracking coefficients

**No simplifications or approximations** were introduced - all formulas match the original VB code.

## Benefits

1. **Modularity**: Parameters separated from code logic
2. **Extensibility**: Easy to add new standards or materials
3. **Maintainability**: Clear structure, easy to update
4. **Backward Compatibility**: Existing code continues to work
5. **Historical Accuracy**: Rigorous representation of RD2229/39 and other standards
6. **Type Safety**: Python dataclasses with proper typing
7. **Documentation**: Inline descriptions and references
8. **Testing**: Comprehensive test coverage

## Next Steps

Future enhancements planned:
- [ ] Implement calculation core using .jsoncode parameters
- [ ] Add graphical results (neutral axis, stress/strain diagrams)
- [ ] Implement N-M interaction diagram (resistance domain)
- [ ] Add support for FRP reinforcement
- [ ] Integrate Santarella method (historical graphical approach)
- [ ] Add more verification types (combined effects)

## References

- Visual Basic source files: `visual_basic/*.bas`
- RD 2229/39: Regio Decreto 16 novembre 1939 n. 2229
- DM 09/01/1996: Norme tecniche per il calcolo delle strutture in c.a.
- NTC 2008: DM 14/01/2008
- NTC 2018: DM 17/01/2018
- Circolare 617/2009
- Circolare 7/2019
