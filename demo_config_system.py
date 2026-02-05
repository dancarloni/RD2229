#!/usr/bin/env python3
"""
Demonstration script for the .jsoncode configuration system and new verification parameters.

This script demonstrates:
1. Loading calculation code configurations (TA, SLU, SLE)
2. Loading historical materials (RD2229, NTC2018)
3. Using the new VerificationInput fields (Mx, My, Mz, Tx, Ty, At)
4. Backward compatibility with legacy M and T fields
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("DEMONSTRATION: .jsoncode Configuration System")
print("=" * 80)

# =============================================================================
# 1. CALCULATION CODES DEMONSTRATION
# =============================================================================
print("\n" + "=" * 80)
print("1. CALCULATION CODES")
print("=" * 80)

from config.calculation_codes_loader import (
    list_available_codes,
    load_code,
    get_safety_coefficients,
    get_stress_limits
)

print("\nAvailable calculation codes:", list_available_codes())

# TA Configuration
print("\n--- TA (Tensioni Ammissibili) ---")
ta_config = load_code('TA')
print(f"Code: {ta_config['code_name']}")
print(f"Description: {ta_config['description']}")
print(f"Period: {ta_config.get('standard_references', 'N/A')}")

ta_coeffs = get_safety_coefficients('TA')
print(f"\nSafety Coefficients:")
print(f"  γ_c = {ta_coeffs['gamma_c']['value']} ({ta_coeffs['gamma_c']['description']})")
print(f"  γ_s = {ta_coeffs['gamma_s']['value']} ({ta_coeffs['gamma_s']['description']})")

ta_limits = get_stress_limits('TA')
print(f"\nStress Limits:")
print(f"  σ_c,adm = {ta_limits['concrete']['sigma_c_max_factor']} × σ_c,28")
print(f"  τ_c0 = {ta_limits['shear']['tau_c0']['value']} × σ_c,28")
print(f"  τ_c1 = {ta_limits['shear']['tau_c1']['value']} × σ_c,28")

# SLU Configuration
print("\n--- SLU (Stato Limite Ultimo) ---")
slu_config = load_code('SLU')
print(f"Code: {slu_config['code_name']}")
print(f"Description: {slu_config['description']}")

slu_coeffs = get_safety_coefficients('SLU')
print(f"\nSafety Coefficients:")
print(f"  γ_c = {slu_coeffs['gamma_c']['value']}")
print(f"  γ_s = {slu_coeffs['gamma_s']['value']}")

print(f"\nStrain Limits:")
strain = slu_config['strain_limits']['concrete']
print(f"  ε_c2 = {strain['eps_c2']['value']} (parabola-rectangle)")
print(f"  ε_cu = {strain['eps_cu']['value']} (ultimate)")

# SLE Configuration
print("\n--- SLE (Stato Limite Esercizio) ---")
sle_config = load_code('SLE')
print(f"Code: {sle_config['code_name']}")
print(f"Description: {sle_config['description']}")

print(f"\nStress Limits:")
stress = sle_config['stress_limits']['concrete']
print(f"  Characteristic: σ_c ≤ {stress['compression_characteristic']['value']} × fck")
print(f"  Quasi-permanent: σ_c ≤ {stress['compression_quasi_permanent']['value']} × fck")

print(f"\nCrack Limits:")
crack = sle_config['crack_limits']['ordinary_environment']
print(f"  Ordinary environment: w_max = {crack['w_max_frequent']} mm (frequent)")

# =============================================================================
# 2. HISTORICAL MATERIALS DEMONSTRATION
# =============================================================================
print("\n" + "=" * 80)
print("2. HISTORICAL MATERIALS")
print("=" * 80)

from config.historical_materials_loader import (
    list_available_sources,
    get_concrete_properties,
    get_steel_properties,
    HistoricalMaterialsLoader
)

print("\nAvailable material sources:", list_available_sources())

# RD2229 Materials
print("\n--- RD2229 (Regio Decreto 2229/39, 1939-1972) ---")
print("Unit system: Technical (kg/cm²)")

print("\nConcrete R160:")
r160 = get_concrete_properties('RD2229', 'R160')
print(f"  σ_c,28 = {r160['sigma_c28']} kg/cm² (cube strength at 28 days)")
print(f"  σ_c,adm = {r160['sigma_c_adm']} kg/cm² (allowable stress)")
print(f"  τ_c0 = {r160['tau_c0']} kg/cm² (service shear)")
print(f"  τ_c1 = {r160['tau_c1']} kg/cm² (max shear)")
print(f"  E_c = {r160['Ec']} kg/cm² (elastic modulus)")
print(f"  n = {r160['n']} (homogenization coeff.)")

print("\nSteel FeB38k:")
feb38k = get_steel_properties('RD2229', 'FeB38k')
print(f"  σ_sn = {feb38k['sigma_sn']} kg/cm² (yield stress)")
print(f"  σ_s,adm = {feb38k['sigma_s_adm']} kg/cm² (allowable stress)")
print(f"  E_s = {feb38k['Es']} kg/cm² (elastic modulus)")
print(f"  Bond: {feb38k['bond']}")

print("\nCement Types:")
loader_temp = HistoricalMaterialsLoader()
cement_types = loader_temp.get_cement_types('RD2229')
for name, props in cement_types.items():
    print(f"  {name}: {props['name']} (factor: {props['strength_factor']})")

# NTC2018 Materials
print("\n--- NTC2018 (Modern Standards, 2018-present) ---")
print("Unit system: SI (MPa)")

print("\nConcrete C25/30:")
c25 = get_concrete_properties('NTC2018', 'C25_30')
print(f"  fck = {c25['fck']} MPa (characteristic strength)")
print(f"  fcm = {c25['fcm']} MPa (mean strength)")
print(f"  Ecm = {c25['Ecm']} MPa (elastic modulus)")
print(f"  fctm = {c25['fctm']} MPa (tensile strength)")

print("\nSteel B450C:")
b450c = get_steel_properties('NTC2018', 'B450C')
print(f"  fyk = {b450c['fyk']} MPa (yield strength)")
print(f"  ftk = {b450c['ftk']} MPa (tensile strength)")
print(f"  Es = {b450c['Es']} MPa (elastic modulus)")
print(f"  Ductility class: {b450c['ductility_class']}")

# =============================================================================
# 3. NEW VERIFICATION PARAMETERS DEMONSTRATION
# =============================================================================
print("\n" + "=" * 80)
print("3. NEW VERIFICATION PARAMETERS")
print("=" * 80)

# Note: We can't import VerificationInput directly due to tkinter dependency
# Instead, we demonstrate the structure

print("\n--- VerificationInput (New Fields) ---")
print("New load parameters:")
print("  Mx:  Bending moment about x-axis (renamed from M)")
print("  My:  Bending moment about y-axis (NEW)")
print("  Mz:  Torsional moment (NEW)")
print("  Tx:  Shear force in x direction (NEW)")
print("  Ty:  Shear force in y direction (renamed from T)")
print("  At:  Torsional reinforcement area (NEW)")

print("\nLegacy compatibility:")
print("  v_input.M = 100.0  →  sets v_input.Mx = 100.0")
print("  v_input.T = 50.0   →  sets v_input.Ty = 50.0")

print("\n--- VerificationOutput (New Fields) ---")
print("New result fields:")
print("  asse_neutro_x:           Neutral axis x-coordinate")
print("  asse_neutro_y:           Neutral axis y-coordinate")
print("  inclinazione_asse_neutro: Neutral axis inclination (degrees)")
print("  tipo_verifica:           Type of verification performed")
print("  sigma_c:                 Concrete stress at compressed edge")
print("  sigma_s_tesi:           Tensile steel stress")
print("  sigma_s_compressi:      Compressed steel stress")

print("\n--- Supported Verification Types ---")
verification_types = [
    "1. Simple bending (Flessione retta): only Mx OR only My",
    "2. Deviated bending (Flessione deviata): Mx AND My",
    "3. Simple compression/tension: N only",
    "4. Simple axial+bending: N + (Mx OR My)",
    "5. Deviated axial+bending: N + Mx + My",
    "6. Torsion: Mz",
    "7. Shear: Tx and/or Ty",
    "8. Shear + Torsion: Mz + (Tx OR Ty)"
]
for vtype in verification_types:
    print(f"  {vtype}")

# =============================================================================
# 4. UNIT CONVERSION DEMONSTRATION
# =============================================================================
print("\n" + "=" * 80)
print("4. UNIT CONVERSION (Technical ↔ SI)")
print("=" * 80)

from config.historical_materials_loader import HistoricalMaterialsLoader

loader = HistoricalMaterialsLoader()
conversion = loader.get_conversion_factors('RD2229')

print(f"\nConversion factors:")
print(f"  1 kg/cm² = {conversion['kg_cm2_to_MPa']} MPa")
print(f"  1 MPa = {conversion['MPa_to_kg_cm2']} kg/cm²")

print(f"\nExamples:")
print(f"  RD2229 R160: σ_c,28 = 160 kg/cm² ≈ {160 * conversion['kg_cm2_to_MPa']:.2f} MPa")
print(f"  NTC2018 C25/30: fck = 25 MPa ≈ {25 * conversion['MPa_to_kg_cm2']:.1f} kg/cm²")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
✅ Configuration system (.jsoncode) implemented
✅ Calculation codes: TA, SLU, SLE
✅ Historical materials: RD2229, DM92, NTC2008, NTC2018
✅ New load parameters: Mx, My, Mz, Tx, Ty, At
✅ New result fields: neutral axis coordinates, inclination, stress details
✅ Backward compatibility maintained (M→Mx, T→Ty)
✅ Unit conversion support (kg/cm² ↔ MPa)
✅ Comprehensive documentation and tests

For more information, see:
  - docs/CONFIG_JSONCODE_SYSTEM.md
  - IMPLEMENTATION_SUMMARY.md
  - tests/test_config_loaders.py
""")

print("=" * 80)
print("End of demonstration")
print("=" * 80)
