"""Persistence helpers for Calcforshort UI settings."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


APP_DIR_NAME = "Calcforshort"
LEGACY_APP_DIR_NAME = "PluginCalculator"
SETTINGS_FILE_NAME = "settings.json"


@dataclass
class AppSettings:
    """Persisted calculator preferences and window state."""

    dark_mode: bool = False
    live_mode: bool = True
    calculator_mode: str = "evaluation"
    angle_mode: str = "radian"
    single_letter_variables: bool = False
    disabled_plugin_ids: list[str] = field(default_factory=list)
    window_geometry: str | None = None
    maximized: bool = False


def get_settings_path() -> Path:
    """Return the platform-appropriate JSON settings file path."""
    if sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / APP_DIR_NAME / SETTINGS_FILE_NAME
        return Path.home() / "AppData" / "Roaming" / APP_DIR_NAME / SETTINGS_FILE_NAME

    return Path.home() / f".{APP_DIR_NAME.lower()}" / SETTINGS_FILE_NAME


def _get_legacy_settings_path() -> Path:
    """Return the legacy settings path used before the app was rebranded."""
    if sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / LEGACY_APP_DIR_NAME / SETTINGS_FILE_NAME
        return Path.home() / "AppData" / "Roaming" / LEGACY_APP_DIR_NAME / SETTINGS_FILE_NAME

    return Path.home() / f".{LEGACY_APP_DIR_NAME.lower()}" / SETTINGS_FILE_NAME


def load_settings() -> AppSettings:
    """Load persisted settings, falling back to defaults on failure."""
    settings_path = get_settings_path()
    if not settings_path.exists():
        settings_path = _get_legacy_settings_path()
    if not settings_path.exists():
        return AppSettings()

    try:
        raw_data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppSettings()

    return AppSettings(
        dark_mode=bool(raw_data.get("dark_mode", False)),
        live_mode=bool(raw_data.get("live_mode", True)),
        calculator_mode=str(raw_data.get("calculator_mode", "evaluation")).lower()
        if str(raw_data.get("calculator_mode", "evaluation")).lower() in {"evaluation", "terminal"}
        else "evaluation",
        angle_mode=str(raw_data.get("angle_mode", "radian")).lower()
        if str(raw_data.get("angle_mode", "radian")).lower() in {"radian", "degree"}
        else "radian",
        single_letter_variables=bool(raw_data.get("single_letter_variables", False)),
        disabled_plugin_ids=list(raw_data.get("disabled_plugin_ids", [])),
        window_geometry=raw_data.get("window_geometry"),
        maximized=bool(raw_data.get("maximized", False)),
    )


def save_settings(settings: AppSettings) -> None:
    """Write *settings* to disk as formatted JSON."""
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")