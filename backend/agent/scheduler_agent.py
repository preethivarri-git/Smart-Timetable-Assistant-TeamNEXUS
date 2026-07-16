from datetime import datetime, timedelta

from backend.agent.nlp_parser import parse_schedule_request
from backend.calendar_service.auth import get_calendar_service
from backend.calendar_service.google_calendar import create_event
from backend.tools.conflict_detector import check_conflicts


def schedule(user_input):

    try:
        data = parse_schedule_request(user_input)

        service = get_calendar_service()

        start = datetime.now() + timedelta(days=data["day_offset"])

        start = start.replace(
            hour=data["hour"],
            minute=data["minute"],
            second=0,
            microsecond=0
        )

        end = start + timedelta(hours=data["duration"])

        conflict, events = check_conflicts(
            service,
            start,
            end
        )

        if conflict:

            print("\n❌ Conflict Detected!\n")

            for event in events:
                print(
                    f"- {event.get('summary', 'No Title')}"
                )

            return

        create_event(
            service,
            data["summary"],
            start,
            end
        )

        print("\n✅ Event Created Successfully!\n")

    except Exception as e:
        print("\nScheduler Error:")
        print(e)