"""Script demo per mostrare CRUD su materiali.

Esempio d'uso:
  python scripts/run_materials_demo.py

Nota: esegui da workspace root e assicurati che `PYTHONPATH=src` per importare il package.
"""
from rd2229.tools.materials_manager import (
    add_material,
    list_materials,
    get_material,
    update_material,
    delete_material,
)


def main():
    print("Aggiungo materiale esempio...")
    mat = {
        "name": "CementoNormale120",
        "type": "concrete",
        "cement_type": "normal",
        "sigma_c28": 120.0,  # Kg/cm²
        "condition": "semplicemente_compresa",
        "controlled_quality": False,
    }
    try:
        add_material(mat)
    except ValueError:
        print("Materiale già presente")

    print("Elenco materiali:")
    for m in list_materials():
        print(" -", m.get("name"), "sigma_c=", m.get("sigma_c"))

    print("Modifico materiale e rimuovo...")
    update_material("CementoNormale120", {"sigma_c28": 200.0, "controlled_quality": True})
    print(get_material("CementoNormale120"))
    delete_material("CementoNormale120")
    print("Dopo cancellazione:", list_materials())


if __name__ == "__main__":
    main()
