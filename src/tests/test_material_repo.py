"""
test_material_repo.py

Test minimi per:
    src/materials/material_repo.py
"""

from src.materials.material_model import Material
from src.materials.material_repo import MaterialRepository


def test_material_repo_add_and_get():
    repo = MaterialRepository()
    m = Material(
        material_id="C25",
        description="Calcestruzzo C25 (stub)",
        family="cls",
        density_kg_m3=2400,
        params={"fck": 250, "E": 300000},
    )
    repo.add_material(m)

    got = repo.get("C25")
    assert got is not None
    assert got.description == "Calcestruzzo C25 (stub)"
