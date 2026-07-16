from datetime import datetime, timedelta


def create_event(service, summary, start_time, end_time, description="", location="", timezone="Asia/Kolkata"):
    """
    Creates a new event on the user's primary Google Calendar.
    """
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': timezone,
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event


def list_events(service, max_results=10):
    """
    Fetches upcoming events from the user's primary Google Calendar.
    """
    now = datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events


def format_event_summary(event):
    """
    Formats an event into a readable string.
    """
    start = event['start'].get('dateTime', event['start'].get('date'))
    summary = event.get('summary', 'No Title')
    return f"{start} — {summary}"