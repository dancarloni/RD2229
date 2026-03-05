#!/usr/bin/env python3
"""Demo script for the verification calculation engine.

This demonstrates the new calculation core integrated with the .jsoncode configuration system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.verification_core import LoadCase, ReinforcementLayer, SectionGeometry  # noqa: E402
from core.verification_engine import create_verification_engine  # noqa: E402

print("=" * 80)
print("VERIFICATION ENGINE DEMONSTRATION")
print("=" * 80)

# =============================================================================
# EXAMPLE 1: Simple Bending Verification (TA Method)
# =============================================================================
print("\n" + "=" * 80)
print("EXAMPLE 1: Simple Bending - TA Method (RD2229)")
print("=" * 80)

# Create verification engine for TA
engine_ta = create_verification_engine("TA")

# Define section geometry (rectangular beam)
section = SectionGeometry(width=30.0, height=50.0)  # 30x50 cm
print(f"\nSection: {section.width} × {section.height} cm")
print(f"Area: {section.area():.2f} cm²")
print(f"Inertia Iy: {section.inertia_y():.0f} cm⁴")

# Define reinforcement
rebar_bottom = ReinforcementLayer(area=12.0, distance=45.0)  # 4φ20 @ d=45cm
rebar_top = ReinforcementLayer(area=4.0, distance=5.0)  # 2φ16 @ d'=5cm
print(f"\nTensile reinforcement: As = {rebar_bottom.area} cm² @ d = {rebar_bottom.distance} cm")
print(f"Compressed reinforcement: As' = {rebar_top.area} cm² @ d' = {rebar_top.distance} cm")

# Get material properties from .jsoncode
material = engine_ta.get_material_properties(
    concrete_class="R160", steel_type="FeB38k", material_source="RD2229"
)
print("\nMaterials (RD2229):")
print(f"  Concrete R160: σ_c,28 = {material.fck} kg/cm², E_c = {material.Ec:.0f} kg/cm²")
print(f"  Steel FeB38k: σ_sn = {material.fyk} kg/cm², E_s = {material.Es:.0f} kg/cm²")
print(f"  Homogenization: n = {material.n:.2f}")

# Define loads (simple bending)
loads = LoadCase(Mx=10000000.0)  # 10000 kg·m = 10^7 kg·cm
print("\nLoads:")
print(f"  Mx = {loads.Mx / 100000:.2f} kg·m")

# Get allowable stresses
sigma_c_adm, sigma_s_adm = engine_ta.get_allowable_stresses(material)
print("\nAllowable stresses (TA):")
print(f"  σ_c,adm = {sigma_c_adm:.1f} kg/cm² (0.5 × σ_c,28)")
print(f"  σ_s,adm = {sigma_s_adm:.1f} kg/cm² (σ_sn / 2)")

# Perform verification
result = engine_ta.perform_verification(
    section=section,
    reinforcement_tensile=rebar_bottom,
    reinforcement_compressed=rebar_top,
    material=material,
    loads=loads,
)

# Display results
print("\n" + "-" * 80)
print("RESULTS")
print("-" * 80)
print(f"Verification type: {result.verification_type.value}")
print("\nNeutral axis:")
print(f"  Distance from top: x = {result.neutral_axis.x:.2f} cm")
print(f"  Depth ratio: x/h = {result.neutral_axis.depth_ratio(section.height):.3f}")

print("\nStresses:")
print(f"  Concrete (compressed): σ_c = {result.stress_state.sigma_c_max:.1f} kg/cm²")
print(f"  Steel (tensile): σ_s = {result.stress_state.sigma_s_tensile:.1f} kg/cm²")
print(f"  Steel (compressed): σ_s' = {result.stress_state.sigma_s_compressed:.1f} kg/cm²")

print("\nUtilization:")
print(f"  Concrete: {result.utilization_concrete:.1%} (σ_c / σ_c,adm)")
print(f"  Steel: {result.utilization_steel:.1%} (σ_s / σ_s,adm)")

print(f"\nVerification: {'✓ PASSED' if result.is_verified else '✗ FAILED'}")
for msg in result.messages:
    print(f"  • {msg}")

# =============================================================================
# EXAMPLE 2: Modern NTC2018 with SLU Method
# =============================================================================
print("\n" + "=" * 80)
print("EXAMPLE 2: Simple Bending - SLU Method (NTC2018)")
print("=" * 80)

# Create verification engine for SLU
engine_slu = create_verification_engine("SLU")

# Get modern material properties
material_ntc = engine_slu.get_material_properties(
    concrete_class="C25_30", steel_type="B450C", material_source="NTC2018"
)
print("\nMaterials (NTC2018):")
print(f"  Concrete C25/30: fck = {material_ntc.fck} MPa, Ecm = {material_ntc.Ec:.0f} MPa")
print(f"  Steel B450C: fyk = {material_ntc.fyk} MPa, Es = {material_ntc.Es:.0f} MPa")

# Same section and loads (in SI units)
loads_si = LoadCase(Mx=100.0)  # 100 kN·m
print("\nLoads:")
print(f"  Mx = {loads_si.Mx} kN·m")

# Get allowable stresses for SLU
sigma_c_adm_slu, sigma_s_adm_slu = engine_slu.get_allowable_stresses(material_ntc)
print("\nDesign strengths (SLU):")
print(f"  fcd = {sigma_c_adm_slu:.2f} MPa (0.85 × fck / γ_c)")
print(f"  fyd = {sigma_s_adm_slu:.2f} MPa (fyk / γ_s)")

# Perform verification
result_slu = engine_slu.perform_verification(
    section=section,
    reinforcement_tensile=rebar_bottom,
    reinforcement_compressed=rebar_top,
    material=material_ntc,
    loads=loads_si,
)

print(f"\nVerification type: {result_slu.verification_type.value}")
print(f"Status: {'✓ PASSED' if result_slu.is_verified else '✗ FAILED'}")

# =============================================================================
# EXAMPLE 3: Multi-Axis Loading
# =============================================================================
print("\n" + "=" * 80)
print("EXAMPLE 3: Multi-Axis Loading (Deviated Bending)")
print("=" * 80)

# Define multi-axis loads
loads_multiaxis = LoadCase(
    N=500000.0,  # 500 kN axial compression
    Mx=8000000.0,  # 80 kN·m bending about x
    My=4000000.0,  # 40 kN·m bending about y
    Mz=1000000.0,  # 10 kN·m torsion
    Tx=50000.0,  # 50 kN shear in x
    Ty=30000.0,  # 30 kN shear in y
)

verif_type = loads_multiaxis.get_verification_type()
print("\nLoads:")
print(f"  N  = {loads_multiaxis.N / 1000:.1f} kN")
print(f"  Mx = {loads_multiaxis.Mx / 100000:.1f} kN·m")
print(f"  My = {loads_multiaxis.My / 100000:.1f} kN·m")
print(f"  Mz = {loads_multiaxis.Mz / 100000:.1f} kN·m")
print(f"  Tx = {loads_multiaxis.Tx / 1000:.1f} kN")
print(f"  Ty = {loads_multiaxis.Ty / 1000:.1f} kN")

print(f"\nDetected verification type: {verif_type.value}")
print("  (Implementation in progress - full calculation coming soon)")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
✅ Verification Engine Implemented
  • TA, SLU, SLE calculation methods
  • Integration with .jsoncode configuration system
  • Material properties from RD2229, NTC2008, NTC2018
  • Support for multi-axis loading (Mx, My, Mz, Tx, Ty, At)

✅ Current Capabilities
  • Simple bending verification (TA method)
  • Neutral axis calculation
  • Stress calculation (homogenized section)
  • Allowable stress verification
  • Load case classification

🔨 In Progress
  • Deviated bending (Mx + My)
  • Axial + bending combined
  • Shear verification (Tx, Ty)
  • Torsion verification (Mz)
  • SLU and SLE full implementations

📚 Next Steps
  • Complete .bas formulas extraction for all cases
  • Integration with verification_table.py
  • Graphical results (neutral axis visualization)
  • Text export functionality
""")

print("=" * 80)
print("Run 'python demo_config_system.py' for .jsoncode system demonstration")
print("=" * 80)
