"""
backend/tools/assignment_tracker.py

DB-backed replacement for the old shared assignments.json version. Every
assignment is scoped to a single user via storage.py's Assignment table,
so one user's assignments never leak into another user's view.

AssignmentTracker takes user_id once, at construction time, so every other
method signature below is unchanged from the old JSON-based version --
call sites only need to change `AssignmentTracker()` to `AssignmentTracker(user_id)`.
"""

from datetime import datetime

from backend.database import storage


class AssignmentTracker:

    def __init__(self, user_id):
        if user_id is None:
            raise ValueError("AssignmentTracker requires a user_id")
        self.user_id = user_id

    # -----------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------

    def _to_dict(self, row):
        """Translate an Assignment ORM row into the old JSON-style dict shape."""
        return {
            "id": row.id,
            "title": row.title,
            "deadline": row.due_date.strftime("%Y-%m-%d") if row.due_date else "",
            "completed": row.status == "done",
        }

    def load_assignments(self):
        """Load this user's assignments."""
        rows = storage.get_assignments(self.user_id)
        return [self._to_dict(r) for r in rows]

    # -----------------------------------------------------
    # CRUD Operations
    # -----------------------------------------------------

    def add_assignment(self, title, deadline):
        """
        Add a new assignment for this user.

        deadline format:
        YYYY-MM-DD
        """
        due_date = datetime.strptime(deadline, "%Y-%m-%d")
        new_id = storage.add_assignment(self.user_id, title, None, due_date)
        print("\nAssignment added successfully.\n")
        return new_id

    # -----------------------------------------------------

    def show_assignments(self):
        """Display all of this user's assignments."""

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
        """Delete assignment using ID. Scoped to this user."""

        ok = storage.delete_assignment(assignment_id, self.user_id)

        if ok:
            print("\nAssignment Removed.\n")
        else:
            print("\nAssignment Not Found.\n")

    # -----------------------------------------------------

    def mark_completed(self, assignment_id):
        """Mark assignment as completed. Scoped to this user."""

        ok = storage.update_assignment_status(assignment_id, self.user_id, "done")

        if ok:
            print(
                "\nAssignment Marked Completed.\n"
            )

        else:

            print(
                "\nAssignment Not Found.\n"
            )

    # -----------------------------------------------------

    def pending_assignments(self):
        """Show only this user's pending assignments."""

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
        """Show this user's completed assignments."""

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
        Returns this user's assignments due within
        the next two days.
        """

        assignments = self.load_assignments()

        today = datetime.now().date()

        due = []

        for assignment in assignments:

            if assignment["completed"]:
                continue

            if not assignment["deadline"]:
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