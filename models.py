from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, UTC
import random

db = SQLAlchemy()


# =========================
# HELPERS
# =========================

def utc_now():
    return datetime.now(UTC)


def generate_reg_no():
    return f"SHL-{random.randint(100000, 999999)}"


# =========================
# USER MODEL
# =========================

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="student"
    )

    registration_number = db.Column(
        db.String(50),
        unique=True
    )

    phone_number = db.Column(
        db.String(20)
    )

    institution = db.Column(
        db.String(120)
    )

    gender = db.Column(
        db.String(10)
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now
    )

    exams_created = db.relationship(
        "Exam",
        backref="creator",
        lazy=True
    )

    sessions = db.relationship(
    "ExamSession",
    back_populates="user",
    lazy=True
    )

    def __repr__(self):
        return f"<User {self.email}>"


# =========================
# EXAM MODEL
# =========================

class Exam(db.Model):

    __tablename__ = "exam"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    duration = db.Column(
        db.Integer,
        default=60
    )

    total_marks = db.Column(
        db.Integer,
        default=100
    )

    pass_mark = db.Column(
        db.Integer,
        default=50
    )

    is_published = db.Column(
        db.Boolean,
        default=False
    )

    show_result_immediately = db.Column(
        db.Boolean,
        default=True
    )

    shuffle_questions = db.Column(
        db.Boolean,
        default=True
    )

    shuffle_options = db.Column(
        db.Boolean,
        default=True
    )

    allow_review = db.Column(
        db.Boolean,
        default=True
    )

    allow_multiple_attempts = db.Column(
        db.Boolean,
        default=False
    )

    negative_marking = db.Column(
        db.Boolean,
        default=False
    )

    negative_mark_value = db.Column(
        db.Float,
        default=0.0
    )

    start_date = db.Column(
        db.DateTime(timezone=True)
    )

    end_date = db.Column(
        db.DateTime(timezone=True)
    )

    exam_code = db.Column(
        db.String(50),
        unique=True
    )

    instructions = db.Column(
        db.Text
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now
    )

    questions = db.relationship(
        "Question",
        backref="exam",
        lazy=True,
        cascade="all, delete-orphan"
    )

    sessions = db.relationship(
        "ExamSession",
        backref="exam",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Exam {self.title}>"


# =========================
# QUESTION MODEL
# =========================

class Question(db.Model):

    __tablename__ = "question"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exam.id"),
        nullable=False
    )

    question = db.Column(
        db.Text,
        nullable=False
    )

    option_a = db.Column(
        db.String(255),
        nullable=False
    )

    option_b = db.Column(
        db.String(255),
        nullable=False
    )

    option_c = db.Column(
        db.String(255),
        nullable=False
    )

    option_d = db.Column(
        db.String(255),
        nullable=False
    )

    answer = db.Column(
        db.String(1),
        nullable=False
    )

    marks = db.Column(
        db.Integer,
        default=1
    )

    status = db.Column(
        db.String(20),
        default="draft"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now
    )


# =========================
# OPTION MODEL
# =========================

class Option(db.Model):

    __tablename__ = "option"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("question.id")
    )

    option_text = db.Column(
        db.Text,
        nullable=False
    )

    is_correct = db.Column(
        db.Boolean,
        default=False
    )


# =========================
# EXAM SESSION MODEL
# =========================

class ExamSession(db.Model):

    __tablename__ = "exam_session"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exam.id"),
        nullable=False
    )

    start_time = db.Column(
        db.DateTime(timezone=True),
        default=utc_now
    )

    submitted = db.Column(
        db.Boolean,
        default=False
    )

    score = db.Column(
        db.Integer,
        default=0
    )

    session_token = db.Column(
        db.String(120),
        unique=True
    )

    last_activity = db.Column(
        db.DateTime(timezone=True),
        default=utc_now
    )

    # Relationships
    user = db.relationship(
        "User",
        back_populates="sessions"
    )


# =========================
# QUESTION BANK
# =========================

class QuestionBank(db.Model):

    __tablename__ = "question_bank"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    topic = db.Column(
        db.String(100)
    )

    question = db.Column(
        db.Text,
        nullable=False
    )

    option_a = db.Column(
        db.String(255),
        nullable=False
    )

    option_b = db.Column(
        db.String(255),
        nullable=False
    )

    option_c = db.Column(
        db.String(255),
        nullable=False
    )

    option_d = db.Column(
        db.String(255),
        nullable=False
    )

    answer = db.Column(
        db.String(1),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now
    )

    def __repr__(self):
        return f"<QuestionBank {self.subject}>"