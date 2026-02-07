import json
import os
from pathlib import Path

from materials_repository import MaterialsRepository
from tools import materials_manager


def sample_materials():
    return [
        {"id": "m1", "name": "C160", "type": "concrete", "code": "C160", "sigma_c28": 160},
        {"id": "m2", "name": "Ferro Dolce", "type": "steel", "code": "FeDolce"},
    ]


def test_load_and_save_jsonm(tmp_path):
    src = tmp_path / "sample.jsonm"
    out = tmp_path / "out.jsonm"

    mats = sample_materials()
    # write source using existing helper to ensure consistency
    materials_manager.save_materials(mats, str(src))

    repo = MaterialsRepository()
    loaded = repo.load_from_jsonm(str(src))
    names = [m.get("name") for m in loaded]
    assert "C160" in names
    assert "Ferro Dolce" in names

    # save to new file and verify content
    repo.save_to_jsonm(str(out))
    assert out.exists()
    reloaded = materials_manager.load_materials(str(out))
    assert any(m.get("name") == "C160" for m in reloaded)
