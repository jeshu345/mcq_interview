from flask import jsonify, request
from ..models import  db, Candidate,Batch, AssignedMCQ, CandidateAnswer, CandidateExamStatus
from flask.views import MethodView
from flask_bcrypt import Bcrypt
import random
import json
from datetime import datetime, timedelta
import pytz # Combined import
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity # Combined import

# Initialize Bcrypt
bcrypt = Bcrypt()

from datetime import datetime

# Initialize Timezone and constants
IST = pytz.timezone('Asia/Kolkata')
OTP_EXPIRY_TIME = 10  # Time in minutes after which OTP expires

from pytz import timezone

IST = timezone('Asia/Kolkata')

class CandidateLoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        user_id = data.get("user_id")
        password = data.get("password")

        if not user_id or not password:
            return jsonify({"message": "User ID and password are required"}), 400

        # Find candidate
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate or candidate.password != password:
            return jsonify({"message": "Invalid User ID or password"}), 401

        # Update last login time
        candidate.last_login_at = datetime.now(IST)
        db.session.commit()

        # Check if exam already submitted
        exam_status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=candidate.batch_id
        ).first()
        is_submitted = exam_status.is_submitted if exam_status else False

        # Generate access token
        access_token = create_access_token(identity=candidate.user_id)

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "candidate_name": candidate.name,
            "batch_id": candidate.batch_id,
            "is_submitted": is_submitted
        }), 200



class CandidateProfileAPI(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        batch = Batch.query.filter_by(batch_id=candidate.batch_id).first()
        if not batch:
            return jsonify({"error": "Batch data not found"}), 404

        return jsonify({
            "candidate_name": candidate.name,
            "batch_title": batch.title,
            "exam_start_date": batch.start_date.strftime("%d-%m-%Y"),
            "exam_end_date": batch.end_date.strftime("%d-%m-%Y"),
            "exam_duration": batch.exam_duration  # integer minutes
        }), 200

class CandidateMcqsAPI(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        assignments = AssignedMCQ.query.filter_by(candidate_id=candidate.candidate_id).all()
        if not assignments:
            return jsonify({"message": "No MCQs assigned to this candidate"}), 200

        mcqs = []
        for a in assignments:
            mcq = a.question
            mcqs.append({
                "question_id": mcq.id,
                "question": mcq.question,
                "options": mcq.options
            })

        return jsonify({
            "mcqs": mcqs
        }), 200
        
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from datetime import datetime
from app.models import Candidate, AssignedMCQ, CandidateAnswer, db
from pytz import timezone

IST = timezone("Asia/Kolkata")
class CandidateSaveAnswerAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'question_id' not in data or 'answer' not in data:
            return jsonify({"error": "Invalid input"}), 400

        # Fetch candidate from token user_id
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        question_id = data['question_id']
        selected_option = data['answer']

        # Ensure this question is assigned to this candidate
        assigned = AssignedMCQ.query.filter_by(
            candidate_id=candidate.candidate_id,
            question_id=question_id
        ).first()

        if not assigned:
            return jsonify({"error": "Question not assigned to candidate"}), 403

        # Check if answer already exists
        existing = CandidateAnswer.query.filter_by(
            candidate_id=candidate.candidate_id,
            question_id=question_id
        ).first()

        if existing:
            existing.selected_option = selected_option
            existing.answered_at = datetime.now(IST)
            existing.is_saved = True
        else:
            new_answer = CandidateAnswer(
                candidate_id=candidate.candidate_id,
                question_id=question_id,
                selected_option=selected_option,
                is_saved=True,
                answered_at=datetime.now(IST)
            )
            db.session.add(new_answer)

        db.session.commit()
        return jsonify({"message": "Answer saved successfully"}), 200
    
class GetAllAnswersAPI(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        # Fetch the candidate using user_id
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        # Get all answers by this candidate
        answers = CandidateAnswer.query.filter_by(candidate_id=candidate.candidate_id).all()
        if not answers:
            return jsonify({"message": "No answers found for this candidate"}), 200

        # Format the answers for response
        answer_list = []
        for answer in answers:
            answer_list.append({
                "question_id": answer.question_id,
                "selected_option": answer.selected_option,
                "is_saved": answer.is_saved,
                "answered_at": answer.answered_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({"answers": answer_list}), 200


IST = timezone('Asia/Kolkata')

class StartExamAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        if not candidate.batch_id:
            return jsonify({"error": "Candidate not assigned to a batch"}), 400

        # 🔒 Check if already submitted
        already_submitted = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=candidate.batch_id,
            is_submitted=True
        ).first()
        if already_submitted:
            return jsonify({"error": "You have already submitted this exam."}), 403

        # ✅ Allow resume if started but not submitted
        ongoing_exam = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=candidate.batch_id,
            is_submitted=False
        ).first()
        if ongoing_exam:
            return jsonify({"message": "Exam already started."}), 200

        # Start new exam session
        new_status = CandidateExamStatus(
            candidate_id=candidate.candidate_id,
            batch_id=candidate.batch_id,
            started_at=datetime.now(IST),
            is_submitted=False
        )
        db.session.add(new_status)
        db.session.commit()

        return jsonify({"message": "Exam started successfully."}), 200

class SubmitExamAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        exam_status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            is_submitted=False
        ).first()

        if not exam_status:
            return jsonify({
                "message": "No ongoing exam found or exam already submitted."
            }), 400

        batch = Batch.query.filter_by(batch_id=exam_status.batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        started_at = exam_status.started_at
        ended_at = datetime.now(IST)

        # Ensure timezone consistency
        if started_at.tzinfo is None:
            started_at = IST.localize(started_at)

        elapsed_minutes = (ended_at - started_at).total_seconds() / 60
        duration_status = "within time" if elapsed_minutes <= batch.exam_duration else "exceeded time"

        # Get answered vs assigned
        assigned_q_ids = {
            a.question_id for a in AssignedMCQ.query.filter_by(candidate_id=candidate.candidate_id).all()
        }
        saved_q_ids = {
            a.question_id for a in CandidateAnswer.query.filter_by(
                candidate_id=candidate.candidate_id, is_saved=True
            ).all()
        }

        unanswered_ids = assigned_q_ids - saved_q_ids

        # Update submission status
        exam_status.is_submitted = True
        exam_status.ended_at = ended_at
        db.session.commit()

        return jsonify({
            "message": "Exam submitted successfully.",
            "exam_duration_used_minutes": round(elapsed_minutes, 2),
            "duration_status": duration_status,
            "unanswered_question_ids": list(unanswered_ids)
        }), 200
