import smtplib
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from backend.database import storage
from backend.tools.assignment_tracker import AssignmentTracker
from backend.tools.reminder import ReminderService

TEST_USER_ID = -999002


class ReminderServiceTests(unittest.TestCase):
    def setUp(self):
        self.tracker = AssignmentTracker(TEST_USER_ID)
        self._created_ids = []

    def tearDown(self):
        for assignment_id in self._created_ids:
            storage.delete_assignment(assignment_id, TEST_USER_ID)

    @patch("backend.tools.reminder.smtplib.SMTP_SSL")
    def test_sends_a_reminder_for_an_assignment_due_today(self, smtp_ssl):
        new_id = self.tracker.add_assignment(
            "DBMS Assignment", datetime.now().strftime("%Y-%m-%d")
        )
        self._created_ids.append(new_id)

        smtp = MagicMock()
        smtp_ssl.return_value.__enter__.return_value = smtp
        service = ReminderService(
            tracker=self.tracker,
            email_address=" sender@example.com ",
            email_password=" test-password \n",
        )

        sent = service.send_due_assignment_reminders("student@example.com")

        self.assertEqual(sent, 1)
        self.assertEqual(service.email_address, "sender@example.com")
        self.assertEqual(service.email_password, "test-password")
        smtp.login.assert_called_once_with("sender@example.com", "test-password")
        smtp.send_message.assert_called_once()

    @patch("backend.tools.reminder.smtplib.SMTP_SSL")
    def test_raises_clear_message_for_gmail_authentication_errors(self, smtp_ssl):
        new_id = self.tracker.add_assignment(
            "DBMS Assignment", datetime.now().strftime("%Y-%m-%d")
        )
        self._created_ids.append(new_id)

        smtp = MagicMock()
        smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
        smtp_ssl.return_value.__enter__.return_value = smtp

        service = ReminderService(
            tracker=self.tracker,
            email_address="sender@example.com",
            email_password="wrong-password",
        )

        with self.assertRaisesRegex(ValueError, "App Password|Gmail"):
            service.send_due_assignment_reminders("student@example.com")

    def test_does_not_require_email_settings_when_nothing_is_due(self):
        service = ReminderService(tracker=self.tracker)

        self.assertEqual(
            service.send_due_assignment_reminders("student@example.com"), 0
        )


if __name__ == "__main__":
    unittest.main()