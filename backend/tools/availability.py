from datetime import datetime, timedelta

from backend.calendar_services.google_calendar import get_events_between


def find_free_slots(
    service,
    day,
    work_start_hour=8,
    work_end_hour=22
):
    """
    Finds all free time slots for a given day.

    Args:
        service: Google Calendar service
        day: datetime object (date to check)
        work_start_hour: first working hour
        work_end_hour: last working hour

    Returns:
        list of tuples (start_datetime, end_datetime)
    """

    day_start = day.replace(
        hour=work_start_hour,
        minute=0,
        second=0,
        microsecond=0
    )

    day_end = day.replace(
        hour=work_end_hour,
        minute=0,
        second=0,
        microsecond=0
    )

    events = get_events_between(service, day_start, day_end)

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

        start = datetime.fromisoformat(
            start.replace("Z", "+00:00")
        ).replace(tzinfo=None)

        end = datetime.fromisoformat(
            end.replace("Z", "+00:00")
        ).replace(tzinfo=None)

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

    if not slots:
        print("No free slots available.")
        return

    print("\nFree Time Slots\n")

    for start, end in slots:
        print(
            f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"
        )