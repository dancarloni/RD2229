# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-02-08 - Complete Architecture Restructuring

### Added - New Modular Architecture

- **Created `/src/` package structure** with complete modular organization
- **Created `/src/legacy/`** directory containing all original project files preserved unchanged
- **Created modular packages:**
  - `src/calc/` - Calculation logic for shear areas and section registry
  - `src/materials/` - Material models, validation, and repository
  - `src/elements/` - Structural element models and input resolution
  - `src/codes/` - Normative code registry with params and clauses
  - `src/actions/` - Verification action repository
  - `src/report/` - Report renderers (MD, HTML, PDF stub) and templates
  - `src/config/` - YAML configuration files (units, numerics, app, features)
  - `src/tools/` - CLI tools and export utilities
  - `src/tests/` - Test suite for all new modules

### Added - Core Modules (STUB S2 Implementation)

- **Shear Area Registry** (`src/calc/shear_area_registry.py`)
  - Registry system for shear area calculations (A_sx, A_sy)
  - Support for section-specific strategies
  - Universal fallback based on Timoshenko kappa
- **Section Registry** (`src/calc/section_registry.py`)
  - Centralized section metadata management
- **Material System** (`src/materials/`)
  - Material model with dataclass structure
  - Validation system for material properties
  - Material repository with legacy JSON loading support
- **Element System** (`src/elements/`)
  - Element model with geometry and material integration
  - Element repository with section assignment
  - Input resolution system for verification pipeline
- **Code Registry** (`src/codes/`)
  - Normative parameter system (NTC2018, EC2 examples)
  - Clause management via YAML files
  - Bootstrap system for automatic code loading
- **Verification Actions** (`src/actions/action_repo.py`)
  - Base verification action interface
  - Example flexure and shear check stubs
- **Report System** (`src/report/`)
  - Markdown renderer with template support
  - HTML renderer with template support
  - PDF renderer stub (placeholder for future implementation)
  - Template files for both formats

### Added - Configuration System

- `src/config/units.yml` - Unit system configuration (cm, cm², kg/cm², etc.)
- `src/config/numerics.yml` - Numerical precision and tolerances
- `src/config/app.yml` - Application settings and defaults
- `src/config/features.yml` - Feature flags for incremental development

### Added - Tools and CLI

- `src/tools/verify_cli.py` - Command-line interface for running verifications
- `src/tools/export_results.py` - Export utilities for JSON/CSV formats

### Added - Test Suite

- `test_shear_area.py` - Tests for shear area calculation registry
- `test_code_routing.py` - Tests for normative code registry
- `test_resolve_inputs.py` - Tests for input resolution system
- `test_reporting.py` - Tests for report renderers
- `test_material_repo.py` - Tests for material repository
- `test_elements_repo.py` - Tests for element repository

### Documentation

- All modules created as **STUB S2** with:
  - Extensive docstrings (Italian language, matching project standards)
  - Clear TODO markers for Copilot Plan expansion
  - Complete type hints
  - Example usage patterns
  - Integration points clearly defined

### Migration Notes

- **All original files preserved** in `src/legacy/` without modification
- **No breaking changes** to existing functionality
- **Backward compatibility** maintained through legacy imports
- **Incremental adoption** - new modules can be progressively implemented

### Technical Details

- **Unit System:** All calculations use cm (length), cm² (area), cm⁴ (inertia), kg/cm² (stress), kg/m³ (density)
- **No implicit conversions:** Unit consistency enforced throughout
- **Modular design:** Each package has single responsibility
- **Test-driven:** All new modules have corresponding test files
- **Configuration-driven:** YAML configs for all system parameters

## Unreleased

- Quality & architecture overhaul: refactor into `src/` layout, add typing, tests, docs, and CI improvements.
