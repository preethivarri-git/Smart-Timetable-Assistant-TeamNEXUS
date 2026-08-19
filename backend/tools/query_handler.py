from datetime import datetime, timedelta

from backend.calendar_service.google_calendar import (
    get_events_for_day,
    format_event_summary,
    normalize_calendar_datetime,
)


def _day_label(day_offset):
    if day_offset == 0:
        return "today"
    if day_offset == 1:
        return "tomorrow"
    day = datetime.now() + timedelta(days=day_offset)
    return f"on {day.strftime('%A, %d %B')}"


class QueryHandler:

    def __init__(self, service):
        self.service = service

    def _get_day_events(self, day_offset=0):
        """
        Returns all events for a specific day.
        """

        day = datetime.now() + timedelta(days=day_offset)

        start = day.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        end = day.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=0
        )

        return get_events_for_day(
            self.service,
            start,
            end
        )

    # ----------------------------------------------------

    def show_schedule(self, day_offset=0):
        """
        Returns a conversational summary of events for the given day.
        """

        events = self._get_day_events(day_offset)
        label = _day_label(day_offset)

        if not events:
            return f"You don't have anything scheduled {label}. 🎉"

        lines = [format_event_summary(event) for event in events]
        return f"Here's what's on {label}:\n\n" + "\n\n".join(lines)

    # ----------------------------------------------------

    def next_event(self):
        """
        Returns the next upcoming event, or a message if there isn't one.
        """

        now = normalize_calendar_datetime(datetime.now())

        future = now + timedelta(days=30)

        events = get_events_for_day(
            self.service,
            now,
            future
        )

        if not events:
            return "You don't have any upcoming events in the next 30 days."

        return "Your next event is:\n\n" + format_event_summary(events[0])

    # ----------------------------------------------------

    def events_after(self, hour):
        """
        Returns events after a given hour today.
        """

        events = self._get_day_events()

        matching = []

        for event in events:

            start = event["start"].get(
                "dateTime",
                event["start"].get("date")
            )

            start = datetime.fromisoformat(
                start.replace("Z", "+00:00")
            )

            if start.hour >= hour:
                matching.append(format_event_summary(event))

        if not matching:
            return f"You don't have anything after {hour}:00 today."

        return f"Events after {hour}:00 today:\n\n" + "\n\n".join(matching)

    # ----------------------------------------------------

    def busy_hours(self, day_offset=0):
        """
        Returns how many hours are occupied for the given day.
        """

        events = self._get_day_events(day_offset)

        total = timedelta()

        for event in events:

            start = event["start"].get(
                "dateTime",
                event["start"].get("date")
            )

            end = event["end"].get(
                "dateTime",
                event["end"].get("date")
            )

            start = datetime.fromisoformat(
                start.replace("Z", "+00:00")
            )

            end = datetime.fromisoformat(
                end.replace("Z", "+00:00")
            )

            total += end - start

        hours = total.total_seconds() / 3600
        label = _day_label(day_offset)

        if hours == 0:
            return f"You're completely free {label}."

        return f"You're busy for {hours:.1f} hour(s) {label}."

    # ----------------------------------------------------

    def has_events(self, day_offset=0):
        """
        Returns whether any events exist for the given day.
        """

        events = self._get_day_events(day_offset)
        label = _day_label(day_offset)

        if events:
            plural = "event" if len(events) == 1 else "events"
            return f"Yes, you have {len(events)} {plural} {label}."

        return f"No, you don't have anything scheduled {label}."

    # ----------------------------------------------------

    def list_titles(self, day_offset=0):
        """
        Returns only event titles for the given day.
        """

        events = self._get_day_events(day_offset)

        if not events:
            return "You don't have any events to list."

        lines = [
            f"{i}. {event.get('summary', 'Untitled')}"
            for i, event in enumerate(events, 1)
        ]

        return "\n".join(lines)

    # ----------------------------------------------------

    def search_event(self, keyword):
        """
        Searches today's events by keyword.
        """

        events = self._get_day_events()

        matches = [
            format_event_summary(event)
            for event in events
            if keyword.lower() in event.get("summary", "").lower()
        ]

        if not matches:
            return f"I couldn't find an event matching '{keyword}' today."

        return "\n\n".join(matches)