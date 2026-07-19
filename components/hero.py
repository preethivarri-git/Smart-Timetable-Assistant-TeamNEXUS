import streamlit as st

from components.cards import metric_card


def render_hero(event_count, due_count, free_hours):
    st.markdown("<div class='hero'><div class='eyebrow'>Your day, intelligently organized</div><h1>Good evening. Plan less, do more.</h1><p>Your AI scheduling workspace keeps events, classes, and deadlines in one focused flow.</p></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    columns = st.columns(4)
    stats = [("Today's schedule", event_count, "Calendar events"), ("Assignments due", due_count, "Next two days"), ("Free time today", free_hours, "Estimated hours"), ("Upcoming meetings", event_count, "On your calendar")]
    for column, stat in zip(columns, stats):
        with column:
            metric_card(*stat)


def render_quick_actions():
    st.markdown("<div class='section-title'><h3>Quick actions</h3></div>", unsafe_allow_html=True)
    one, two, three = st.columns(3)
    with one:
        create = st.button("Create event", use_container_width=True)
    with two:
        ask = st.button("Ask AI", use_container_width=True)
    with three:
        sync = st.button("Sync calendar", use_container_width=True)
    return create, ask, sync
