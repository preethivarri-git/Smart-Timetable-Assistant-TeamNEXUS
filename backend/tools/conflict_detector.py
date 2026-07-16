from datetime import datetime

from backend.calendar_services.google_calendar import get_events_between


def check_conflicts(service, start_time, end_time):
    """
    Checks if a new event overlaps with existing events.

    Returns:
        (False, [])               -> No conflict
        (True, conflicting_events)-> Conflict exists
    """

    events = get_events_between(service, start_time, end_time)

    conflicts = []

    for event in events:

        event_start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        event_end = event["end"].get(
            "dateTime",
            event["end"].get("date")
        )

        event_start = datetime.fromisoformat(
            event_start.replace("Z", "+00:00")
        )

        event_end = datetime.fromisoformat(
            event_end.replace("Z", "+00:00")
        )

        if start_time < event_end and end_time > event_start:
            conflicts.append(event)

    return len(conflicts) > 0, conflicts