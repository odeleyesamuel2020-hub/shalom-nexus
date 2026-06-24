from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json
db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(150),
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


class Exam(db.Model):

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
        db.DateTime
    )

    end_date = db.Column(
        db.DateTime
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
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)

    question = db.Column(db.Text, nullable=False)

    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)

    answer = db.Column(db.String(1), nullable=False)  # a/b/c/d
    marks = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Option(db.Model):

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

class ExamSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))

    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    submitted = db.Column(db.Boolean, default=False)

    score = db.Column(db.Integer, default=0)

    # 🔐 NEW SECURITY FIELDS
    session_token = db.Column(db.String(120), unique=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)