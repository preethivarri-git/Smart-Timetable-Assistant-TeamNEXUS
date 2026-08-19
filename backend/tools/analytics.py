"""
backend/tools/analytics.py

Real (non-hardcoded) analytics calculations for the Analytics page.
Kept out of app.py so this logic can be unit tested with a fake Calendar
service, the same pattern used elsewhere in backend/tools/.
"""

from datetime import datetime, timedelta

from backend.calendar_service.google_calendar import get_events_between
from backend.tools.availability import find_free_slots_with_classes

WORK_START_HOUR = 8
WORK_END_HOUR = 22
HOURS_PER_DAY = WORK_END_HOUR - WORK_START_HOUR
DAYS_PER_WEEK = 7
TOTAL_WEEKLY_HOURS = HOURS_PER_DAY * DAYS_PER_WEEK


def week_free_hours(service, user_id, reference_day=None):
    """Total free hours across the next 7 days (today + 6), combining
    Google Calendar events and local timetable classes. Returns None if
    no Calendar service is connected."""
    if not service:
        return None

    reference_day = reference_day or datetime.now()
    total = 0.0

    for offset in range(DAYS_PER_WEEK):
        day = reference_day + timedelta(days=offset)
        try:
            slots = find_free_slots_with_classes(
                service=service,
                user_id=user_id,
                day=day,
                work_start_hour=WORK_START_HOUR,
                work_end_hour=WORK_END_HOUR,
            )
        except Exception:
            continue
        for start, end in slots:
            total += (end - start).total_seconds() / 3600

    return total


def calendar_utilization_percent(free_hours):
    """Percentage of the week's working hours that are occupied.
    Returns None if free_hours is None (no Calendar connected)."""
    if free_hours is None:
        return None
    occupied_pct = 100 - (free_hours / TOTAL_WEEKLY_HOURS * 100)
    return max(0, min(100, occupied_pct))


def assignments_complete_percent(assignments):
    """assignments: list of dicts with a 'completed' bool (the shape
    AssignmentTracker.load_assignments() returns). Returns None if there
    are no assignments at all."""
    if not assignments:
        return None
    completed = sum(1 for a in assignments if a["completed"])
    return completed / len(assignments) * 100


def exam_has_study_sessions(service, exam):
    """True if a 'Study: {subject}' calendar event exists between now
    and the exam date."""
    now = datetime.now()
    if exam.exam_date <= now:
        return False
    try:
        events = get_events_between(service, now, exam.exam_date)
    except Exception:
        return False
    target_summary = f"Study: {exam.subject}"
    return any(event.get("summary") == target_summary for event in events)


def exams_with_study_plan_percent(service, upcoming_exams):
    """Percentage of upcoming (incomplete) exams that already have at
    least one study session on the calendar. Returns None if there are
    no upcoming exams, or no Calendar connected."""
    if not upcoming_exams or not service:
        return None
    with_plan = sum(1 for exam in upcoming_exams if exam_has_study_sessions(service, exam))
    return with_plan / len(upcoming_exams) * 100