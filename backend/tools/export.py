from datetime import datetime, timedelta
import csv
import io
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event as ICSEvent

DEFAULT_TIMEZONE = "Asia/Kolkata"


def _to_ics_datetime(value):
    """Ensures a value has tzinfo before handing it to icalendar — a naive
    datetime would otherwise be written as a "floating" time with no
    timezone, which some calendar apps interpret ambiguously."""
    if value.tzinfo is None:
        return value.replace(tzinfo=ZoneInfo(DEFAULT_TIMEZONE))
    return value


def _classes_to_ics_components(classes, weeks_ahead=12):
    """Classes are recurring (day-of-week only, no date), so this expands
    each one into one ICS event per matching weekday over the next
    `weeks_ahead` weeks, rather than expressing true RRULE recurrence —
    simpler, and works reliably when imported into any calendar app."""
    components = []
    weekday_index = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
    today = datetime.now().date()

    for class_entry in classes:
        target_weekday = weekday_index.get(class_entry.get("day"))
        if target_weekday is None:
            continue
        start_time_str = class_entry.get("start_time")
        end_time_str = class_entry.get("end_time")
        if not start_time_str or not end_time_str:
            continue
        try:
            start_time = datetime.strptime(str(start_time_str), "%H:%M").time()
            end_time = datetime.strptime(str(end_time_str), "%H:%M").time()
        except ValueError:
            continue

        days_until_first = (target_weekday - today.weekday()) % 7
        first_date = today + timedelta(days=days_until_first)

        for week in range(weeks_ahead):
            occurrence_date = first_date + timedelta(weeks=week)
            start_dt = _to_ics_datetime(datetime.combine(occurrence_date, start_time))
            end_dt = _to_ics_datetime(datetime.combine(occurrence_date, end_time))

            ics_event = ICSEvent()
            ics_event.add("summary", f"{class_entry['name']} ({class_entry.get('type', 'Lecture')})")
            ics_event.add("dtstart", start_dt)
            ics_event.add("dtend", end_dt)
            if class_entry.get("room"):
                ics_event.add("location", class_entry["room"])
            components.append(ics_event)

    return components


def _exams_to_ics_components(exams):
    """exams: list of Exam ORM rows (from backend.database.storage.get_exams)."""
    components = []
    for exam in exams:
        ics_event = ICSEvent()
        ics_event.add("summary", f"Exam: {exam.subject}")
        start_dt = _to_ics_datetime(exam.exam_date)
        end_dt = start_dt + timedelta(minutes=exam.duration_minutes or 180)
        ics_event.add("dtstart", start_dt)
        ics_event.add("dtend", end_dt)
        components.append(ics_event)
    return components


def _google_events_to_ics_components(events):
    """events: list of Google Calendar event dicts. All-day events (which
    only have a 'date', not a 'dateTime') are skipped — no time to anchor
    them by; the Week/Day/Month calendar views still show those directly."""
    components = []
    for event in events:
        start_raw = event["start"].get("dateTime")
        end_raw = event["end"].get("dateTime")
        if not start_raw or not end_raw:
            continue
        ics_event = ICSEvent()
        ics_event.add("summary", event.get("summary", "Untitled event"))
        ics_event.add("dtstart", datetime.fromisoformat(start_raw.replace("Z", "+00:00")))
        ics_event.add("dtend", datetime.fromisoformat(end_raw.replace("Z", "+00:00")))
        description = event.get("description")
        if description:
            ics_event.add("description", description)
        location = event.get("location")
        if location:
            ics_event.add("location", location)
        components.append(ics_event)
    return components


def export_full_schedule_to_ics(classes, exams, events, weeks_ahead=12):
    """Combines classes, exams, and Google Calendar events into one ICS
    file. Returns bytes, ready to hand to st.download_button."""
    cal = Calendar()
    cal.add("prodid", "-//Smart Scheduler//smart-scheduler//")
    cal.add("version", "2.0")

    for component in _classes_to_ics_components(classes, weeks_ahead):
        cal.add_component(component)
    for component in _exams_to_ics_components(exams):
        cal.add_component(component)
    for component in _google_events_to_ics_components(events):
        cal.add_component(component)

    return cal.to_ical()


def assignments_to_csv(assignments):
    """assignments: list of dicts from AssignmentTracker.load_assignments().
    Returns a CSV string."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Title", "Deadline", "Priority", "Status"])
    for a in assignments:
        writer.writerow([
            a["title"],
            a["deadline"],
            a.get("priority", "medium"),
            "Completed" if a["completed"] else "Pending",
        ])
    return buffer.getvalue()


def exams_to_csv(exams):
    """exams: list of Exam ORM rows. Returns a CSV string."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Subject", "Exam Date", "Duration (min)", "Required Study Hours", "Completed"])
    for exam in exams:
        writer.writerow([
            exam.subject,
            exam.exam_date.strftime("%Y-%m-%d %H:%M"),
            exam.duration_minutes,
            exam.required_study_hours,
            "Yes" if exam.completed else "No",
        ])
    return buffer.getvalue()