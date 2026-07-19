import tempfile
import unittest
from pathlib import Path

from backend.tools.assignment_tracker import AssignmentTracker


class AssignmentTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "assignments.json"
        self.tracker = AssignmentTracker(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_empty_storage_is_initialized(self):
        self.assertEqual(self.tracker.load_assignments(), [])

    def test_add_and_complete_assignment(self):
        self.tracker.add_assignment("DBMS Assignment", "2026-07-25")
        self.tracker.mark_completed(1)

        assignments = self.tracker.load_assignments()
        self.assertEqual(len(assignments), 1)
        self.assertTrue(assignments[0]["completed"])


if __name__ == "__main__":
    unittest.main()
