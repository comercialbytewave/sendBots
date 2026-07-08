from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sendbots.watcher import scan_folder


class WatcherTest(unittest.TestCase):
    def test_groups_by_whatsapp_and_ignores_sent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "Nfe0001_5585998146212_abc.pdf").write_bytes(b"note")
            (folder / "Boleto0001_5585998146212_def.pdf").write_bytes(b"boleto")
            (folder / "Nfe0002_5585998146212_abc_ENV.pdf").write_bytes(b"sent")
            (folder / "qualquer.pdf").write_bytes(b"invalid")

            groups, invalid, skipped = scan_folder(folder)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].whatsapp, "5585998146212")
        self.assertTrue(groups[0].is_pair_complete)
        self.assertEqual(len(invalid), 1)
        self.assertEqual(len(skipped), 1)


if __name__ == "__main__":
    unittest.main()

