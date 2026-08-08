"""
backend/calendar_service/schedule_manager.py

DB-backed replacement for the old class_schedule.json / semester_templates.json
version. All functions are scoped by user_id and talk to storage.py instead of
flat files.

IMPORTANT: callers (e.g. components/calendar.py) still work with the *old*
JSON-shaped dicts -- keys like "name", "day", "room", "type", "id" -- rather
than storage.py's column names ("course_name", "day_of_week", "location",
"class_type"). This module is a translation layer: it fetches from the DB
using the new column names, then hands back dicts shaped like the old ones,
so rendering code elsewhere doesn't also need to be rewritten.

Every public function now takes user_id as its first argument. Call sites
in calendar.py and app.py need to be updated to pass st.session_state.user_id.
"""

from backend.database import storage

CLASS_TYPES = ["Lecture", "Lab", "Tutorial"]

# Per your brief: Lecture = purple, Lab = orange, Tutorial = green
TYPE_COLORS = {
    "Lecture": "#6C63FF",
    "Lab": "#F59E0B",
    "Tutorial": "#22C55E",
}


def _to_dict(row):
    """Translate a ClassSchedule ORM row into the old JSON-style dict shape."""
    return {
        "id": row.id,
        "name": row.course_name,
        "day": row.day_of_week,
        "start_time": row.start_time,
        "end_time": row.end_time,
        "room": row.location or "",
        "instructor": row.instructor or "",
        "type": row.class_type or "Lecture",
        "semester": row.semester,
    }


def load_schedule(user_id):
    """All classes for this user, across every semester."""
    rows = storage.get_class_schedules(user_id)
    return [_to_dict(r) for r in rows]


def add_class(user_id, name, day, start_time, end_time, room="", instructor="",
              class_type="Lecture", semester="Unassigned"):
    if class_type not in CLASS_TYPES:
        class_type = "Lecture"
    new_id = storage.add_class_schedule(
        user_id,
        course_name=name,
        day_of_week=day,
        start_time=str(start_time),
        end_time=str(end_time),
        course_code="",
        class_type=class_type,
        location=room,
        instructor=instructor,
        semester=semester,
    )
    return new_id


def delete_class(user_id, class_id):
    """Deletes a class. Scoped to user_id -- one user can't delete another's class."""
    return storage.delete_class_schedule(class_id, user_id)


def get_color_for_class(class_entry):
    """Color is based on class type (Lecture/Lab/Tutorial), per the design brief."""
    return TYPE_COLORS.get(class_entry.get("type", "Lecture"), TYPE_COLORS["Lecture"])


def classes_for_semester(user_id, semester):
    rows = storage.get_class_schedules(user_id, semester=semester)
    return [_to_dict(r) for r in rows]


def list_semesters(user_id):
    return storage.list_semesters(user_id)


# ---------- Semester templates (Week 5-6 checkpoint 1) ----------

def save_current_as_template(user_id, template_name, semester):
    """Snapshot a semester's current classes as a reusable template."""
    storage.save_semester_template(user_id, template_name, semester)


def load_templates(user_id):
    """
    Returns {template_name: [class_dict, ...]} to match the old JSON shape
    that calendar.py expects (it calls .keys() on the result).
    """
    templates = storage.get_semester_templates(user_id)
    result = {}
    for t in templates:
        result[t["name"]] = [
            {
                "name": c.get("course_name"),
                "day": c.get("day_of_week"),
                "start_time": c.get("start_time"),
                "end_time": c.get("end_time"),
                "room": c.get("location") or "",
                "instructor": c.get("instructor") or "",
                "type": c.get("class_type") or "Lecture",
            }
            for c in t["classes"]
        ]
    return result


def apply_template(user_id, template_name, target_semester):
    """Populate a semester's timetable from a saved template. Returns the new class dicts."""
    new_ids = storage.apply_semester_template(user_id, template_name, target_semester)
    if not new_ids:
        return []
    rows = storage.get_class_schedules(user_id, semester=target_semester)
    added = [_to_dict(r) for r in rows if r.id in new_ids]
    return added