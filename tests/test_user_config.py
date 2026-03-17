"""Test round-trip per UserConfig."""

from __future__ import annotations

from pathlib import Path

from src.core.user_config import UserConfig


def test_user_config_save_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    cfg = UserConfig(
        recent_projects=["a.jsonp", "b.jsonp"],
        default_norm_code="NTC2018",
        theme="dark",
        last_output_dir="out",
        autosave_enabled=True,
        autosave_minutes=7,
    )

    cfg.save(path)
    loaded = UserConfig.load(path)

    assert loaded.default_norm_code == "NTC2018"
    assert loaded.theme == "dark"
    assert loaded.last_output_dir == "out"
    assert loaded.autosave_enabled is True
    assert loaded.autosave_minutes == 7
    assert loaded.recent_projects == ["a.jsonp", "b.jsonp"]


def test_user_config_recent_is_capped(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    cfg = UserConfig()

    for idx in range(20):
        cfg.add_recent(f"p{idx}.jsonp")

    cfg.save(path)
    loaded = UserConfig.load(path)

    assert len(loaded.recent_projects) == UserConfig.MAX_RECENT
    assert loaded.recent_projects[0] == "p19.jsonp"


def test_user_config_autosave_minutes_clamped(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        '{"autosave_enabled": true, "autosave_minutes": 0}',
        encoding="utf-8",
    )

    loaded = UserConfig.load(path)

    assert loaded.autosave_enabled is True
    assert loaded.autosave_minutes == 1
