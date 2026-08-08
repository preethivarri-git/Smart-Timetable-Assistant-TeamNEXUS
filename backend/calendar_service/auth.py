import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from backend.database.storage import save_google_token, get_google_token


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


def authenticate_google(user_id):
    creds = None

    token_json = get_google_token(user_id)
    if token_json:
        creds = Credentials.from_authorized_user_info(
            json.loads(token_json),
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        save_google_token(user_id, creds.to_json())

    return creds


def get_calendar_service(user_id):
    """
    Returns authenticated Google Calendar service for a specific user.
    """

    creds = authenticate_google(user_id)

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service