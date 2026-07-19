from datetime import datetime
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = "Asia/Kolkata"


def normalize_calendar_datetime(value, timezone=DEFAULT_TIMEZONE):
    """Return an offset-aware datetime suitable for the Calendar API.

    Google Calendar requires ``timeMin`` and ``timeMax`` to be RFC 3339
    timestamps.  A naive ``datetime.isoformat()`` has no UTC offset, so the
    API rejects it with a 400 Bad Request.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=ZoneInfo(timezone))
    return value


def create_event(
    service,
    summary,
    start_time,
    end_time,
    description="",
    location="",
    timezone=DEFAULT_TIMEZONE
):
    """
    Creates a new event in Google Calendar.
    """

    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": normalize_calendar_datetime(start_time, timezone).isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": normalize_calendar_datetime(end_time, timezone).isoformat(),
            "timeZone": timezone,
        },
    }

    created_event = (
        service.events()
        .insert(calendarId="primary", body=event)
        .execute()
    )

    return created_event


def list_events(service, max_results=10):
    """
    Returns upcoming events.
    """

    now = datetime.utcnow().isoformat() + "Z"

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events_result.get("items", [])


def get_events_between(service, start_time, end_time):
    """
    Returns all events between two datetimes.
    Used for conflict detection.
    """

    start_time = normalize_calendar_datetime(start_time)
    end_time = normalize_calendar_datetime(end_time)

    if end_time <= start_time:
        raise ValueError("end_time must be after start_time")

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events_result.get("items", [])


def get_events_for_day(service, start_time, end_time):
    """Return events in the supplied day or time-range window.

    The name is used by availability and schedule-query tools.  The supplied
    boundaries are forwarded to the single range-query implementation so they
    receive the same RFC 3339 timezone normalization.
    """

    return get_events_between(service, start_time, end_time)


def format_event_summary(event):
    """
    Returns a readable event summary.
    """

    start = event["start"].get(
        "dateTime",
        event["start"].get("date")
    )

    end = event["end"].get(
        "dateTime",
        event["end"].get("date")
    )

    summary = event.get("summary", "No Title")

    return f"{summary}\nStart: {start}\nEnd: {end}"
