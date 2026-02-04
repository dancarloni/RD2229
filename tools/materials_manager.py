"""Gestione materiali: creazione, salvataggio, modifica, cancellazione.

Questo modulo conserva i materiali (calcestruzzo, acciaio, ecc.) in un
file JSON (`data/materials.json` per default). Le unità storiche usate
per tensioni e resistenze sono Kg/cm² come convenuto.

API principali (funzioni pensate per essere chiamate da GUI o script):
- `add_material(material_dict)` -> crea e salva un materiale
- `get_material(name)` -> ritorna il materiale per nome
- `update_material(name, **fields)` -> modifica campi
- `delete_material(name)` -> rimuove materiale
- `list_materials()` -> lista tutti i materiali

I materiali sono rappresentati come dizionari con campi standard:
{
  "name": "NomeCalcestruzzo",
  "type": "concrete",
  "cement_type": "normal" | "high",
  "sigma_c28": 120.0,   # Kg/cm²
  "sigma_c": 35.0,      # Kg/cm² (calcolata)
  "E": null             # modulo elastico (opzionale, Kg/cm²? o altre unità), da definire
}

Il modulo è scritto in modo da non interrompere gli altri componenti del
progetto: usa `src/rd2229/.rd2229_config.yaml` per trovare il percorso
del file materiali, se presente.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from .concrete_strength import (
    CementType,
    SectionCondition,
    compute_allowable_compressive_stress,
    compute_sigma_c_all,
    compute_allowable_shear,
    compute_ec,
    compute_ec_conventional,
    compute_gc,
)

_DEFAULT_MATERIALS_PATH = os.path.join("data", "materials.json")

# Cache for loaded materials to avoid repeated file reads
_materials_cache: Dict[str, tuple[List[Dict], float]] = {}


def _resolve_materials_path(config: Optional[Dict] = None) -> str:
    if config is None:
        # try read config file if exists
        cfg_path = os.path.join(os.getcwd(), ".rd2229_config.yaml")
        try:
            import yaml  # type: ignore

            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as fh:
                    cfg = yaml.safe_load(fh) or {}
                    return cfg.get("materials_file", _DEFAULT_MATERIALS_PATH)
        except Exception:
            pass
    return _DEFAULT_MATERIALS_PATH


def _map_cement_type(cement_key: Optional[str]) -> CementType:
    if cement_key == "aluminous":
        return CementType.ALUMINOUS
    if cement_key == "high":
        return CementType.HIGH
    if cement_key == "slow":
        return CementType.SLOW
    return CementType.NORMAL


def _ensure_derived_fields(material: Dict) -> bool:
    """Populate derived fields on a concrete material. Returns True if updated."""
    if material.get("type") != "concrete":
        return False
    dirty = False
    sigma_c28 = material.get("sigma_c28")
    sigma_used = material.get("sigma_c") or material.get("sigma_c_simple")
    cement = _map_cement_type(material.get("cement_type"))

    # E_calculated and G range from sigma_c28
    if sigma_c28 is not None:
        try:
            ec = compute_ec(float(sigma_c28))
            gmin, gmean, gmax = compute_gc(ec)
            if material.get("E_calculated") != ec:
                material["E_calculated"] = ec
                dirty = True
            if material.get("G") != gmean:
                material["G"] = gmean
                dirty = True
            if material.get("G_min") != gmin:
                material["G_min"] = gmin
                dirty = True
            if material.get("G_max") != gmax:
                material["G_max"] = gmax
                dirty = True
            # If E not present, set to calculated and mark undefined
            if material.get("E") is None:
                material["E"] = ec
                material["E_defined"] = False
                dirty = True
            elif material.get("E_defined") is None:
                material["E_defined"] = True
                dirty = True
        except Exception:
            pass

    # Conventional E from sigma_c28 and cement type
    try:
        e_conv = compute_ec_conventional(sigma_c28, cement) if sigma_c28 is not None else None
        if material.get("E_conventional") != e_conv:
            material["E_conventional"] = e_conv
            dirty = True
    except Exception:
        if material.get("E_conventional") is not None:
            material["E_conventional"] = None
            dirty = True

    return dirty


def load_materials(path: Optional[str] = None) -> List[Dict]:
    path = path or _resolve_materials_path()
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return []
    
    # Check cache
    mtime = os.path.getmtime(path)
    if path in _materials_cache:
        cached_mats, cached_mtime = _materials_cache[path]
        if mtime == cached_mtime:
            return cached_mats.copy()  # Return copy to avoid mutations
    
    with open(path, "r", encoding="utf-8") as fh:
        mats = json.load(fh)
    dirty_any = False
    for m in mats:
        try:
            if _ensure_derived_fields(m):
                dirty_any = True
        except Exception:
            pass
    if dirty_any:
        save_materials(mats, path)
    # Update cache
    _materials_cache[path] = (mats.copy(), mtime)
    return mats


def save_materials(materials: List[Dict], path: Optional[str] = None) -> None:
    path = path or _resolve_materials_path()
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(materials, fh, indent=2, ensure_ascii=False)
    # Invalidate cache
    if path in _materials_cache:
        del _materials_cache[path]


def list_materials(path: Optional[str] = None) -> List[Dict]:
    return load_materials(path)


def get_material(name: str, path: Optional[str] = None) -> Optional[Dict]:
    materials = load_materials(path)
    for m in materials:
        if m.get("name") == name:
            return m
    return None


def add_material(material: Dict, path: Optional[str] = None) -> None:
    """Aggiunge un materiale. Se `σ_c` mancante e il tipo è `concrete`, lo calcola."""
    materials = load_materials(path)
    if any(m.get("name") == material.get("name") for m in materials):
        raise ValueError(f"Material with name '{material.get('name')}' already exists")

    # Se concrete e manca σ_c, calcolalo secondo regole storiche (Kg/cm²)
    if material.get("type") == "concrete":
        sigma_c28 = material.get("sigma_c28")
        cement = _map_cement_type(material.get("cement_type"))
        controlled = bool(material.get("controlled_quality"))
        if sigma_c28 is not None:
            # compute comprehensive results
            sigma_all = compute_sigma_c_all(float(sigma_c28), cement, controlled)
            material["sigma_c28"] = float(sigma_c28)
            material["sigma_c_simple"] = sigma_all.get("semplice")
            material["sigma_c_inflessa"] = sigma_all.get("inflessa")
            material["sigma_c_presso_inflessa"] = sigma_all.get("presso_inflessa")
            # legacy field for backward compatibility
            material["sigma_c"] = material.get("sigma_c_simple")
            # shear
            service_tau, max_tau = compute_allowable_shear(cement)
            material["tau_service"] = service_tau
            material["tau_max"] = max_tau
            # Elastic modulus (E_c) and tangential modulus (G_c)
            try:
                if sigma_c28 is not None:
                    ec = compute_ec(float(sigma_c28))
                    g_min, g_mean, g_max = compute_gc(ec)
                    # If user provided E explicitly, respect it; otherwise store computed E
                    if material.get("E") is None:
                        material["E"] = ec
                        material["E_defined"] = False
                    else:
                        material["E_defined"] = bool(material.get("E_defined", True))
                    # store calculated and conventional E, and mean/range G
                    material["E_calculated"] = ec
                    material["G"] = g_mean
                    material["G_min"] = g_min
                    material["G_max"] = g_max
                    # conventional Ec based on cement and sigma_c28
                    try:
                        e_conv = compute_ec_conventional(float(sigma_c28), cement)
                        material["E_conventional"] = e_conv
                    except Exception:
                        material["E_conventional"] = None
            except Exception:
                pass

    materials.append(material)
    save_materials(materials, path)


def update_material(name: str, updates: Dict, path: Optional[str] = None) -> None:
    materials = load_materials(path)
    for i, m in enumerate(materials):
        if m.get("name") == name:
            materials[i] = {**m, **updates}
            # If σ_c updated or σ_c28 changed, recalc if concrete
            if materials[i].get("type") == "concrete":
                sigma_c28 = materials[i].get("sigma_c28")
                cement = _map_cement_type(materials[i].get("cement_type"))
                controlled = bool(materials[i].get("controlled_quality"))
                # Recompute if sigma_c missing or sigma_c28 changed
                if sigma_c28 is not None and updates.get("sigma_c") is None:
                    sigma_all = compute_sigma_c_all(float(sigma_c28), cement, controlled)
                    materials[i]["sigma_c28"] = float(sigma_c28)
                    materials[i]["sigma_c_simple"] = sigma_all.get("semplice")
                    materials[i]["sigma_c_inflessa"] = sigma_all.get("inflessa")
                    materials[i]["sigma_c_presso_inflessa"] = sigma_all.get("presso_inflessa")
                    materials[i]["sigma_c"] = materials[i]["sigma_c_simple"]
                    service_tau, max_tau = compute_allowable_shear(cement)
                    materials[i]["tau_service"] = service_tau
                    materials[i]["tau_max"] = max_tau
                    # Elastic modulus (E_c) and tangential modulus (G_c)
                    try:
                        ec = compute_ec(float(sigma_c28))
                        g_min, g_mean, g_max = compute_gc(ec)
                        # respect user-defined E if present
                        if materials[i].get("E") is None:
                            materials[i]["E"] = ec
                            materials[i]["E_defined"] = False
                        else:
                            materials[i]["E_defined"] = bool(materials[i].get("E_defined", True))
                        materials[i]["E_calculated"] = ec
                        materials[i]["G"] = g_mean
                        materials[i]["G_min"] = g_min
                        materials[i]["G_max"] = g_max
                        try:
                            materials[i]["E_conventional"] = compute_ec_conventional(float(sigma_c28), cement)
                        except Exception:
                            materials[i]["E_conventional"] = None
                    except Exception:
                        pass
            save_materials(materials, path)
            return
    raise KeyError(f"Material with name '{name}' not found")


def delete_material(name: str, path: Optional[str] = None) -> None:
    materials = load_materials(path)
    new = [m for m in materials if m.get("name") != name]
    if len(new) == len(materials):
        raise KeyError(f"Material with name '{name}' not found")
    save_materials(new, path)


__all__ = [
    "list_materials",
    "get_material",
    "add_material",
    "update_material",
    "delete_material",
]

