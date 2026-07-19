from datetime import datetime

from backend.calendar_service.google_calendar import (
    get_events_for_day,
    normalize_calendar_datetime,
)


def find_free_slots(
    service,
    day,
    work_start_hour=8,
    work_end_hour=22,
):
    """
    Finds all free time slots for a given day.

    Args:
        service: Google Calendar service
        day: datetime object representing the day to check
        work_start_hour: Working day start hour
        work_end_hour: Working day end hour

    Returns:
        List of tuples:
        [
            (start_datetime, end_datetime),
            ...
        ]
    """

    day_start = day.replace(
        hour=work_start_hour,
        minute=0,
        second=0,
        microsecond=0,
    )

    day_end = day.replace(
        hour=work_end_hour,
        minute=0,
        second=0,
        microsecond=0,
    )

    day_start = normalize_calendar_datetime(day_start)
    day_end = normalize_calendar_datetime(day_end)

    events = get_events_for_day(
        service,
        day_start,
        day_end,
    )

    occupied = []

    for event in events:

        start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        end = event["end"].get(
            "dateTime",
            event["end"].get("date")
        )

        start = normalize_calendar_datetime(
            datetime.fromisoformat(
                start.replace("Z", "+00:00")
            )
        )

        end = normalize_calendar_datetime(
            datetime.fromisoformat(
                end.replace("Z", "+00:00")
            )
        )

        occupied.append((start, end))

    occupied.sort(key=lambda x: x[0])

    free_slots = []

    current = day_start

    for start, end in occupied:

        if current < start:
            free_slots.append((current, start))

        if end > current:
            current = end

    if current < day_end:
        free_slots.append((current, day_end))

    return free_slots


def print_free_slots(slots):
    """
    Print free slots in a readable format.
    """

    if not slots:
        print("\nNo free slots available.\n")
        return

    print("\nAvailable Free Slots\n")

    for start, end in slots:

        print(
            f"{start.strftime('%I:%M %p')}  -  {end.strftime('%I:%M %p')}"
        )