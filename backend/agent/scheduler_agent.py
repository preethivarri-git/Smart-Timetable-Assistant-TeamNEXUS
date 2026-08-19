from datetime import datetime, timedelta
from backend.agent.nlp_parser import parse_schedule_request
from backend.calendar_service.auth import get_calendar_service
from backend.calendar_service.google_calendar import create_event
from backend.tools.assignment_tracker import AssignmentTracker
from backend.tools.availability import (find_free_slots,print_free_slots,)
from backend.tools.conflict_detector import check_conflicts
from backend.tools.query_handler import QueryHandler
from backend.calendar_service.schedule_manager import load_schedule, update_class
from backend.tools.validation import validate_event_request, validate_class_time
from googleapiclient.errors import HttpError
from backend.tools.friendly_errors import friendly_calendar_error, friendly_missing_credentials_message
def schedule(user_input, user_id):
    try:

        service = get_calendar_service(user_id)
        query = QueryHandler(service)
        tracker = AssignmentTracker(user_id)

        command = user_input.lower().strip()

        # ===================================================
        # Assignment Commands
        # ===================================================

        if command == "show assignments":
            tracker.show_assignments()
            return

        elif command.startswith("mark assignment"):
            try:
                assignment_id = int(command.split()[2])
                tracker.mark_completed(assignment_id)
            except Exception:
                print("\nUsage: mark assignment <id>\n")
            return

        elif command.startswith("remove assignment"):
            try:
                assignment_id = int(command.split()[2])
                tracker.remove_assignment(assignment_id)
            except Exception:
                print("\nUsage: remove assignment <id>\n")
            return

        # ===================================================
        # Free Time
        # ===================================================

        elif "free time" in command:
            day = datetime.now()
            if "tomorrow" in command:
                day += timedelta(days=1)
            slots = find_free_slots(service, day)
            print_free_slots(slots)
            return

        # ===================================================
        # Schedule Queries
        # ===================================================

        elif "schedule today" in command:
            query.show_schedule(0)
            return

        elif "schedule tomorrow" in command:
            query.show_schedule(1)
            return

        elif "next meeting" in command or "next event" in command:
            query.next_event()
            return

        elif "anything tomorrow" in command:
            query.has_events(1)
            return

        elif "busy tomorrow" in command:
            query.busy_hours(1)
            return

        # ===================================================
        # NLP
        # ===================================================

        data = parse_schedule_request(user_input)
        intent = data.get("intent")

        if intent == "question":
            return data.get(
                "response",
                "That looks like a question, so I did not create anything."
            )

        if intent == "confirmation":
            return "Please use the Yes button for the event currently waiting for approval."

        if intent == "cancellation":
            return "Please use the No button to cancel the event currently waiting for approval."

        if intent == "unknown":
            return data.get(
                "response",
                "I am not sure what you would like to do. Please rephrase your request."
            )

        if intent == "move_class":
            return _handle_move_class(data, user_id)

        if intent not in {"event", "assignment"}:
            return "I did not understand that request, so I did not create anything."

        # ===================================================
        # Assignment Intent
        # ===================================================

        if data["intent"] == "assignment":
            tracker.add_assignment(data["title"], data["deadline"])
            return

        # ===================================================
        # Event Intent
        # ===================================================

        summary = str(data.get("summary", "")).strip()

        if not summary:
            return "I could not identify an event name, so I did not create anything."

        try:
            day_offset = int(data["day_offset"])
            hour = int(data["hour"])
            minute = int(data["minute"])
            duration = float(data["duration"])
        except (KeyError, TypeError, ValueError):
            return "I could not understand the event date or time, so I did not create anything."

        validation_error = validate_event_request(day_offset, hour, minute, duration)
        if validation_error:
            return f"{validation_error} I did not create anything."

        start = datetime.now() + timedelta(days=day_offset)
        start = start.replace(hour=hour, minute=minute, second=0, microsecond=0)
        end = start + timedelta(hours=duration)

        result = check_conflicts(service, start, end, user_id=user_id)

        if result["conflict"]:
            # No console input() here — hand a structured conflict payload
            # back to the caller (chat.py) so it can render Yes/No buttons.
            conflicting_titles = [e.get("summary", "Untitled Event") for e in result["events"]]
            return {
                "status": "conflict",
                "summary": summary,
                "conflicting_events": conflicting_titles,
                "requested_start": start,
                "requested_end": end,
                "suggested_start": result["suggested_start"],
                "suggested_end": result["suggested_end"],
            }

        create_event(service, summary, start, end)
        return f"✅ '{summary}' scheduled for {start.strftime('%A %d %b, %I:%M %p')}."

    except FileNotFoundError:
        return friendly_missing_credentials_message()
    except HttpError as error:
        return friendly_calendar_error(error)
    except Exception as e:
        return f"Something went wrong while processing that request: {e}. Please try again."

def _parse_time_field(value):
    """Accepts '14:00', '09:05:00', '2:00 PM', or '2 PM'. Returns a
    datetime.time, or None if it can't be parsed."""
    if value is None:
        return None
    value = str(value).strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I %p"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def _handle_move_class(data, user_id):
    class_query = str(data.get("class_query", "")).strip().lower()
    if not class_query:
        return (
            "I couldn't tell which class to move. Please name it explicitly, "
            "e.g. 'move DBMS to Wednesday 2pm'."
        )

    classes = load_schedule(user_id)
    matches = [c for c in classes if class_query in c["name"].lower()]

    if not matches:
        return f"I couldn't find a class matching '{class_query}' in your timetable."

    if len(matches) > 1:
        names = ", ".join(sorted({c["name"] for c in matches}))
        return f"That matched more than one class ({names}). Please be more specific."

    target = matches[0]

    new_day = data.get("new_day") or target["day"]

    new_start_time = _parse_time_field(data.get("new_start_time")) or _parse_time_field(target["start_time"])
    new_end_time = _parse_time_field(data.get("new_end_time")) or _parse_time_field(target["end_time"])

    if new_start_time is None or new_end_time is None:
        return (
            "I couldn't understand the new day/time for that class. "
            "Please try rephrasing, e.g. 'move DBMS to Wednesday 2pm-3pm'."
        )

    validation_error = validate_class_time(new_start_time, new_end_time)
    if validation_error:
        return f"{validation_error} I did not move the class."

    update_class(
        user_id,
        target["id"],
        day_of_week=new_day,
        start_time=new_start_time.strftime("%H:%M"),
        end_time=new_end_time.strftime("%H:%M"),
    )

    return (
        f"✅ Moved '{target['name']}' to {new_day} "
        f"{new_start_time.strftime('%I:%M %p')}–{new_end_time.strftime('%I:%M %p')}."
    )

def confirm_conflict_schedule(summary, suggested_start, suggested_end, user_id):
    """Called from chat.py when the user clicks 'Yes' on a conflict prompt."""
    try:
        service = get_calendar_service(user_id)
        create_event(service, summary, suggested_start, suggested_end)
        return f"✅ '{summary}' scheduled for {suggested_start.strftime('%A %d %b, %I:%M %p')} (moved to avoid conflict)."
    except FileNotFoundError:
        return friendly_missing_credentials_message()
    except HttpError as error:
        return friendly_calendar_error(error)
    except Exception as e:
        return f"Something went wrong while scheduling that: {e}. Please try again."