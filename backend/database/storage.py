"""
backend/calendar_service/database/storage.py

SQLite + SQLAlchemy ORM layer for Timetable Scheduler.
All data (schedules, templates, assignments, google tokens) is scoped by user_id.
"""

import json
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ---------------------------------------------------------------------------
# Engine / Session setup
# ---------------------------------------------------------------------------
# SQLite file lives at project root. Switching to MySQL/Postgres later is a
# one-line change: e.g. "mysql+pymysql://user:pass@host/dbname"
DATABASE_URL = "sqlite:///scheduler.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite + Streamlit
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


@contextmanager
def get_session():
    """Context manager for a DB session. Usage: `with get_session() as db:`"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    google_token = relationship("GoogleToken", back_populates="user", uselist=False, cascade="all, delete-orphan")
    class_schedules = relationship("ClassSchedule", back_populates="user", cascade="all, delete-orphan")
    semester_templates = relationship("SemesterTemplate", back_populates="user", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="user", cascade="all, delete-orphan")


class GoogleToken(Base):
    __tablename__ = "google_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    token_json = Column(Text, nullable=False)  # serialized google.oauth2.credentials.Credentials
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="google_token")


class SemesterTemplate(Base):
    """
    A reusable snapshot of a weekly class timetable, NOT a date-ranged
    semester. Saved from a user's current classes for a given semester
    label and can be re-applied to populate a (possibly different)
    semester later. Scoped per-user; template names are unique per user.
    """
    __tablename__ = "semester_templates"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)           # e.g. "Fall 2026 Timetable"
    classes_json = Column(Text, nullable=False, default="[]")  # snapshot: list of class dicts
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="semester_templates")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_template_name"),
    )


class ClassSchedule(Base):
    """
    One recurring weekly class slot for a user. `semester` is a plain
    label (e.g. "Fall 2026") rather than a foreign key -- each semester
    is just the set of ClassSchedule rows sharing that label, giving the
    user one canonical weekly timetable per semester.
    """
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    semester = Column(String(100), nullable=False, default="Unassigned", index=True)

    course_name = Column(String(120), nullable=False)
    course_code = Column(String(30))
    class_type = Column(String(20), default="Lecture")   # Lecture / Lab / Tutorial
    day_of_week = Column(String(10), nullable=False)      # Monday, Tuesday, ...
    start_time = Column(String(5), nullable=False)        # "09:00"
    end_time = Column(String(5), nullable=False)          # "10:00"
    location = Column(String(120))
    instructor = Column(String(120))

    user = relationship("User", back_populates="class_schedules")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(150), nullable=False)
    course_name = Column(String(120))
    due_date = Column(DateTime, nullable=False)
    priority = Column(String(10), default="medium")       # low / medium / high
    status = Column(String(15), default="pending")        # pending / done
    description = Column(Text)

    user = relationship("User", back_populates="assignments")


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------
def init_db():
    """Create all tables if they don't exist. Call once at app startup."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# User helpers (used by components/login.py)
# ---------------------------------------------------------------------------
def create_user(username: str, email: str, password_hash: str) -> "User":
    with get_session() as db:
        user = User(username=username, email=email, password_hash=password_hash)
        db.add(user)
        db.flush()
        db.refresh(user)
        return User(id=user.id, username=user.username, email=user.email, password_hash=user.password_hash)


def get_user_by_username(username: str):
    with get_session() as db:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return None
        return User(id=user.id, username=user.username, email=user.email, password_hash=user.password_hash)


def get_user_by_id(user_id: int):
    with get_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None
        return User(id=user.id, username=user.username, email=user.email, password_hash=user.password_hash)


# ---------------------------------------------------------------------------
# Google token helpers (used by backend/calendar_service/auth.py)
# ---------------------------------------------------------------------------
def save_google_token(user_id: int, token_json: str):
    with get_session() as db:
        existing = db.query(GoogleToken).filter(GoogleToken.user_id == user_id).first()
        if existing:
            existing.token_json = token_json
            existing.updated_at = datetime.utcnow()
        else:
            db.add(GoogleToken(user_id=user_id, token_json=token_json))


def get_google_token(user_id: int):
    with get_session() as db:
        row = db.query(GoogleToken).filter(GoogleToken.user_id == user_id).first()
        return row.token_json if row else None


# ---------------------------------------------------------------------------
# Class schedule / semester template / assignment CRUD
# ---------------------------------------------------------------------------
def add_class_schedule(user_id, course_name, day_of_week, start_time, end_time,
                        course_code="", class_type="Lecture", location="",
                        instructor="", semester="Unassigned"):
    with get_session() as db:
        entry = ClassSchedule(
            user_id=user_id, course_name=course_name, course_code=course_code,
            class_type=class_type, day_of_week=day_of_week, start_time=start_time,
            end_time=end_time, location=location, instructor=instructor,
            semester=semester,
        )
        db.add(entry)
        db.flush()
        return entry.id


def get_class_schedules(user_id, semester=None):
    with get_session() as db:
        q = db.query(ClassSchedule).filter(ClassSchedule.user_id == user_id)
        if semester:
            q = q.filter(ClassSchedule.semester == semester)
        return q.order_by(ClassSchedule.day_of_week, ClassSchedule.start_time).all()


def update_class_schedule(schedule_id, user_id, **fields):
    """Update any subset of a class's editable columns. Scoped to user_id."""
    editable = {
        "course_name", "course_code", "class_type", "day_of_week",
        "start_time", "end_time", "location", "instructor", "semester",
    }
    with get_session() as db:
        entry = db.query(ClassSchedule).filter(
            ClassSchedule.id == schedule_id, ClassSchedule.user_id == user_id
        ).first()
        if not entry:
            return False
        for key, value in fields.items():
            if key in editable:
                setattr(entry, key, value)
        return True


def delete_class_schedule(schedule_id, user_id):
    with get_session() as db:
        entry = db.query(ClassSchedule).filter(
            ClassSchedule.id == schedule_id, ClassSchedule.user_id == user_id
        ).first()
        if entry:
            db.delete(entry)
            return True
        return False


def list_semesters(user_id):
    """Distinct semester labels this user currently has classes under."""
    with get_session() as db:
        rows = db.query(ClassSchedule.semester).filter(
            ClassSchedule.user_id == user_id
        ).distinct().all()
        semesters = sorted({r[0] for r in rows})
        return semesters or ["Unassigned"]


# ---------- Semester templates: reusable weekly-timetable snapshots ----------

def save_semester_template(user_id, name, semester):
    """
    Snapshot a user's current classes for `semester` into a named,
    reusable template. Overwrites an existing template of the same name
    for this user.
    """
    classes = get_class_schedules(user_id, semester=semester)
    snapshot = [
        {
            "course_name": c.course_name,
            "course_code": c.course_code,
            "class_type": c.class_type,
            "day_of_week": c.day_of_week,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "location": c.location,
            "instructor": c.instructor,
        }
        for c in classes
    ]
    classes_json = json.dumps(snapshot)

    with get_session() as db:
        existing = db.query(SemesterTemplate).filter(
            SemesterTemplate.user_id == user_id, SemesterTemplate.name == name
        ).first()
        if existing:
            existing.classes_json = classes_json
        else:
            db.add(SemesterTemplate(user_id=user_id, name=name, classes_json=classes_json))


def get_semester_templates(user_id):
    """Returns a list of dicts: {id, name, created_at, classes: [...]}."""
    with get_session() as db:
        rows = db.query(SemesterTemplate).filter(
            SemesterTemplate.user_id == user_id
        ).order_by(SemesterTemplate.name).all()
        return [
            {
                "id": t.id,
                "name": t.name,
                "created_at": t.created_at,
                "classes": json.loads(t.classes_json),
            }
            for t in rows
        ]


def delete_semester_template(user_id, name):
    with get_session() as db:
        existing = db.query(SemesterTemplate).filter(
            SemesterTemplate.user_id == user_id, SemesterTemplate.name == name
        ).first()
        if existing:
            db.delete(existing)
            return True
        return False


def apply_semester_template(user_id, template_name, target_semester):
    """
    Populate `target_semester` with classes from a saved template.
    Returns the list of newly created ClassSchedule ids.
    """
    with get_session() as db:
        template = db.query(SemesterTemplate).filter(
            SemesterTemplate.user_id == user_id, SemesterTemplate.name == template_name
        ).first()
        if not template:
            return []
        classes = json.loads(template.classes_json)
        new_ids = []
        for c in classes:
            entry = ClassSchedule(
                user_id=user_id,
                semester=target_semester,
                course_name=c.get("course_name"),
                course_code=c.get("course_code"),
                class_type=c.get("class_type", "Lecture"),
                day_of_week=c.get("day_of_week"),
                start_time=c.get("start_time"),
                end_time=c.get("end_time"),
                location=c.get("location"),
                instructor=c.get("instructor"),
            )
            db.add(entry)
            db.flush()
            new_ids.append(entry.id)
        return new_ids


def add_assignment(user_id, title, course_name, due_date, priority="medium", description=""):
    with get_session() as db:
        a = Assignment(
            user_id=user_id, title=title, course_name=course_name,
            due_date=due_date, priority=priority, description=description
        )
        db.add(a)
        db.flush()
        return a.id


def get_assignments(user_id, status=None):
    with get_session() as db:
        q = db.query(Assignment).filter(Assignment.user_id == user_id)
        if status:
            q = q.filter(Assignment.status == status)
        return q.order_by(Assignment.due_date).all()


def update_assignment_status(assignment_id, user_id, status):
    """Scoped to user_id so one user can't mark another user's assignment."""
    with get_session() as db:
        a = db.query(Assignment).filter(
            Assignment.id == assignment_id, Assignment.user_id == user_id
        ).first()
        if a:
            a.status = status
            return True
        return False


def delete_assignment(assignment_id, user_id):
    with get_session() as db:
        a = db.query(Assignment).filter(
            Assignment.id == assignment_id, Assignment.user_id == user_id
        ).first()
        if a:
            db.delete(a)
            return True
        return False