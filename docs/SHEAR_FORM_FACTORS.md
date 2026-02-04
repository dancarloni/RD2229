Shear Form Factors (κ) used in RD2229
======================================

Overview
--------
This document summarizes the shear form factor (Timoshenko shear correction) defaults used in the "Gestione Proprietà Sezioni" module and documents the assumptions for the reference areas (A_ref_y, A_ref_z).

Definitions
-----------
- Timoshenko shear deformation is characterized by:
    γ_y = V_y / (G * A_y)
    γ_z = V_z / (G * A_z)
  where A_y and A_z are the effective shear areas in the local axes.
- Effective shear areas are computed as:
    A_y = κ_y * A_ref_y
    A_z = κ_z * A_ref_z

Default κ values and assumptions
--------------------------------
The application uses a centralized table of default κ values (approximate, literature-based):

- RECTANGULAR (b × h): κ_y = κ_z = 5/6 ≈ 0.8333
  - A_ref_y = A_ref_z = gross area (A = b*h)

- CIRCULAR (solid): κ_y = κ_z = 10/9 ≈ 1.1111
  - A_ref_y = A_ref_z = gross area (π r²)

- CIRCULAR_HOLLOW: κ_y = κ_z = 1.0 (approximation)
  - A_ref: gross cross-sectional area (A_outer - A_inner)

- RECTANGULAR_HOLLOW: κ_y = κ_z ≈ 5/6 (approximation)

- T_SECTION / I_SECTION / INVERTED_T_SECTION / C_SECTION:
  - κ_y ≈ 1.0, κ_z ≈ 0.9 (engineering approximation)
  - A_ref_y is taken as the web area (web_thickness × web_height) when web geometry is available.
  - A_ref_z is typically the gross area.

Notes on persistence and CSV compatibility
-----------------------------------------
- The application persists both κ (as `kappa_y` and `kappa_z`) and the computed effective areas `A_y` and `A_z` alongside other properties in the sections archive (CSV/JSON).
- When importing CSVs that include `A_y`/`A_z` but not κ, the importer derives κ = A_y / area to preserve the effective area on round-trip export.
- When importing older CSVs without `A_y`/`A_z` or κ, the application computes A_y/A_z from defaults.

References / Sources
--------------------
- Classical shear correction factors and Timoshenko beam theory (standard engineering texts):
  - Timoshenko & Gere, Theory of Elastic Stability (and other texts on Timoshenko beam theory)
  - Roark's Formulas for Stress and Strain (tables of correction factors for common shapes)
  - Practical engineering tables and course material describing shear correction factors for standard cross-sections

These defaults are practical approximations intended to be reasonable for design-level estimates. Users are encouraged to override κ values in the UI when more precise or literature-specific values are required.
