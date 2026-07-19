from datetime import datetime, timedelta

import streamlit as st
from googleapiclient.discovery import build

from backend.agent.scheduler_agent import schedule
from backend.calendar_service.auth import authenticate_google
from backend.calendar_service.google_calendar import create_event, list_events
from backend.calendar_service.schedule_manager import add_class, load_schedule
from backend.tools.assignment_tracker import AssignmentTracker
from components.analytics import render_analytics
from components.calendar import render_calendar
from components.cards import event_list, render_topbar
from components.chat import render_agent
from components.hero import render_hero, render_quick_actions
from components.sidebar import render_sidebar
from components.styles import inject_styles


st.set_page_config(page_title="Smart Scheduler", page_icon="S", layout="wide", initial_sidebar_state="expanded")
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
        credentials = authenticate_google()
        st.session_state.service = build("calendar", "v3", credentials=credentials)
        st.success("Google Calendar connected.")
    except Exception as error:
        st.error(f"Could not connect Calendar: {error}")


page, connect_clicked = render_sidebar()
if connect_clicked:
    connect_calendar()
render_topbar()
if st.session_state.get("light_mode"):
    st.markdown("<style>.stApp{background:#f7f8fc;color:#141725}.glass-card,.metric-card{background:#ffffffdd;border-color:#e4e7f0}.muted,.metric-label,.event-time{color:#687086!important}p,span,label,[data-testid='stMetricValue']{color:#141725!important}.stTextInput input,.stTextArea textarea{background:#fff!important;color:#141725!important}</style>", unsafe_allow_html=True)

tracker = AssignmentTracker()
assignments = tracker.load_assignments()
timetable = load_schedule()
events = calendar_events()
due = tracker.check_due_assignments()

if page == "Dashboard":
    render_hero(len(events), len(due), "4.5h")
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    create, ask, sync = render_quick_actions()
    if create:
        st.info("Open Calendar from the sidebar to create an event.")
    if ask:
        st.session_state.dashboard_action = "agent"
    if sync:
        connect_calendar()
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    left, right = st.columns([3, 2])
    with left:
        render_calendar(events)
    with right:
        st.markdown("<div class='glass-card'><div class='section-title'><h3>Assignments due</h3><span class='muted'>Next 2 days</span></div>", unsafe_allow_html=True)
        if due:
            for assignment in due:
                st.markdown(f"<div class='event-row'><span class='event-dot'></span><div><div class='event-title'>{assignment['title']}</div><div class='event-time'>Due {assignment['deadline']}</div></div></div>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='muted'>Nothing urgent. You are ahead of schedule.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    if st.session_state.pop("dashboard_action", None) == "agent":
        st.info("Open AI Agent from the sidebar to start planning.")

elif page == "AI Agent":
    st.markdown("<div class='eyebrow'>AI workspace</div><h1>Your scheduling copilot</h1><p class='muted'>Ask naturally. The agent can plan events, find openings, and manage assignment deadlines.</p>", unsafe_allow_html=True)
    render_agent(schedule)

elif page == "Calendar":
    st.markdown("<div class='eyebrow'>Calendar</div><h1>Your schedule, in one view</h1>", unsafe_allow_html=True)
    if not st.session_state.service:
        st.info("Connect Google Calendar from the sidebar to load live events.")
    render_calendar(events)
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

elif page == "Timetable":
    st.markdown("<div class='eyebrow'>Weekly rhythm</div><h1>Class timetable</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if timetable:
        st.dataframe(timetable, use_container_width=True, hide_index=True)
    else:
        st.markdown("<p class='muted'>No classes yet. Add your first class below.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    with st.form("class_form", clear_on_submit=True):
        st.subheader("Add a class")
        one, two, three = st.columns(3)
        subject = one.text_input("Subject")
        day = two.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        room = three.text_input("Room")
        start, end = st.columns(2)
        start_time = start.time_input("Start time")
        end_time = end.time_input("End time")
        if st.form_submit_button("Add class"):
            if not subject.strip():
                st.warning("Enter a class name.")
            else:
                add_class(subject.strip(), day, str(start_time), str(end_time), room)
                st.success("Class added.")
                st.rerun()

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
    render_analytics(len(events), len(timetable), len([item for item in assignments if not item["completed"]]))

else:
    st.markdown("<div class='eyebrow'>Workspace</div><h1>Settings</h1><div class='glass-card'><h3>Appearance</h3><p class='muted'>Smart Scheduler is optimized for a dark, focused workspace.</p></div>", unsafe_allow_html=True)
