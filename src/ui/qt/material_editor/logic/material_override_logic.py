"""
MaterialOverrideLogic — Gestione override manuale parametri calcolati
"""

from typing import Dict, Any

class MaterialOverrideLogic:
    @staticmethod
    def is_overridden(material: Dict[str, Any], param: str) -> bool:
        return material.get(f'{param}_override', False)

    @staticmethod
    def get_value(material: Dict[str, Any], param: str, auto_value: Any) -> Any:
        if MaterialOverrideLogic.is_overridden(material, param):
            return material.get(param)
        return auto_value

    @staticmethod
    def set_override(material: Dict[str, Any], param: str, override: bool, value: Any = None):
        material[f'{param}_override'] = override
        if override and value is not None:
            material[param] = value

    @staticmethod
    def clear_override(material: Dict[str, Any], param: str):
        material[f'{param}_override'] = False
        # Optionally remove manual value

# Per test rapido
if __name__ == "__main__":
    mat = {'f_ck': 25.0, 'f_ck_override': False}
    auto_val = 30.0
    print(MaterialOverrideLogic.get_value(mat, 'f_ck', auto_val))
    MaterialOverrideLogic.set_override(mat, 'f_ck', True, 28.0)
    print(MaterialOverrideLogic.get_value(mat, 'f_ck', auto_val))
    MaterialOverrideLogic.clear_override(mat, 'f_ck')
    print(MaterialOverrideLogic.get_value(mat, 'f_ck', auto_val))
