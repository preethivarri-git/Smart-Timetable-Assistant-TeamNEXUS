import streamlit as st

from components.cards import metric_card


def render_analytics(event_count, class_count, assignment_count):
    one, two, three, four = st.columns(4)
    for column, stat in zip([one, two, three, four], [("Events this week", event_count, "Calendar activity"), ("Classes", class_count, "Weekly timetable"), ("Assignments", assignment_count, "Open items"), ("Free hours", "18.5", "Estimated this week")]):
        with column:
            metric_card(*stat)
    left, right = st.columns([3, 2])
    with left:
        st.markdown("<div class='glass-card'><div class='section-title'><h3>Weekly planning rhythm</h3><span class='muted'>This week</span></div><div class='muted'>Calendar utilization</div><div class='bar'><span style='width:62%'></span></div><div class='muted'>Focus blocks protected</div><div class='bar'><span style='width:76%'></span></div><div class='muted'>Assignments complete</div><div class='bar'><span style='width:45%'></span></div></div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='glass-card'><h3 style='text-align:center'>Schedule balance</h3><div class='progress-ring' style='--progress:62%' data-value='62%'></div><p style='text-align:center' class='muted'>Healthy calendar utilization</p></div>", unsafe_allow_html=True)
