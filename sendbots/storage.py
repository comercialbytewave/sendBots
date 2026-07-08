from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from sendbots.config import database_path
from sendbots.models import HistoryEntry


class HistoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    whatsapp TEXT NOT NULL,
                    files TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add(self, whatsapp: str, files: list[str], status: str, detail: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO history (created_at, whatsapp, files, status, detail)
                VALUES (?, ?, ?, ?, ?)
                """,
                (datetime.now().isoformat(timespec="seconds"), whatsapp, "\n".join(files), status, detail[:2000]),
            )
            conn.commit()

    def latest(self, limit: int = 100) -> list[HistoryEntry]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT created_at, whatsapp, files, status, detail
                FROM history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            HistoryEntry(
                created_at=datetime.fromisoformat(row[0]),
                whatsapp=row[1],
                files=row[2],
                status=row[3],
                detail=row[4],
            )
            for row in rows
        ]

