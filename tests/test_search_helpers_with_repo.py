from materials_repository import MaterialsRepository
from sections_app.services import search_helpers


def sample_materials():
    return [
        {"id": "m1", "name": "C160", "type": "concrete", "code": "C160", "sigma_c28": 160},
        {"id": "m2", "name": "Ferro Dolce", "type": "steel", "code": "FeDolce"},
        {"id": "m3", "name": "C100", "type": "concrete", "code": "C100"},
    ]


def test_search_materials_repo_matching():
    repo = MaterialsRepository()
    # inject sample materials in-memory
    repo._materials = sample_materials()

    res = search_helpers.search_materials(repo, None, "160", type_filter="concrete")
    assert any("C160" == r for r in res)

    res2 = search_helpers.search_materials(repo, None, "ferro", type_filter="steel")
    assert any("Ferro Dolce" == r for r in res2)
