from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json",
    SCOPES
)

creds = flow.run_local_server(port=0)

service = build("calendar", "v3", credentials=creds)

print("✅ Google Calendar Connected!")

calendar_list = service.calendarList().list().execute()

for calendar in calendar_list["items"]:
    print(calendar["summary"])