import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from auth_flow import SCOPES, load_config
from smoke_test import run


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

    def test_readonly_and_watch_calls_use_authorized_session(self):
        responses = {
            "/profile": {"historyId": "100"},
            "/messages": {"messages": [{"id": "message-id"}]},
            "/history": {"history": []},
            "/events": {"items": [{"id": "event-id"}]},
            "/watch": {"historyId": "101", "expiration": "1"},
            "/events/watch": {"resourceId": "resource-id", "expiration": "2"},
        }

        def request(method, url, **kwargs):
            response = Mock()
            response.raise_for_status.return_value = None
            key = next(
                key for key in sorted(responses, key=len, reverse=True) if url.endswith(key)
            )
            response.json.return_value = responses[key]
            return response

        session = Mock()
        session.request.side_effect = request
        environment = {
            "GOOGLE_GMAIL_PUBSUB_TOPIC": "projects/test/topics/gmail",
            "GOOGLE_CALENDAR_WATCH_ADDRESS": "https://example.test/watch",
        }
        with (
            patch("smoke_test.authenticate", return_value=object()),
            patch("smoke_test.AuthorizedSession", return_value=session),
            patch.dict(os.environ, environment, clear=False),
        ):
            result = run(dry_run=False, watch=True)

        self.assertEqual(result["checks"]["watch"], "pass")
        self.assertTrue(result["gmail"]["history_id_present"])
        self.assertEqual(result["calendar"]["event_count"], 1)


if __name__ == "__main__":
    unittest.main()
