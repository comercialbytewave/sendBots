from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from sendbots.alowchat import AlowChatClient, build_multipart
from sendbots.models import AppConfig, ParsedFile


class AlowChatTest(unittest.TestCase):
    def test_build_multipart_contains_fields_and_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "Nfe0001_5585998146212_abc.pdf"
            file_path.write_bytes(b"pdf-data")

            body, boundary = build_multipart({"number": "5585998146212", "body": "Mensagem"}, [file_path])

        self.assertIn(boundary.encode("utf-8"), body)
        self.assertIn(b'name="number"', body)
        self.assertIn(b"5585998146212", body)
        self.assertIn(b'filename="Nfe0001_5585998146212_abc.pdf"', body)
        self.assertIn(b"pdf-data", body)

    def test_company_status_uses_slug_and_bearer_token(self) -> None:
        response = Mock()
        response.status = 200
        response.read.return_value = b'{"name":"HENTS BURG","slug":"hents-burg","status":true}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        config = AppConfig(
            api_base_url="https://retaguarda.alowchat.com.br",
            token="secret-token",
            company_slug="hents-burg",
        )

        with patch("sendbots.alowchat.request.urlopen", return_value=response) as urlopen:
            result = AlowChatClient(config).check_company_status()

        request_sent = urlopen.call_args.args[0]
        self.assertTrue(result.success)
        self.assertTrue(result.active)
        self.assertEqual(result.name, "HENTS BURG")
        self.assertEqual(
            request_sent.full_url,
            "https://retaguarda.alowchat.com.br/api/company/status/hents-burg",
        )
        self.assertEqual(request_sent.get_header("Authorization"), "Bearer secret-token")

    def test_company_status_false_is_inactive(self) -> None:
        response = Mock()
        response.status = 200
        response.read.return_value = b'{"name":"HENTS BURG","slug":"hents-burg","status":false}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        config = AppConfig(api_base_url="https://api.test", token="token", company_slug="inactive")

        with patch("sendbots.alowchat.request.urlopen", return_value=response):
            result = AlowChatClient(config).check_company_status()

        self.assertTrue(result.success)
        self.assertFalse(result.active)
        self.assertIn("inativa", result.error)

    def test_send_pdf_uses_company_whatsapp_endpoint_and_multipart(self) -> None:
        response = Mock()
        response.status = 201
        response.read.return_value = b'{"success":true}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        config = AppConfig(
            api_base_url="https://api.test/",
            token="company-token",
            message_body="Segue o PDF.",
        )

        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "Nfe1_5585999999999_chave.pdf"
            file_path.write_bytes(b"pdf-data")
            parsed_file = ParsedFile(
                path=file_path,
                kind="note",
                document_id="1",
                whatsapp="5585999999999",
                reference="chave",
            )

            with patch("sendbots.alowchat.request.urlopen", return_value=response) as urlopen:
                result = AlowChatClient(config).send(parsed_file.whatsapp, [parsed_file])

        request_sent = urlopen.call_args.args[0]
        self.assertTrue(result.success)
        self.assertEqual(request_sent.method, "POST")
        self.assertEqual(
            request_sent.full_url,
            "https://api.test/api/company/messages/whatsapp",
        )
        self.assertEqual(request_sent.get_header("Authorization"), "Bearer company-token")
        self.assertTrue(
            request_sent.get_header("Content-type").startswith("multipart/form-data; boundary=")
        )
        self.assertIn(b'filename="Nfe1_5585999999999_chave.pdf"', request_sent.data)
        self.assertIn(b"pdf-data", request_sent.data)


if __name__ == "__main__":
    unittest.main()
