from src.rd2229 import plugin_registry
from src.rd2229.mvp.pipeline import run_mvp_demo


def test_mvp_end_to_end_headless(tmp_path):
    db_path = tmp_path / "e2e.db"
    config_path = tmp_path / "mvp.jsoncode"
    config_path.write_text(
        (
            "{\n"
            '  "id": "MVP_PLACEHOLDER",\n'
            '  "version": "1.0.0",\n'
            '  "namespace": "NTC2018",\n'
            '  "payload": {\n'
            '    "threshold": 1000.0,\n'
            '    "norm_references": ["TODO:REF"]\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    summary = run_mvp_demo(str(db_path), str(config_path))

    assert summary["project_id"]
    assert summary["result_id"]
    assert summary["plugins_loaded"] == "2"
    assert plugin_registry.get_spec("core_structural_checks") is not None
    assert plugin_registry.get_spec("fire_module") is not None
