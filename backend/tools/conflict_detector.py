from datetime import datetime, timedelta

from backend.calendar_service.google_calendar import (
    get_events_between,
    normalize_calendar_datetime,
)


def check_conflicts(service, start_time, end_time):
    """
    Check if a new event overlaps with existing calendar events.

    Args:
        service: Google Calendar service object
        start_time (datetime): Proposed start time
        end_time (datetime): Proposed end time

    Returns:
        {
            "conflict": bool,
            "events": list,
            "suggested_start": datetime | None,
            "suggested_end": datetime | None
        }
    """

    start_time = normalize_calendar_datetime(start_time)
    end_time = normalize_calendar_datetime(end_time)

    events = get_events_between(service, start_time, end_time)

    conflicts = []

    for event in events:

        existing_start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        existing_end = event["end"].get(
            "dateTime",
            event["end"].get("date")
        )

        existing_start = normalize_calendar_datetime(
            datetime.fromisoformat(existing_start.replace("Z", "+00:00"))
        )

        existing_end = normalize_calendar_datetime(
            datetime.fromisoformat(existing_end.replace("Z", "+00:00"))
        )

        if start_time < existing_end and end_time > existing_start:
            conflicts.append(event)

    if not conflicts:
        return {
            "conflict": False,
            "events": [],
            "suggested_start": None,
            "suggested_end": None
        }

    # Suggest next available slot after last conflicting event
    latest_end = max(
        normalize_calendar_datetime(
            datetime.fromisoformat(
                e["end"]["dateTime"].replace("Z", "+00:00")
            )
        )
        for e in conflicts
    )

    duration = end_time - start_time

    return {
        "conflict": True,
        "events": conflicts,
        "suggested_start": latest_end,
        "suggested_end": latest_end + duration
    }