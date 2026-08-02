from datetime import datetime

import streamlit as st


def render_topbar():
    date = datetime.now().strftime("%A, %d %B")
    # TODO: once login is implemented, pull name from st.session_state.user_name
    name = st.session_state.get("user_name", "Jagadeesh")

    left, right = st.columns([3, 2])
    with left:
        st.text_input("Search", placeholder="Search events, classes, assignments...", label_visibility="collapsed")
    with right:
        st.markdown(
            f"""
            <div class='topbar' style='justify-content:flex-end;gap:12px'>
                <span class='date-chip'>{date}</span>
                <span class='date-chip'>🔔</span>
                <span class='profile-chip'>👤 &nbsp;{name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def metric_card(label, value, note=""):
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>{label}</div>"
        f"<div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>",
        unsafe_allow_html=True,
    )


def event_list(events, empty_text="Nothing scheduled yet."):
    if not events:
        st.markdown(f"<p class='muted'>{empty_text}</p>", unsafe_allow_html=True)
        return
    for event in events:
        start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", "All day"))
        title = event.get("summary", "Untitled event")
        st.markdown(
            f"<div class='event-row'><span class='event-dot'></span>"
            f"<div><div class='event-title'>{title}</div><div class='event-time'>{start}</div></div></div>",
            unsafe_allow_html=True,
        )