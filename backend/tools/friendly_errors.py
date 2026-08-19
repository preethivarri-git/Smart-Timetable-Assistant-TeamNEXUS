"""
backend/tools/friendly_errors.py

Turns raw Google Calendar / Gemini exceptions into short, actionable
messages for the UI, instead of dumping the raw exception text at the
user. Used by both the chat agent (scheduler_agent.py) and the direct
calendar actions in app.py, so the wording stays consistent everywhere.
"""

from googleapiclient.errors import HttpError


def friendly_calendar_error(error):
    """error: an HttpError raised by the Google Calendar API client."""
    status = getattr(getattr(error, "resp", None), "status", None)

    if status in (401, 403):
        return (
            "Your Google Calendar connection needs to be refreshed. "
            "Please click 'Connect Google Calendar' in the sidebar."
        )
    if status == 429:
        return "Google Calendar is rate-limiting requests right now. Please try again in a minute."
    if status in (500, 502, 503, 504):
        return "Google Calendar is temporarily unavailable. Please try again shortly."
    return f"Google Calendar returned an error (status {status}). Please try again."


def friendly_missing_credentials_message():
    return (
        "Google Calendar isn't set up yet — credentials.json is missing from the "
        "project folder. Please add it and restart the app."
    )