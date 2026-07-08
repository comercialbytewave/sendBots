from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sendbots.config import ConfigStore, mask_token
from sendbots.models import AppConfig, MIN_SCAN_INTERVAL_SECONDS


class ConfigTest(unittest.TestCase):
    def test_min_interval_is_enforced_on_load(self) -> None:
        config = AppConfig.from_json({"scan_interval_seconds": 1})

        self.assertEqual(config.scan_interval_seconds, MIN_SCAN_INTERVAL_SECONDS)

    def test_merge_pdf_option_round_trip(self) -> None:
        config = AppConfig.from_json({"merge_pdfs_before_send": True})

        self.assertTrue(config.merge_pdfs_before_send)
        self.assertTrue(config.to_json()["merge_pdfs_before_send"])

    def test_config_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            store = ConfigStore(path)
            expected = AppConfig(api_base_url="https://api.test", token="token", watched_folder=tmp)

            store.save(expected)
            loaded = store.load()

        self.assertEqual(loaded.api_base_url, expected.api_base_url)
        self.assertEqual(loaded.token, expected.token)

    def test_mask_token(self) -> None:
        self.assertEqual(mask_token("1234567890"), "1234...7890")
        self.assertEqual(mask_token("1234"), "****")


if __name__ == "__main__":
    unittest.main()
