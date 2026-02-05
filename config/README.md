# Configuration System README

## Quick Start

The `.jsoncode` configuration system provides modular access to calculation parameters and historical materials for structural verification.

### Installation

No installation needed - the configuration system is built-in. Configuration files are located in:
- `config/calculation_codes/` - Calculation method parameters (TA, SLU, SLE)
- `config/historical_materials/` - Material properties (RD2229, DM92, NTC2008, NTC2018)

### Basic Usage

```python
# Import loaders
from config.calculation_codes_loader import load_code, get_safety_coefficients
from config.historical_materials_loader import get_concrete_properties, get_steel_properties

# Load calculation code
ta_config = load_code('TA')
print(ta_config['description'])

# Get safety coefficients
coeffs = get_safety_coefficients('SLU')
gamma_c = coeffs['gamma_c']['value']  # 1.5

# Get historical material properties
r160 = get_concrete_properties('RD2229', 'R160')
print(f"R160 concrete: σ_c,28 = {r160['sigma_c28']} kg/cm²")

# Get modern material properties
c25 = get_concrete_properties('NTC2018', 'C25_30')
print(f"C25/30 concrete: fck = {c25['fck']} MPa")
```

### Available Configurations

**Calculation Codes:**
- `TA` - Tensioni Ammissibili (Allowable stress method, RD2229/DM92 compatible)
- `SLU` - Stato Limite Ultimo (Ultimate limit state, NTC2008/2018)
- `SLE` - Stato Limite Esercizio (Serviceability limit state, NTC2008/2018)

**Material Sources:**
- `RD2229` - Royal Decree 2229/39 (1939-1972) - Technical units (kg/cm²)
- `DM92` - DM 1992-1996 - SI units (MPa)
- `NTC2008` - NTC 2008 standards - SI units (MPa)
- `NTC2018` - NTC 2018 standards - SI units (MPa)

### Documentation

- **Full documentation:** `docs/CONFIG_JSONCODE_SYSTEM.md`
- **Implementation summary:** `IMPLEMENTATION_SUMMARY.md`
- **Demo script:** Run `python demo_config_system.py`
- **Tests:** Run tests in `tests/test_config_loaders.py`

### New Verification Parameters

The `VerificationInput` dataclass now supports:

| Parameter | Description | Units |
|-----------|-------------|-------|
| `N` | Axial force | kg or kN |
| `Mx` | Bending moment about x-axis | kg·cm or kN·m |
| `My` | Bending moment about y-axis (NEW) | kg·cm or kN·m |
| `Mz` | Torsional moment (NEW) | kg·cm or kN·m |
| `Tx` | Shear force in x direction (NEW) | kg or kN |
| `Ty` | Shear force in y direction | kg or kN |
| `At` | Torsional reinforcement area (NEW) | cm² |

**Legacy compatibility:** Properties `M` and `T` map to `Mx` and `Ty` respectively.

### Verification Types Supported

1. Simple bending (Flessione retta)
2. Deviated bending (Flessione deviata)
3. Simple compression/tension
4. Simple axial + bending
5. Deviated axial + bending
6. Torsion
7. Shear
8. Shear + Torsion

### Unit Conversion

```python
from config.historical_materials_loader import HistoricalMaterialsLoader

loader = HistoricalMaterialsLoader()
factors = loader.get_conversion_factors('RD2229')

# Convert kg/cm² to MPa
sigma_mpa = 160 * factors['kg_cm2_to_MPa']  # 15.69 MPa

# Convert MPa to kg/cm²
fck_kgcm2 = 25 * factors['MPa_to_kg_cm2']  # 254.9 kg/cm²
```

### Examples

See `demo_config_system.py` for complete working examples of:
- Loading all calculation codes
- Accessing safety coefficients and limits
- Working with historical materials (RD2229)
- Working with modern materials (NTC2018)
- Unit conversions
- New verification parameters

### Architecture

The system uses a two-level architecture:

1. **Configuration files (.jsoncode)** - JSON files with calculation parameters
   - Rigorously extracted from Visual Basic files
   - No simplifications or approximations
   - Organized by standard and material source

2. **Loader modules** - Python modules for accessing configurations
   - Automatic caching for performance
   - Type-safe access to parameters
   - Convenience functions for common queries

### Extending the System

To add a new standard or material source:

1. Create a new `.jsoncode` file in the appropriate directory
2. Follow the structure of existing files
3. Use the loaders to access the new configuration
4. No code changes required - the loaders discover files automatically

### Support

For questions or issues:
- Check the documentation in `docs/CONFIG_JSONCODE_SYSTEM.md`
- Review examples in `demo_config_system.py`
- Run the test suite in `tests/test_config_loaders.py`
- Refer to Visual Basic source files in `visual_basic/` for formula references
