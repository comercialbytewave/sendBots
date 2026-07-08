from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from sendbots.config import logs_dir


def setup_logging() -> None:
    folder = logs_dir()
    folder.mkdir(parents=True, exist_ok=True)
    log_file = folder / "sendbots.log"

    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(handler)

