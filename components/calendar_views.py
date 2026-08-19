

from datetime import datetime, timedelta, date as date_cls
from zoneinfo import ZoneInfo

import streamlit as st

from backend.calendar_service.google_calendar import get_events_between, DEFAULT_TIMEZONE
from backend.calendar_service.schedule_manager import get_color_for_class
from backend.database.storage import get_exams

DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

HOUR_HEIGHT_PX = 52
EXAM_COLOR = "#DE3030B6"
CLASS_BADGE_COLOR = "#298EE0B3"
EVENT_COLOR = "#C24FF7A2"


def _hour_decimal(time_str, fallback=None):
    """Parses 'HH:MM' or 'HH:MM:SS' into a decimal hour (e.g. '09:30' -> 9.5)."""
    if not time_str:
        return fallback
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            t = datetime.strptime(str(time_str), fmt).time()
            return t.hour + t.minute / 60
        except ValueError:
            continue
    return fallback


def _event_time_range(event):
    """Returns (start_datetime, end_datetime, is_all_day) for a Calendar event
    dict, normalized to the app's local timezone."""
    start_raw = event["start"].get("dateTime")
    end_raw = event["end"].get("dateTime")
    if not start_raw or not end_raw:
        return None, None, True
    tz = ZoneInfo(DEFAULT_TIMEZONE)
    start_dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00")).astimezone(tz).replace(tzinfo=None)
    end_dt = datetime.fromisoformat(end_raw.replace("Z", "+00:00")).astimezone(tz).replace(tzinfo=None)
    return start_dt, end_dt, False


def _week_bounds(reference_date):
    monday = reference_date - timedelta(days=reference_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _fetch_week_events(service, monday):
    if not service:
        return []
    week_start = datetime.combine(monday, datetime.min.time())
    week_end = week_start + timedelta(days=7)
    try:
        return get_events_between(service, week_start, week_end)
    except Exception:
        return []


def _fetch_exams_safe(user_id):
    try:
        return get_exams(user_id, include_completed=True)
    except Exception:
        return []


def _class_block_html(name, class_type, room, top_px, height_px, color):
    return "<div style=\"position:absolute;top:" + str(top_px) + "px;left:2px;right:2px;height:" + str(max(height_px, 22)) + "px;background:" + color + "22;border-left:3px solid " + color + ";border-radius:8px;padding:4px 6px;overflow:hidden;\"><div style=\"font-size:.68rem;font-weight:700;color:" + color + ";line-height:1.1\">" + class_type + "</div><div style=\"font-weight:600;font-size:.74rem;line-height:1.15;color:var(--text)\">" + name + "</div><div style=\"font-size:.65rem;color:var(--muted)\">" + room + "</div></div>"


def _event_block_html(summary, top_px, height_px):
    return "<div style=\"position:absolute;top:" + str(top_px) + "px;left:2px;right:2px;height:" + str(max(height_px, 22)) + "px;background:" + EVENT_COLOR + "22;border-left:3px solid " + EVENT_COLOR + ";border-radius:8px;padding:4px 6px;overflow:hidden;\"><div style=\"font-size:.68rem;font-weight:700;color:" + EVENT_COLOR + ";line-height:1.1\">Event</div><div style=\"font-weight:600;font-size:.74rem;line-height:1.15;color:var(--text)\">" + summary + "</div></div>"


def _exam_block_html(subject, top_px, height_px):
    return "<div style=\"position:absolute;top:" + str(top_px) + "px;left:2px;right:2px;height:" + str(max(height_px, 22)) + "px;background:" + EXAM_COLOR + "22;border-left:3px solid " + EXAM_COLOR + ";border-radius:8px;padding:4px 6px;overflow:hidden;\"><div style=\"font-size:.68rem;font-weight:700;color:" + EXAM_COLOR + ";line-height:1.1\">Exam</div><div style=\"font-weight:600;font-size:.74rem;line-height:1.15;color:var(--text)\">" + subject + "</div></div>"


def render_weekly_grid(classes, service, user_id, reference_date=None, work_start_hour=7, work_end_hour=22):
    """A time-axis weekly grid: hour rows on the left, day columns across the top,
    classes, exams, and Google Calendar events positioned by their actual
    start time/duration.

    Note: all-day Google Calendar events are skipped here (no time to position
    them by) — they still show up in the Day and Month views below.
    """
    reference_date = reference_date or datetime.now().date()
    monday, sunday = _week_bounds(reference_date)
    events = _fetch_week_events(service, monday)
    exams = [e for e in _fetch_exams_safe(user_id) if monday <= e.exam_date.date() <= sunday]

    total_hours = work_end_hour - work_start_hour
    grid_height = total_hours * HOUR_HEIGHT_PX

    st.markdown(
        "<div class='muted' style='margin-bottom:8px'>" + monday.strftime('%d %b') + " – " + sunday.strftime('%d %b %Y') + "</div>",
        unsafe_allow_html=True,
    )

    hour_labels = "".join(
        "<div style='height:" + str(HOUR_HEIGHT_PX) + "px;font-size:.68rem;color:var(--muted);border-top:1px solid var(--line);padding-top:2px'>" + f"{h:02d}:00" + "</div>"
        for h in range(work_start_hour, work_end_hour)
    )

    day_columns_html = ""
    for offset in range(7):
        day_date = monday + timedelta(days=offset)
        day_name = day_date.strftime("%A")

        blocks_html = ""

        for c in classes:
            if c.get("day") != day_name:
                continue
            start_h = _hour_decimal(c.get("start_time"))
            end_h = _hour_decimal(c.get("end_time"))
            if start_h is None or end_h is None:
                continue
            if end_h <= work_start_hour or start_h >= work_end_hour:
                continue
            top = (max(start_h, work_start_hour) - work_start_hour) * HOUR_HEIGHT_PX
            height = (min(end_h, work_end_hour) - max(start_h, work_start_hour)) * HOUR_HEIGHT_PX
            color = get_color_for_class(c)
            blocks_html += _class_block_html(c["name"], c.get("type", "Lecture"), c.get("room", ""), top, height, color)

        for event in events:
            start_dt, end_dt, is_all_day = _event_time_range(event)
            if is_all_day or start_dt.date() != day_date:
                continue
            start_h = start_dt.hour + start_dt.minute / 60
            end_h = end_dt.hour + end_dt.minute / 60
            if end_h <= work_start_hour or start_h >= work_end_hour:
                continue
            top = (max(start_h, work_start_hour) - work_start_hour) * HOUR_HEIGHT_PX
            height = (min(end_h, work_end_hour) - max(start_h, work_start_hour)) * HOUR_HEIGHT_PX
            blocks_html += _event_block_html(event.get("summary", "Untitled"), top, height)

        for exam in exams:
            if exam.exam_date.date() != day_date:
                continue
            start_h = exam.exam_date.hour + exam.exam_date.minute / 60
            end_h = start_h + (exam.duration_minutes or 180) / 60
            if end_h <= work_start_hour or start_h >= work_end_hour:
                continue
            top = (max(start_h, work_start_hour) - work_start_hour) * HOUR_HEIGHT_PX
            height = (min(end_h, work_end_hour) - max(start_h, work_start_hour)) * HOUR_HEIGHT_PX
            blocks_html += _exam_block_html(exam.subject, top, height)

        day_columns_html += "<div style=\"flex:1;min-width:0;border-left:1px solid var(--line);position:relative;height:" + str(grid_height) + "px\">" + blocks_html + "</div>"

    day_headers_html = "".join(
        "<div style='flex:1;text-align:center;font-size:.75rem;font-weight:600;color:var(--text)'>" + (monday + timedelta(days=o)).strftime('%a %d') + "</div>"
        for o in range(7)
    )

    grid_html = "<div class='glass-card' style='padding:14px 10px'>" + "<div style=\"display:flex;margin-left:52px;margin-bottom:6px\">" + day_headers_html + "</div>" + "<div style=\"display:flex\">" + "<div style=\"width:52px;flex-shrink:0\">" + hour_labels + "</div>" + "<div style=\"display:flex;flex:1\">" + day_columns_html + "</div>" + "</div>" + "</div>"

    st.markdown(grid_html, unsafe_allow_html=True)


def render_daily_view(classes, service, user_id, selected_date):
    """Hour-by-hour list for a single day, combining local classes, exams,
    and Google Calendar events."""
    day_name = selected_date.strftime("%A")

    items = []

    for c in classes:
        if c.get("day") != day_name:
            continue
        start_h = _hour_decimal(c.get("start_time"), fallback=0)
        items.append({
            "sort_key": start_h,
            "label": c["name"] + " (" + c.get("type", "Lecture") + ")",
            "time_str": str(c.get("start_time", "")) + " – " + str(c.get("end_time", "")),
            "detail": c.get("room", ""),
            "color": get_color_for_class(c),
        })

    for exam in _fetch_exams_safe(user_id):
        if exam.exam_date.date() != selected_date:
            continue
        exam_end = exam.exam_date + timedelta(minutes=exam.duration_minutes or 180)
        items.append({
            "sort_key": exam.exam_date.hour + exam.exam_date.minute / 60,
            "label": exam.subject + " (Exam)",
            "time_str": exam.exam_date.strftime('%I:%M %p') + " – " + exam_end.strftime('%I:%M %p'),
            "detail": "",
            "color": EXAM_COLOR,
        })

    if service:
        day_start = datetime.combine(selected_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        try:
            events = get_events_between(service, day_start, day_end)
        except Exception:
            events = []
        for event in events:
            start_dt, end_dt, is_all_day = _event_time_range(event)
            if is_all_day:
                items.append({"sort_key": -1, "label": event.get("summary", "Untitled"), "time_str": "All day", "detail": "", "color": EVENT_COLOR})
            else:
                items.append({
                    "sort_key": start_dt.hour + start_dt.minute / 60,
                    "label": event.get("summary", "Untitled"),
                    "time_str": start_dt.strftime('%I:%M %p') + " – " + end_dt.strftime('%I:%M %p'),
                    "detail": "",
                    "color": EVENT_COLOR,
                })

    items.sort(key=lambda i: i["sort_key"])

    st.markdown("<div class='muted' style='margin-bottom:8px'>" + selected_date.strftime('%A, %d %B %Y') + "</div>", unsafe_allow_html=True)

    if not items:
        st.markdown("<p class='muted'>Nothing scheduled this day.</p>", unsafe_allow_html=True)
        return

    rows_html = ""
    for item in items:
        detail_suffix = (" • " + item["detail"]) if item["detail"] else ""
        rows_html += "<div class='event-row' style='border-left:3px solid " + item["color"] + ";padding-left:10px'>" + "<div>" + "<div class='event-title'>" + item["label"] + "</div>" + "<div class='event-time'>" + item["time_str"] + detail_suffix + "</div>" + "</div>" + "</div>"

    st.markdown("<div class='glass-card'>" + rows_html + "</div>", unsafe_allow_html=True)


def render_monthly_view(classes, service, user_id, year, month):
    """A 6x7 month grid. Each cell shows the date and a count of items that
    day: recurring classes (green badge), exams (red badge), and Google
    Calendar events (blue badge)."""
    import calendar as pycal

    month_start = date_cls(year, month, 1)
    _, days_in_month = pycal.monthrange(year, month)
    month_end = date_cls(year, month, days_in_month)

    events_by_date = {}
    if service:
        range_start = datetime.combine(month_start, datetime.min.time())
        range_end = datetime.combine(month_end, datetime.min.time()) + timedelta(days=1)
        try:
            events = get_events_between(service, range_start, range_end)
        except Exception:
            events = []
        for event in events:
            start_dt, _, is_all_day = _event_time_range(event)
            event_date = start_dt.date() if start_dt else None
            if event_date is None:
                raw = event["start"].get("date")
                if raw:
                    event_date = datetime.strptime(raw, "%Y-%m-%d").date()
            if event_date:
                events_by_date.setdefault(event_date, []).append(event)

    exams_by_date = {}
    for exam in _fetch_exams_safe(user_id):
        d = exam.exam_date.date()
        if month_start <= d <= month_end:
            exams_by_date.setdefault(d, []).append(exam)

    classes_by_weekday = {}
    for c in classes:
        classes_by_weekday.setdefault(c.get("day"), []).append(c)

    st.markdown("<h3 style='margin:0 0 10px'>" + month_start.strftime('%B %Y') + "</h3>", unsafe_allow_html=True)

    header_cols = st.columns(7)
    for col, label in zip(header_cols, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        col.markdown("<div class='muted' style='text-align:center;font-weight:600;font-size:.75rem'>" + label + "</div>", unsafe_allow_html=True)

    first_weekday = month_start.weekday()
    total_cells = first_weekday + days_in_month
    total_rows = -(-total_cells // 7)

    cell_index = 0
    for _ in range(total_rows):
        row_cols = st.columns(7)
        for col in row_cols:
            day_number = cell_index - first_weekday + 1
            if 1 <= day_number <= days_in_month:
                cell_date = date_cls(year, month, day_number)
                weekday_name = cell_date.strftime("%A")
                class_count = len(classes_by_weekday.get(weekday_name, []))
                exam_count = len(exams_by_date.get(cell_date, []))
                event_count = len(events_by_date.get(cell_date, []))
                is_today = cell_date == datetime.now().date()

                border = "2px solid var(--primary)" if is_today else "1px solid var(--line)"
                dots = ""
                if class_count:
                    dots += "<span style='background:" + CLASS_BADGE_COLOR + ";color:white;border-radius:999px;padding:1px 6px;font-size:.62rem;margin-right:3px'>" + str(class_count) + " class</span>"
                if exam_count:
                    dots += "<span style='background:" + EXAM_COLOR + ";color:white;border-radius:999px;padding:1px 6px;font-size:.62rem;margin-right:3px'>" + str(exam_count) + " exam</span>"
                if event_count:
                    dots += "<span style='background:" + EVENT_COLOR + ";color:white;border-radius:999px;padding:1px 6px;font-size:.62rem'>" + str(event_count) + " event</span>"

                cell_html = "<div style='border:" + border + ";border-radius:10px;padding:6px;min-height:64px'>" + "<div style='font-size:.78rem;font-weight:600'>" + str(day_number) + "</div>" + "<div style='margin-top:4px'>" + dots + "</div>" + "</div>"
                col.markdown(cell_html, unsafe_allow_html=True)
            else:
                col.markdown("<div style='min-height:64px'></div>", unsafe_allow_html=True)
            cell_index += 1