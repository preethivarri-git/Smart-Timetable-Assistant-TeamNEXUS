from datetime import datetime, timedelta

from backend.calendar_service.google_calendar import (
    get_events_for_day,
    format_event_summary,
    normalize_calendar_datetime,
)


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
        Prints all events for today/tomorrow/etc.
        """

        events = self._get_day_events(day_offset)

        if not events:
            print("\nNo events scheduled.\n")
            return

        print("\nYour Schedule\n")

        for event in events:
            print(format_event_summary(event))
            print("-" * 40)

    # ----------------------------------------------------

    def next_event(self):
        """
        Prints the next upcoming event.
        """

        now = normalize_calendar_datetime(datetime.now())

        future = now + timedelta(days=30)

        events = get_events_for_day(
            self.service,
            now,
            future
        )

        if not events:
            print("\nNo upcoming events.\n")
            return

        print("\nNext Event\n")
        print(format_event_summary(events[0]))

    # ----------------------------------------------------

    def events_after(self, hour):
        """
        Shows all events after a given hour.
        """

        events = self._get_day_events()

        found = False

        print(f"\nEvents after {hour}:00\n")

        for event in events:

            start = event["start"].get(
                "dateTime",
                event["start"].get("date")
            )

            start = datetime.fromisoformat(
                start.replace("Z", "+00:00")
            )

            if start.hour >= hour:

                found = True
                print(format_event_summary(event))
                print("-" * 40)

        if not found:
            print("No events found.")

    # ----------------------------------------------------

    def busy_hours(self, day_offset=0):
        """
        Calculates occupied hours.
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

        print(
            f"\nBusy for {hours:.1f} hour(s)\n"
        )

    # ----------------------------------------------------

    def has_events(self, day_offset=0):
        """
        Checks whether any events exist.
        """

        events = self._get_day_events(day_offset)

        if events:
            print(
                f"\nYes, you have {len(events)} event(s).\n"
            )
        else:
            print(
                "\nNo events scheduled.\n"
            )

    # ----------------------------------------------------

    def list_titles(self, day_offset=0):
        """
        Prints only event titles.
        """

        events = self._get_day_events(day_offset)

        if not events:
            print("\nNo events found.\n")
            return

        print("\nEvent List\n")

        for i, event in enumerate(events, 1):

            print(
                f"{i}. {event.get('summary', 'Untitled')}"
            )

    # ----------------------------------------------------

    def search_event(self, keyword):
        """
        Searches today's events by keyword.
        """

        events = self._get_day_events()

        found = False

        for event in events:

            title = event.get(
                "summary",
                ""
            ).lower()

            if keyword.lower() in title:

                found = True
                print(format_event_summary(event))
                print("-" * 40)

        if not found:
            print(
                "\nNo matching event found.\n"
            )