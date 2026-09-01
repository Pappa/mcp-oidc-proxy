"""Thin launcher for the committed NanoIDP demo configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from nanoidp.__main__ import main as nanoidp_main


def get_config_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "config"


def main() -> None:
    config_dir = get_config_dir()
    os.chdir(config_dir)
    os.environ.setdefault("NANOIDP_CONFIG_DIR", str(config_dir))

    argv = [sys.argv[0], "--config", str(config_dir), *sys.argv[1:]]
    sys.argv = argv

    nanoidp_main()
