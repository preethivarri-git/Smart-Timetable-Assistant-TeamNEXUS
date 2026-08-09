from datetime import datetime, timedelta

import streamlit as st
from googleapiclient.discovery import build

from backend.agent.scheduler_agent import schedule
from backend.calendar_service.auth import authenticate_google
from backend.calendar_service.google_calendar import create_event, list_events
from backend.calendar_service.schedule_manager import list_semesters, load_schedule
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
    semesters = list_semesters(st.session_state.user_id)
    selected = st.session_state.get("semester_select")
    current_semester = selected if selected and selected != "+ New semester" else (semesters[0] if semesters else "Unassigned")
    render_hero(semester=current_semester)
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
    PRIORITY_COLORS = {"high": "#e5484d", "medium": "#f5a623", "low": "#30a46c"}
    PRIORITY_LABELS = {"high": "High", "medium": "Medium", "low": "Low"}

    with st.form("assignment_form", clear_on_submit=True):
        first, second, third = st.columns([2, 1, 1])
        title = first.text_input("Assignment title")
        deadline = second.date_input("Deadline", min_value=datetime.now().date())
        priority = third.selectbox("Priority", ["high", "medium", "low"], index=1, format_func=lambda p: PRIORITY_LABELS[p])
        if st.form_submit_button("Add assignment"):
            if title.strip():
                tracker.add_assignment(title.strip(), deadline.isoformat(), priority)
                st.success("Assignment added.")
                st.rerun()
            else:
                st.warning("Enter an assignment title.")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if assignments:
        for assignment in assignments:
            status = "Completed" if assignment["completed"] else f"Due {assignment['deadline']}"
            p = assignment.get("priority", "medium")
            color = PRIORITY_COLORS.get(p, "#f5a623")
            badge = f"<span style='background:{color}22;color:{color};border:1px solid {color}55;border-radius:999px;padding:2px 10px;font-size:.72rem;font-weight:600;margin-left:8px'>{PRIORITY_LABELS.get(p, 'Medium')}</span>"
            row, action, prio_col = st.columns([4, 1, 1.3])
            row.markdown(f"<div class='event-row'><span class='event-dot'></span><div><div class='event-title'>{assignment['title']}{badge}</div><div class='event-time'>{status}</div></div></div>", unsafe_allow_html=True)
            if not assignment["completed"] and action.button("Done", key=f"done_{assignment['id']}"):
                tracker.mark_completed(assignment["id"])
                st.rerun()
            new_priority = prio_col.selectbox(
                "Priority", ["high", "medium", "low"], index=["high", "medium", "low"].index(p),
                key=f"prio_{assignment['id']}", label_visibility="collapsed",
                format_func=lambda x: PRIORITY_LABELS[x],
            )
            if new_priority != p:
                tracker.set_priority(assignment["id"], new_priority)
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