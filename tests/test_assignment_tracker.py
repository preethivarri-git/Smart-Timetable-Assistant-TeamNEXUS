import unittest
from datetime import datetime, timedelta
from backend.database import storage
from backend.tools.assignment_tracker import AssignmentTracker

# A sentinel id unlikely to collide with a real user, since these tests
# write into the same scheduler.db the app uses. We clean up in tearDown
# regardless.
TEST_USER_ID = -999001


class AssignmentTrackerTests(unittest.TestCase):
    def setUp(self):
        self.tracker = AssignmentTracker(TEST_USER_ID)
        self._created_ids = []

    def tearDown(self):
        for assignment_id in self._created_ids:
            storage.delete_assignment(assignment_id, TEST_USER_ID)

    def test_empty_storage_is_initialized(self):
        self.assertEqual(self.tracker.load_assignments(), [])

    def test_add_and_complete_assignment(self):
        new_id = self.tracker.add_assignment("DBMS Assignment", "2026-07-25")
        self._created_ids.append(new_id)

        self.tracker.mark_completed(new_id)

        assignments = self.tracker.load_assignments()
        self.assertEqual(len(assignments), 1)
        self.assertTrue(assignments[0]["completed"])

        def test_check_due_assignments_respects_days_before(self):

            far_deadline = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            new_id = self.tracker.add_assignment("Far Off Assignment", far_deadline)
            self._created_ids.append(new_id)

            self.assertEqual(self.tracker.check_due_assignments(days_before=2), [])
            due = self.tracker.check_due_assignments(days_before=6)
            self.assertEqual(len(due), 1)
            self.assertEqual(due[0]["title"], "Far Off Assignment")
    def test_show_assignments_returns_a_summary_string(self):
        new_id = self.tracker.add_assignment("DBMS Assignment", "2026-07-25")
        self._created_ids.append(new_id)

        summary = self.tracker.show_assignments()
        self.assertIn("DBMS Assignment", summary)

    def test_show_assignments_when_empty(self):
        summary = self.tracker.show_assignments()
        self.assertIn("don't have any assignments", summary)

    def test_mark_completed_returns_a_status_message(self):
        new_id = self.tracker.add_assignment("DBMS Assignment", "2026-07-25")
        self._created_ids.append(new_id)

        message = self.tracker.mark_completed(new_id)
        self.assertIn("marked completed", message.lower())

    def test_mark_completed_unknown_id_returns_not_found(self):
        message = self.tracker.mark_completed(999999)
        self.assertIn("not found", message.lower())

    def test_remove_assignment_returns_a_status_message(self):
        new_id = self.tracker.add_assignment("DBMS Assignment", "2026-07-25")
        message = self.tracker.remove_assignment(new_id)
        self.assertIn("removed", message.lower())
        # Not added to self._created_ids — it's already deleted, cleanup would no-op anyway.

if __name__ == "__main__":
    unittest.main()