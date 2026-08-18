from datetime import datetime

from backend.database.storage import get_exams
from backend.calendar_service.auth import get_calendar_service
from backend.tools.study_planner import create_exam_study_plan
from backend.tools.availability import find_free_slots_with_classes
from datetime import timedelta


USER_ID = 1  # Change this to your actual user ID


def main():

    exams = get_exams(
        USER_ID,
        include_completed=False,
    )

    if not exams:
        print("No upcoming exams found.")
        return

    exam = exams[0]

    print("\nEXAM")
    print("-" * 50)

    print("Subject:", exam.subject)
    print(
        "Exam:",
        exam.exam_date.strftime("%d %B %Y, %I:%M %p"),
    )
    print(
        "Required study:",
        exam.required_study_hours,
        "hours",
    )

    service = get_calendar_service(USER_ID)


    print("\nAVAILABILITY CHECK")
    print("-" * 60)

    check_day = datetime.now().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    exam_day = exam.exam_date.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    while check_day < exam_day:

        slots = find_free_slots_with_classes(
         service=service,
         user_id=USER_ID,
         day=check_day,
         work_start_hour=8,
         work_end_hour=22,
        )

        print(
            f"{check_day.strftime('%A, %d %b')}: "
            f"{len(slots)} free slot(s)"
        )

        for start, end in slots:
            print(
                f"    {start.strftime('%I:%M %p')} - "
                f"{end.strftime('%I:%M %p')}"
            )

        check_day += timedelta(days=1)

    print("-" * 60)

    plan = create_exam_study_plan(
        service=service,
        user_id=USER_ID,
        exam=exam,
        start_date=datetime.now(),
        max_hours_per_day=2,
        session_minutes=60,
    )

    print("\nSTUDY PLAN")
    print("-" * 60)

    sessions = plan["sessions"]

    for session in sessions:

        print(
            f"{session['start'].strftime('%A, %d %b')}  "
            f"{session['start'].strftime('%I:%M %p')} - "
            f"{session['end'].strftime('%I:%M %p')}  "
            f"({session['duration_minutes']} min)"
        )


    print("-" * 60)

    print(
        f"Required: "
        f"{exam.required_study_hours:.1f} hours"
    )
    print(
    f"Allocated: "
    f"{plan['allocated_minutes'] / 60:.1f} hours"
    )

    print(
    f"Remaining: "
    f"{plan['remaining_minutes'] / 60:.1f} hours"
    )

    if plan["fully_allocated"]:
        print(
            "STATUS: Study requirement satisfied."
        )
    else:
        print(
            "STATUS: Not enough free time before exam."
        )

if __name__ == "__main__":
    main()