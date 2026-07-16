import json
import os

SCHEDULE_FILE = "class_schedule.json"

# Assign a consistent color per subject (cycles through this palette)
COLOR_PALETTE = [
    "#4F86F7", "#F76C6C", "#6BCB77", "#FFD93D",
    "#B39DDB", "#FF9F45", "#4ECDC4", "#FF6F91"
]


def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, "r") as f:
        return json.load(f)


def save_schedule(schedule):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=2)


def add_class(name, day, start_time, end_time, room="", instructor=""):
    schedule = load_schedule()
    class_entry = {
        "id": len(schedule) + 1,
        "name": name,
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
        "room": room,
        "instructor": instructor
    }
    schedule.append(class_entry)
    save_schedule(schedule)
    return class_entry


def delete_class(class_id):
    schedule = load_schedule()
    schedule = [c for c in schedule if c["id"] != class_id]
    save_schedule(schedule)


def get_color_for_class(name, schedule):
    """Assigns the same color to the same subject name every time."""
    unique_names = sorted(set(c["name"] for c in schedule))
    if name not in unique_names:
        return COLOR_PALETTE[0]
    index = unique_names.index(name) % len(COLOR_PALETTE)
    return COLOR_PALETTE[index]