from datetime import datetime
import unittest
from backend.tools.availability import find_free_slots
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
    """Fake Calendar API service — no OAuth, no network."""

    def __init__(self, items):
        self._resource = _EventsResource(items)

    def events(self):
        return self._resource

class FindFreeSlotsTests(unittest.TestCase):
    def test_finds_gaps_around_a_single_event(self):
        service = _CalendarService(
            [
                {
                    "start": {"dateTime": "2026-08-18T10:00:00+05:30"},
                    "end": {"dateTime": "2026-08-18T11:00:00+05:30"},
                }
            ]
        )

        day = datetime(2026, 8, 18)  # Tuesday
        slots = find_free_slots(service, day, work_start_hour=8, work_end_hour=22)

        self.assertEqual(len(slots), 2)
        self.assertEqual((slots[0][0].hour, slots[0][1].hour), (8, 10))
        self.assertEqual((slots[1][0].hour, slots[1][1].hour), (11, 22))

    def test_no_events_returns_the_full_working_day(self):
        service = _CalendarService([])

        day = datetime(2026, 8, 19)
        slots = find_free_slots(service, day, work_start_hour=9, work_end_hour=17)

        self.assertEqual(len(slots), 1)
        self.assertEqual((slots[0][0].hour, slots[0][1].hour), (9, 17))

    def test_back_to_back_events_leave_no_gap_between_them(self):
        service = _CalendarService(
            [
                {
                    "start": {"dateTime": "2026-08-18T09:00:00+05:30"},
                    "end": {"dateTime": "2026-08-18T11:00:00+05:30"},
                },
                {
                    "start": {"dateTime": "2026-08-18T11:00:00+05:30"},
                    "end": {"dateTime": "2026-08-18T12:00:00+05:30"},
                },
            ]
        )

        day = datetime(2026, 8, 18)
        slots = find_free_slots(service, day, work_start_hour=8, work_end_hour=22)

        self.assertEqual(len(slots), 2)
        self.assertEqual((slots[0][0].hour, slots[0][1].hour), (8, 9))
        self.assertEqual((slots[1][0].hour, slots[1][1].hour), (12, 22))

if __name__ == "__main__":
    unittest.main()