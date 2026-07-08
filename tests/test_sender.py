from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sendbots.models import AppConfig, CompanyStatusResult, FileGroup, ParsedFile, SendResult
from sendbots.sender import SenderService
from sendbots.storage import HistoryStore


class SenderTest(unittest.TestCase):
    def test_incomplete_pair_explains_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "history.sqlite3"
            boleto = ParsedFile(
                path=Path("Boleto31_558598146212_123456789.pdf"),
                kind="boleto",
                document_id="31",
                whatsapp="558598146212",
                reference="123456789",
            )
            group = FileGroup(whatsapp="558598146212", boletos=[boleto])
            service = SenderService(AppConfig(require_pair=True), HistoryStore(db_path))

            result = service.process_group(group)

            history = service.history.latest()

        self.assertFalse(result.success)
        self.assertIn("Faltando: Nota Fiscal Nfe", result.error)
        self.assertIn("mesmo WhatsApp", result.error)
        self.assertEqual(history[0].status, "ignored")
        self.assertIn("Boleto31_558598146212_123456789.pdf", history[0].detail)

    def test_merge_pair_sends_single_pdf_and_renames_originals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            db_path = folder / "history.sqlite3"
            note_path = folder / "Nfe31_558598146212_1234567489.pdf"
            boleto_path = folder / "Boleto31_558598146212_123456789.pdf"
            merged_path = folder / "Nota_Boleto_558598146212.pdf"
            note_path.write_bytes(b"note")
            boleto_path.write_bytes(b"boleto")
            merged_path.write_bytes(b"merged")
            note = ParsedFile(note_path, "note", "31", "558598146212", "1234567489")
            boleto = ParsedFile(boleto_path, "boleto", "31", "558598146212", "123456789")
            group = FileGroup(whatsapp="558598146212", notes=[note], boletos=[boleto])
            service = SenderService(
                AppConfig(
                    api_base_url="https://api.test",
                    token="token",
                    company_slug="active-merge-test",
                    merge_pdfs_before_send=True,
                ),
                HistoryStore(db_path),
            )
            sent_files: list[str] = []

            class FakeClient:
                def check_company_status(self) -> CompanyStatusResult:
                    return CompanyStatusResult(True, active=True, name="Empresa Teste")

                def send(self, whatsapp: str, files: list[ParsedFile]) -> SendResult:
                    sent_files.extend(path.path.name for path in files)
                    return SendResult(True, 200, "{}")

            service.client = FakeClient()  # type: ignore[assignment]

            with patch("sendbots.sender.merge_group_pdfs", return_value=merged_path):
                result = service.process_group(group)

            history = service.history.latest()

            self.assertTrue(result.success)
            self.assertEqual(sent_files, ["Nota_Boleto_558598146212.pdf"])
            sent_folder = folder / "Enviados"
            self.assertTrue((sent_folder / "Nfe31_558598146212_1234567489_ENV.pdf").exists())
            self.assertTrue((sent_folder / "Boleto31_558598146212_123456789_ENV.pdf").exists())
            self.assertFalse(merged_path.exists())
            self.assertEqual(history[0].status, "sent")
            self.assertIn("PDF unico enviado", history[0].detail)

    def test_inactive_company_blocks_send(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "history.sqlite3"
            note = ParsedFile(Path("Nfe31_558598146212_key.pdf"), "note", "31", "558598146212", "key")
            group = FileGroup(whatsapp="558598146212", notes=[note])
            service = SenderService(
                AppConfig(
                    api_base_url="https://api.test",
                    token="token",
                    company_slug="inactive-sender-test",
                    require_pair=False,
                ),
                HistoryStore(db_path),
            )

            class InactiveClient:
                def check_company_status(self) -> CompanyStatusResult:
                    return CompanyStatusResult(True, active=False, error="A empresa esta inativa na AlowChat.")

                def send(self, whatsapp: str, files: list[ParsedFile]) -> SendResult:
                    self.fail("send nao deveria ser chamado")  # type: ignore[attr-defined]

            service.client = InactiveClient()  # type: ignore[assignment]
            result = service.process_group(group)
            history = service.history.latest()

        self.assertFalse(result.success)
        self.assertIn("inativa", result.error)
        self.assertEqual(history[0].status, "company_inactive")


if __name__ == "__main__":
    unittest.main()
