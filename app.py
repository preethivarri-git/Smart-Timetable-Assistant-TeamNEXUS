import streamlit as st
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from auth import authenticate_google
from calendar_service.google_calendar import create_event, list_events, format_event_summary
from calendar_service.schedule_manager import (
    load_schedule, save_schedule, add_class, delete_class, get_color_for_class
)

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
if "service" not in st.session_state:
    st.session_state.service = None

if st.button("🔐 Connect Google Calendar"):
    try:
        creds = authenticate_google()
        service = build("calendar", "v3", credentials=creds)
        st.session_state.service = service

        calendars = service.calendarList().list().execute()

        st.success("✅ Google Calendar Connected Successfully!")
        st.subheader("Your Calendars")
        for calendar in calendars["items"]:
            st.write(f"📅 {calendar['summary']}")

    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------
# Only show event features once connected
# ---------------------------
if st.session_state.service:

    service = st.session_state.service

    st.divider()

    # ---------------------------
    # Section: View Upcoming Events
    # ---------------------------
    st.header("📋 Upcoming Events")

    if st.button("Refresh Events"):
        events = list_events(service)
        if not events:
            st.info("No upcoming events found.")
        else:
            for event in events:
                st.write(format_event_summary(event))

    # ---------------------------
    # Section: Create New Event
    # ---------------------------
    st.header("➕ Create New Event")

    with st.form("create_event_form"):
        summary = st.text_input("Event Title")
        location = st.text_input("Location (optional)")
        description = st.text_area("Description (optional)")

        col1, col2 = st.columns(2)
        with col1:
            event_date = st.date_input("Event Date")
            start_time_input = st.time_input("Start Time")
        with col2:
            duration_minutes = st.number_input("Duration (minutes)", min_value=15, value=60, step=15)

        submitted = st.form_submit_button("Create Event")

        if submitted:
            start_datetime = datetime.combine(event_date, start_time_input)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)

            created_event = create_event(
                service,
                summary=summary,
                start_time=start_datetime,
                end_time=end_datetime,
                description=description,
                location=location
            )
            st.success(f"✅ Event created: {created_event.get('summary')}")

# ---------------------------
# Section: Class Schedule
# ---------------------------
st.divider()
st.header("🗓️ Class Schedule")

# --- Add a class ---
with st.form("add_class_form"):
    st.subheader("➕ Add a Class")
    col1, col2 = st.columns(2)

    with col1:
        class_name = st.text_input("Class Name (e.g. Data Structures)")
        day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        room = st.text_input("Room (optional)")

    with col2:
        st.write("Start Time")
        sc1, sc2 = st.columns(2)
        with sc1:
            start_hour = st.number_input("Hour", min_value=0, max_value=23, value=9, step=1, key="start_hour")
        with sc2:
            start_min = st.number_input("Minute", min_value=0, max_value=59, value=0, step=1, key="start_min")

        st.write("End Time")
        ec1, ec2 = st.columns(2)
        with ec1:
            end_hour = st.number_input("Hour", min_value=0, max_value=23, value=10, step=1, key="end_hour")
        with ec2:
            end_min = st.number_input("Minute", min_value=0, max_value=59, value=0, step=1, key="end_min")

        instructor = st.text_input("Instructor (optional)")

    add_submitted = st.form_submit_button("Add Class")

    if add_submitted:
        if not class_name:
            st.warning("Please enter a class name.")
        else:
            add_class(
                name=class_name,
                day=day,
                start_time=f"{start_hour:02d}:{start_min:02d}",
                end_time=f"{end_hour:02d}:{end_min:02d}",
                room=room,
                instructor=instructor
            )
            st.success(f"✅ Added {class_name} on {day}")
            st.rerun()

# --- Display the colorful weekly grid ---
schedule = load_schedule()

if not schedule:
    st.info("No classes added yet. Use the form above to add your first class.")
else:
    st.subheader("📊 Weekly Timetable")

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    html = """
    <style>
        .timetable-container {
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding: 10px 0;
        }
        .day-column {
            min-width: 180px;
            flex: 1;
        }
        .day-header {
            text-align: center;
            font-weight: 700;
            padding: 8px;
            border-radius: 8px;
            background-color: #2C3E50;
            color: white;
            margin-bottom: 8px;
        }
        .class-card {
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 8px;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }
        .class-name {
            font-weight: 700;
            font-size: 15px;
        }
        .class-time {
            font-size: 13px;
            opacity: 0.9;
        }
        .class-meta {
            font-size: 12px;
            opacity: 0.85;
        }
    </style>
    <div class="timetable-container">
    """

    for day in days_order:
        html += f'<div class="day-column"><div class="day-header">{day}</div>'
        day_classes = sorted(
            [c for c in schedule if c["day"] == day],
            key=lambda x: x["start_time"]
        )
        if not day_classes:
            html += '<div style="text-align:center; color:#999; font-size:12px;">—</div>'
        for c in day_classes:
            color = get_color_for_class(c["name"], schedule)
            meta_line = ""
            if c.get("room"):
                meta_line += f'📍 {c["room"]} '
            if c.get("instructor"):
                meta_line += f'👤 {c["instructor"]}'
            html += f"""
            <div class="class-card" style="background-color:{color};">
                <div class="class-name">{c['name']}</div>
                <div class="class-time">{c['start_time']} - {c['end_time']}</div>
                <div class="class-meta">{meta_line}</div>
            </div>
            """
        html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    # --- Delete a class ---
    st.subheader("🗑️ Remove a Class")
    class_options = {f"{c['name']} ({c['day']} {c['start_time']})": c["id"] for c in schedule}
    to_delete = st.selectbox("Select class to remove", list(class_options.keys()))
    if st.button("Delete Selected Class"):
        delete_class(class_options[to_delete])
        st.success("Removed.")
        st.rerun()

    # --- Sync to Google Calendar ---
    st.subheader("🔄 Sync to Google Calendar")
    st.caption("This creates an event for each class on its next upcoming occurrence.")

    if st.session_state.service:
        if st.button("Sync All Classes to Google Calendar"):
            service = st.session_state.service
            today = datetime.today()
            days_map = {d: i for i, d in enumerate(days_order)}
            synced_count = 0

            for c in schedule:
                target_weekday = days_map[c["day"]]
                days_ahead = (target_weekday - today.weekday()) % 7
                days_ahead = days_ahead if days_ahead != 0 else 7
                next_date = today + timedelta(days=days_ahead)

                start_h, start_m = map(int, c["start_time"].split(":"))
                end_h, end_m = map(int, c["end_time"].split(":"))

                start_dt = next_date.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                end_dt = next_date.replace(hour=end_h, minute=end_m, second=0, microsecond=0)

                create_event(
                    service,
                    summary=c["name"],
                    start_time=start_dt,
                    end_time=end_dt,
                    description=f"Instructor: {c.get('instructor', 'N/A')}",
                    location=c.get("room", "")
                )
                synced_count += 1

            st.success(f"✅ Synced {synced_count} classes to Google Calendar!")
    else:
        st.warning("⚠️ Connect Google Calendar above first before syncing.")

st.success("🚀 Project setup completed successfully!")