import json
import os
from datetime import datetime

from dotenv import load_dotenv

try:
    import google.generativeai as genai
except Exception:
    genai = None

load_dotenv()

def _get_model():
    """Lazily configure and return the Gemini model. Raises informative error if library missing or key not set."""
    if genai is None:
        raise RuntimeError(
            "google.generativeai is not installed. Please install the official library: pip install google-generative-ai"
        )

api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    )


SYSTEM_PROMPT = f"""
You are an AI Scheduling Assistant.

Today's date is {datetime.now().strftime("%Y-%m-%d")}.

Your task is to identify the user's intent.

There are ONLY TWO intents:

1. event
2. assignment

Return ONLY valid JSON.

------------------------------------------------

If the user wants to schedule a calendar event,
return JSON in this format:

{{
    "intent": "event",
    "summary": "",
    "day_offset": 0,
    "hour": 0,
    "minute": 0,
    "duration": 1
}}

Rules:

- today → day_offset = 0
- tomorrow → day_offset = 1
- Convert PM to 24-hour format
- If minutes aren't mentioned, use 0
- If duration isn't mentioned, use 1 hour

Examples

User:
Schedule AI Lab tomorrow at 3 PM for 2 hours

Output

{{
    "intent":"event",
    "summary":"AI Lab",
    "day_offset":1,
    "hour":15,
    "minute":0,
    "duration":2
}}

----------------------------

User:
Book Gym today at 6 PM

Output

{{
    "intent":"event",
    "summary":"Gym",
    "day_offset":0,
    "hour":18,
    "minute":0,
    "duration":1
}}

------------------------------------------------

If the user wants to manage an assignment,
return JSON in this format:

{{
    "intent":"assignment",
    "title":"",
    "deadline":"YYYY-MM-DD"
}}

Examples

User:
Add assignment DBMS due tomorrow

Output

{{
    "intent":"assignment",
    "title":"DBMS",
    "deadline":"2026-07-20"
}}

----------------------------

User:
AI Report due Friday

Output

{{
    "intent":"assignment",
    "title":"AI Report",
    "deadline":"2026-07-24"
}}

----------------------------

User:
Add assignment Machine Learning Project due August 1

Output

{{
    "intent":"assignment",
    "title":"Machine Learning Project",
    "deadline":"2026-08-01"
}}

------------------------------------------------

Return ONLY valid JSON.

Do not explain anything.
"""


def parse_schedule_request(user_input):
    """
    Converts natural language into structured JSON.
    """

    response = model.generate_content(
        SYSTEM_PROMPT + "\n\nUser:\n" + user_input
    )

    text = response.text.strip()

    # Remove markdown if Gemini returns ```json
    if text.startswith("```"):
        text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

    return json.loads(text)
