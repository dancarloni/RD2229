"""
MaterialBatchEditLogic — Gestione batch editing, selezione multipla, audit
"""

from typing import List, Dict, Any

class MaterialBatchEditLogic:
    @staticmethod
    def apply_batch(materials: List[Dict[str, Any]], indices: List[int], key: str, value: Any):
        for idx in indices:
            old = materials[idx].get(key)
            materials[idx][key] = value
            # Audit: append log if needed

# Per test rapido
if __name__ == "__main__":
    mats = [{'gamma_c': 1.5}, {'gamma_c': 1.6}, {'gamma_c': 1.7}]
    MaterialBatchEditLogic.apply_batch(mats, [0,2], 'gamma_c', 2.0)
    print(mats)
