from datetime import datetime

def validate_class_time(start_time, end_time):
    if start_time is None or end_time is None:
        return "Enter both a start time and an end time."
    if start_time >= end_time:
        return "End time must be after start time."
    return None

def validate_class_fields(name, day, start_time, end_time, room="", instructor=""):
    if not name or not name.strip():
        return "Enter a class name."
    if not day:
        return "Select a day."
    return validate_class_time(start_time, end_time)

def validate_assignment_deadline(deadline_date):
    if deadline_date is None:
        return "Select a deadline."
    if deadline_date < datetime.now().date():
        return "Deadline cannot be in the past."
    return None

def validate_event_request(day_offset, hour, minute, duration):
    if day_offset is None or day_offset < 0:
        return "The event date is invalid."
    if hour is None or hour not in range(24):
        return "The event hour is invalid."
    if minute is None or minute not in range(60):
        return "The event minute is invalid."
    if duration is None or duration <= 0:
        return "The event duration must be greater than zero."
    if duration > 12:
        return "The event duration seems too long (over 12 hours) — please double check."
    return None