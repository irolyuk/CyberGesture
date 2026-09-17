from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


class SettingsError(Exception):
    """Помилка завантаження або збереження налаштувань."""


def _resource_path(relative_path: str) -> Path:
    """
    Шлях до ресурсів програми.

    Під час звичайного запуску:
        <project_root>/...

    Після збірки PyInstaller:
        тимчасова папка _MEIPASS/...
    """
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[2]

    return base_path / relative_path


def _user_settings_path() -> Path:
    """
    Користувацькі налаштування CyberGesture.

    Windows:
        %LOCALAPPDATA%/CyberGesture/settings.json
    """
    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:
        base_path = Path(local_app_data)
    else:
        base_path = Path.home() / "AppData" / "Local"

    return (
        base_path
        / "CyberGesture"
        / "settings.json"
    )


class SettingsManager:
    def __init__(
        self,
        defaults_path: str | Path | None = None,
        user_path: str | Path | None = None,
    ):
        if defaults_path is None:
            self._defaults_path = _resource_path(
                "cybercam/config/defaults.json"
            )
        else:
            self._defaults_path = Path(defaults_path)

        if user_path is None:
            self._user_path = _user_settings_path()
        else:
            self._user_path = Path(user_path)

        self._settings: dict[str, Any] = {}

        self.load()

    @property
    def data(self) -> dict[str, Any]:
        return deepcopy(self._settings)

    def load(self) -> None:
        defaults = self._load_json(
            self._defaults_path
        )

        self._settings = deepcopy(defaults)

        if self._user_path.exists():
            user_settings = self._load_json(
                self._user_path
            )

            self._merge(
                self._settings,
                user_settings,
            )

    def save(self) -> None:
        try:
            self._user_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self._user_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    self._settings,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        except OSError as error:
            raise SettingsError(
                f"Failed to save settings: {error}"
            ) from error

    def get(
        self,
        key: str,
        default=None,
    ):
        value: Any = self._settings

        for part in key.split("."):
            if not isinstance(value, dict):
                return default

            if part not in value:
                return default

            value = value[part]

        return value

    def set(
        self,
        key: str,
        value,
    ) -> None:
        parts = key.split(".")

        target = self._settings

        for part in parts[:-1]:
            if (
                part not in target
                or not isinstance(target[part], dict)
            ):
                target[part] = {}

            target = target[part]

        target[parts[-1]] = value

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict[str, Any]:
        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except FileNotFoundError as error:
            raise SettingsError(
                f"Settings file not found: {path}"
            ) from error

        except json.JSONDecodeError as error:
            raise SettingsError(
                f"Invalid JSON in {path}: {error}"
            ) from error

        if not isinstance(data, dict):
            raise SettingsError(
                f"Settings root must be an object: {path}"
            )

        return data

    @classmethod
    def _merge(
        cls,
        base: dict,
        override: dict,
    ) -> None:
        for key, value in override.items():
            if (
                key in base
                and isinstance(base[key], dict)
                and isinstance(value, dict)
            ):
                cls._merge(
                    base[key],
                    value,
                )
            else:
                base[key] = value