from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from sendbots.alowchat import AlowChatClient
from sendbots.models import AppConfig, FileGroup, ParsedFile, SendResult
from sendbots.pdf_merge import PdfMergeError, merge_group_pdfs
from sendbots.renamer import mark_as_sent
from sendbots.storage import HistoryStore


LOGGER = logging.getLogger(__name__)
_COMPANY_STATUS_CACHE: dict[tuple[str, str, str], tuple[date, SendResult]] = {}


class SenderService:
    def __init__(self, config: AppConfig, history: HistoryStore | None = None) -> None:
        self.config = config
        self.history = history or HistoryStore()
        self.client = AlowChatClient(config)

    def process_group(self, group: FileGroup) -> SendResult:
        if self.config.require_pair and not group.is_pair_complete:
            detail = _pending_pair_detail(group)
            LOGGER.info("Grupo %s nao enviado: %s", group.whatsapp, detail)
            self.history.add(group.whatsapp, _file_names(group.files), "ignored", detail)
            return SendResult(False, None, "", detail)

        company_status = self._ensure_company_active()
        if not company_status.success:
            detail = company_status.error or "Empresa inativa ou nao autorizada."
            LOGGER.warning("Envio bloqueado para %s: %s", group.whatsapp, detail)
            self.history.add(group.whatsapp, _file_names(group.files), "company_inactive", detail)
            return company_status

        if self.config.merge_pdfs_before_send and group.is_pair_complete:
            return self._send_merged_group(group)

        if self.config.send_files_together:
            return self._send_and_rename(group.whatsapp, group.files)

        final_result = SendResult(True, None, "", "")
        for item in group.files:
            result = self._send_and_rename(group.whatsapp, [item])
            if not result.success:
                final_result = result
        return final_result

    def _ensure_company_active(self) -> SendResult:
        cache_key = (
            self.config.api_base_url.rstrip("/"),
            self.config.company_slug.strip(),
            self.config.token,
        )
        cached = _COMPANY_STATUS_CACHE.get(cache_key)
        today = date.today()
        if cached and cached[0] == today:
            return cached[1]

        status = self.client.check_company_status()
        if status.success and status.active:
            result = SendResult(
                True,
                status.status_code,
                status.response_body,
                "",
            )
        else:
            detail = status.error or "A empresa esta inativa na AlowChat."
            result = SendResult(False, status.status_code, status.response_body, detail)
        _COMPANY_STATUS_CACHE[cache_key] = (today, result)
        return result

    def _send_merged_group(self, group: FileGroup) -> SendResult:
        try:
            merged_path = merge_group_pdfs(group)
        except PdfMergeError as exc:
            detail = str(exc)
            LOGGER.exception("Falha ao juntar PDFs do grupo %s", group.whatsapp)
            self.history.add(group.whatsapp, _file_names(group.files), "merge_error", detail)
            return SendResult(False, None, "", detail)

        merged_file = ParsedFile(
            path=merged_path,
            kind="merged",
            document_id="",
            whatsapp=group.whatsapp,
            reference="nota_boleto",
        )

        result = self._send_files(group.whatsapp, [merged_file])
        try:
            if result.success:
                renamed = self._rename_files(group.files)
                detail = (
                    f"PDF unico enviado: {merged_path.name}. "
                    f"Arquivos originais movidos para Enviados: "
                    f"{', '.join(str(path.name) for path in renamed)}"
                )
                self.history.add(group.whatsapp, _file_names(group.files), "sent", detail)
            else:
                detail = result.error or result.response_body or "Falha desconhecida no envio."
                self.history.add(group.whatsapp, _file_names(group.files), "error", detail)
        finally:
            merged_path.unlink(missing_ok=True)

        return result

    def _send_and_rename(self, whatsapp: str, files: list[ParsedFile]) -> SendResult:
        result = self._send_files(whatsapp, files)
        if result.success:
            renamed = self._rename_files(files)
            detail = (
                "Enviado com sucesso. Arquivos movidos para Enviados: "
                f"{', '.join(str(path.name) for path in renamed)}"
            )
            self.history.add(whatsapp, _file_names(files), "sent", detail)
            return result

        detail = result.error or result.response_body or "Falha desconhecida no envio."
        self.history.add(whatsapp, _file_names(files), "error", detail)
        return result

    def _send_files(self, whatsapp: str, files: list[ParsedFile]) -> SendResult:
        last_result = SendResult(False, None, "", "Envio nao executado.")
        attempts = max(self.config.max_retries, 0) + 1
        for attempt in range(1, attempts + 1):
            LOGGER.info("Enviando %s arquivo(s) para %s, tentativa %s", len(files), whatsapp, attempt)
            last_result = self.client.send(whatsapp, files)
            if last_result.success:
                return last_result
            LOGGER.warning(
                "Falha no envio para %s. status=%s erro=%s",
                whatsapp,
                last_result.status_code,
                last_result.error,
            )

        return last_result

    def _rename_files(self, files: list[ParsedFile]) -> list[Path]:
        renamed: list[Path] = []
        for item in files:
            try:
                renamed.append(mark_as_sent(item.path))
            except OSError as exc:
                LOGGER.exception("Falha ao renomear arquivo %s", item.path)
                self.history.add(item.whatsapp, [str(item.path)], "rename_error", str(exc))
        return renamed


def _file_names(files: list[ParsedFile]) -> list[str]:
    return [str(item.path) for item in files]


def _pending_pair_detail(group: FileGroup) -> str:
    found: list[str] = []
    missing: list[str] = []

    if group.notes:
        found.append(f"{len(group.notes)} nota(s): {_short_names(group.notes)}")
    else:
        missing.append("Nota Fiscal Nfe")

    if group.boletos:
        found.append(f"{len(group.boletos)} boleto(s): {_short_names(group.boletos)}")
    else:
        missing.append("Boleto")

    found_text = "; ".join(found) if found else "nenhum arquivo valido"
    missing_text = " e ".join(missing)
    return (
        "Aguardando par Nota Fiscal + Boleto. "
        f"WhatsApp do grupo: {group.whatsapp}. "
        f"Encontrado: {found_text}. "
        f"Faltando: {missing_text}. "
        "Como a opcao 'Aguardar nota + boleto' esta ativa, os arquivos so enviam quando "
        "existirem Nfe e Boleto com o mesmo WhatsApp no nome."
    )


def _short_names(files: list[ParsedFile]) -> str:
    return ", ".join(item.path.name for item in files)
