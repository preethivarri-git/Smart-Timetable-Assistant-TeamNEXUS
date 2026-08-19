import unittest
from unittest.mock import MagicMock

from backend.tools.friendly_errors import friendly_calendar_error, friendly_missing_credentials_message


def _make_http_error(status):
    error = MagicMock()
    error.resp.status = status
    return error


class FriendlyCalendarErrorTests(unittest.TestCase):
    def test_auth_errors_suggest_reconnecting(self):
        for status in (401, 403):
            message = friendly_calendar_error(_make_http_error(status))
            self.assertIn("Connect Google Calendar", message)

    def test_rate_limit_suggests_retry(self):
        message = friendly_calendar_error(_make_http_error(429))
        self.assertIn("try again", message.lower())

    def test_server_errors_suggest_retry(self):
        for status in (500, 502, 503, 504):
            message = friendly_calendar_error(_make_http_error(status))
            self.assertIn("temporarily unavailable", message)

    def test_unknown_status_falls_back_to_a_generic_message(self):
        message = friendly_calendar_error(_make_http_error(418))
        self.assertIn("418", message)

    def test_missing_credentials_message_mentions_credentials_json(self):
        self.assertIn("credentials.json", friendly_missing_credentials_message())


if __name__ == "__main__":
    unittest.main()