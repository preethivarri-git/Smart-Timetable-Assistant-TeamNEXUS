"""
components/login.py

Streamlit login/signup UI. Call `require_login()` at the top of app.py —
it blocks the rest of the app from rendering until the user is logged in,
and sets st.session_state['user_id'] / ['username'] once they are.
"""

import re
import bcrypt
import streamlit as st

from backend.database.storage import (
    init_db, create_user, get_user_by_username
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None


def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()


def _login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        if not username or not password:
            st.error("Please enter both username and password.")
            return

        user = get_user_by_username(username)
        if user and _verify_password(password, user.password_hash):
            st.session_state.logged_in = True
            st.session_state.user_id = user.id
            st.session_state.username = user.username
            st.rerun()
        else:
            st.error("Invalid username or password.")


def _signup_form():
    with st.form("signup_form"):
        username = st.text_input("Choose a username")
        email = st.text_input("Email")
        password = st.text_input("Choose a password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Sign up")

    if submitted:
        if not username or not email or not password:
            st.error("All fields are required.")
            return
        if not EMAIL_RE.match(email):
            st.error("Please enter a valid email address.")
            return
        if len(password) < 6:
            st.error("Password must be at least 6 characters.")
            return
        if password != confirm:
            st.error("Passwords do not match.")
            return
        if get_user_by_username(username):
            st.error("That username is already taken.")
            return

        create_user(username, email, _hash_password(password))
        st.success("Account created! Please log in from the Login tab.")


def render_login_page():
    st.title("📅 Timetable Scheduler — Login")
    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])
    with tab_login:
        _login_form()
    with tab_signup:
        _signup_form()


def require_login():
    """Call this at the very top of app.py. Initializes the DB, shows the
    login page if needed, and stops execution until the user is logged in."""
    init_db()
    _init_session_state()

    if not st.session_state.logged_in:
        render_login_page()
        st.stop()