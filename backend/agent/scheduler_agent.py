from datetime import datetime, timedelta

from backend.agent.nlp_parser import parse_schedule_request
from backend.calendar_service.auth import get_calendar_service
from backend.calendar_service.google_calendar import create_event
from backend.tools.conflict_detector import check_conflicts
from backend.tools.availability import (
    find_free_slots,
    print_free_slots,
)
from backend.tools.query_handler import QueryHandler


def schedule(user_input):
    """
    Main AI Scheduling Agent.

    Handles:
    - Create Event
    - Conflict Detection
    - Free Time Queries
    - Schedule Queries
    """

    try:

        service = get_calendar_service()
        query = QueryHandler(service)

        command = user_input.lower().strip()

        # ==================================================
        # FREE TIME
        # ==================================================

        if (
            "free time" in command
            or "free slot" in command
            or "availability" in command
        ):

            day = datetime.now()

            if "tomorrow" in command:
                day += timedelta(days=1)

            slots = find_free_slots(
                service,
                day
            )

            print_free_slots(slots)
            return

        # ==================================================
        # SHOW SCHEDULE
        # ==================================================

        elif (
            "schedule today" in command
            or "today schedule" in command
        ):

            query.show_schedule(0)
            return

        elif (
            "schedule tomorrow" in command
            or "tomorrow schedule" in command
        ):

            query.show_schedule(1)
            return

        # ==================================================
        # NEXT EVENT
        # ==================================================

        elif (
            "next meeting" in command
            or "next event" in command
        ):

            query.next_event()
            return

        # ==================================================
        # EVENTS AFTER TIME
        # ==================================================

        elif "after 5" in command:

            query.events_after(17)
            return

        elif "after 6" in command:

            query.events_after(18)
            return

        # ==================================================
        # BUSY HOURS
        # ==================================================

        elif "busy" in command:

            offset = 0

            if "tomorrow" in command:
                offset = 1

            query.busy_hours(offset)
            return

        # ==================================================
        # CHECK EVENTS
        # ==================================================

        elif (
            "anything tomorrow" in command
            or "do i have anything tomorrow" in command
        ):

            query.has_events(1)
            return

        elif (
            "anything today" in command
            or "do i have anything today" in command
        ):

            query.has_events(0)
            return

        # ==================================================
        # CREATE EVENT
        # ==================================================

        data = parse_schedule_request(user_input)

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

        # ==================================================
        # CONFLICT FOUND
        # ==================================================

        if result["conflict"]:

            print("\n⚠ Conflict Detected!\n")

            for event in result["events"]:

                title = event.get(
                    "summary",
                    "Untitled Event"
                )

                event_start = event["start"].get(
                    "dateTime",
                    event["start"].get("date")
                )

                event_end = event["end"].get(
                    "dateTime",
                    event["end"].get("date")
                )

                print(title)
                print(
                    f"{event_start}  -->  {event_end}\n"
                )

            print("Suggested Time")

            print(
                f"{result['suggested_start']}"
            )

            print("to")

            print(
                f"{result['suggested_end']}"
            )

            choice = input(
                "\nSchedule at suggested time instead? (y/n): "
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

                print(
                    "\nEvent Cancelled.\n"
                )

            return

        # ==================================================
        # CREATE EVENT
        # ==================================================

        create_event(
            service,
            data["summary"],
            start,
            end,
        )

        print(
            "\n✅ Event Created Successfully!\n"
        )

    except Exception as e:

        print("\nScheduler Error:\n")
        print(e)