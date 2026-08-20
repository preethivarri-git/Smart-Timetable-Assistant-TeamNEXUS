# Smart Scheduler — AI Timetable Assistant

An AI-powered scheduling assistant for college students that manages class timetables, assignments, exams, and Google Calendar events through a natural-language chat interface.

## 🎯 Project Overview
Part of the Capabl Shakshyam Internship Programme.

## 🛠️ Tech Stack
- **Frontend:** Streamlit, HTML, CSS
- **Backend:** Python
- **AI:** Google Gemini API (via `google-generativeai`)
- **Calendar:** Google Calendar API, Google OAuth
- **Storage:** SQLite via SQLAlchemy ORM (`scheduler.db`), scoped per user
- **Auth:** Username/password login with bcrypt password hashing

## 📁 Project Structure
Smart-Timetable-Assistant/
├── app.py # Main Streamlit entry point
├── main.py # CLI entry point for testing the agentdirectly
├── credentials.json # Google OAuth credentials(gitignored)
├── token.json # Google OAuth token (gitignored, per-user tokens now live in the DB)
├── .env # API keys and email credentials (gitignored)
├── requirements.txt
├── scheduler.db # SQLite database (gitignored)
├── components/
│ ├── styles.py # Theme / design system
│ ├── login.py # Login / sign-up UI, session gate
│ ├── sidebar.py # Navigation sidebar, Calendar connect button
│ ├── hero.py # Welcome/greeting section
│ ├── calendar.py # Home page timetable: add/edit/delete classes
│ ├── calendar_views.py # Courses page: Week/Day/Month calendar views
│ ├── chat.py # AI Scheduling Assistant chat panel
│ ├── cards.py # Topbar, metric cards, event list
│ └── analytics.py # Analytics page (real, not placeholder, stats)
├── backend/
│ ├── agent/
│ │ ├── scheduler_agent.py # Main AI agent logic — routes commands, handles NLP intents
│ │ └── nlp_parser.py # Gemini-powered intent parsing
│ ├── calendar_service/
│ │ ├── auth.py # Google OAuth flow (per-user tokens, DB-backed)
│ │ ├── google_calendar.py # Calendar API calls
│ │ └── schedule_manager.py # Class/semester template CRUD
│ ├── database/
│ │ └── storage.py # SQLite/SQLAlchemy models: users, classes, assignments, exams, notification settings, Google tokens
│ └── tools/
│ ├── assignment_tracker.py # Assignment CRUD, due-date checks
│ ├── availability.py # Free-slot finding (Calendar + local classes)
│ ├── conflict_detector.py # Conflict detection (Calendar + local classes)
│ ├── query_handler.py # Conversational timetable queries
│ ├── reminder.py # Email reminders for due assignments
│ ├── study_planner.py # Exam study-session scheduling
│ ├── validation.py # Shared validation (class times, event requests, deadlines)
│ ├── friendly_errors.py # Human-readable Gemini/Calendar error messages
│ ├── analytics.py # Real analytics calculations (utilization, completion %, etc.)
│ └── export.py # ICS / CSV export
├── scripts/ # Manual/live scripts (not part of the automated test suite) — run directly, not via unittest
├── tests/ # Automated unit tests (mocked Calendar/Gemini, no live network)
├── assets/
├── pages/
└── utils/


## 🚀 Setup Instructions
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Add Google OAuth credentials as `credentials.json` in the project root
5. Create a `.env` file in the project root with:
GEMINI_API_KEY=your_gemini_api_key_here
EMAIL_ADDRESS=your_sender_email@gmail.com
EMAIL_PASSWORD=your_app_password
   - Get a free Gemini key at https://aistudio.google.com/apikey
   - `EMAIL_ADDRESS`/`EMAIL_PASSWORD` are only needed if you want assignment-deadline email reminders (Settings page). For Gmail with 2FA, use an **App Password**, not your normal password — Gmail will reject the real one for SMTP.
6. Run the app: `streamlit run app.py`
7. **Sign up** for an account on first launch (Login page → Sign up tab), then log in.
8. Click **"Connect Google Calendar"** in the sidebar and authorize with your Google account.

## 🌟 Features
- **Account system** — sign-up/login with bcrypt-hashed passwords; all data (classes, assignments, exams, Calendar tokens, notification settings) is scoped per user
- **AI Scheduling Assistant** — natural-language chat (powered by Gemini) to schedule events, move classes, find free time, track assignments, and answer conversational timetable questions ("what's on today", "am I busy tomorrow", "when's my next event"), with in-chat Yes/No confirmation on scheduling conflicts
- **Google Calendar Integration** — secure OAuth2 login, view and create events directly on your primary Google Calendar
- **Calendar Views** — Week (time-axis grid), Day (hour-by-hour list), and Month (badge grid) views combining local classes, exams, and Google Calendar events in one place
- **Weekly Timetable** — add, edit, and delete classes; Lecture/Lab/Tutorial each shown in a distinct color
- **Move a Class** — reschedule an existing class either from the timetable UI or via chat ("move DBMS to Wednesday 2pm")
- **Semester Templates** — save a semester's full class list as a reusable template and apply it to a new semester in one click
- **Assignment Tracking** — add, complete, and track assignment deadlines with priority levels, plus CSV export
- **Conflict Detection** — flags overlapping events against both Google Calendar *and* your local timetable, and suggests an alternative time before booking
- **Exam Scheduling** — exam tracking with automatic study-session allocation around your existing commitments, shown on the calendar in red
- **Email Reminders** — configurable per-user notification settings (enable/disable, days-before threshold, recipient email) for assignments due soon
- **Analytics Page** — real (not placeholder) weekly stats: calendar utilization, assignment completion rate, and % of upcoming exams with a study plan already scheduled
- **Export** — download your full schedule (classes + exams + Calendar events) as an `.ics` file, or assignments/exams as `.csv`
- **Friendly error handling** — Gemini quota/rate-limit and Google Calendar auth/availability errors show plain-language guidance instead of raw exception text

## ⚠️ Known Limitations
- **SQLite is not deployment-durable** — on most hosting platforms, `scheduler.db` won't persist across restarts/redeploys. Fine for local use and demos; a managed Postgres/MySQL instance is the next step for a real deployment.
- **Google OAuth uses a local-browser flow** (`InstalledAppFlow.run_local_server`), which only works when running the app on your own machine. Deploying this to a hosted platform requires switching to a web-based OAuth flow (authorization code + redirect URI), which is a real architecture change, not just a config tweak.
- **Email reminders are manually triggered**, not sent automatically in the background. Streamlit only runs code while someone has the page open, so true scheduled daily sends would need a separate background job (e.g. a cron script calling `ReminderService`) outside the Streamlit process.
- **`google-generativeai` is deprecated** upstream (Google's own deprecation notice) in favor of `google.genai`. Still functional as of this writing, but worth migrating eventually.