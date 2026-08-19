import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace

from backend.tools.analytics import (
    calendar_utilization_percent,
    assignments_complete_percent,
    exam_has_study_sessions,
    exams_with_study_plan_percent,
)


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


class CalendarUtilizationTests(unittest.TestCase):
    def test_none_when_no_calendar_connected(self):
        self.assertIsNone(calendar_utilization_percent(None))

    def test_fully_free_week_is_zero_percent_utilized(self):
        self.assertEqual(calendar_utilization_percent(98.0), 0)

    def test_fully_busy_week_is_100_percent(self):
        self.assertEqual(calendar_utilization_percent(0.0), 100)

    def test_clamps_over_100_percent(self):
        self.assertEqual(calendar_utilization_percent(200.0), 0)


class AssignmentsCompletePercentTests(unittest.TestCase):
    def test_none_when_no_assignments(self):
        self.assertIsNone(assignments_complete_percent([]))

    def test_computes_percentage(self):
        assignments = [
            {"completed": True},
            {"completed": True},
            {"completed": False},
            {"completed": False},
        ]
        self.assertEqual(assignments_complete_percent(assignments), 50.0)


class ExamHasStudySessionsTests(unittest.TestCase):
    def test_false_for_a_past_exam(self):
        exam = SimpleNamespace(subject="DBMS", exam_date=datetime.now() - timedelta(days=1))
        self.assertFalse(exam_has_study_sessions(_CalendarService([]), exam))

    def test_true_when_a_matching_study_event_exists(self):
        exam = SimpleNamespace(subject="DBMS", exam_date=datetime.now() + timedelta(days=5))
        service = _CalendarService([{
            "summary": "Study: DBMS",
            "start": {"dateTime": (datetime.now() + timedelta(days=1)).isoformat() + "+05:30"},
            "end": {"dateTime": (datetime.now() + timedelta(days=1, hours=1)).isoformat() + "+05:30"},
        }])
        self.assertTrue(exam_has_study_sessions(service, exam))

    def test_false_when_no_matching_event(self):
        exam = SimpleNamespace(subject="DBMS", exam_date=datetime.now() + timedelta(days=5))
        service = _CalendarService([{
            "summary": "Study: NLP",
            "start": {"dateTime": (datetime.now() + timedelta(days=1)).isoformat() + "+05:30"},
            "end": {"dateTime": (datetime.now() + timedelta(days=1, hours=1)).isoformat() + "+05:30"},
        }])
        self.assertFalse(exam_has_study_sessions(service, exam))


class ExamsWithStudyPlanPercentTests(unittest.TestCase):
    def test_none_when_no_upcoming_exams(self):
        self.assertIsNone(exams_with_study_plan_percent(_CalendarService([]), []))

    def test_none_when_no_service(self):
        exam = SimpleNamespace(subject="DBMS", exam_date=datetime.now() + timedelta(days=5))
        self.assertIsNone(exams_with_study_plan_percent(None, [exam]))


if __name__ == "__main__":
    unittest.main()