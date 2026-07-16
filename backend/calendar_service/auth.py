import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# Google Calendar permissions
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def authenticate_google():
    creds = None

    # Check if token already exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # If credentials don't exist or have expired
    if not creds or not creds.valid:

        # Refresh expired token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            # First-time login
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save token for future logins
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds