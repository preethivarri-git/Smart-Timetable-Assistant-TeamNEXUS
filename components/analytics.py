import streamlit as st

from components.cards import metric_card


def _bar_row(label, value_pct, unavailable_text=None):
    if value_pct is None:
        return ("<div class='muted'>" + label + "</div>"
                + "<div class='bar'><span style='width:0%'></span></div>"
                + "<p class='muted' style='font-size:.72rem;margin:-10px 0 12px'>" + (unavailable_text or "Not enough data yet.") + "</p>")
    width = max(0, min(100, value_pct))
    return ("<div class='muted'>" + label + "</div>"
            + "<div class='bar'><span style='width:" + f"{width:.0f}" + "%'></span></div>")


def render_analytics(
    event_count,
    class_count,
    assignment_count,
    free_hours=None,
    calendar_utilization_pct=None,
    focus_blocks_pct=None,
    assignments_complete_pct=None,
):
    free_hours_display = f"{free_hours:.1f}" if free_hours is not None else "—"

    one, two, three, four = st.columns(4)
    for column, stat in zip(
        [one, two, three, four],
        [
            ("Events this week", event_count, "Calendar activity"),
            ("Classes", class_count, "Weekly timetable"),
            ("Assignments", assignment_count, "Open items"),
            ("Free hours", free_hours_display, "Estimated this week" if free_hours is not None else "Connect Google Calendar"),
        ],
    ):
        with column:
            metric_card(*stat)

    left, right = st.columns([3, 2])

    with left:
        rows = (
            _bar_row("Calendar utilization", calendar_utilization_pct, "Connect Google Calendar to see this.")
            + _bar_row("Exams with a study plan", focus_blocks_pct, "No upcoming exams yet.")
            + _bar_row("Assignments complete", assignments_complete_pct, "No assignments yet.")
        )
        st.markdown(
            "<div class='glass-card'><div class='section-title'><h3>Weekly planning rhythm</h3><span class='muted'>This week</span></div>" + rows + "</div>",
            unsafe_allow_html=True,
        )

    with right:
        ring_pct = calendar_utilization_pct if calendar_utilization_pct is not None else 0
        ring_caption = "Healthy calendar utilization" if calendar_utilization_pct is not None else "Connect Google Calendar to see this"
        st.markdown(
            "<div class='glass-card'><h3 style='text-align:center'>Schedule balance</h3>"
            + "<div class='progress-ring' style='--progress:" + f"{ring_pct:.0f}" + "%' data-value='" + f"{ring_pct:.0f}" + "%'></div>"
            + "<p style='text-align:center' class='muted'>" + ring_caption + "</p></div>",
            unsafe_allow_html=True,
        )