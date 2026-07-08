from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sendbots.alowchat import build_multipart


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


if __name__ == "__main__":
    unittest.main()

