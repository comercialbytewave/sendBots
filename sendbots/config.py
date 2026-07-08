from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from sendbots.models import AppConfig


APP_DIR_NAME = "SendBots"


def user_data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / APP_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "sendbots"


def config_path() -> Path:
    return user_data_dir() / "config.json"


def database_path() -> Path:
    return user_data_dir() / "history.sqlite3"


def logs_dir() -> Path:
    return user_data_dir() / "logs"


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or config_path()

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()
        with self.path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return AppConfig.from_json(data)

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(config.to_json(), fh, indent=2, ensure_ascii=True)


def mask_token(token: str) -> str:
    token = token.strip()
    if not token:
        return ""
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}...{token[-4:]}"

