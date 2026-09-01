"""Unit tests for auth-server launcher helpers."""

import sys
from pathlib import Path

import pytest
from auth_server import get_config_dir, main


def test_get_config_dir_points_at_committed_config() -> None:
    config_dir = get_config_dir()
    assert config_dir.name == "config"
    assert (config_dir / "settings.yaml").is_file()
    assert (config_dir / "users.yaml").is_file()


def test_main_prepares_nanoidp_launch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_dir = get_config_dir()
    launched: dict[str, object] = {}

    def fake_nanoidp_main() -> None:
        launched["argv"] = list(sys.argv)
        launched["cwd"] = Path.cwd()
        launched["config_dir"] = config_dir

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("auth_server.nanoidp_main", fake_nanoidp_main)
    monkeypatch.setattr(sys, "argv", ["auth-server"])

    main()

    assert launched["cwd"] == config_dir
    assert launched["config_dir"] == config_dir
    assert launched["argv"] == [
        "auth-server",
        "--config",
        str(config_dir),
    ]
