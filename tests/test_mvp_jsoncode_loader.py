import pytest

from src.rd2229.mvp.jsoncode_loader import load_jsoncode_config


def test_jsoncode_loader_reads_check_code_and_provenance(tmp_path):
    config_path = tmp_path / "ok.jsoncode"
    config_path.write_text(
        (
            "{\n"
            '  "id": "MVP_PLACEHOLDER",\n'
            '  "version": "1.0.0",\n'
            '  "namespace": "NTC2018",\n'
            '  "payload": {\n'
            '    "check_code": "MVP_REAL_MIN",\n'
            '    "threshold": 1500.0,\n'
            '    "provenance": {"threshold": "project_profile"},\n'
            '    "norm_references": ["TODO(NTC/EC/RD):REF"]\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    cfg = load_jsoncode_config(str(config_path))
    assert cfg.check_code == "MVP_REAL_MIN"
    assert cfg.provenance["threshold"] == "project_profile"


def test_jsoncode_loader_rejects_invalid_threshold_type(tmp_path):
    config_path = tmp_path / "bad.jsoncode"
    config_path.write_text(
        (
            "{\n"
            '  "id": "MVP_PLACEHOLDER",\n'
            '  "version": "1.0.0",\n'
            '  "namespace": "NTC2018",\n'
            '  "payload": {\n'
            '    "threshold": "bad",\n'
            '    "norm_references": ["TODO(NTC/EC/RD):REF"]\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_jsoncode_config(str(config_path))
