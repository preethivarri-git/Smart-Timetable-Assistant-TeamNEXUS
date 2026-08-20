# 📅 Smart Scheduler — AI Timetable Assistant

Smart Scheduler is an AI-powered scheduling assistant for college students. It manages class timetables, assignments, and exams, and syncs with Google Calendar — all through a natural-language chat interface alongside a full visual dashboard.

The project integrates a **Streamlit frontend**, a **SQLite/SQLAlchemy backend**, and **Google's Gemini API** to turn plain-English requests like *"schedule a meeting tomorrow at 3pm"* into real calendar events, with conflict detection across both Google Calendar and your local timetable.

## 📖 Overview

Juggling classes, assignments, and exams across a messy patchwork of a paper planner, a phone calendar, and sticky notes is how deadlines get missed. Smart Scheduler centralizes all of it — timetable, assignments, exams, and Google Calendar — into one dashboard, and layers an AI assistant on top that understands requests in plain English instead of requiring a dozen dropdown menus.

## ✨ Features

- Account system with per-user data (bcrypt-hashed passwords)
- AI chat assistant (Gemini-powered) — schedule events, move classes, check free time, ask about your schedule
- Google Calendar integration (OAuth2, live event sync)
- Week / Day / Month calendar views combining classes, exams, and Calendar events
- Conflict detection across **both** Google Calendar and your local timetable, with in-chat Yes/No resolution
- Exam tracking with automatic study-session scheduling around your existing commitments
- Assignment tracking with priorities and configurable email reminders
- Semester templates — save and reapply a full timetable in one click
- Real analytics — calendar utilization, assignment completion rate, exam study coverage
- Export your schedule as `.ics`, and assignments/exams as `.csv`
- Friendly, human-readable error messages instead of raw exception text

## 🛠️ Technologies Used

**Frontend** — Streamlit, HTML, CSS
- User interface, timetable rendering, chat panel, calendar views

**Backend** — Python, SQLAlchemy, SQLite
- Business logic, per-user data storage, conflict/availability calculations

**AI** — Google Gemini (`google-generativeai`)
- Natural-language intent parsing for the chat assistant

**Calendar** — Google Calendar API, `google-auth-oauthlib`
- OAuth2 authentication, event creation and retrieval

**Other** — `bcrypt`, `icalendar`

## 🏗️ System Architecture
                         ┌──────────────┐
                         │     User     │
                         └──────┬───────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Streamlit Frontend   │
                    │       app.py         │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼─────────────────┐
              ▼                ▼                 ▼
       ┌─────────────┐  ┌─────────────┐  ┌───────────────┐
       │ Timetable   │  │ AI Chat     │  │ Calendar      │
       │ UI          │  │ Panel       │  │ Views         │
       └──────┬──────┘  └──────┬──────┘  └───────┬───────┘
              │                │                 │
              │                ▼                 │
              │       ┌──────────────────┐       │
              │       │ Gemini Intent    │       │
              │       │ Parser           │       │
              │       │ backend/agent/   │       │
              │       └────────┬─────────┘       │
              │                │                 │
              └────────────────┼─────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │   Scheduler Agent    │
                    │ backend/agent/       │
                    │ scheduler_agent.py   │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼──────────────────┐
              ▼                ▼                  ▼
     ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
     │ Conflict       │ │ Availability │ │ Study Planner  │
     │ Detector       │ │              │ │                │
     └───────┬────────┘ └──────┬───────┘ └───────┬────────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                 ┌──────────────────────────────┐
                 │       Data / Services        │
                 └──────────────┬───────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
          ┌──────────────────┐    ┌────────────────────┐
          │ Google Calendar  │    │ SQLite / SQLAlchemy │
          │ API              │    │                    │
          │                  │    │ users              │
          │ Events           │    │ classes            │
          │ OAuth            │    │ assignments        │
          │                  │    │ exams              │
          └──────────────────┘    │ notification       │
                                  │ settings           │
                                  │ Google tokens      │
                                  └────────────────────┘


## 🔄 Request Flow (Chat Example)

1. User types a request in the chat ("schedule DBMS review tomorrow at 5pm").
2. `scheduler_agent.py` first checks for simple keyword commands (e.g. "free time", "schedule today").
3. If none match, the request goes to `nlp_parser.py`, which calls Gemini to classify intent and extract structured fields (day, time, duration, etc.).
4. For an event request, `conflict_detector.py` checks both Google Calendar and the local timetable for overlaps.
5. No conflict → the event is created via the Calendar API. Conflict found → a Yes/No prompt is returned to the chat for the user to resolve.
6. The response is rendered back in the chat as plain, conversational text.

## 🚀 Installation

```bash
git clone https://github.com/<username>/Smart-Timetable-Assistant.git
cd Smart-Timetable-Assistant

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

Add your Google OAuth credentials as `credentials.json` in the project root, and create a `.env` file:
   GEMINI_API_KEY=your_gemini_api_key_here
   EMAIL_ADDRESS=your_sender_email@gmail.com
   EMAIL_PASSWORD=your_app_password

Run the app:

```bash
streamlit run app.py
```

Sign up for an account, log in, then click **"Connect Google Calendar"** in the sidebar.


## 👨‍💻 Authors

*POOJITHA*, *JAGRUTHI*, *PREETHI*

Built as part of the Capabl Shakshyam Internship Programme.