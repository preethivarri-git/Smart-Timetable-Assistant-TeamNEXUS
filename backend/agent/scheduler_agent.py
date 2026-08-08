from datetime import datetime, timedelta

from backend.agent.nlp_parser import parse_schedule_request
from backend.calendar_service.auth import get_calendar_service
from backend.calendar_service.google_calendar import create_event
from backend.tools.assignment_tracker import AssignmentTracker
from backend.tools.availability import (
    find_free_slots,
    print_free_slots,
)
from backend.tools.conflict_detector import check_conflicts
from backend.tools.query_handler import QueryHandler


def schedule(user_input, user_id):
    """
    Main AI Scheduling Agent
    """

    try:

        service = get_calendar_service(user_id)
        query = QueryHandler(service)
        tracker = AssignmentTracker(user_id)

        command = user_input.lower().strip()

        # ===================================================
        # Assignment Commands
        # ===================================================

        if command == "show assignments":
            tracker.show_assignments()
            return

        elif command.startswith("mark assignment"):
            try:
                assignment_id = int(command.split()[2])
                tracker.mark_completed(assignment_id)
            except Exception:
                print("\nUsage: mark assignment <id>\n")
            return

        elif command.startswith("remove assignment"):
            try:
                assignment_id = int(command.split()[2])
                tracker.remove_assignment(assignment_id)
            except Exception:
                print("\nUsage: remove assignment <id>\n")
            return

        # ===================================================
        # Free Time
        # ===================================================

        elif "free time" in command:
            day = datetime.now()
            if "tomorrow" in command:
                day += timedelta(days=1)
            slots = find_free_slots(service, day)
            print_free_slots(slots)
            return

        # ===================================================
        # Schedule Queries
        # ===================================================

        elif "schedule today" in command:
            query.show_schedule(0)
            return

        elif "schedule tomorrow" in command:
            query.show_schedule(1)
            return

        elif "next meeting" in command or "next event" in command:
            query.next_event()
            return

        elif "anything tomorrow" in command:
            query.has_events(1)
            return

        elif "busy tomorrow" in command:
            query.busy_hours(1)
            return

        # ===================================================
        # NLP
        # ===================================================

        data = parse_schedule_request(user_input)

        # ===================================================
        # Assignment Intent
        # ===================================================

        if data["intent"] == "assignment":
            tracker.add_assignment(data["title"], data["deadline"])
            return

        # ===================================================
        # Event Intent
        # ===================================================

        start = datetime.now() + timedelta(days=data["day_offset"])
        start = start.replace(hour=data["hour"], minute=data["minute"], second=0, microsecond=0)
        end = start + timedelta(hours=data["duration"])

        result = check_conflicts(service, start, end)

        if result["conflict"]:
            # No console input() here — hand a structured conflict payload
            # back to the caller (chat.py) so it can render Yes/No buttons.
            conflicting_titles = [e.get("summary", "Untitled Event") for e in result["events"]]
            return {
                "status": "conflict",
                "summary": data["summary"],
                "conflicting_events": conflicting_titles,
                "suggested_start": result["suggested_start"],
                "suggested_end": result["suggested_end"],
            }

        create_event(service, data["summary"], start, end)
        return f"✅ '{data['summary']}' scheduled for {start.strftime('%A %d %b, %I:%M %p')}."

    except Exception as e:
        return f"Scheduler Error: {e}"


def confirm_conflict_schedule(summary, suggested_start, suggested_end, user_id):
    """Called from chat.py when the user clicks 'Yes' on a conflict prompt."""
    service = get_calendar_service(user_id)
    create_event(service, summary, suggested_start, suggested_end)
    return f"✅ '{summary}' scheduled for {suggested_start.strftime('%A %d %b, %I:%M %p')} (moved to avoid conflict)."