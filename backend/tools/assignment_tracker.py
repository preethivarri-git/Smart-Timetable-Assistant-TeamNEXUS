import json
from datetime import datetime, timedelta
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "database" / "assignments.json"


class AssignmentTracker:

    def __init__(self, file_path=None):
        self.file_path = Path(file_path) if file_path else DATABASE_PATH
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists() or not self.file_path.read_text(encoding="utf-8").strip():
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    # -----------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------

    def load_assignments(self):
        """Load assignments from JSON."""

        with self.file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_assignments(self, assignments):
        """Save assignments to JSON."""

        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(assignments, f, indent=4)

    # -----------------------------------------------------
    # CRUD Operations
    # -----------------------------------------------------

    def add_assignment(self, title, deadline):
        """
        Add a new assignment.

        deadline format:
        YYYY-MM-DD
        """

        assignments = self.load_assignments()

        assignment = {
            "id": max((item["id"] for item in assignments), default=0) + 1,
            "title": title,
            "deadline": deadline,
            "completed": False,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        }

        assignments.append(assignment)

        self.save_assignments(assignments)

        print("\nAssignment added successfully.\n")

    # -----------------------------------------------------

    def show_assignments(self):
        """Display all assignments."""

        assignments = self.load_assignments()

        if not assignments:

            print("\nNo assignments found.\n")
            return

        print("\nAssignments\n")

        for assignment in assignments:

            status = (
                "Completed"
                if assignment["completed"]
                else "Pending"
            )

            print(
                f"ID        : {assignment['id']}"
            )

            print(
                f"Title     : {assignment['title']}"
            )

            print(
                f"Deadline  : {assignment['deadline']}"
            )

            print(
                f"Status    : {status}"
            )

            print("-" * 40)

    # -----------------------------------------------------

    def remove_assignment(self, assignment_id):
        """Delete assignment using ID."""

        assignments = self.load_assignments()

        updated = [
            a
            for a in assignments
            if a["id"] != assignment_id
        ]

        self.save_assignments(updated)

        print("\nAssignment Removed.\n")

    # -----------------------------------------------------

    def mark_completed(self, assignment_id):
        """Mark assignment as completed."""

        assignments = self.load_assignments()

        found = False

        for assignment in assignments:

            if assignment["id"] == assignment_id:

                assignment["completed"] = True
                found = True
                break

        if found:

            self.save_assignments(assignments)

            print(
                "\nAssignment Marked Completed.\n"
            )

        else:

            print(
                "\nAssignment Not Found.\n"
            )

    # -----------------------------------------------------

    def pending_assignments(self):
        """Show only pending assignments."""

        assignments = self.load_assignments()

        pending = [
            a
            for a in assignments
            if not a["completed"]
        ]

        if not pending:

            print("\nNo pending assignments.\n")
            return

        print("\nPending Assignments\n")

        for assignment in pending:

            print(
                f"{assignment['title']}"
            )

            print(
                f"Deadline : {assignment['deadline']}"
            )

            print("-" * 30)

    # -----------------------------------------------------

    def completed_assignments(self):
        """Show completed assignments."""

        assignments = self.load_assignments()

        completed = [
            a
            for a in assignments
            if a["completed"]
        ]

        if not completed:

            print("\nNo completed assignments.\n")
            return

        print("\nCompleted Assignments\n")

        for assignment in completed:

            print(
                f"{assignment['title']}"
            )

            print(
                f"Deadline : {assignment['deadline']}"
            )

            print("-" * 30)

    # -----------------------------------------------------

    def check_due_assignments(self):
        """
        Returns assignments due within
        the next two days.
        """

        assignments = self.load_assignments()

        today = datetime.now().date()

        due = []

        for assignment in assignments:

            if assignment["completed"]:
                continue

            deadline = datetime.strptime(
                assignment["deadline"],
                "%Y-%m-%d"
            ).date()

            days_left = (
                deadline - today
            ).days

            if 0 <= days_left <= 2:

                due.append(
                    {
                        "title": assignment["title"],
                        "deadline": assignment["deadline"],
                        "days_left": days_left,
                    }
                )

        return due
