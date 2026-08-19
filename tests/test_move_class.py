import unittest
from unittest.mock import patch

from backend.agent.scheduler_agent import _handle_move_class, _parse_time_field
from datetime import time


class ParseTimeFieldTests(unittest.TestCase):
    def test_parses_24_hour_format(self):
        self.assertEqual(_parse_time_field("14:00"), time(14, 0))

    def test_parses_12_hour_format(self):
        self.assertEqual(_parse_time_field("2:00 PM"), time(14, 0))

    def test_returns_none_for_garbage(self):
        self.assertIsNone(_parse_time_field("not a time"))

    def test_returns_none_for_none(self):
        self.assertIsNone(_parse_time_field(None))


class HandleMoveClassTests(unittest.TestCase):
    def setUp(self):
        self.schedule = [
            {
                "id": 1,
                "name": "DBMS",
                "day": "Tuesday",
                "start_time": "10:00",
                "end_time": "11:00",
            },
            {
                "id": 2,
                "name": "DBMS Lab",
                "day": "Wednesday",
                "start_time": "14:00",
                "end_time": "16:00",
            },
        ]

    @patch("backend.agent.scheduler_agent.update_class")
    @patch("backend.agent.scheduler_agent.load_schedule")
    def test_moves_class_to_new_day_and_time(self, mock_load, mock_update):
        mock_load.return_value = self.schedule

        result = _handle_move_class(
            {"class_query": "DBMS", "new_day": "Thursday", "new_start_time": "15:00", "new_end_time": "16:00"},
            user_id=1,
        )

        # "DBMS" matches both "DBMS" and "DBMS Lab" via substring — expect a clarification, not a silent pick.
        self.assertIn("more than one class", result)
        mock_update.assert_not_called()

    @patch("backend.agent.scheduler_agent.update_class")
    @patch("backend.agent.scheduler_agent.load_schedule")
    def test_moves_uniquely_matched_class(self, mock_load, mock_update):
        mock_load.return_value = [self.schedule[0]]  # only one class this time

        result = _handle_move_class(
            {"class_query": "dbms", "new_day": "Thursday", "new_start_time": "15:00", "new_end_time": "16:00"},
            user_id=1,
        )

        self.assertIn("Moved", result)
        mock_update.assert_called_once_with(
            1, 1, day_of_week="Thursday", start_time="15:00", end_time="16:00"
        )

    @patch("backend.agent.scheduler_agent.load_schedule")
    def test_no_match_returns_clear_message(self, mock_load):
        mock_load.return_value = self.schedule

        result = _handle_move_class(
            {"class_query": "physics", "new_day": "Thursday"}, user_id=1
        )

        self.assertIn("couldn't find", result)

    @patch("backend.agent.scheduler_agent.update_class")
    @patch("backend.agent.scheduler_agent.load_schedule")
    def test_invalid_new_time_is_rejected(self, mock_load, mock_update):
        mock_load.return_value = [self.schedule[0]]

        result = _handle_move_class(
            {"class_query": "dbms", "new_day": "Thursday", "new_start_time": "16:00", "new_end_time": "15:00"},
            user_id=1,
        )

        self.assertIn("End time must be after start time", result)
        mock_update.assert_not_called()


if __name__ == "__main__":
    unittest.main()