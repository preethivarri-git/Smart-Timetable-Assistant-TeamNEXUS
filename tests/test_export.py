import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace

from icalendar import Calendar

from backend.tools.export import (
    export_full_schedule_to_ics,
    assignments_to_csv,
    exams_to_csv,
)


class ExportIcsTests(unittest.TestCase):
    def test_produces_valid_parseable_ics(self):
        classes = [{"name": "DBMS", "type": "Lecture", "day": "Tuesday", "start_time": "10:00", "end_time": "11:00", "room": "309"}]
        exams = [SimpleNamespace(subject="NLP", exam_date=datetime.now() + timedelta(days=10), duration_minutes=180, required_study_hours=5, completed=False)]
        events = [{"summary": "Doctor", "start": {"dateTime": "2026-08-20T09:00:00+05:30"}, "end": {"dateTime": "2026-08-20T10:00:00+05:30"}}]

        ics_bytes = export_full_schedule_to_ics(classes, exams, events)

        # Round-trips through the real parser, not just a text match.
        parsed = Calendar.from_ical(ics_bytes)
        vevents = [c for c in parsed.walk() if c.name == "VEVENT"]

        # 12 weekly DBMS occurrences (default weeks_ahead) + 1 exam + 1 event.
        self.assertEqual(len(vevents), 14)

    def test_skips_all_day_google_events(self):
        events = [{"summary": "Holiday", "start": {"date": "2026-08-20"}, "end": {"date": "2026-08-21"}}]
        ics_bytes = export_full_schedule_to_ics([], [], events)
        parsed = Calendar.from_ical(ics_bytes)
        vevents = [c for c in parsed.walk() if c.name == "VEVENT"]
        self.assertEqual(len(vevents), 0)

    def test_skips_a_class_with_an_unparsable_time(self):
        classes = [{"name": "Broken", "day": "Monday", "start_time": "not-a-time", "end_time": "11:00"}]
        ics_bytes = export_full_schedule_to_ics(classes, [], [])
        parsed = Calendar.from_ical(ics_bytes)
        vevents = [c for c in parsed.walk() if c.name == "VEVENT"]
        self.assertEqual(len(vevents), 0)


class CsvExportTests(unittest.TestCase):
    def test_assignments_to_csv_includes_header_and_rows(self):
        assignments = [{"title": "DBMS HW", "deadline": "2026-08-25", "priority": "high", "completed": False}]
        csv_text = assignments_to_csv(assignments)
        self.assertIn("Title,Deadline,Priority,Status", csv_text)
        self.assertIn("DBMS HW", csv_text)
        self.assertIn("Pending", csv_text)

    def test_exams_to_csv_includes_header_and_rows(self):
        exams = [SimpleNamespace(subject="NLP", exam_date=datetime(2026, 9, 1, 10, 0), duration_minutes=180, required_study_hours=5, completed=False)]
        csv_text = exams_to_csv(exams)
        self.assertIn("Subject,Exam Date", csv_text)
        self.assertIn("NLP", csv_text)
        self.assertIn("2026-09-01 10:00", csv_text)


if __name__ == "__main__":
    unittest.main()