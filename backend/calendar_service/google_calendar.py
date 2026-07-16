from datetime import datetime


def create_event(
    service,
    summary,
    start_time,
    end_time,
    description="",
    location="",
    timezone="Asia/Kolkata"
):
    """
    Creates a new event in Google Calendar.
    """

    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time.isoformat(),
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