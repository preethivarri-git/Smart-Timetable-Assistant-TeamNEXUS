import json
import os

SCHEDULE_FILE = "class_schedule.json"
TEMPLATES_FILE = "semester_templates.json"

CLASS_TYPES = ["Lecture", "Lab", "Tutorial"]

# Per your brief: Lecture = purple, Lab = orange, Tutorial = green
TYPE_COLORS = {
    "Lecture": "#6C63FF",
    "Lab": "#F59E0B",
    "Tutorial": "#22C55E",
}


def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, "r") as f:
        schedule = json.load(f)
    return [_migrate_entry(c) for c in schedule]


def _migrate_entry(entry):
    """Backfills type/semester on classes saved before this update."""
    entry.setdefault("type", "Lecture")
    entry.setdefault("semester", "Unassigned")
    return entry


def save_schedule(schedule):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=2)


def add_class(name, day, start_time, end_time, room="", instructor="", class_type="Lecture", semester="Unassigned"):
    if class_type not in CLASS_TYPES:
        class_type = "Lecture"
    schedule = load_schedule()
    class_entry = {
        "id": (max((c["id"] for c in schedule), default=0)) + 1,
        "name": name,
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
        "room": room,
        "instructor": instructor,
        "type": class_type,
        "semester": semester,
    }
    schedule.append(class_entry)
    save_schedule(schedule)
    return class_entry


def delete_class(class_id):
    schedule = load_schedule()
    schedule = [c for c in schedule if c["id"] != class_id]
    save_schedule(schedule)


def get_color_for_class(class_entry):
    """Color is now based on class type (Lecture/Lab/Tutorial), per the design brief."""
    return TYPE_COLORS.get(class_entry.get("type", "Lecture"), TYPE_COLORS["Lecture"])


def classes_for_semester(semester):
    return [c for c in load_schedule() if c.get("semester") == semester]


def list_semesters():
    semesters = sorted({c.get("semester", "Unassigned") for c in load_schedule()})
    return semesters or ["Unassigned"]


# ---------- Semester templates (Week 5-6 checkpoint 1) ----------

def load_templates():
    if not os.path.exists(TEMPLATES_FILE):
        return {}
    with open(TEMPLATES_FILE, "r") as f:
        return json.load(f)


def save_templates(templates):
    with open(TEMPLATES_FILE, "w") as f:
        json.dump(templates, f, indent=2)


def save_current_as_template(template_name, semester):
    """Snapshot a semester's current classes as a reusable template."""
    templates = load_templates()
    classes = classes_for_semester(semester)
    templates[template_name] = [
        {k: v for k, v in c.items() if k != "id"} for c in classes
    ]
    save_templates(templates)


def apply_template(template_name, target_semester):
    """Populate a semester's timetable from a saved template."""
    templates = load_templates()
    if template_name not in templates:
        return []
    schedule = load_schedule()
    next_id = max((c["id"] for c in schedule), default=0) + 1
    added = []
    for entry in templates[template_name]:
        new_entry = dict(entry)
        new_entry["id"] = next_id
        new_entry["semester"] = target_semester
        schedule.append(new_entry)
        added.append(new_entry)
        next_id += 1
    save_schedule(schedule)
    return added