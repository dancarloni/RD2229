import json
from pathlib import Path

import pytest

from src.core_calculus.solaio_input import (
    InputValidationError,
    _repo_data_path,
    load_fields_metadata,
    load_tipologie,
    parse_solaio_input,
)


def load_example() -> dict:
    fixture = Path(__file__).resolve().parent / "fixtures" / "solaio_input_valid.json"
    return json.loads(fixture.read_text(encoding="utf-8"))


def test_parse_valid_input():
    data = load_example()
    soli = parse_solaio_input(data)
    ready = soli.as_ready_dict()

    assert ready["meta"]["tipologia"] == "laterocemento"
    assert ready["normalized"]["geometria"]["luce_m"] == pytest.approx(4.5, rel=1e-6)
    assert ready["normalized"]["carichi"]["G1_kN_m2"] == pytest.approx(2.942, rel=1e-3)
    assert ready["meta"]["unit_system_detected"] == "legacy_kgf_cm"


def test_missing_field_raises():
    data = load_example()
    del data["geometria"]

    with pytest.raises(InputValidationError) as exc:
        parse_solaio_input(data)

    assert any("geometria" in issue.field for issue in exc.value.issues)


def test_negative_values_raise():
    data = load_example()
    data["materiali"]["f_ck"] = -1

    with pytest.raises(InputValidationError) as exc:
        parse_solaio_input(data)

    assert any("f_ck" in issue.field for issue in exc.value.issues)


def test_invalid_tipologia_raise():
    data = load_example()
    data["tipologia"] = "invalida"

    with pytest.raises(InputValidationError) as exc:
        parse_solaio_input(data)

    assert any("tipologia" in issue.field for issue in exc.value.issues)


def test_multiple_errors_are_aggregated():
    data = load_example()
    data["tipologia"] = "errata"
    data["materiali"]["f_ck"] = -2
    data["carichi"]["Q"] = -1

    with pytest.raises(InputValidationError) as exc:
        parse_solaio_input(data)

    assert len(exc.value.issues) >= 3


def test_ready_dict_contains_original_and_normalized():
    data = load_example()
    ready = parse_solaio_input(data).as_ready_dict()

    assert "original" in ready
    assert "normalized" in ready
    assert ready["original"]["geometria"]["luce_cm"] == 450
    assert ready["normalized"]["geometria"]["luce_m"] == pytest.approx(4.5, rel=1e-6)


def test_load_tipologie_data_source():
    tipologie = load_tipologie()
    assert "laterocemento" in tipologie
    assert "predalles" in tipologie


def test_load_fields_metadata_data_source():
    metadata = load_fields_metadata()
    assert "tipologia" in metadata
    assert metadata["tipologia"]["label_it"]


def test_missing_data_file_raises_runtime_error(monkeypatch):
    bad_path = _repo_data_path("data/solai_tipologie.json")
    monkeypatch.setattr(
        "src.core_calculus.solaio_input.pkgutil.get_data", lambda *_args, **_kwargs: None
    )
    original_exists = Path.exists

    def patched_exists(path_obj: Path) -> bool:
        if path_obj == bad_path:
            return False
        return original_exists(path_obj)

    monkeypatch.setattr(Path, "exists", patched_exists)

    with pytest.raises(RuntimeError):
        load_tipologie()
