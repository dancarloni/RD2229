"""Adapter tra src.materials.Material e src.core_calculus.core.materials.

Converte tra i due modelli mantenendo coerenza di unità:
- src.materials → kg/cm² (sistema interno storico)
- src.core_calculus → MPa (sistema SI moderno)

Fattore conversione: 1 kg/cm² = 0.0980665 MPa
"""

from __future__ import annotations

from src.core_calculus.core.materials import (
    Concrete as CoreConcrete,
)
from src.core_calculus.core.materials import (
    Material as CoreMaterial,
)
from src.core_calculus.core.materials import (
    Steel as CoreSteel,
)
from src.materials.material_model import Material

_KG_CM2_TO_MPA = 0.0980665
_MPA_TO_KG_CM2 = 1.0 / _KG_CM2_TO_MPA


def material_to_core(mat: Material) -> CoreMaterial:
    """Converte src.materials.Material → src.core_calculus.core.materials.

    I valori vengono convertiti da kg/cm² a MPa.

    Args:
        mat: Materiale in formato src.materials (kg/cm²).

    Returns:
        CoreMaterial (Concrete o Steel) in MPa.
    """
    if mat.famiglia == "calcestruzzo":
        f_ck_mpa = mat.f_ck * _KG_CM2_TO_MPA if mat.f_ck > 0 else 25.0
        return CoreConcrete(
            name=mat.material_id,
            f_ck=f_ck_mpa,
            f_ck_cube=f_ck_mpa / 0.83,  # f_ck_cube ≈ f_ck / 0.83
            gamma_c=mat.gamma_c,
            alpha_cc=mat.alpha_cc,
            density=mat.densita_kg_m3,
            E=mat.E * _KG_CM2_TO_MPA if mat.E > 0 else 0.0,
            nu=mat.nu,
        )

    if mat.famiglia == "acciaio":
        f_yk_mpa = mat.f_yk * _KG_CM2_TO_MPA if mat.f_yk > 0 else 450.0
        return CoreSteel(
            name=mat.material_id,
            f_yk=f_yk_mpa,
            f_tk=f_yk_mpa * 1.15,
            gamma_s=mat.gamma_s,
            density=mat.densita_kg_m3,
            E=mat.E * _KG_CM2_TO_MPA if mat.E > 0 else 200000.0,
            nu=mat.nu,
        )

    # Generico (muratura, legno, ecc.)
    return CoreMaterial(
        name=mat.material_id,
        material_type=mat.famiglia,
        E=mat.E * _KG_CM2_TO_MPA if mat.E > 0 else 0.0,
        nu=mat.nu,
        density=mat.densita_kg_m3,
    )


def core_to_material(core: CoreMaterial) -> Material:
    """Converte src.core_calculus.core.materials → src.materials.Material.

    I valori vengono convertiti da MPa a kg/cm².

    Args:
        core: Materiale in formato core_calculus (MPa).

    Returns:
        Material in kg/cm².
    """
    if isinstance(core, CoreConcrete):
        return Material(
            material_id=core.name,
            descrizione=f"Calcestruzzo {core.name} (da core_calculus)",
            famiglia="calcestruzzo",
            densita_kg_m3=core.density,
            f_ck=core.f_ck * _MPA_TO_KG_CM2,
            gamma_c=core.gamma_c,
            alpha_cc=core.alpha_cc,
            E=core.E * _MPA_TO_KG_CM2 if core.E > 0 else 0.0,
            nu=core.nu,
        )

    if isinstance(core, CoreSteel):
        return Material(
            material_id=core.name,
            descrizione=f"Acciaio {core.name} (da core_calculus)",
            famiglia="acciaio",
            densita_kg_m3=core.density,
            f_yk=core.f_yk * _MPA_TO_KG_CM2,
            gamma_s=core.gamma_s,
            E=core.E * _MPA_TO_KG_CM2 if core.E > 0 else 0.0,
            nu=core.nu,
        )

    return Material(
        material_id=core.name,
        descrizione=f"{core.material_type} {core.name} (da core_calculus)",
        famiglia=core.material_type or "calcestruzzo",
        densita_kg_m3=core.density,
        E=core.E * _MPA_TO_KG_CM2 if core.E > 0 else 0.0,
        nu=core.nu,
    )
