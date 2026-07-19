import streamlit as st


PAGES = ["Dashboard", "Calendar", "AI Agent", "Timetable", "Assignments", "Analytics", "Settings"]


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="brand"><div class="brand-mark">S</div>Smart Scheduler</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")
        st.divider()
        st.caption("CALENDAR CONNECTION")
        status = "Connected" if st.session_state.service else "Not connected"
        st.markdown(f"<div class='date-chip'>{status}</div>", unsafe_allow_html=True)
        if st.button("Connect Google Calendar", use_container_width=True):
            return page, True
        st.caption("Your planning command center")
    return page, False
