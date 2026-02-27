# CLAUDE.md - AI Assistant Guide for RD2229

## Project Overview

RD2229 is a Python project for digitalizing and calculating historical structural engineering methods from **Regio Decreto 2229/1939** (Italian Royal Decree), along with classic references like Santarella and Giangreco. The project provides:

- A calculation engine for historical concrete/steel structural analysis
- GUI applications (Tkinter) for section geometry and materials management
- Tools for computing allowable stresses according to 1939-era Italian building codes

**Primary Language**: Italian (domain-specific terminology, comments, docstrings)

## Critical Conventions

### Units System - IMPORTANT
All stress and pressure values use **historical units: Kg/cm²** (kilograms per square centimeter), NOT modern SI units (MPa). This is intentional to match the historical documentation and formulas.

- 1 Kg/cm² = 0.0980665 MPa
- Conversion functions exist in `src/rd2229/tools/concrete_strength.py`
- Geometric dimensions (sections) use **cm** (centimeters)

### Greek Letters Convention
The project uses Unicode Greek letters (σ, τ, etc.) in docstrings and documentation. A pre-commit hook (`scripts/replace_sigma.py`) automatically replaces standalone "sigma" with "σ" in `.py`, `.md`, `.rst`, `.txt` files.

## Directory Structure

```
RD2229/
├── src/rd2229/           # Main source package
│   ├── core/             # Fundamental modules (materials, geometry, interpolation)
│   ├── core_models/      # Domain models (materials, loads)
│   ├── calculations/     # Structural calculations by element type
│   │   ├── travi/        # Beams (bending, shear, torsion)
│   │   ├── pilastri/     # Columns (compression, buckling)
│   │   ├── solette/      # Slabs
│   │   └── scale/        # Stairs
│   ├── sections_app/     # GUI application for section management
│   │   ├── models/       # Section dataclasses
│   │   ├── services/     # Calculations, repository
│   │   └── ui/           # Tkinter windows
│   ├── gui/              # Additional GUI components (materials_gui.py)
│   └── tools/            # Utility modules
│       ├── concrete_strength.py   # Allowable stress calculations
│       ├── materials_manager.py   # CRUD for materials.json
│       └── sync_verifications.py  # Structure synchronization
├── data/                 # JSON data files
│   ├── materials.json    # User-created materials (persisted)
│   └── tables.schema.json# Schema for historical coefficient tables
├── docs/                 # Documentation
├── tests/                # Pytest tests
├── scripts/              # CLI utilities and demos
└── logs/                 # Application logs
```

## Key Modules

### Core (`src/rd2229/core/`)

| File | Purpose |
|------|---------|
| `materials.py` | Base Material, Concrete, Steel dataclasses |
| `geometry.py` | Section geometry classes (Rectangular, Circular, T, L, I, Pi, Hollow) |
| `section_properties.py` | Property computation (area, inertia, centroid) |
| `interpolation.py` | Linear/bilinear interpolation for historical tables |
| `reinforcement.py` | Reinforcement bar configuration |

### Tools (`src/rd2229/tools/`)

| File | Purpose |
|------|---------|
| `concrete_strength.py` | Historical allowable stress rules: σ_c from σ_c28, shear limits, E_c, G_c |
| `materials_manager.py` | CRUD API for `data/materials.json` with auto-computed derived fields |

### Sections App (`src/rd2229/sections_app/`)
A complete Tkinter GUI for managing cross-sections:
- `models/sections.py`: Section classes (RectangularSection, CircularSection, TSection)
- `services/repository.py`: CSV-based persistence
- `services/calculations.py`: Canvas transform utilities
- `ui/main_window.py`: Main GUI with dynamic field generation

### GUI (`src/rd2229/gui/`)
- `materials_gui.py`: Tkinter GUI for materials CRUD with preview of calculated values

## Configuration

### `.rd2229_config.yaml`
Project configuration file:
```yaml
calculations_path: src/rd2229/calculations
verifications_path: src/rd2229/verifications
sync_rule: "mirror"  # Each calculation module should have a verification counterpart
materials_file: data/materials.json
modules:
  - travi
  - pilastri
  - solette
  - solai
  - fondazioni
  - scale
  - muri
```

**Sync Rule**: When adding a new module under `calculations/`, create a corresponding placeholder in `verifications/`.

### Pre-commit Hooks (`.pre-commit-config.yaml`)
- `replace-sigma`: Replaces standalone "sigma" with "σ" in documentation

## Running the Project

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt  # pandas, matplotlib
```

### Run Tests
```bash
pytest tests/
```

### Run GUIs
```bash
# Materials GUI
PYTHONPATH=src python scripts/run_materials_gui.py

# Sections GUI (if available)
PYTHONPATH=src python -m rd2229
```

## Code Patterns

### Section Classes
All section types inherit from `Section` base class and implement:
- `_compute() -> SectionProperties`: Calculate geometric properties
- `_fill_dimension_fields(data: Dict)`: Serialize dimensions to dict
- `_dimension_key() -> Tuple`: Unique key for duplicate detection
- `to_dict() -> Dict`: Full serialization for CSV

### Material Management
Materials are stored in `data/materials.json` with derived fields auto-calculated:
```python
{
    "name": "CA-01",
    "type": "concrete",
    "cement_type": "normal",  # normal, high, aluminous, slow
    "sigma_c28": 225.0,       # Characteristic strength at 28 days (Kg/cm²)
    "sigma_c": 60,            # Allowable stress (Kg/cm²) - auto-calculated
    "sigma_c_simple": 60,     # For simply compressed sections
    "sigma_c_inflessa": 75,   # For bent/press-bent sections
    "tau_service": 4.0,       # Service shear (Kg/cm²)
    "tau_max": 14.0,          # Max shear (Kg/cm²)
    "E": 126923.1,            # Elastic modulus (Kg/cm²)
    "E_calculated": 291176,   # Formula-derived E_c
    "E_conventional": 250000, # Historical conventional value
    "G": 127390,              # Shear modulus G_c (Kg/cm²)
}
```

### Historical Stress Formulas
Key functions in `concrete_strength.py`:
- `compute_allowable_compressive_stress()`: σ_c from σ_c28 using historical rules
- `compute_allowable_shear()`: Returns (τ_service, τ_max) based on cement type
- `compute_ec()`: E_c = 550000 * σ_c28 / (σ_c28 + 200)
- `compute_gc()`: G_c ≈ 0.43-0.445 * E_c

### Dynamic GUI Fields
Section type selection dynamically rebuilds input fields using `SECTION_DEFINITIONS` dict in `main_window.py`. Each entry defines:
- `class`: The section model class
- `fields`: List of (field_name, label) tuples
- `tooltip`: Section description
- `field_tooltips`: Per-field help text

## Development Guidelines

### Adding New Section Types
1. Create dataclass in `src/rd2229/sections_app/models/sections.py`
2. Implement `_compute()`, `_fill_dimension_fields()`, `_dimension_key()`
3. Add to `SECTION_CLASS_MAP` and `SECTION_DEFINITIONS` in UI
4. Optionally add drawing method in `_draw_section()`

### Adding New Calculation Modules
1. Create package under `src/rd2229/calculations/<element_type>/`
2. Create corresponding package under `src/rd2229/verifications/<element_type>/`
3. Document formulas and normative references in docstrings
4. Return intermediate calculation steps for GUI display

### Testing
- Use pytest for all tests
- Test files: `tests/test_*.py`
- Include property computation validation against known values

## Important Notes for AI Assistants

1. **Preserve Italian terminology** - Domain terms (travi, pilastri, solette, etc.) should remain in Italian
2. **Use Kg/cm² units** - Never convert to MPa unless explicitly requested
3. **Follow sync rule** - Keep calculations/ and verifications/ structure mirrored
4. **Derived fields are auto-calculated** - Don't manually set σ_c, τ values when σ_c28 is provided
5. **Pre-commit hooks active** - "sigma" → "σ" replacement happens automatically
6. **GUI is Tkinter-based** - Keep UI code simple, avoid complex frameworks
7. **Historical accuracy matters** - Formulas must match RD 2229/1939 specifications
8. **Logging** - GUI operations are logged to `logs/gui_operations.log`

## Quantities Registry
A CSV-based registry (`src/quantities_registry.csv`) tracks physical quantities with their symbols and units, managed via `src/quantities_registry.py` using pandas.

## External Dependencies
- `pandas` - Data manipulation (quantities registry)
- `matplotlib` - Plotting (future use)
- Optional: `PyYAML` - Config file parsing
