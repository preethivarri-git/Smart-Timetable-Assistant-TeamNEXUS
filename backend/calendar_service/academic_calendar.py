from datetime import date


# Indian academic calendar events.
# Dates can be updated each academic year.
INDIAN_ACADEMIC_CALENDAR = {
    2026: {
        # Public holidays / major festivals
        "holidays": {
            date(2026, 1, 26): "Republic Day",
            date(2026, 3, 4): "Holi",
            date(2026, 3, 21): "Eid-ul-Fitr",
            date(2026, 4, 3): "Good Friday",
            date(2026, 5, 1): "May Day",
            date(2026, 8, 15): "Independence Day",
            date(2026, 8, 26): "Janmashtami",
            date(2026, 10, 2): "Gandhi Jayanti",
            date(2026, 10, 20): "Dussehra",
            date(2026, 11, 8): "Diwali",
            date(2026, 11, 24): "Guru Nanak Jayanti",
            date(2026, 12, 25): "Christmas",
        },

        # College/academic breaks.
        # These are configurable rather than assumed to be universal.
        "breaks": [
            {
                "name": "Winter Break",
                "start": date(2026, 1, 1),
                "end": date(2026, 1, 4),
            },
            {
                "name": "Summer Vacation",
                "start": date(2026, 5, 15),
                "end": date(2026, 6, 15),
            },
        ],
    }
}


def get_holiday(date_value):
    """Return the holiday name for a date, or None."""
    year_data = INDIAN_ACADEMIC_CALENDAR.get(date_value.year, {})
    holidays = year_data.get("holidays", {})

    return holidays.get(date_value)


def is_holiday(date_value):
    """Return True if the date is a public/festival holiday."""
    return get_holiday(date_value) is not None


def get_academic_break(date_value):
    """Return the academic break containing the date, or None."""
    year_data = INDIAN_ACADEMIC_CALENDAR.get(date_value.year, {})

    for academic_break in year_data.get("breaks", []):
        if academic_break["start"] <= date_value <= academic_break["end"]:
            return academic_break

    return None


def is_academic_break(date_value):
    """Return True if the date falls inside an academic break."""
    return get_academic_break(date_value) is not None


def is_non_academic_day(date_value):
    """
    Return True when study scheduling should normally avoid the date.
    """
    return is_holiday(date_value) or is_academic_break(date_value)


def get_calendar_event(date_value):
    """Return information about a holiday/break for display."""
    holiday = get_holiday(date_value)

    if holiday:
        return {
            "type": "holiday",
            "name": holiday,
        }

    academic_break = get_academic_break(date_value)

    if academic_break:
        return {
            "type": "break",
            "name": academic_break["name"],
        }

    return None

def get_holidays(year):
    """Return all configured holidays for a year."""
    year_data = INDIAN_ACADEMIC_CALENDAR.get(year, {})
    return year_data.get("holidays", {})


def get_academic_breaks(year):
    """Return all configured academic breaks for a year."""
    year_data = INDIAN_ACADEMIC_CALENDAR.get(year, {})
    return year_data.get("breaks", [])


def add_holiday(year, holiday_date, name):
    """Add or update a holiday."""
    INDIAN_ACADEMIC_CALENDAR.setdefault(
        year,
        {"holidays": {}, "breaks": []}
    )

    INDIAN_ACADEMIC_CALENDAR[year]["holidays"][holiday_date] = name


def add_academic_break(year, name, start, end):
    """Add an academic break."""
    INDIAN_ACADEMIC_CALENDAR.setdefault(
        year,
        {"holidays": {}, "breaks": []}
    )

    INDIAN_ACADEMIC_CALENDAR[year]["breaks"].append({
        "name": name,
        "start": start,
        "end": end,
    })