import streamlit as st

from components.cards import event_list


def render_calendar(events):
    st.markdown("<div class='section-title'><h3>Calendar timeline</h3><span class='muted'>Upcoming</span></div>", unsafe_allow_html=True)
    left, right = st.columns([3, 2])
    with left:
        st.markdown("<div class='glass-card'><div class='eyebrow'>Today</div><h2>Your schedule</h2>", unsafe_allow_html=True)
        event_list(events[:4], "Your day is clear. Enjoy the focus time.")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='glass-card'><div class='eyebrow'>Focus window</div><h2>Free this afternoon</h2><p class='muted'>No meetings are planned after your next event.</p><div class='progress-ring' style='--progress:68%' data-value='68%'></div><p style='text-align:center' class='muted'>Calendar availability</p></div>", unsafe_allow_html=True)
