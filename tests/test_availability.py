from datetime import datetime, timedelta

from backend.calendar_services.auth import authenticate_google
from backend.tools.availability import (
    find_free_slots,
    print_free_slots,
)

service = authenticate_google()

tomorrow = datetime.now() + timedelta(days=1)

slots = find_free_slots(service, tomorrow)

print_free_slots(slots)