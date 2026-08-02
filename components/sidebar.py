import streamlit as st


PAGES = [
    ("Home", "🏠"),
    ("Courses", "📚"),
    ("Assignments", "📝"),
    ("Analytics", "📊"),
    ("Settings", "⚙️"),
]


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="brand"><div class="brand-mark">S</div>Smart Scheduler</div>', unsafe_allow_html=True)

        labels = [f"{icon}  {name}" for name, icon in PAGES]
        selection = st.radio("Navigation", labels, label_visibility="collapsed", key="nav_radio")
        page = selection.split("  ", 1)[1]

        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] [data-testid="stRadio"] label {
                border-radius: 10px; padding: 10px 12px; margin-bottom: 2px;
                width: 100%; font-weight: 500; transition: background .15s ease, color .15s ease;
            }
            [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
                background: var(--primary-light); color: var(--primary) !important;
                font-weight: 600;
            }
            [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
                color: var(--primary) !important;
            }
            [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 2px; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.caption("CALENDAR CONNECTION")
        status = "🟢 Connected" if st.session_state.service else "⚪ Not connected"
        st.markdown(f"<div class='date-chip'>{status}</div>", unsafe_allow_html=True)
        connect_clicked = st.button("Connect Google Calendar", use_container_width=True)

        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        st.divider()
        st.button("Logout", use_container_width=True, key="logout_btn")

    return page, connect_clicked