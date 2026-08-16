from datetime import datetime, timedelta
import streamlit as st
from googleapiclient.discovery import build
from backend.agent.scheduler_agent import schedule
from backend.calendar_service.auth import (authenticate_google,get_calendar_service,)
from backend.calendar_service.google_calendar import (create_event,list_events,)
from backend.calendar_service.schedule_manager import (list_semesters,load_schedule,)
from backend.database.storage import (init_db,add_exam,get_exams,update_exam,delete_exam,mark_exam_completed,)
from backend.tools.assignment_tracker import AssignmentTracker
from backend.tools.study_planner import (create_exam_study_plan,add_study_plan_to_calendar,prioritize_exams)
from components.analytics import render_analytics
from components.calendar import render_timetable
from components.cards import event_list, render_topbar
from components.chat import render_agent
from components.hero import render_hero
from components.login import require_login
from components.sidebar import render_sidebar
from components.styles import inject_styles

st.set_page_config(page_title="Smart Scheduler",page_icon="S",layout="wide",initial_sidebar_state="expanded",)

init_db()
require_login()
inject_styles()

if "service" not in st.session_state:
    st.session_state.service = None


def calendar_events():
    if not st.session_state.service:
        return []
    try:
        return list_events(
            st.session_state.service,
            max_results=12,
        )
    except Exception as error:
        st.warning(
            f"Calendar unavailable: {error}"
        )
        return []


def connect_calendar():
    try:
        credentials = authenticate_google(
            st.session_state.user_id
        )
        st.session_state.service = build(
            "calendar",
            "v3",
            credentials=credentials,
        )
        st.success(
            "Google Calendar connected."
        )
    except Exception as error:
        st.error(
            f"Could not connect Calendar: {error}"
        )

page, connect_clicked = render_sidebar()

if connect_clicked:
    connect_calendar()

render_topbar()


# ---------------------------------------------------------
# COMMON DATA
# ---------------------------------------------------------

tracker = AssignmentTracker(
    st.session_state.user_id
)

assignments = tracker.load_assignments()

events = calendar_events()

due = tracker.check_due_assignments()


# =========================================================
# HOME
# =========================================================

if page == "Home":

    semesters = list_semesters(
        st.session_state.user_id
    )

    selected = st.session_state.get(
        "semester_select"
    )

    current_semester = (
        selected
        if selected and selected != "+ New semester"
        else (
            semesters[0]
            if semesters
            else "Unassigned"
        )
    )

    render_hero(
        semester=current_semester
    )

    st.markdown(
        "<div style='height:14px'></div>",
        unsafe_allow_html=True,
    )

    sync_clicked = render_timetable()

    if sync_clicked:
        connect_calendar()

    st.markdown(
        "<div style='height:20px'></div>",
        unsafe_allow_html=True,
    )

    render_agent(schedule)


# =========================================================
# COURSES / CALENDAR
# =========================================================

elif page == "Courses":

    st.markdown(
        "<div class='eyebrow'>Calendar</div>"
        "<h1>Your schedule, in one view</h1>",
        unsafe_allow_html=True,
    )

    if not st.session_state.service:
        st.info(
            "Connect Google Calendar from the sidebar "
            "to load live events."
        )

    st.markdown(
        "<div class='glass-card'>"
        "<div class='section-title'>"
        "<h3>All upcoming events</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    event_list(
        events,
        "No upcoming events. Create one and reclaim your calendar.",
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander(
        "Create a calendar event"
    ):

        if not st.session_state.service:

            st.info(
                "Connect Google Calendar first."
            )

        else:

            with st.form(
                "calendar_event_form",
                clear_on_submit=True,
            ):

                title = st.text_input(
                    "Event title"
                )

                event_date, event_time = st.columns(2)

                date = event_date.date_input(
                    "Date"
                )

                time = event_time.time_input(
                    "Start time"
                )

                duration = st.number_input(
                    "Duration (minutes)",
                    min_value=15,
                    max_value=480,
                    value=60,
                    step=15,
                )

                if st.form_submit_button(
                    "Create event"
                ):

                    if not title.strip():

                        st.warning(
                            "Enter an event title."
                        )

                    else:

                        start = datetime.combine(
                            date,
                            time,
                        )

                        create_event(
                            st.session_state.service,
                            title.strip(),
                            start,
                            start
                            + timedelta(
                                minutes=duration
                            ),
                        )

                        st.success(
                            "Event created."
                        )


# =========================================================
# ASSIGNMENTS
# =========================================================

elif page == "Assignments":

    st.markdown(
        "<div class='eyebrow'>Academic workflow</div>"
        "<h1>Assignment tracker</h1>",
        unsafe_allow_html=True,
    )

    PRIORITY_COLORS = {
        "high": "#e5484d",
        "medium": "#f5a623",
        "low": "#30a46c",
    }

    PRIORITY_LABELS = {
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }

    with st.form(
        "assignment_form",
        clear_on_submit=True,
    ):

        first, second, third = st.columns(
            [2, 1, 1]
        )

        title = first.text_input(
            "Assignment title"
        )

        deadline = second.date_input(
            "Deadline",
            min_value=datetime.now().date(),
        )

        priority = third.selectbox(
            "Priority",
            ["high", "medium", "low"],
            index=1,
            format_func=lambda p:
                PRIORITY_LABELS[p],
        )

        if st.form_submit_button(
            "Add assignment"
        ):

            if title.strip():

                tracker.add_assignment(
                    title.strip(),
                    deadline.isoformat(),
                    priority,
                )

                st.success(
                    "Assignment added."
                )

                st.rerun()

            else:

                st.warning(
                    "Enter an assignment title."
                )

    st.markdown(
        "<div class='glass-card'>",
        unsafe_allow_html=True,
    )

    if assignments:

        for assignment in assignments:

            status = (
                "Completed"
                if assignment["completed"]
                else f"Due {assignment['deadline']}"
            )

            p = assignment.get(
                "priority",
                "medium",
            )

            color = PRIORITY_COLORS.get(
                p,
                "#f5a623",
            )

            badge = (
                f"<span style='"
                f"background:{color}22;"
                f"color:{color};"
                f"border:1px solid {color}55;"
                f"border-radius:999px;"
                f"padding:2px 10px;"
                f"font-size:.72rem;"
                f"font-weight:600;"
                f"margin-left:8px'>"
                f"{PRIORITY_LABELS.get(p, 'Medium')}"
                f"</span>"
            )

            row, action, prio_col = st.columns(
                [4, 1, 1.3]
            )

            row.markdown(
                f"<div class='event-row'>"
                f"<span class='event-dot'></span>"
                f"<div>"
                f"<div class='event-title'>"
                f"{assignment['title']}{badge}"
                f"</div>"
                f"<div class='event-time'>"
                f"{status}"
                f"</div>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            if (
                not assignment["completed"]
                and action.button(
                    "Done",
                    key=f"done_{assignment['id']}",
                )
            ):

                tracker.mark_completed(
                    assignment["id"]
                )

                st.rerun()

            new_priority = prio_col.selectbox(
                "Priority",
                ["high", "medium", "low"],
                index=[
                    "high",
                    "medium",
                    "low",
                ].index(p),
                key=f"prio_{assignment['id']}",
                label_visibility="collapsed",
                format_func=lambda x:
                    PRIORITY_LABELS[x],
            )

            if new_priority != p:

                tracker.set_priority(
                    assignment["id"],
                    new_priority,
                )

                st.rerun()

    else:

        st.markdown(
            "<p class='muted'>"
            "No assignments yet. "
            "Add a deadline to stay ahead."
            "</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# EXAMS
# =========================================================

elif page == "Exams":

    st.markdown(
        "<div class='eyebrow'>Academic planning</div>"
        "<h1>Exam Schedule</h1>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # ADD EXAM FORM
    # -----------------------------------------------------

    with st.form(
        "exam_form",
        clear_on_submit=True,
    ):

        first, second = st.columns(
            [2, 1]
        )

        subject = first.text_input(
            "Subject"
        )

        exam_date = second.date_input(
            "Exam date",
            min_value=datetime.now().date(),
        )

        third, fourth, fifth = st.columns(
            [1, 1, 1]
        )

        exam_time = third.time_input(
            "Exam start time",
            step=300,
        )

        duration = fourth.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=600,
            value=180,
            step=1,
        )

        study_hours = fifth.number_input(
            "Required study hours",
            min_value=1,
            max_value=100,
            value=5,
            step=1,
        )

        if st.form_submit_button(
            "Add Exam"
        ):

            if not subject.strip():

                st.warning(
                    "Enter the subject."
                )

            elif study_hours <= 0:

                st.warning(
                    "Required study hours must be greater than 0."
                )

            elif duration <= 0:

                st.warning(
                    "Exam duration must be greater than 0."
                )

            else:

                exam_datetime = datetime.combine(
                    exam_date,
                    exam_time,
                )

                existing_exams = get_exams(
                    st.session_state.user_id,
                    include_completed=True,
                )

                duplicate_exam = any(
                    exam.subject.strip().lower()
                    == subject.strip().lower()
                    and exam.exam_date
                    == exam_datetime
                    for exam in existing_exams
                )

                if duplicate_exam:

                    st.warning(
                        "An exam with the same subject, "
                        "date, and time already exists."
                    )

                else:

                    add_exam(
                        user_id=st.session_state.user_id,
                        subject=subject.strip(),
                        exam_date=exam_datetime,
                        duration_minutes=duration,
                        required_study_hours=study_hours,
                    )

                    st.success(
                        "Exam added successfully."
                    )

                    st.rerun()

    # -----------------------------------------------------
    # EXAM SUMMARY
    # -----------------------------------------------------

    summary_exams = get_exams(
        st.session_state.user_id,
        include_completed=False,
    )

    total_exams = len(summary_exams)

    total_study_hours = sum(
        exam.required_study_hours
        for exam in summary_exams
    )

    next_exam = (
        summary_exams[0]
        if summary_exams
        else None
    )

    if next_exam:

        next_exam_name = next_exam.subject

        next_exam_date = (
            next_exam.exam_date.strftime(
                "%d %b"
            )
        )

    else:

        next_exam_name = "No exams"
        next_exam_date = ""

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.metric(
            "Upcoming Exams",
            total_exams,
        )

    with summary_col2:

        st.metric(
            "Total Study Hours",
            f"{total_study_hours} hrs",
        )

    with summary_col3:

        st.metric(
            "Next Exam",
            next_exam_name,
            next_exam_date,
        )

    # -----------------------------------------------------
    # UPCOMING EXAMS CARD
    # -----------------------------------------------------

    st.markdown(
        "<div class='glass-card'>"
        "<div class='section-title'>"
        "<h3>Upcoming Exams</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    exams = get_exams(
        st.session_state.user_id,
        include_completed=False,
    )
    exams = prioritize_exams(exams)

    if exams:

        for exam in exams:

            # =============================================
            # EDIT EXAM
            # =============================================

            if st.session_state.get(
                f"editing_exam_{exam.id}",
                False,
            ):

                st.markdown(
                    "#### Edit Exam"
                )

                with st.form(
                    f"edit_exam_form_{exam.id}"
                ):

                    edit_subject = st.text_input(
                        "Subject",
                        value=exam.subject,
                    )

                    edit_date = st.date_input(
                        "Exam date",
                        value=exam.exam_date.date(),
                        min_value=datetime.now().date(),
                    )

                    edit_time = st.time_input(
                        "Exam start time",
                        value=exam.exam_date.time(),
                    )

                    edit_duration = st.number_input(
                        "Duration (minutes)",
                        min_value=15,
                        max_value=600,
                        value=exam.duration_minutes,
                        step=15,
                    )

                    edit_study_hours = st.number_input(
                        "Required study hours",
                        min_value=1,
                        max_value=100,
                        value=max(
                            1,
                            exam.required_study_hours,
                        ),
                        step=1,
                    )

                    save_col, cancel_col = st.columns(2)

                    with save_col:

                        save_exam = st.form_submit_button(
                            "Save Changes"
                        )

                    with cancel_col:

                        cancel_exam = st.form_submit_button(
                            "Cancel"
                        )

                    if cancel_exam:

                        st.session_state[
                            f"editing_exam_{exam.id}"
                        ] = False

                        st.rerun()

                    if save_exam:

                        if not edit_subject.strip():

                            st.error(
                                "Subject cannot be empty."
                            )

                        else:

                            edited_datetime = datetime.combine(
                                edit_date,
                                edit_time,
                            )

                            if edited_datetime <= datetime.now():

                                st.error(
                                    "Exam date and time must be in the future."
                                )

                            elif edit_duration <= 0:

                                st.error(
                                    "Exam duration must be greater than 0."
                                )

                            elif edit_study_hours <= 0:

                                st.error(
                                    "Required study hours must be greater than 0."
                                )

                            else:

                                update_exam(
                                    exam.id,
                                    st.session_state.user_id,
                                    subject=edit_subject.strip(),
                                    exam_date=edited_datetime,
                                    duration_minutes=edit_duration,
                                    required_study_hours=edit_study_hours,
                                )

                                st.session_state[
                                    f"editing_exam_{exam.id}"
                                ] = False

                                st.success(
                                    "Exam updated successfully."
                                )

                                st.rerun()

            # =============================================
            # EXAM STATUS
            # =============================================

            days_remaining = (
                exam.exam_date.date()
                - datetime.now().date()
            ).days

            if days_remaining > 1:

                remaining_text = (
                    f"{days_remaining} days remaining"
                )

                status_text = "Upcoming"
                status_icon = "🟢"

            elif days_remaining == 1:

                remaining_text = (
                    "1 day remaining"
                )

                status_text = "Tomorrow"
                status_icon = "🟡"

            elif days_remaining == 0:

                remaining_text = "Today"

                status_text = "Today"
                status_icon = "🔴"

            else:

                remaining_text = "Past exam"

                status_text = "Overdue"
                status_icon = "⚫"

            # =============================================
            # EXAM INFORMATION + ACTIONS
            # =============================================

            row, action = st.columns(
                [4.5, 3]
            )

            with row:

                st.markdown(
                    f"""<div class='event-row'>
                    <span class='event-dot'></span>
                    <div>
                    <div class='event-title'>{status_icon} {exam.subject}</div>
                    <div class='event-time'>
                     📅 {exam.exam_date.strftime('%d %b %Y')}
                    &nbsp; • &nbsp;
                    ⏰ {exam.exam_date.strftime('%I:%M %p')}
                    </div>
                    <div class='event-time'>
                    ⏱️ {exam.duration_minutes} minutes
                    &nbsp; • &nbsp;
                    📚 {exam.required_study_hours} study hours
                    &nbsp; • &nbsp;
                    {remaining_text}
                    &nbsp; • &nbsp;
                    {status_text}
                    </div>
                    </div>
                    </div>""",
                            unsafe_allow_html=True,
                        )

            with action:

                edit_col, done_col, delete_col, study_col = st.columns(
                    [1, 1, 1, 1],
                    gap="small",
                )

                # -----------------------------------------
                # EDIT
                # -----------------------------------------

                with edit_col:

                    if st.button(
                        "Edit",
                        key=f"exam_edit_{exam.id}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            f"editing_exam_{exam.id}"
                        ] = True

                        st.rerun()

                # -----------------------------------------
                # DONE
                # -----------------------------------------

                with done_col:

                    if st.button(
                        "Done",
                        key=f"exam_done_{exam.id}",
                        use_container_width=True,
                    ):

                        mark_exam_completed(
                            exam.id,
                            st.session_state.user_id,
                        )

                        st.rerun()

                # -----------------------------------------
                # DELETE
                # -----------------------------------------

                with delete_col:

                    if st.button(
                        "Delete",
                        key=f"exam_delete_{exam.id}",
                        use_container_width=True,
                    ):

                        delete_exam(
                            exam.id,
                            st.session_state.user_id,
                        )

                        st.rerun()

                # -----------------------------------------
                # GENERATE STUDY PLAN
                # -----------------------------------------

                with study_col:

                    if st.button(
                        "Study Plan",
                        key=f"generate_study_{exam.id}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            f"generating_study_{exam.id}"
                        ] = True

                        st.rerun()

            # =============================================
            # STUDY PLAN
            # =============================================

            if st.session_state.get(
                f"generating_study_{exam.id}",
                False,
            ):

                st.markdown(
                    "#### 📚 Study Plan"
                )

                plan = st.session_state.get(
                    f"study_plan_{exam.id}"
                )

                # -----------------------------------------
                # GENERATE ONLY IF NOT ALREADY GENERATED
                # -----------------------------------------

                if plan is None:

                    try:

                        # IMPORTANT:
                        # This returns the actual Google
                        # Calendar service, not Credentials.
                        service = get_calendar_service(
                            st.session_state.user_id
                        )

                        plan = create_exam_study_plan(
                            service=service,
                            user_id=st.session_state.user_id,
                            exam=exam,
                            start_date=datetime.now(),
                            max_hours_per_day=2,
                            session_minutes=60,
                        )

                        st.session_state[
                            f"study_plan_{exam.id}"
                        ] = plan

                    except Exception as e:

                        st.error(
                            "Unable to generate the study plan."
                        )

                        st.exception(e)

                        plan = None

                # -----------------------------------------
                # DISPLAY PLAN
                # -----------------------------------------

                if plan:

                    required_hours = (
                        plan["required_minutes"]
                        / 60
                    )

                    allocated_hours = (
                        plan["allocated_minutes"]
                        / 60
                    )

                    remaining_hours = (
                        plan["remaining_minutes"]
                        / 60
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Required",
                            f"{required_hours:.1f} hrs",
                        )

                    with col2:

                        st.metric(
                            "Allocated",
                            f"{allocated_hours:.1f} hrs",
                        )

                    with col3:

                        st.metric(
                            "Remaining",
                            f"{remaining_hours:.1f} hrs",
                        )

                    if plan["fully_allocated"]:

                        st.success(
                            "All required study time "
                            "can be scheduled."
                        )

                    else:

                        st.warning(
                            f"{remaining_hours:.1f} study hours "
                            "could not be scheduled before the exam."
                        )

                    # -------------------------------------
                    # SESSIONS
                    # -------------------------------------
                    if plan["sessions"]:
                        st.markdown(
                            "##### Planned Study Sessions"
                        )
                        sessions_by_date = {}
                        for session in plan["sessions"]:
                            start = session["start"]
                            end = session["end"]
                            date_key = start.date()
                            if date_key not in sessions_by_date:
                                sessions_by_date[date_key] = {"start": start,"end": end,}
                            else:
                                sessions_by_date[date_key]["start"] = min(sessions_by_date[date_key]["start"], start)
                                sessions_by_date[date_key]["end"] = max(sessions_by_date[date_key]["end"], end)
                        edited_sessions = []

                        for index, (date_key, session_times) in enumerate(
                            sessions_by_date.items()
                        ):

                            start = session_times["start"]
                            end = session_times["end"]

                            st.markdown(
                                f"**📚 Session {index + 1}**"
                            )

                            col_date, col_start, col_end = st.columns(3)

                            with col_date:
                                edited_date = st.date_input(
                                    "Date",
                                    value=start.date(),
                                    key=f"study_date_{exam.id}_{index}",
                                )

                            with col_start:
                                edited_start_time = st.time_input(
                                    "Start",
                                    value=start.time(),
                                    key=f"study_start_{exam.id}_{index}",
                                )

                            with col_end:
                                edited_end_time = st.time_input(
                                    "End",
                                    value=end.time(),
                                    key=f"study_end_{exam.id}_{index}",
                                )

                            edited_start = datetime.combine(
                                edited_date,
                                edited_start_time,
                            ).replace(tzinfo=start.tzinfo)

                            edited_end = datetime.combine(
                                edited_date,
                                edited_end_time,
                            ).replace(tzinfo=end.tzinfo)

                            if edited_end <= edited_start:
                                st.error(
                                    f"Session {index + 1}: End time must be after start time."
                                )
                            else:
                                duration_minutes = int(
                                    (edited_end - edited_start).total_seconds() / 60
                                )

                            edited_sessions.append(
                                {
                                    "start": edited_start,
                                    "end": edited_end,
                                    "duration_minutes": duration_minutes,
                                }
                            )

                            st.markdown("---")

                        edited_allocated_minutes = sum(
                            session["duration_minutes"]
                            for session in edited_sessions
                        )

                        required_minutes = int(
                            exam.required_study_hours * 60
                        )

                        edited_remaining_minutes = max(
                            required_minutes - edited_allocated_minutes,
                            0,
                        )

                        st.markdown(
                            f"**Edited study time:** "
                            f"{edited_allocated_minutes // 60}h "
                            f"{edited_allocated_minutes % 60}m"
                        )

                        if edited_remaining_minutes > 0:
                            st.warning(
                                f"You still need "
                                f"{edited_remaining_minutes // 60}h "
                                f"{edited_remaining_minutes % 60}m "
                                f"of study time."
                            )                        

                        else:
                            st.success(
                                "All required study time is scheduled."
                            )

    # Keep the edited sessions in the plan
                        plan["sessions"] = edited_sessions
                        plan["allocated_minutes"] = edited_allocated_minutes
                        plan["remaining_minutes"] = edited_remaining_minutes
                        plan["fully_allocated"] = (
                            edited_remaining_minutes == 0
                        )

                    else:

                        st.info(
                            "No available study slots were found "
                            "before this exam."
                        )


                    col_confirm, col_cancel = st.columns(2)

                    with col_confirm:

                        if st.button(
                            "✅ Confirm & Add to Calendar",
                            key=f"confirm_study_{exam.id}",
                            disabled=(
                                not plan["sessions"]
                                or not plan["fully_allocated"]
                            ),
                        ):

                            try:

                                service = get_calendar_service(
                                    st.session_state.user_id
                                )

                                created_events = add_study_plan_to_calendar(
                                service=service,
                                exam=exam,
                                plan=plan,
                                )

                                st.session_state[
                                    f"study_plan_confirmed_{exam.id}"
                                ] = True

                                st.success(
                                    f"{len(created_events)} study session(s) "
                                    "added to Google Calendar."
                                )

                            except Exception as e:

                                st.error(
                                    "Unable to add study plan to Google Calendar."
                                )
                    with col_cancel:

                        if st.button(
                            "❌ Cancel",
                            key=f"cancel_study_{exam.id}",
                        ):

                            st.session_state.pop(
                                f"study_plan_{exam.id}",
                                None,
                            )

                            st.session_state[
                                f"generating_study_{exam.id}"
                            ] = False

                            st.rerun()
                    if st.button(
                        "Hide Study Plan",
                        key=f"hide_study_{exam.id}",
                    ):

                        st.session_state[
                            f"generating_study_{exam.id}"
                        ] = False

                        st.session_state.pop(
                            f"study_plan_{exam.id}",
                            None,
                        )

                        st.rerun()

    else:

        st.markdown(
            "<p class='muted'>"
            "No upcoming exams. "
            "Add your first exam above."
            "</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":

    st.markdown(
        "<div class='eyebrow'>Insights</div>"
        "<h1>Planning analytics</h1>",
        unsafe_allow_html=True,
    )

    open_assignments = len(
        [
            item
            for item in assignments
            if not item["completed"]
        ]
    )

    render_analytics(
        len(events),
        len(
            load_schedule(
                st.session_state.user_id
            )
        ),
        open_assignments,
    )


# =========================================================
# SETTINGS
# =========================================================

else:

    st.markdown(
        "<div class='eyebrow'>Workspace</div>"
        "<h1>Settings</h1>"
        "<div class='glass-card'>"
        "<h3>Appearance</h3>"
        "<p class='muted'>"
        "Smart Scheduler uses a clean, light workspace theme."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )