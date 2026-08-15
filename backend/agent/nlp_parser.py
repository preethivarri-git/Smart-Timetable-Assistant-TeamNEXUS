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
You are the message classifier for a student scheduling assistant.

Today's date is {datetime.now().strftime("%Y-%m-%d")}.

Return ONLY valid JSON. Do not use Markdown.

Choose exactly one intent:

1. event
Use only when the user clearly asks to create a new calendar event or reminder.

Return:
{{
    "intent": "event",
    "summary": "",
    "day_offset": 0,
    "hour": 0,
    "minute": 0,
    "duration": 1
}}
Event rules:
- today means day_offset = 0
- tomorrow means day_offset = 1
- Convert AM/PM time to 24-hour format
- If minutes are not mentioned, use 0
- If duration is not mentioned, use 1 hour
- summary must be the event name and must never be empty


2. assignment
Use only when the user clearly asks to add an assignment.

Return:
{{
    "intent": "assignment",
    "title": "",
    "deadline": "YYYY-MM-DD"
}}

3. move_class
Use when the user asks to move an existing class.

Return:
{{
    "intent": "move_class",
    "class_query": "",
    "new_day": null,
    "new_start_time": null,
    "new_end_time": null
}}

4. question
Use when the user asks a question, explains something, corrects the assistant,
or makes a normal conversational statement.

Return:
{{
    "intent": "question",
    "response": "A short, helpful reply to the user's question."
}}
For a question, write a short helpful response.
Do not invent calendar events, assignments, conflicts, or approvals.
If the answer requires personal calendar data you do not have, say that clearly.

5. confirmation
Use only when the user clearly says yes, approve, confirm, or accept.

Return:
{{
    "intent": "confirmation"
}}

6. cancellation
Use only when the user clearly says no, cancel, reject, or do not schedule.

Return:
{{
    "intent": "cancellation"
}}

7. unknown
Use when the message is unclear.

Return:
{{
    "intent": "unknown",
    "response": "I am not sure what you would like to do. Please ask me to schedule an event, add an assignment, or ask about your timetable."
}}

Important rules:
- Never classify a question or normal comment as an event.
- Never create an event with an empty summary.
- "What was the conflict?" is a question.
- "I didn't approve it" is a question.
- "Schedule a doctor appointment tomorrow at 1 PM" is an event.
- "Add DBMS assignment due Friday" is an assignment.
"""
def parse_schedule_request(user_input):
    """
    Converts natural language into structured JSON.
    """
    model = _get_model()
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

    try:
        data = json.loads(text)

        if not isinstance(data, dict) or "intent" not in data:
            raise ValueError("Gemini returned an invalid response")

        return data

    except (json.JSONDecodeError, ValueError):
        return {
            "intent": "unknown",
            "response": "I could not understand that safely. Please rephrase your request."
        }