from pathlib import Path

from rd2229.ui_qt.services.settings_service import SettingsService


def test_settings_service_persists_runtime_defaults(tmp_path):
    service = SettingsService(workspace_root=Path(tmp_path))
    updated = service.update_runtime_defaults(
        axial_n=210.0,
        factor=1.2,
        threshold=900.0,
        check_code="MVP_REAL_MIN",
        db_name="custom.db",
    )

    assert updated.default_axial_n == 210.0
    assert updated.default_factor == 1.2
    assert updated.default_threshold == 900.0
    assert updated.default_check_code == "MVP_REAL_MIN"
    assert updated.default_db_name == "custom.db"

    reloaded = SettingsService(workspace_root=Path(tmp_path)).get_model()
    assert reloaded.default_axial_n == 210.0
    assert reloaded.default_db_name == "custom.db"
