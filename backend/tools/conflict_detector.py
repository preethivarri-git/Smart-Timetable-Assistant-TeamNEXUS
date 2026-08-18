from datetime import datetime, timedelta
from backend.calendar_service.google_calendar import (get_events_between,normalize_calendar_datetime,)
from backend.calendar_service.schedule_manager import load_schedule

def _local_class_conflicts(user_id, start_time, end_time):
    if user_id is None:
        return []

    weekday = start_time.strftime("%A")
    conflicts = []

    for class_entry in load_schedule(user_id):
        if class_entry.get("day") != weekday:
            continue

        raw_start = class_entry.get("start_time")
        raw_end = class_entry.get("end_time")
        if not raw_start or not raw_end:
            continue

        try:
            class_start_time = datetime.strptime(str(raw_start), "%H:%M").time()
            class_end_time = datetime.strptime(str(raw_end), "%H:%M").time()
        except ValueError:
            try:
                class_start_time = datetime.strptime(str(raw_start), "%H:%M:%S").time()
                class_end_time = datetime.strptime(str(raw_end), "%H:%M:%S").time()
            except ValueError:
                continue

        class_start = start_time.replace(hour=class_start_time.hour,minute=class_start_time.minute,second=0,microsecond=0,)
        class_end = start_time.replace(hour=class_end_time.hour,minute=class_end_time.minute,second=0,microsecond=0,)
        class_start = normalize_calendar_datetime(class_start)
        class_end = normalize_calendar_datetime(class_end)

        if start_time < class_end and end_time > class_start:
            conflicts.append({
                "summary": f"{class_entry.get('name', 'Class')} ({class_entry.get('type', 'Lecture')})",
                "start": {"dateTime": class_start.isoformat()},
                "end": {"dateTime": class_end.isoformat()},
            })

    return conflicts


def check_conflicts(service, start_time, end_time, user_id=None):

    start_time = normalize_calendar_datetime(start_time)
    end_time = normalize_calendar_datetime(end_time)

    events = get_events_between(service, start_time, end_time)

    conflicts = []

    for event in events:

        existing_start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        existing_end = event["end"].get(
            "dateTime",
            event["end"].get("date")
        )

        existing_start = normalize_calendar_datetime(
            datetime.fromisoformat(existing_start.replace("Z", "+00:00"))
        )

        existing_end = normalize_calendar_datetime(
            datetime.fromisoformat(existing_end.replace("Z", "+00:00"))
        )

        if start_time < existing_end and end_time > existing_start:
            conflicts.append(event)

    # Local weekly timetable classes count as conflicts too now.
    conflicts.extend(_local_class_conflicts(user_id, start_time, end_time))

    if not conflicts:
        return {
            "conflict": False,
            "events": [],
            "suggested_start": None,
            "suggested_end": None
        }

    # Suggest next available slot after last conflicting event
    latest_end = max(
        normalize_calendar_datetime(
            datetime.fromisoformat(
                e["end"]["dateTime"].replace("Z", "+00:00")
            )
        )
        for e in conflicts
    )

    duration = end_time - start_time

    return {
        "conflict": True,
        "events": conflicts,
        "suggested_start": latest_end,
        "suggested_end": latest_end + duration
    }