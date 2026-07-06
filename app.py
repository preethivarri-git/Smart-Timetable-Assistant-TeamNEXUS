import streamlit as st
from googleapiclient.discovery import build
from auth import authenticate_google

# ---------------------------
# Streamlit Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Smart Scheduler",
    page_icon="📅",
    layout="wide"
)

# ---------------------------
# UI
# ---------------------------
st.title("📅 Smart Scheduler")
st.subheader("AI-Powered Student Scheduling Assistant")

st.write("""
Welcome to Smart Scheduler!

### Features
- 📅 Google Calendar Integration
- 📝 Timetable Management
- ⏰ Assignment Reminders
""")

# ---------------------------
# Google Authentication
# ---------------------------
if st.button("🔐 Connect Google Calendar"):

    try:
        creds = authenticate_google()

        service = build(
            "calendar",
            "v3",
            credentials=creds
        )

        calendars = service.calendarList().list().execute()

        st.success("✅ Google Calendar Connected Successfully!")

        st.subheader("Your Calendars")

        for calendar in calendars["items"]:
            st.write(f"📅 {calendar['summary']}")

    except Exception as e:
        st.error(f"Error: {e}")

st.success("🚀 Project setup completed successfully!")