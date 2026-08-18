from datetime import datetime

from backend.tools.study_planner import allocate_study_time


slots = [
    # Tuesday
    (
        datetime(2026, 8, 18, 8, 0),
        datetime(2026, 8, 18, 10, 15),
    ),

    # Wednesday
    (
        datetime(2026, 8, 19, 9, 0),
        datetime(2026, 8, 19, 13, 0),
    ),

    # Thursday
    (
        datetime(2026, 8, 20, 14, 0),
        datetime(2026, 8, 20, 18, 0),
    ),
]


sessions = allocate_study_time(
    available_slots=slots,
    required_hours=10,
    max_hours_per_day=2,
    session_minutes=60,
)


print("\nSTUDY PLAN")
print("-" * 60)

total_minutes = 0

for session in sessions:
    print(
        f"{session['start'].strftime('%A, %d %b')}  "
        f"{session['start'].strftime('%I:%M %p')} - "
        f"{session['end'].strftime('%I:%M %p')}  "
        f"({session['duration_minutes']} min)"
    )

    total_minutes += session["duration_minutes"]


print("-" * 60)
print(f"Total allocated: {total_minutes / 60:.1f} hours")