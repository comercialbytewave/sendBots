from __future__ import annotations

import unittest
from pathlib import Path

from sendbots.parser import is_marked_sent, parse_file


class ParserTest(unittest.TestCase):
    def test_parse_note(self) -> None:
        parsed = parse_file(Path("Nfe0001_5585998146212_12312313212315.pdf"))

        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.kind, "note")
        self.assertEqual(parsed.document_id, "0001")
        self.assertEqual(parsed.whatsapp, "5585998146212")
        self.assertEqual(parsed.reference, "12312313212315")

    def test_parse_boleto(self) -> None:
        parsed = parse_file(Path("Boleto0001_5585998146212_123123123123.pdf"))

        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.kind, "boleto")
        self.assertEqual(parsed.document_id, "0001")
        self.assertEqual(parsed.whatsapp, "5585998146212")
        self.assertEqual(parsed.reference, "123123123123")

    def test_ignore_sent_file(self) -> None:
        self.assertTrue(is_marked_sent(Path("Nfe0001_5585998146212_123_ENV.pdf")))
        self.assertIsNone(parse_file(Path("Nfe0001_5585998146212_123_ENV.pdf")))

    def test_invalid_name(self) -> None:
        self.assertIsNone(parse_file(Path("arquivo.pdf")))


if __name__ == "__main__":
    unittest.main()

