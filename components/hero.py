from datetime import datetime

import streamlit as st


def render_hero(name=None, semester="Unassigned"):
    name = name or st.session_state.get("username", "there")
    today = datetime.now().strftime("%A, %d %B")
    st.markdown(
        f"""
        <div class='hero'>
            <div class='eyebrow'>{today}</div>
            <h1>Hi, {name} 👋</h1>
            <p style="margin-bottom:2px;"><b>{semester}</b></p>
            <p class='muted'>Here's your timetable for this week.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )