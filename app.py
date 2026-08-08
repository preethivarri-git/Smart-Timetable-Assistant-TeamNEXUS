from datetime import datetime, timedelta

import streamlit as st
from googleapiclient.discovery import build

from backend.agent.scheduler_agent import schedule
from backend.calendar_service.auth import authenticate_google
from backend.calendar_service.google_calendar import create_event, list_events
from backend.calendar_service.schedule_manager import load_schedule
from backend.database.storage import init_db
from backend.tools.assignment_tracker import AssignmentTracker
from components.analytics import render_analytics
from components.calendar import render_timetable
from components.cards import event_list, render_topbar
from components.chat import render_agent
from components.hero import render_hero
from components.login import require_login
from components.sidebar import render_sidebar
from components.styles import inject_styles


st.set_page_config(page_title="Smart Scheduler", page_icon="S", layout="wide", initial_sidebar_state="expanded")
init_db()
require_login()
inject_styles()

if "service" not in st.session_state:
    st.session_state.service = None


def calendar_events():
    if not st.session_state.service:
        return []
    try:
        return list_events(st.session_state.service, max_results=12)
    except Exception as error:
        st.warning(f"Calendar unavailable: {error}")
        return []


def connect_calendar():
    try:
        credentials = authenticate_google(st.session_state.user_id)
        st.session_state.service = build("calendar", "v3", credentials=credentials)
        st.success("Google Calendar connected.")
    except Exception as error:
        st.error(f"Could not connect Calendar: {error}")


page, connect_clicked = render_sidebar()
if connect_clicked:
    connect_calendar()
render_topbar()

tracker = AssignmentTracker(st.session_state.user_id)
assignments = tracker.load_assignments()
events = calendar_events()
due = tracker.check_due_assignments()

if page == "Home":
    render_hero()
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    sync_clicked = render_timetable()
    if sync_clicked:
        connect_calendar()
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_agent(schedule)

elif page == "Courses":
    st.markdown("<div class='eyebrow'>Calendar</div><h1>Your schedule, in one view</h1>", unsafe_allow_html=True)
    if not st.session_state.service:
        st.info("Connect Google Calendar from the sidebar to load live events.")
    st.markdown("<div class='glass-card'><div class='section-title'><h3>All upcoming events</h3></div>", unsafe_allow_html=True)
    event_list(events, "No upcoming events. Create one and reclaim your calendar.")
    st.markdown("</div>", unsafe_allow_html=True)
    with st.expander("Create a calendar event"):
        if not st.session_state.service:
            st.info("Connect Google Calendar first.")
        else:
            with st.form("calendar_event_form", clear_on_submit=True):
                title = st.text_input("Event title")
                event_date, event_time = st.columns(2)
                date = event_date.date_input("Date")
                time = event_time.time_input("Start time")
                duration = st.number_input("Duration (minutes)", min_value=15, max_value=480, value=60, step=15)
                if st.form_submit_button("Create event"):
                    if not title.strip():
                        st.warning("Enter an event title.")
                    else:
                        start = datetime.combine(date, time)
                        create_event(st.session_state.service, title.strip(), start, start + timedelta(minutes=duration))
                        st.success("Event created.")

elif page == "Assignments":
    st.markdown("<div class='eyebrow'>Academic workflow</div><h1>Assignment tracker</h1>", unsafe_allow_html=True)
    with st.form("assignment_form", clear_on_submit=True):
        first, second = st.columns([2, 1])
        title = first.text_input("Assignment title")
        deadline = second.date_input("Deadline", min_value=datetime.now().date())
        if st.form_submit_button("Add assignment"):
            if title.strip():
                tracker.add_assignment(title.strip(), deadline.isoformat())
                st.success("Assignment added.")
                st.rerun()
            else:
                st.warning("Enter an assignment title.")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if assignments:
        for assignment in assignments:
            status = "Completed" if assignment["completed"] else f"Due {assignment['deadline']}"
            row, action = st.columns([5, 1])
            row.markdown(f"<div class='event-row'><span class='event-dot'></span><div><div class='event-title'>{assignment['title']}</div><div class='event-time'>{status}</div></div></div>", unsafe_allow_html=True)
            if not assignment["completed"] and action.button("Done", key=f"done_{assignment['id']}"):
                tracker.mark_completed(assignment["id"])
                st.rerun()
    else:
        st.markdown("<p class='muted'>No assignments yet. Add a deadline to stay ahead.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Analytics":
    st.markdown("<div class='eyebrow'>Insights</div><h1>Planning analytics</h1>", unsafe_allow_html=True)
    open_assignments = len([item for item in assignments if not item["completed"]])
    render_analytics(len(events), len(load_schedule(st.session_state.user_id)), open_assignments)

else:  # Settings
    st.markdown(
        "<div class='eyebrow'>Workspace</div><h1>Settings</h1>"
        "<div class='glass-card'><h3>Appearance</h3>"
        "<p class='muted'>Smart Scheduler uses a clean, light workspace theme.</p></div>",
        unsafe_allow_html=True,
    )