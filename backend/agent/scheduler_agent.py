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


def schedule(user_input):
    """
    Main AI Scheduling Agent
    """

    try:

        service = get_calendar_service()
        query = QueryHandler(service)
        tracker = AssignmentTracker()

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

            slots = find_free_slots(
                service,
                day
            )

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

            tracker.add_assignment(
                data["title"],
                data["deadline"]
            )

            return

        # ===================================================
        # Event Intent
        # ===================================================

        start = datetime.now() + timedelta(
            days=data["day_offset"]
        )

        start = start.replace(
            hour=data["hour"],
            minute=data["minute"],
            second=0,
            microsecond=0,
        )

        end = start + timedelta(
            hours=data["duration"]
        )

        result = check_conflicts(
            service,
            start,
            end,
        )

        if result["conflict"]:

            print("\n⚠ Conflict Detected!\n")

            for event in result["events"]:

                print(
                    f"- {event.get('summary','Untitled Event')}"
                )

            print("\nSuggested Time")

            print(result["suggested_start"])
            print(result["suggested_end"])

            choice = input(
                "\nSchedule at suggested time? (y/n): "
            )

            if choice.lower() == "y":

                create_event(
                    service,
                    data["summary"],
                    result["suggested_start"],
                    result["suggested_end"],
                )

                print(
                    "\n✅ Event Created Successfully!\n"
                )

            else:

                print("\nEvent Cancelled.\n")

            return

        create_event(
            service,
            data["summary"],
            start,
            end,
        )

        print("\n✅ Event Created Successfully!\n")

    except Exception as e:

        print("\nScheduler Error:\n")
        print(e)