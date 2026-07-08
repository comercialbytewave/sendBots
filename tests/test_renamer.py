from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sendbots.renamer import SENT_FOLDER_NAME, archive_marked_sent, mark_as_sent, sent_name_for


class RenamerTest(unittest.TestCase):
    def test_sent_name_adds_env(self) -> None:
        path = Path("Nfe0001_5585998146212_abc.pdf")

        target = sent_name_for(path)

        self.assertEqual(target.parent.name, SENT_FOLDER_NAME)
        self.assertEqual(target.name, "Nfe0001_5585998146212_abc_ENV.pdf")

    def test_mark_as_sent_handles_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = folder / "Nfe0001_5585998146212_abc.pdf"
            sent_folder = folder / SENT_FOLDER_NAME
            sent_folder.mkdir()
            conflict = sent_folder / "Nfe0001_5585998146212_abc_ENV.pdf"
            original.write_bytes(b"file")
            conflict.write_bytes(b"old")

            renamed = mark_as_sent(original)

        self.assertEqual(renamed.name, "Nfe0001_5585998146212_abc_ENV_1.pdf")

    def test_archives_an_existing_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            old_sent = folder / "Nfe0001_5585998146212_abc_ENV.pdf"
            old_sent.write_bytes(b"sent")

            archived = archive_marked_sent(old_sent)

            self.assertFalse(old_sent.exists())
            self.assertEqual(archived.parent.name, SENT_FOLDER_NAME)
            self.assertTrue(archived.exists())


if __name__ == "__main__":
    unittest.main()
