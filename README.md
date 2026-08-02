# Smart Scheduler — AI Timetable Assistant

An AI-powered scheduling assistant for college students that manages class timetables, assignments, and Google Calendar events through a natural-language chat interface.

## 🎯 Project Overview
Part of the Capabl Shakshyam Internship Programme.

## 🛠️ Tech Stack
- **Frontend:** Streamlit, HTML, CSS
- **Backend:** Python
- **AI:** Google Gemini API (via `google-generativeai`)
- **Calendar:** Google Calendar API, Google OAuth
- **Storage:** JSON (current) → MySQL (in progress)

## 📁 Project Structure
```
TIMETABLE SCHEDULER/
├── app.py                      # Main Streamlit entry point
├── class_schedule.json         # Class/timetable data
├── semester_templates.json     # Saved semester templates
├── credentials.json            # Google OAuth credentials (gitignored)
├── token.json                  # Google OAuth token (gitignored)
├── .env                        # API keys (gitignored)
├── requirements.txt
├── components/
│   ├── styles.py                # Theme / design system
│   ├── sidebar.py                # Navigation sidebar
│   ├── hero.py                  # Welcome/greeting section
│   ├── calendar.py               # Weekly timetable UI
│   ├── chat.py                  # AI Scheduling Assistant chat panel
│   ├── cards.py                  # Topbar, metric cards, event list
│   └── analytics.py              # Analytics page
├── backend/
│   ├── agent/
│   │   ├── scheduler_agent.py    # Main AI agent logic
│   │   └── nlp_parser.py         # Gemini-powered intent parsing
│   ├── calendar_service/
│   │   ├── auth.py               # Google OAuth flow
│   │   ├── google_calendar.py    # Calendar API calls
│   │   └── schedule_manager.py   # Class/semester template CRUD
│   ├── database/
│   │   └── storage.py            # MySQL storage layer (in progress)
│   └── tools/
│       ├── assignment_tracker.py
│       ├── availability.py
│       ├── conflict_detector.py
│       ├── query_handler.py
│       └── reminder.py
└── tests/
```

## 🚀 Setup Instructions
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Add Google OAuth credentials as `credentials.json` in the project root
5. Create a `.env` file in the project root with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   (Get a free key at https://aistudio.google.com/apikey)
6. Run the app: `streamlit run app.py`
7. Click "Connect Google Calendar" in the sidebar and log in with your Google account.

## 🌟 Features
- **AI Scheduling Assistant** — natural-language chat (powered by Gemini) to schedule classes, find free time, track assignments, and detect conflicts, with in-chat Yes/No confirmation when a conflict is found
- **Google Calendar Integration** — secure OAuth2 login, view and create events directly on your primary Google Calendar
- **Weekly Timetable** — day-based grid (Mon–Sat) showing classes with subject, room, and instructor
- **Course-Specific Scheduling** — classes tagged as Lecture / Lab / Tutorial, each shown with a distinct color (purple / orange / green)
- **Semester Templates** — save a semester's full class list as a reusable template and apply it to a new semester in one click
- **Assignment Tracking** — add, complete, and track assignment deadlines
- **Conflict Detection** — flags overlapping events and suggests an alternative time before booking
- **Analytics Page** — weekly planning stats (events, classes, assignments, calendar utilization)

## ✅ Progress

**Week 1-2: Foundation**
- [x] Repo structure created
- [x] Development environment set up
- [x] Google Calendar authentication working
- [x] Simple event creation and viewing
- [x] Basic class schedule input and storage
- [x] Calendar display in Streamlit interface
- [ ] Deploy basic version on Streamlit Cloud

**Week 3-4: Core Scheduling Agent**
- [x] Natural language scheduling via Gemini-powered AI agent
- [x] Conflict detection for overlapping events (with in-chat confirmation)
- [x] Assignment deadline tracking
- [x] Scheduling queries ("find free time tomorrow", etc.)

**Week 5-6: Domain Specialization (Option A1 — Academic Schedule Manager)**
- [x] Semester/term-based schedule templates
- [x] Course-specific scheduling (Lecture / Lab / Tutorial)
- [ ] Exam schedule management with study time allocation
- [ ] Assignment deadline tracking with priority levels
- [ ] Indian academic calendar support (semester breaks, festivals)

**Week 7-8: Polish & Production**
- [x] Professional Streamlit interface (Smart Scheduler design system)
- [ ] MySQL-backed storage (currently JSON)
- [ ] Login page with user accounts
- [ ] Export functionality (calendar files, schedule reports)
- [ ] Deployment