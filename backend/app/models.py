from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone
from sqlalchemy.dialects.mysql import JSON

db = SQLAlchemy()
IST = timezone('Asia/Kolkata')

class Admin(db.Model):
    __tablename__ = 'admins'

    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), default=None)
    password = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date)
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True, nullable=False)
    otp = db.Column(db.String(6))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), onupdate=lambda: datetime.now(IST))
    otp_expiry = db.Column(db.DateTime, default=lambda: datetime.now(IST) + timedelta(minutes=10))



class Candidate(db.Model):
    __tablename__ = 'candidates'

    candidate_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # plain text (not secure for prod)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), onupdate=lambda: datetime.now(IST))
    is_active = db.Column(db.Boolean, default=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'))
    last_login_at = db.Column(db.DateTime)


class Batch(db.Model):
    __tablename__ = 'batches'

    batch_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    keywords = db.Column(JSON)
    total_candidates = db.Column(db.Integer, default=0)
    exam_duration = db.Column(db.Integer, default=60)  # 🕒 duration in minutes
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    is_active = db.Column(db.Boolean, default=True)
    
    candidates = db.relationship('Candidate', backref='batch', lazy=True)
    rounds = db.relationship('InterviewRound', backref='batch', lazy=True)
    
    exam_statuses = db.relationship('CandidateExamStatus', backref='batch', lazy=True)
        
class InterviewRound(db.Model):
    __tablename__ = 'interview_rounds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))




    
class CandidateAnswer(db.Model):
    __tablename__ = 'candidate_answers'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('python_mcqs.id'), nullable=False)
    selected_option = db.Column(db.String(1))
    is_saved = db.Column(db.Boolean, default=False)
    answered_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))

    candidate = db.relationship('Candidate', backref='answers')
    # No duplicate backref on question here, because PythonMCQ already has `answers` relationship
    question = db.relationship('PythonMCQ')

   





class CandidateExamStatus(db.Model):
    __tablename__ = 'candidate_exam_status'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'), nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    ended_at = db.Column(db.DateTime)
    is_submitted = db.Column(db.Boolean, default=False)

class PythonMCQ(db.Model):
    __tablename__ = 'python_mcqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(JSON, nullable=False)
    answer = db.Column(db.String(1), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Enum('Easy', 'Medium', 'Hard'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=True)

    answers = db.relationship('CandidateAnswer', backref='python_question', lazy=True)


class BatchQuestion(db.Model):
    __tablename__ = 'batch_questions'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('python_mcqs.id'), nullable=False)
    
class AssignedMCQ(db.Model):
    __tablename__ = 'assigned_mcqs'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('python_mcqs.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    assigned_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=False)

    candidate = db.relationship('Candidate', backref='assigned_mcqs', lazy=True)
    question = db.relationship('PythonMCQ', backref='assigned_mcqs', lazy=True)  # ✅ this is required


