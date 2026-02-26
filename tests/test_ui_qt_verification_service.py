from pathlib import Path

from rd2229.ui_qt.services.settings_service import SettingsService
from rd2229.ui_qt.services.verification_service import VerificationService


def test_verification_service_runs_mvp_module_with_inputs(tmp_path):
    workspace = Path(tmp_path)
    config_dir = workspace / "config" / "calculation_codes"
    config_dir.mkdir(parents=True, exist_ok=True)

    (config_dir / "MVP_PLACEHOLDER.jsoncode").write_text(
        (
            '{\n'
            '  "id": "MVP_PLACEHOLDER",\n'
            '  "version": "1.0.0",\n'
            '  "namespace": "NTC2018",\n'
            '  "payload": {\n'
            '    "check_code": "MVP_REAL_MIN",\n'
            '    "threshold": 1000.0,\n'
            '    "norm_references": ["TODO(NTC/EC/RD):REF"]\n'
            '  }\n'
            '}\n'
        ),
        encoding="utf-8",
    )

    settings = SettingsService(workspace_root=workspace)
    service = VerificationService(workspace_root=workspace, settings_service=settings)

    result = service.run_module(
        "mvp_structural",
        {
            "axial_n": 150.0,
            "factor": 1.0,
            "threshold": 100.0,
            "check_code": "MVP_REAL_MIN",
            "db_name": "alpha_test.db",
        },
    )

    assert result["status"] == "OK"
    assert result["summary"]["check_code"] == "MVP_REAL_MIN"
    assert result["summary"]["status"] == "FAIL"
    assert Path(result["db_path"]).exists()


def test_verification_service_not_ready_module(tmp_path):
    service = VerificationService(workspace_root=Path(tmp_path))
    result = service.run_module("reporting_audit")
    assert result["status"] == "NOT_READY"
