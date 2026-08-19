import unittest

from backend.database import storage

TEST_USER_ID = -999003


class NotificationSettingsTests(unittest.TestCase):
    def tearDown(self):
        with storage.get_session() as db:
            existing = db.query(storage.NotificationSettings).filter(
                storage.NotificationSettings.user_id == TEST_USER_ID
            ).first()
            if existing:
                db.delete(existing)

    def test_defaults_when_nothing_saved_yet(self):
        settings = storage.get_notification_settings(TEST_USER_ID)
        self.assertFalse(settings["email_reminders_enabled"])
        self.assertEqual(settings["reminder_days_before"], 2)
        self.assertEqual(settings["notification_email"], "")

    def test_save_and_retrieve(self):
        storage.save_notification_settings(
            TEST_USER_ID, True, 4, "student@example.com"
        )

        settings = storage.get_notification_settings(TEST_USER_ID)
        self.assertTrue(settings["email_reminders_enabled"])
        self.assertEqual(settings["reminder_days_before"], 4)
        self.assertEqual(settings["notification_email"], "student@example.com")

    def test_save_twice_overwrites_instead_of_duplicating(self):
        storage.save_notification_settings(TEST_USER_ID, True, 2, "a@example.com")
        storage.save_notification_settings(TEST_USER_ID, False, 7, "b@example.com")

        settings = storage.get_notification_settings(TEST_USER_ID)
        self.assertFalse(settings["email_reminders_enabled"])
        self.assertEqual(settings["reminder_days_before"], 7)
        self.assertEqual(settings["notification_email"], "b@example.com")

    def test_mark_reminders_sent_today_sets_a_date(self):
        storage.save_notification_settings(TEST_USER_ID, True, 2, "a@example.com")
        storage.mark_reminders_sent_today(TEST_USER_ID)

        settings = storage.get_notification_settings(TEST_USER_ID)
        self.assertIsNotNone(settings["last_sent_date"])


if __name__ == "__main__":
    unittest.main()