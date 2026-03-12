from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


APP_DIR_NAME = "PluginCalculator"
SETTINGS_FILE_NAME = "settings.json"


@dataclass
class AppSettings:
    dark_mode: bool = False
    live_mode: bool = False
    enabled_plugin_ids: list[str] = field(default_factory=list)
    window_geometry: str | None = None
    maximized: bool = False


def get_settings_path() -> Path:
    if sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / APP_DIR_NAME / SETTINGS_FILE_NAME
        return Path.home() / "AppData" / "Roaming" / APP_DIR_NAME / SETTINGS_FILE_NAME

    return Path.home() / f".{APP_DIR_NAME.lower()}" / SETTINGS_FILE_NAME


def load_settings() -> AppSettings:
    settings_path = get_settings_path()
    if not settings_path.exists():
        return AppSettings()

    try:
        raw_data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppSettings()

    return AppSettings(
        dark_mode=bool(raw_data.get("dark_mode", False)),
        live_mode=bool(raw_data.get("live_mode", False)),
        enabled_plugin_ids=list(raw_data.get("enabled_plugin_ids", [])),
        window_geometry=raw_data.get("window_geometry"),
        maximized=bool(raw_data.get("maximized", False)),
    )


def save_settings(settings: AppSettings) -> None:
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")