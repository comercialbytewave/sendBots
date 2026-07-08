from __future__ import annotations

import json
import mimetypes
import uuid
from pathlib import Path
from urllib import error, request
from urllib.parse import quote

from sendbots.models import AppConfig, CompanyStatusResult, ParsedFile, SendResult


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _part(name: str, value: str, boundary: str) -> bytes:
    return (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
        f"{value}\r\n"
    ).encode("utf-8")


def _file_part(name: str, path: Path, boundary: str) -> bytes:
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    return header + path.read_bytes() + b"\r\n"


def build_multipart(fields: dict[str, str], files: list[Path]) -> tuple[bytes, str]:
    boundary = f"----SendBots{uuid.uuid4().hex}"
    body = bytearray()
    for name, value in fields.items():
        body.extend(_part(name, value, boundary))
    for path in files:
        body.extend(_file_part("medias", path, boundary))
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return bytes(body), boundary


class AlowChatClient:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def check_company_status(self) -> CompanyStatusResult:
        slug = quote(self.config.company_slug.strip(), safe="")
        url = f"{self.config.api_base_url.rstrip('/')}/api/company/status/{slug}"
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Accept": "application/json",
        }
        req = request.Request(url, headers=headers, method="GET")

        try:
            with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                try:
                    data = json.loads(response_body)
                except json.JSONDecodeError:
                    return CompanyStatusResult(
                        False,
                        status_code=response.status,
                        response_body=response_body,
                        error="A API retornou uma resposta invalida ao consultar a empresa.",
                    )

                active = data.get("status") is True
                name = str(data.get("name") or "")
                returned_slug = str(data.get("slug") or "")
                detail = "" if active else "A empresa esta inativa na AlowChat."
                return CompanyStatusResult(
                    True,
                    active,
                    name,
                    returned_slug,
                    response.status,
                    response_body,
                    detail,
                )
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            detail = _extract_error(response_body) or exc.reason
            return CompanyStatusResult(
                False,
                status_code=exc.code,
                response_body=response_body,
                error=f"Falha ao consultar empresa: {detail}",
            )
        except Exception as exc:  # noqa: BLE001 - user-facing operational error.
            return CompanyStatusResult(False, error=f"Falha ao consultar empresa: {exc}")

    def send(self, whatsapp: str, files: list[ParsedFile]) -> SendResult:
        fields = {
            "number": whatsapp,
            "body": self.config.message_body,
            "userId": self.config.user_id,
            "queueId": self.config.queue_id,
            "sendSignature": _bool_text(self.config.send_signature),
            "closeTicket": _bool_text(self.config.close_ticket),
        }
        file_paths = [item.path for item in files]
        body, boundary = build_multipart(fields, file_paths)
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
        req = request.Request(self.config.endpoint_url, data=body, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                success = 200 <= response.status < 300
                return SendResult(success=success, status_code=response.status, response_body=response_body)
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            detail = _extract_error(response_body) or exc.reason
            return SendResult(False, exc.code, response_body, str(detail))
        except Exception as exc:  # noqa: BLE001 - user-facing operational error.
            return SendResult(False, None, "", str(exc))


def _extract_error(response_body: str) -> str:
    try:
        data = json.loads(response_body)
    except json.JSONDecodeError:
        return response_body[:500]
    for key in ("message", "error", "detail"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return response_body[:500]
