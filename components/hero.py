from datetime import datetime

import streamlit as st


def render_hero(name=None, semester="Semester 5", course="Computer Science"):
    # TODO: once login is implemented, pull name from st.session_state.user_name
    name = name or "Jagadeesh"
    today = datetime.now().strftime("%A, %d %B")
    st.markdown(
        f"""
        <div class='hero'>
            <div class='eyebrow'>{today}</div>
            <h1>Hi, {name} 👋</h1>
            <p style="margin-bottom:2px;"><b>{semester}</b> • {course}</p>
            <p class='muted'>Here's your timetable for this week.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )