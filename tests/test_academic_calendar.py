from datetime import date

from backend.calendar_service.academic_calendar import (
    get_holidays,
    get_academic_breaks,
    add_holiday,
    add_academic_break,
    is_non_academic_day,
    get_calendar_event,
)


def main():
    print("2026 HOLIDAYS")
    print("-" * 40)

    for holiday_date, name in get_holidays(2026).items():
        print(holiday_date, "-", name)

    print("\n2026 ACADEMIC BREAKS")
    print("-" * 40)

    for academic_break in get_academic_breaks(2026):
        print(
            academic_break["name"],
            ":",
            academic_break["start"],
            "to",
            academic_break["end"],
        )

    # Test adding a custom holiday
    add_holiday(
        2026,
        date(2026, 9, 5),
        "College Foundation Day",
    )

    print("\nCUSTOM HOLIDAY")
    print("-" * 40)
    print(get_calendar_event(date(2026, 9, 5)))

    # Test adding a custom academic break
    add_academic_break(
        2026,
        "Semester Break",
        date(2026, 12, 20),
        date(2026, 12, 31),
    )

    print("\nCUSTOM BREAK")
    print("-" * 40)
    print(get_calendar_event(date(2026, 12, 25)))

    print("\nNON-ACADEMIC DAY CHECK")
    print("-" * 40)
    print(
        "15 Aug:",
        is_non_academic_day(date(2026, 8, 15)),
    )
    print(
        "18 Aug:",
        is_non_academic_day(date(2026, 8, 18)),
    )


if __name__ == "__main__":
    main()