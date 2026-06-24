import random
from datetime import datetime, timedelta

class CBTSessionEngine:

    def __init__(self, exam, session):
        self.exam = exam
        self.session = session

    # 🔥 QUESTION LOADING RULES
    def load_questions(self, questions):

        if self.exam.shuffle_questions:
            random.shuffle(questions)

        if self.exam.shuffle_options:
            for q in questions:
                random.shuffle(q.options)

        return questions

    # ⏱ TIME CHECK ENGINE
    def is_time_up(self):
        return datetime.utcnow() > self.session.start_time + timedelta(minutes=self.exam.duration)

    # 🧠 SCORING ENGINE
    def score_exam(self, answers, questions):

        score = 0

        for q in questions:
            user_answer = answers.get(str(q.id))

            if user_answer and user_answer == q.answer:
                score += q.marks

        return score

    # 🚨 AUTO SUBMIT RULE
    def force_submit(self):
        self.session.submitted = True
        self.session.submitted_at = datetime.utcnow()