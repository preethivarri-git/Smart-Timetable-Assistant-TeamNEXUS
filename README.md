# Smart Timetable Assistant AI Agent

An AI-powered agent that helps manage and optimize schedules using Google Calendar, built with LangChain and Streamlit.

## 🎯 Project Overview
Part of the Capabl Shakshyam Internship Programme.

## 🛠️ Tech Stack
- Python
- LangChain
- Streamlit
- Google Calendar API

## 📁 Project Structure
## 🚀 Setup Instructions
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Add Google API credentials to `credentials/` folder
5. Run the app: `streamlit run app.py`
6. Click "🔐 Connect Google Calendar" and log in with your Google account.

## 🌟 Features
- **Google Calendar Integration** — secure OAuth2 login, connects to your primary Google Calendar
- **Event Creation & Viewing** — create calendar events directly from the app and view upcoming events
- **Class Schedule Management** — add, view, and delete classes with flexible (minute-level) time input
- **Colorful Weekly Timetable** — classes displayed in a clean, color-coded grid by day, with consistent colors per subject
- **Google Calendar Sync** — push your entire class schedule to Google Calendar with one click

## ✅ Progress
- [x] Repo structure created
- [x] Development environment set up
- [x] Google Calendar authentication working
- [x] Implement simple event creation and viewing functionality
- [x] Add basic class schedule input and storage
- [x] Create simple calendar display in Streamlit interface (color-coded weekly grid)
- [x] Sync class schedule to Google Calendar
- [ ] Deploy basic version on Streamlit Cloud