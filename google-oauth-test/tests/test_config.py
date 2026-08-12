import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from auth_flow import SCOPES, load_config


class ConfigTests(unittest.TestCase):
    def test_scopes_are_read_only(self):
        self.assertEqual(SCOPES, [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/calendar.readonly",
        ])

    def test_paths_are_configurable(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {
                "GOOGLE_CLIENT_SECRET_FILE": str(Path(directory) / "secret.json"),
                "GOOGLE_TOKEN_FILE": str(Path(directory) / "token.json"),
            }, clear=False):
                secret, token = load_config()
        self.assertTrue(str(secret).endswith("secret.json"))
        self.assertTrue(str(token).endswith("token.json"))


if __name__ == "__main__":
    unittest.main()
