from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from cbt_engine import CBTSessionEngine

from datetime import datetime, timedelta

import uuid

import random

import json

from models import (
    db,
    User,
    Exam,
    Question,
    ExamSession
)

app = Flask(__name__)

# ======================
# CONFIG
# ======================
app.config["SECRET_KEY"] = "CHANGE_TO_SECURE_KEY"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shalom.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        email="odeleyesamuel2020@gmail.com"
    ).first()

    if not admin:

        admin = User(
            full_name="System Administrator",
            email="odeleyesamuel2020@gmail.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("✅ Default admin created")
# ======================
# LOGIN SETUP
# ======================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ======================
# ROLE GUARD
# ======================
def admin_required(func):
    def wrapper(*args, **kwargs):
        if current_user.role != "admin":
            return redirect(url_for("dashboard"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ======================
# HOME
# ======================
@app.route("/")
def home():
    return render_template("index.html")


# ======================
# AUTH
# ======================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")

        existing = User.query.filter_by(
            email=email
        ).first()

        if existing:
            return render_template(
                "register.html",
                error="Email already registered"
            )

        user = User(
            full_name=request.form.get("full_name"),
            email=email,
            password=generate_password_hash(
                request.form.get("password")
            ),
            role="student"
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = User.query.filter_by(email=request.form["email"]).first()

        if not user or not check_password_hash(user.password, request.form["password"]):
            return render_template("login.html", error="Invalid credentials")

        login_user(user)

        if user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# ======================
# DASHBOARDS
# ======================
@app.route("/dashboard")
@login_required
def dashboard():

    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))

    total_exams = Exam.query.filter_by(
        is_published=True
    ).count()

    taken = ExamSession.query.filter_by(
        user_id=current_user.id,
        submitted=True
    ).count()

    return render_template(
        "dashboard.html",
        total_exams=total_exams,
        taken=taken,
        user=current_user
    )


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    students = User.query.filter_by(
        role="student"
    ).count()

    exams = Exam.query.count()

    questions = Question.query.count()

    attempts = ExamSession.query.count()

    published_exams = Exam.query.filter_by(
        is_published=True
    ).count()

    return render_template(
        "admin_dashboard.html",
        user=current_user,
        students=students,
        exams=exams,
        questions=questions,
        attempts=attempts,
        published_exams=published_exams
    )


# ======================
# CREATE EXAM
# ======================
@app.route("/admin/create-exam", methods=["GET", "POST"])
@login_required
def create_exam():

    if current_user.role != "admin":
        return redirect(url_for("exams"))

    if request.method == "POST":

        exam = Exam(
            title=request.form.get("title"),
            subject=request.form.get("subject"),
            duration=int(
                request.form.get("duration", 60)
            )
        )

        db.session.add(exam)
        db.session.commit()

        return redirect(
            url_for(
                "question_builder",
                exam_id=exam.id
            )
        )

    return render_template("create_exam.html")

# MANAGE EXAM
@app.route("/admin/exam/<int:exam_id>/manage")
@login_required
def manage_exam(exam_id):

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    exam = Exam.query.get_or_404(exam_id)

    questions = Question.query.filter_by(exam_id=exam_id).all()

    return render_template(
        "manage_exam.html",
        exam=exam,
        questions=questions
    )


@app.route("/admin/exams")
@login_required
def admin_exams():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    exams = Exam.query.all()

    return render_template("admin_exams.html", exams=exams)
    
    
@app.route("/admin/question-builder/<int:exam_id>", methods=["GET", "POST"])
@login_required
def question_builder(exam_id):

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    exam = Exam.query.get_or_404(exam_id)

    if request.method == "POST":

        questions = request.form.getlist("question[]")
        option_a = request.form.getlist("option_a[]")
        option_b = request.form.getlist("option_b[]")
        option_c = request.form.getlist("option_c[]")
        option_d = request.form.getlist("option_d[]")
        answers = request.form.getlist("answer[]")

        saved_questions = []

        for q, a, b, c, d, ans in zip(
            questions,
            option_a,
            option_b,
            option_c,
            option_d,
            answers
        ):

            if not q or not q.strip():
                continue

            new_question = Question(
                exam_id=exam.id,
                question=q.strip(),
                option_a=a.strip() if a else "",
                option_b=b.strip() if b else "",
                option_c=c.strip() if c else "",
                option_d=d.strip() if d else "",
                answer=ans.lower().strip(),
                marks=1
            )

            db.session.add(new_question)
            saved_questions.append(new_question)

        db.session.commit()

        flash(
            f"{len(saved_questions)} question(s) saved successfully!",
            "success"
        )

        return redirect(
            url_for("manage_exam", exam_id=exam.id)
        )

    return render_template(
        "question_builder.html",
        exam=exam
    )
    
# ======================
# PUBLISH EXAM
# ======================
@app.route("/admin/publish-exam/<int:exam_id>")
@login_required
def publish_exam(exam_id):

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    exam = Exam.query.get_or_404(exam_id)

    exam.is_published = True
    db.session.commit()

    flash("Exam published successfully!", "success")

    return redirect(url_for("manage_exam", exam_id=exam.id))


# ======================
# STUDENT EXAMS
# ======================
@app.route("/exams")
@login_required
def exams():

    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))

    exams = Exam.query.filter_by(
        is_published=True
    ).all()

    return render_template(
        "exams.html",
        exams=exams
    )

# ======================
# START EXAM (SAAS ENGINE)
# ======================
@app.route("/exam/start/<int:exam_id>")
@login_required
def start_exam(exam_id):

    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))

    exam = Exam.query.get_or_404(exam_id)
    now = datetime.utcnow()

    # ⛔ availability check
    if exam.start_date and now < exam.start_date:
        flash("Exam not started", "warning")
        return redirect(url_for("exams"))

    if exam.end_date and now > exam.end_date:
        flash("Exam ended", "danger")
        return redirect(url_for("exams"))

    # 🔐 session lock
    session = ExamSession.query.filter_by(
        user_id=current_user.id,
        exam_id=exam_id
    ).first()

    if session and session.submitted:
        return redirect(url_for("results", exam_id=exam_id))

    if not session:
        session = ExamSession(
            user_id=current_user.id,
            exam_id=exam_id,
            start_time=now,
            submitted=False,
            session_token=str(uuid.uuid4())
        )
        db.session.add(session)
        db.session.commit()

    # ⏱ server timer enforcement
    elapsed = now - session.start_time

    if elapsed.total_seconds() > exam.duration * 60:
        session.submitted = True
        session.score = 0
        db.session.commit()

        return redirect(url_for("view_result", exam_id=exam_id))

    # 📦 load questions
    questions = Question.query.filter_by(exam_id=exam_id).all()

    if exam.shuffle_questions:
        random.shuffle(questions)

    return render_template(
        "take_exam.html",
        exam=exam,
        session=session,
        questions=questions,
        session_token=session.session_token
    )


# ======================
# SUBMIT EXAM
# ======================
@app.route("/submit-exam/<int:exam_id>", methods=["POST"])
@login_required
def submit_exam(exam_id):

    questions = Question.query.filter_by(
        exam_id=exam_id
    ).all()

    score = 0

    # scoring logic here...

    exam_session = ExamSession.query.filter_by(
        user_id=current_user.id,
        exam_id=exam_id
    ).first()

    exam_session.score = score
    exam_session.submitted = True

    db.session.commit()

    return render_template(
        "results.html",
        session=exam_session,
        total=len(questions)
    )


@app.route("/results")
@login_required
def results():

    student_results = (
        ExamSession.query
        .filter_by(
            user_id=current_user.id,
            submitted=True
        )
        .order_by(ExamSession.id.desc())
        .all()
    )

    return render_template(
        "results.html",
        results=student_results
    )


@app.before_request
def anti_cheat_guard():

    if current_user.is_authenticated:

        # block exam tampering routes if needed
        blocked_routes = []

        if request.endpoint in blocked_routes:
            return redirect(url_for("dashboard"))


@app.route("/admin/results")
@login_required
def admin_results():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    exams = Exam.query.all()

    return render_template("admin_results.html", exams=exams)

@app.route("/admin/results/<int:exam_id>")
@login_required
def view_results(exam_id):

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    exam = Exam.query.get_or_404(exam_id)
    sessions = ExamSession.query.filter_by(exam_id=exam_id).all()

    return render_template(
        "view_results.html",
        exam=exam,
        sessions=sessions
    )
    

@app.route("/admin/change-email", methods=["GET", "POST"])
@login_required
def change_email():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        new_email = request.form.get("email")

        if not new_email:
            flash("Email cannot be empty", "danger")
            return redirect(url_for("change_email"))

        current_user.email = new_email
        db.session.commit()

        flash("Email updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("change_email.html")
    
    

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)