from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


MIN_SCAN_INTERVAL_SECONDS = 10


@dataclass(slots=True)
class AppConfig:
    api_base_url: str = ""
    token: str = ""
    watched_folder: str = ""
    scan_interval_seconds: int = MIN_SCAN_INTERVAL_SECONDS
    message_body: str = "Segue nota fiscal e boleto."
    user_id: str = ""
    queue_id: str = ""
    send_signature: bool = False
    close_ticket: bool = False
    timeout_seconds: int = 30
    max_retries: int = 3
    require_pair: bool = True
    send_files_together: bool = True
    merge_pdfs_before_send: bool = False

    @property
    def endpoint_url(self) -> str:
        return f"{self.api_base_url.rstrip('/')}/api/messages/send"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.api_base_url.strip():
            errors.append("URL base da API e obrigatoria.")
        if not self.token.strip():
            errors.append("Token Bearer e obrigatorio.")
        if not self.watched_folder.strip():
            errors.append("Pasta monitorada e obrigatoria.")
        elif not Path(self.watched_folder).exists():
            errors.append("Pasta monitorada nao existe.")
        elif not Path(self.watched_folder).is_dir():
            errors.append("Caminho monitorado nao e uma pasta.")
        if self.scan_interval_seconds < MIN_SCAN_INTERVAL_SECONDS:
            errors.append("Intervalo minimo de varredura e 10 segundos.")
        if self.timeout_seconds < 1:
            errors.append("Timeout deve ser maior que zero.")
        if self.max_retries < 0:
            errors.append("Quantidade de tentativas nao pode ser negativa.")
        return errors

    def to_json(self) -> dict[str, Any]:
        return {
            "api_base_url": self.api_base_url,
            "token": self.token,
            "watched_folder": self.watched_folder,
            "scan_interval_seconds": self.scan_interval_seconds,
            "message_body": self.message_body,
            "user_id": self.user_id,
            "queue_id": self.queue_id,
            "send_signature": self.send_signature,
            "close_ticket": self.close_ticket,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "require_pair": self.require_pair,
            "send_files_together": self.send_files_together,
            "merge_pdfs_before_send": self.merge_pdfs_before_send,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "AppConfig":
        defaults = cls()
        values = defaults.to_json()
        values.update(data)
        values["scan_interval_seconds"] = max(
            int(values.get("scan_interval_seconds") or MIN_SCAN_INTERVAL_SECONDS),
            MIN_SCAN_INTERVAL_SECONDS,
        )
        values["timeout_seconds"] = int(values.get("timeout_seconds") or 30)
        values["max_retries"] = int(values.get("max_retries") or 3)
        values["send_signature"] = bool(values.get("send_signature"))
        values["close_ticket"] = bool(values.get("close_ticket"))
        values["require_pair"] = bool(values.get("require_pair"))
        values["send_files_together"] = bool(values.get("send_files_together"))
        values["merge_pdfs_before_send"] = bool(values.get("merge_pdfs_before_send"))
        return cls(**values)


@dataclass(frozen=True, slots=True)
class ParsedFile:
    path: Path
    kind: str
    document_id: str
    whatsapp: str
    reference: str


@dataclass(slots=True)
class FileGroup:
    whatsapp: str
    notes: list[ParsedFile] = field(default_factory=list)
    boletos: list[ParsedFile] = field(default_factory=list)

    @property
    def files(self) -> list[ParsedFile]:
        return [*self.notes, *self.boletos]

    @property
    def is_pair_complete(self) -> bool:
        return bool(self.notes and self.boletos)


@dataclass(slots=True)
class SendResult:
    success: bool
    status_code: int | None = None
    response_body: str = ""
    error: str = ""


@dataclass(slots=True)
class HistoryEntry:
    created_at: datetime
    whatsapp: str
    files: str
    status: str
    detail: str
