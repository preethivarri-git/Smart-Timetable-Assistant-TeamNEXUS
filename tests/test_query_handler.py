import unittest

from backend.tools.query_handler import QueryHandler


class _ListRequest:
    def __init__(self, items):
        self._items = items

    def execute(self):
        return {"items": self._items}


class _EventsResource:
    def __init__(self, items):
        self._items = items

    def list(self, **kwargs):
        return _ListRequest(self._items)


class _CalendarService:
    def __init__(self, items):
        self._resource = _EventsResource(items)

    def events(self):
        return self._resource


class QueryHandlerTests(unittest.TestCase):
    def test_show_schedule_returns_friendly_message_when_empty(self):
        handler = QueryHandler(_CalendarService([]))
        result = handler.show_schedule(0)
        self.assertIn("don't have anything scheduled", result)
        self.assertIn("today", result)

    def test_show_schedule_lists_events(self):
        service = _CalendarService([
            {
                "summary": "Physics Lecture",
                "start": {"dateTime": "2026-08-19T09:00:00+05:30"},
                "end": {"dateTime": "2026-08-19T10:00:00+05:30"},
            }
        ])
        result = QueryHandler(service).show_schedule(0)
        self.assertIn("Physics Lecture", result)

    def test_next_event_returns_message_when_none_upcoming(self):
        result = QueryHandler(_CalendarService([])).next_event()
        self.assertIn("don't have any upcoming events", result)

    def test_has_events_true(self):
        service = _CalendarService([
            {
                "summary": "Meeting",
                "start": {"dateTime": "2026-08-19T09:00:00+05:30"},
                "end": {"dateTime": "2026-08-19T10:00:00+05:30"},
            }
        ])
        result = QueryHandler(service).has_events(0)
        self.assertIn("Yes, you have 1 event", result)

    def test_has_events_false(self):
        result = QueryHandler(_CalendarService([])).has_events(1)
        self.assertIn("No,", result)
        self.assertIn("tomorrow", result)

    def test_busy_hours_computes_total_duration(self):
        service = _CalendarService([
            {
                "summary": "Meeting",
                "start": {"dateTime": "2026-08-19T09:00:00+05:30"},
                "end": {"dateTime": "2026-08-19T10:30:00+05:30"},
            }
        ])
        result = QueryHandler(service).busy_hours(0)
        self.assertIn("1.5 hour", result)


if __name__ == "__main__":
    unittest.main()