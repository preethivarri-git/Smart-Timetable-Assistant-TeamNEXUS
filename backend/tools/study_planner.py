from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from backend.calendar_service.google_calendar import (DEFAULT_TIMEZONE,create_event,get_events_between,)
from backend.tools.availability import find_free_slots_with_classes
from backend.calendar_service.academic_calendar import is_non_academic_day

def _to_naive_local(value):
    """Convert a datetime to naive Asia/Kolkata local time."""
    if value.tzinfo is not None:
        value = value.astimezone(
            ZoneInfo(DEFAULT_TIMEZONE)
        ).replace(tzinfo=None)

    return value

def allocate_study_time(available_slots,required_hours,max_hours_per_day=2,session_minutes=60,):
    if required_hours <= 0:
        return []
    required_minutes = int(required_hours * 60)
    max_daily_minutes = int(max_hours_per_day * 60)
    sessions = []
    allocated_minutes = 0
    daily_minutes = {}
    for slot_start, slot_end in sorted(available_slots,key=lambda slot: slot[0],):
        if allocated_minutes >= required_minutes:
            break
        current = slot_start
        day = current.date()
        used_today = daily_minutes.get(day, 0)
        while current < slot_end:
            if allocated_minutes >= required_minutes:
                break
            remaining_daily = (max_daily_minutes- used_today)
            if remaining_daily <= 0:
                break
            remaining_required = (required_minutes- allocated_minutes)
            available_minutes = int((slot_end - current).total_seconds() / 60)
            session_length = min(session_minutes,available_minutes,remaining_daily,remaining_required,)
            if session_length <= 0:
                break
            session_end = current + timedelta(minutes=session_length)
            sessions.append({"start": current,"end": session_end,"duration_minutes": session_length,})
            allocated_minutes += session_length
            used_today += session_length
            daily_minutes[day] = used_today
            current = session_end
    return sessions

def create_exam_study_plan(service,user_id,exam,start_date=None,work_start_hour=8,work_end_hour=22,max_hours_per_day=2,session_minutes=60,):
    now = datetime.now()
    if start_date is None:
        start_date = now
    elif start_date.tzinfo is not None:
        start_date = start_date.astimezone(
            ZoneInfo(DEFAULT_TIMEZONE)
        ).replace(tzinfo=None)
    exam_date = exam.exam_date
    if exam_date.tzinfo is not None:
        exam_date = exam_date.astimezone(
            ZoneInfo(DEFAULT_TIMEZONE)
        ).replace(tzinfo=None)
    start_date = start_date.replace(hour=0,minute=0,second=0,microsecond=0,)
    exam_date = exam_date.replace(hour=0,minute=0,second=0,microsecond=0,)
    if start_date >= exam_date:
        return []
    all_free_slots = []
    current_day = start_date
    while current_day < exam_date:
        if is_non_academic_day(current_day.date()):
            current_day += timedelta(days=1)
            continue
        now = datetime.now()
        if current_day.date() == now.date():
            if now.hour >= work_end_hour:
                free_slots = []
            else:
                day_start = max(
                    current_day.replace(
                        hour=work_start_hour,
                        minute=0,
                        second=0,
                        microsecond=0,
                    ),
                    now,
                )
                free_slots = find_free_slots_with_classes(
                    service=service,
                    user_id=user_id,
                    day=current_day,
                    work_start_hour=day_start.hour,
                    work_end_hour=work_end_hour,
                )
                free_slots = [
                    (
                        _to_naive_local(start),
                        _to_naive_local(end),
                    )
                    for start, end in free_slots
                ]
                adjusted_slots = []
                for start, end in free_slots:
                    if end <= now:
                        continue
                    if start < now:
                        start = now
                    if start < end:
                        adjusted_slots.append(
                            (start, end)
                        )
                free_slots = adjusted_slots
        else:
            free_slots = find_free_slots_with_classes(
                service=service,
                user_id=user_id,
                day=current_day,
                work_start_hour=work_start_hour,
                work_end_hour=work_end_hour,
            )
            free_slots = [
                (
                    _to_naive_local(start),
                    _to_naive_local(end),
                )
                for start, end in free_slots
            ]
        all_free_slots.extend(free_slots)
        current_day += timedelta(days=1)
    sessions = allocate_study_time(
        available_slots=all_free_slots,
        required_hours=exam.required_study_hours,
        max_hours_per_day=max_hours_per_day,
        session_minutes=session_minutes,
    )
    required_minutes = int(
        exam.required_study_hours * 60
    )
    allocated_minutes = sum(
        session["duration_minutes"]
        for session in sessions
    )
    remaining_minutes = max(
        required_minutes - allocated_minutes,
        0,
    )
    return {
        "sessions": sessions,
        "required_minutes": required_minutes,
        "allocated_minutes": allocated_minutes,
        "remaining_minutes": remaining_minutes,
        "fully_allocated": remaining_minutes == 0,
    }
def add_study_plan_to_calendar(service, exam, plan):
    if not plan or not plan.get("sessions"):
        return []
    created_events = []
    for session in plan["sessions"]:
        existing_events = get_events_between(service,session["start"],session["end"],)
        duplicate = False
        for event in existing_events:
            if event.get("summary") == f"Study: {exam.subject}":
                duplicate = True
                break
        if duplicate:
            continue
        event = create_event(
            service=service,
            summary=f"Study: {exam.subject}",
            start_time=session["start"],
            end_time=session["end"],
            description=(
                f"Study session for {exam.subject}.\n"
                f"Exam date: "
                f"{exam.exam_date.strftime('%d %B %Y, %I:%M %p')}\n"
                f"Duration: "
                f"{session['duration_minutes']} minutes."),)
        created_events.append(event)
    return created_events
def prioritize_exams(exams):
    return sorted(exams,key=lambda exam: exam.exam_date,)