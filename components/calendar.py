import streamlit as st
from datetime import time, datetime
from backend.tools.validation import validate_class_fields
from backend.calendar_service.schedule_manager import (CLASS_TYPES,add_class,apply_template,classes_for_semester,delete_class,get_color_for_class,list_semesters,load_templates,save_current_as_template,update_class,)
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
def render_timetable():
    user_id = st.session_state.user_id
    st.markdown("<div class='section-title'><h3>Weekly Timetable</h3></div>", unsafe_allow_html=True)

    # ---- Controls row: semester selector, week selector, add class, sync ----
    semesters = list_semesters(user_id)
    c1, c2, c3, c4 = st.columns([2, 2, 1.3, 1.3])
    with c1:
        semester = st.selectbox("Semester", semesters + ["+ New semester"], key="semester_select")
        if semester == "+ New semester":
            semester = st.text_input("New semester name", placeholder="e.g. Semester 6") or "Unassigned"
    with c2:
        st.selectbox("Week", ["This week", "Next week"], key="week_select", disabled=True,
                     help="Recurring weekly schedule — week-specific overrides coming later")
    with c3:
        add_clicked = st.button("+ Add Class", use_container_width=True)
    with c4:
        sync_clicked = st.button("Sync Calendar", use_container_width=True)

    if add_clicked:
        st.session_state.show_add_class = True

    if st.session_state.get("show_add_class"):
        _render_add_class_form(user_id, semester)

    with st.expander("Semester templates"):
        _render_template_controls(user_id, semester, semesters)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ---- Day-based grid: columns per day, no times ----
    classes = classes_for_semester(user_id, semester)
    columns = st.columns(len(DAYS))
    for col, day in zip(columns, DAYS):
        with col:
            st.markdown(f"<div class='muted' style='font-weight:600;margin-bottom:8px'>{day[:3]}</div>", unsafe_allow_html=True)
            day_classes = sorted([c for c in classes if c["day"] == day], key=lambda c: c.get("start_time", ""))
            if not day_classes:
                st.markdown("<p class='muted' style='font-size:.78rem'>—</p>", unsafe_allow_html=True)
            for c in day_classes:
                color = get_color_for_class(c)
                st.markdown(
                    f"""
                    <div class='event-card' style='background:{color}15;border-left:3px solid {color};
                        border-radius:10px;padding:8px 10px;margin-bottom:8px'>
                        <div style='font-size:.72rem;font-weight:700;color:{color}'>{c.get('type','Lecture')}</div>
                        <div style='font-weight:600;font-size:.85rem'>{c['name']}</div>
                        <div class='muted' style='font-size:.72rem'>{c.get('room','')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                edit_col, del_col = st.columns(2)
                with edit_col:
                    if st.button("✎", key=f"edit_{c['id']}", help="Edit / move class", use_container_width=True):
                        st.session_state[f"editing_class_{c['id']}"] = True
                with del_col:
                    if st.button("✕", key=f"del_{c['id']}", help="Delete class", use_container_width=True):
                        delete_class(user_id, c["id"])
                        st.rerun()

                if st.session_state.get(f"editing_class_{c['id']}"):
                    _render_edit_class_form(user_id, c)

    return sync_clicked


def _render_add_class_form(user_id, semester):
    with st.form("add_class_form", clear_on_submit=True):
        one, two, three = st.columns(3)
        name = one.text_input("Subject")
        day = two.selectbox("Day", DAYS)
        class_type = three.selectbox("Type", CLASS_TYPES)
        four, five, six = st.columns(3)
        room = four.text_input("Room")
        instructor = five.text_input("Instructor")
        six.text_input("Semester", value=semester, disabled=True)
        start, end = st.columns(2)
        start_time = start.time_input("Start time")
        end_time = end.time_input("End time")
        submitted = st.form_submit_button("Add class")
        if submitted:
            error = validate_class_fields(name, day, start_time, end_time, room, instructor)
            if error:
                st.warning(error)
            else:
                add_class(user_id, name.strip(), day, str(start_time), str(end_time), room, instructor, class_type, semester)
                st.session_state.show_add_class = False
                st.success("Class added.")
                st.rerun()

def _parse_time_string(value, fallback=time(9, 0)):
    if not value:
        return fallback
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(str(value), fmt).time()
        except ValueError:
            continue
    return fallback


def _render_edit_class_form(user_id, class_entry):
    class_id = class_entry["id"]
    with st.form(f"edit_class_form_{class_id}"):
        name = st.text_input("Subject", value=class_entry["name"])

        day_index = DAYS.index(class_entry["day"]) if class_entry["day"] in DAYS else 0
        day = st.selectbox("Day", DAYS, index=day_index)

        type_index = CLASS_TYPES.index(class_entry.get("type", "Lecture")) if class_entry.get("type") in CLASS_TYPES else 0
        class_type = st.selectbox("Type", CLASS_TYPES, index=type_index)

        room = st.text_input("Room", value=class_entry.get("room", ""))
        instructor = st.text_input("Instructor", value=class_entry.get("instructor", ""))

        start, end = st.columns(2)
        start_time = start.time_input("Start time", value=_parse_time_string(class_entry.get("start_time")))
        end_time = end.time_input("End time", value=_parse_time_string(class_entry.get("end_time")))

        save_col, cancel_col = st.columns(2)
        save_clicked = save_col.form_submit_button("Save changes")
        cancel_clicked = cancel_col.form_submit_button("Cancel")

        if cancel_clicked:
            st.session_state[f"editing_class_{class_id}"] = False
            st.rerun()

        if save_clicked:
            error = validate_class_fields(name, day, start_time, end_time, room, instructor)
            if error:
                st.warning(error)
            else:
                update_class(
                    user_id,
                    class_id,
                    course_name=name.strip(),
                    day_of_week=day,
                    class_type=class_type,
                    location=room,
                    instructor=instructor,
                    start_time=str(start_time),
                    end_time=str(end_time),
                )
                st.session_state[f"editing_class_{class_id}"] = False
                st.success("Class updated.")
                st.rerun()

def _render_template_controls(user_id, semester, semesters):
    col1, col2 = st.columns(2)
    with col1:
        template_name = st.text_input("Template name", placeholder="e.g. CSE Semester template")
        if st.button("Save current semester as template", use_container_width=True):
            if template_name.strip():
                save_current_as_template(user_id, template_name.strip(), semester)
                st.success(f"Saved '{template_name}' from {semester}.")
            else:
                st.warning("Enter a template name.")
    with col2:
        templates = list(load_templates(user_id).keys())
        if templates:
            chosen_template = st.selectbox("Apply template", templates)
            target = st.selectbox("To semester", semesters + ["+ New semester"], key="template_target")
            if target == "+ New semester":
                target = st.text_input("New semester name", key="template_new_sem") or "Unassigned"
            if st.button("Apply", use_container_width=True):
                added = apply_template(user_id, chosen_template, target)
                st.success(f"Added {len(added)} classes to {target}.")
                st.rerun()
        else:
            st.markdown("<p class='muted' style='font-size:.8rem'>No templates saved yet.</p>", unsafe_allow_html=True)