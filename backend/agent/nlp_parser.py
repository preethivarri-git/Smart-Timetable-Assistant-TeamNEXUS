import json
import os
from datetime import datetime

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-flash-latest")


SYSTEM_PROMPT = f"""
You are an AI scheduling assistant.

Today's date is {datetime.now().strftime("%Y-%m-%d")}.

Extract scheduling information from the user's request.

Return ONLY valid JSON.

The JSON format must always be:

{{
    "summary": "",
    "day_offset": 0,
    "hour": 0,
    "minute": 0,
    "duration": 1
}}

Rules:

1. "today" → day_offset = 0
2. "tomorrow" → day_offset = 1
3. Convert PM into 24-hour format.
4. If minutes aren't mentioned, use 0.
5. If duration isn't mentioned, assume 1 hour.

Examples

User:
Schedule AI Lab tomorrow at 3 PM for 2 hours

Output

{{
    "summary":"AI Lab",
    "day_offset":1,
    "hour":15,
    "minute":0,
    "duration":2
}}

--------------------

User:
Book gym today at 6 PM

Output

{{
    "summary":"Gym",
    "day_offset":0,
    "hour":18,
    "minute":0,
    "duration":1
}}

--------------------

User:
Meeting tomorrow at 10:30 AM for 3 hours

Output

{{
    "summary":"Meeting",
    "day_offset":1,
    "hour":10,
    "minute":30,
    "duration":3
}}
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
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)