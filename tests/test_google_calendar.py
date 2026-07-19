from datetime import datetime
import unittest

from backend.calendar_service.google_calendar import get_events_between


class _ListRequest:
    def __init__(self, calls):
        self.calls = calls

    def execute(self):
        return {"items": []}


class _EventsResource:
    def __init__(self):
        self.calls = []

    def list(self, **kwargs):
        self.calls.append(kwargs)
        return _ListRequest(self.calls)


class _CalendarService:
    def __init__(self):
        self.resource = _EventsResource()

    def events(self):
        return self.resource


class GoogleCalendarTests(unittest.TestCase):
    def test_get_events_between_sends_rfc3339_timestamps_with_timezone(self):
        service = _CalendarService()

        get_events_between(
            service,
            datetime(2026, 8, 6, 9, 0),
            datetime(2026, 8, 6, 10, 0),
        )

        request = service.resource.calls[0]
        self.assertEqual(request["timeMin"], "2026-08-06T09:00:00+05:30")
        self.assertEqual(request["timeMax"], "2026-08-06T10:00:00+05:30")


if __name__ == "__main__":
    unittest.main()
