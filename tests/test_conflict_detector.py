from datetime import datetime
import unittest
from unittest.mock import patch

from backend.tools.conflict_detector import check_conflicts


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


class CheckConflictsWithLocalClassesTests(unittest.TestCase):
    @patch("backend.tools.conflict_detector.load_schedule")
    def test_flags_conflict_with_a_local_class(self, mock_load_schedule):
        mock_load_schedule.return_value = [
            {
                "name": "DBMS",
                "day": "Tuesday",
                "start_time": "10:00",
                "end_time": "11:00",
                "type": "Lecture",
            }
        ]

        service = _CalendarService([])  # no Google Calendar events

        start = datetime(2026, 8, 18, 10, 30)  # Tuesday, overlaps the class
        end = datetime(2026, 8, 18, 11, 30)

        result = check_conflicts(service, start, end, user_id=1)

        self.assertTrue(result["conflict"])
        self.assertEqual(len(result["events"]), 1)
        self.assertIn("DBMS", result["events"][0]["summary"])

    @patch("backend.tools.conflict_detector.load_schedule")
    def test_no_conflict_when_class_is_on_a_different_day(self, mock_load_schedule):
        mock_load_schedule.return_value = [
            {
                "name": "DBMS",
                "day": "Wednesday",
                "start_time": "10:00",
                "end_time": "11:00",
                "type": "Lecture",
            }
        ]

        service = _CalendarService([])

        start = datetime(2026, 8, 18, 10, 30)  # Tuesday
        end = datetime(2026, 8, 18, 11, 30)

        result = check_conflicts(service, start, end, user_id=1)

        self.assertFalse(result["conflict"])

    def test_no_user_id_only_checks_google_calendar(self):
        service = _CalendarService([])

        start = datetime(2026, 8, 18, 10, 30)
        end = datetime(2026, 8, 18, 11, 30)

        result = check_conflicts(service, start, end)  # user_id defaults to None

        self.assertFalse(result["conflict"])


if __name__ == "__main__":
    unittest.main()