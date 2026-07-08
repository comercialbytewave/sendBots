from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sendbots.renamer import mark_as_sent, sent_name_for


class RenamerTest(unittest.TestCase):
    def test_sent_name_adds_env(self) -> None:
        path = Path("Nfe0001_5585998146212_abc.pdf")

        self.assertEqual(sent_name_for(path).name, "Nfe0001_5585998146212_abc_ENV.pdf")

    def test_mark_as_sent_handles_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = folder / "Nfe0001_5585998146212_abc.pdf"
            conflict = folder / "Nfe0001_5585998146212_abc_ENV.pdf"
            original.write_bytes(b"file")
            conflict.write_bytes(b"old")

            renamed = mark_as_sent(original)

        self.assertEqual(renamed.name, "Nfe0001_5585998146212_abc_ENV_1.pdf")


if __name__ == "__main__":
    unittest.main()

