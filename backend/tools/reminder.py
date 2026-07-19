import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from backend.tools.assignment_tracker import AssignmentTracker


load_dotenv()


class ReminderService:
    """Email reminders for assignments that are due within two days."""

    def __init__(
        self,
        tracker=None,
        email_address=None,
        email_password=None,
        smtp_host="smtp.gmail.com",
        smtp_port=465,
    ):
        self.tracker = tracker or AssignmentTracker()
        self.email_address = email_address or os.getenv("EMAIL_ADDRESS")
        self.email_password = email_password or os.getenv("EMAIL_PASSWORD")
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_due_assignment_reminders(self, recipient):
        """Send one reminder per incomplete assignment due within two days.

        Returns the number of messages sent.  No email is sent when there are
        no upcoming assignments.
        """

        due_assignments = self.tracker.check_due_assignments()

        if not due_assignments:
            return 0

        if not self.email_address or not self.email_password:
            raise ValueError(
                "Set EMAIL_ADDRESS and EMAIL_PASSWORD before sending reminders."
            )

        with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
            smtp.login(self.email_address, self.email_password)

            for assignment in due_assignments:
                days_left = assignment["days_left"]
                day_label = "today" if days_left == 0 else f"in {days_left} day(s)"

                message = EmailMessage()
                message["From"] = self.email_address
                message["To"] = recipient
                message["Subject"] = f"Assignment reminder: {assignment['title']}"
                message.set_content(
                    f"{assignment['title']} is due {day_label} "
                    f"({assignment['deadline']})."
                )
                smtp.send_message(message)

        return len(due_assignments)
