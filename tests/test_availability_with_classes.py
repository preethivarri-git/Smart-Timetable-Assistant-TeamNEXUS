from datetime import datetime

from backend.tools.availability import find_free_slots_with_classes
from backend.calendar_service.auth import get_calendar_service

def main():
    user_id = 1  # CHANGE THIS to your actual logged-in user ID

    day = datetime(2026, 8, 18)  # Tuesday

    service = get_calendar_service(user_id)

    slots = find_free_slots_with_classes(
        service=service,
        user_id=user_id,
        day=day,
        work_start_hour=8,
        work_end_hour=22,
    )

    print("\nFREE SLOTS FOR:", day.strftime("%A, %d %B %Y"))
    print("-" * 50)

    if not slots:
        print("No free slots available.")
        return

    for start, end in slots:
        print(
            f"{start.strftime('%I:%M %p')} - "
            f"{end.strftime('%I:%M %p')}"
        )


if __name__ == "__main__":
    main()