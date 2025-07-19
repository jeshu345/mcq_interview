from flask import jsonify, request
from app.models import Admin, db,PythonMCQ , Batch , Candidate, BatchQuestion, AssignedMCQ, CandidateAnswer, CandidateExamStatus
from flask.views import MethodView
from flask_bcrypt import Bcrypt
import random
import json
from datetime import datetime, timedelta
import pytz # Combined import
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity # Combined import

# Initialize Bcrypt
bcrypt = Bcrypt()

# Initialize Timezone and constants
IST = pytz.timezone('Asia/Kolkata')
OTP_EXPIRY_TIME = 10  # Time in minutes after which OTP expires

class RegisterAdmin(MethodView):
    def post(self):
        data = request.get_json()
        name = data.get('name') # type: ignore
        email = data.get('email') # type: ignore
        password = data.get('password') # type: ignore
        mobile = data.get('mobile') # type: ignore
        is_active = data.get('is_active', True)

        # Ensure all fields are provided
        if not all([name, email, password, mobile]): # admin_id removed from check
            return jsonify({'error': 'Name, email, password, and mobile are required.'}), 400

        try:
            # Check for duplicates
            if Admin.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already registered.'}), 409

            if Admin.query.filter_by(mobile=mobile).first():
                return jsonify({'error': 'Mobile already registered.'}), 409

            # Hash password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Create and save new admin
            new_admin = Admin(
                name=name,
                email=email,
                password=hashed_password,
                mobile=mobile,
                is_active=is_active
            )
            db.session.add(new_admin)
            db.session.commit()

            return jsonify({'message': 'Admin registered successfully.'}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
class AdminLoginAPI(MethodView):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')  # type: ignore
            mobile = data.get('mobile')  # type: ignore
            password = data.get('password')  # type: ignore

            # Check if either email or mobile matches for admin
            admin = None
            if email:
                admin = Admin.query.filter_by(email=email).first()
            elif mobile:
                admin = Admin.query.filter_by(mobile=mobile).first()

            if admin:
                # Verify if the password matches using flask_bcrypt
                if bcrypt.check_password_hash(admin.password, password):
                    # Convert admin_id to string before creating token
                    access_token = create_access_token(identity=str(admin.admin_id), expires_delta=False)

                    return jsonify({'message': 'Admin Logged-in Successfully', 'access_token': access_token}), 200
                else:
                    return jsonify({'message': 'Invalid password'}), 401
            else:
                return jsonify({'message': 'Admin not found'}), 404

        except Exception as e:
            return jsonify({'message': 'Something went wrong!!!', 'error': str(e)}), 500


class ForgotPasswordAPI(MethodView):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email') # type: ignore
            
            if not email:
                return jsonify({'message': 'Email is required'}), 400

            # Fetch the student based on email
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                # Generate a 6-digit OTP
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                expiry_time = datetime.now(IST) + timedelta(minutes=OTP_EXPIRY_TIME)

                # Store the OTP and expiry time in the student's record
                admin.otp = otp
                admin.otp_expiry = expiry_time
                db.session.commit()

                # Simulate sending the OTP via email (replace this with actual email sending)
                print(f"OTP SENT TO {email}, YOUR OTP: {otp}")

                return jsonify({'message': 'OTP sent successfully', 'otp': otp}), 200
            else:
                return jsonify({'message': 'Admin not found'}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

class ResendOTPAPI(MethodView):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email') # type: ignore

            if not email:
                return jsonify({'message': 'Email is required'}), 400
            
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                # Generate a new OTP
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                expiry_time = datetime.now(IST) + timedelta(minutes=OTP_EXPIRY_TIME)

                # Store the new OTP and expiry time in the professor's record
                admin.otp = otp
                admin.otp_expiry = expiry_time
                db.session.commit()

                # Simulate sending the OTP via email (replace this with actual email sending)
                print(f"OTP RESENT TO {email}, YOUR NEW OTP: {otp}")

                return jsonify({'message': 'OTP resent successfully','new_otp':otp}), 200
            else:
                return jsonify({'message': 'Admin not found'}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

from pytz import utc # Already imported pytz, just need utc if used directly

class VerifyOTP(MethodView):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email') # type: ignore
            otp = data.get('otp') # type: ignore
            
            if not email or not otp:
                return jsonify({'message': 'Email and OTP are required'}), 400

            admin = Admin.query.filter_by(email=email).first()

            if not admin:
                return jsonify({'message': 'Admin not found'}), 404

            now_ist = datetime.now(utc).astimezone(IST)

            # Ensure otp_expiry is timezone-aware
            otp_expiry_aware = admin.otp_expiry.astimezone(IST) if admin.otp_expiry.tzinfo else IST.localize(admin.otp_expiry) # type: ignore

            if admin.otp == otp and otp_expiry_aware > now_ist:
                admin.is_verified = True
                admin.otp = "00000"  # Reset OTP
                db.session.commit()
                return jsonify({'message': 'OTP verified successfully'}), 200
            else:
                return jsonify({'message': 'Invalid OTP or OTP expired'}), 400

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


class ChangePassword(MethodView):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email') # type: ignore
            new_password = data.get('new_password') # type: ignore
            confirm_password = data.get('confirm_password') # type: ignore
            
            if not email or not new_password or not confirm_password:
                return jsonify({'message': 'Email, new password, and confirm password are required'}), 400

            # Fetch the proffesor based on email
            admin = Admin.query.filter_by(email=email).first()

            if not admin:
                return jsonify({'message': 'Admin not found'}), 404

            # Check if the Professor has been verified through OTP
            if admin.is_verified:
                # Check if new password and confirm password match
                if new_password == confirm_password:
                    # Hash the new password and update the student's password
                    new_hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    admin.password = new_hashed_password

                    # Reset verification status after successful password change
                    admin.is_verified = False  # Unset OTP verification status
                    admin.updated_at = datetime.now(IST)
                    db.session.commit()

                    return jsonify({'message': 'Password changed successfully'}), 200
                else:
                    return jsonify({'message': 'New password and confirm password do not match'}), 400
            else:
                return jsonify({'message': 'OTP not verified. Please verify OTP first.'}), 403

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

class NewPassword(MethodView):
    @jwt_required()
    def post(self):
        current_admin_id = get_jwt_identity() # This is admin_id (integer)
        try:
            admin = Admin.query.get(current_admin_id)
            if not admin:
                # This case should ideally be caught by @jwt_required if token is invalid/expired
                # or if user deleted after token issuance.
                return jsonify({'message': 'Admin not found or unauthorized'}), 404

            # Extract JSON data
            data = request.get_json()
            old_password = data.get('old_password') # type: ignore
            new_password = data.get('new_password') # type: ignore

            # Check for missing fields
            if not old_password or not new_password:
                return jsonify({'message': 'Old password and new password are required'}), 400

            # Validate the stored password hash
            if not admin.password:
                # Should not happen for a registered admin
                return jsonify({'message': 'Password is not set for this user. Please contact support.'}), 500

            # Verify the old password using bcrypt
            if not bcrypt.check_password_hash(admin.password, old_password):
                return jsonify({'message': 'Old password is incorrect'}), 400

            # Hash and update the new password
            new_hashed_password_str = bcrypt.generate_password_hash(new_password).decode('utf-8')

            admin.password = new_hashed_password_str
            admin.updated_at = datetime.now(IST)
            db.session.commit()

            return jsonify({'message': 'Password changed successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
            

class UpdateAdminProfile(MethodView):

    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()

        # Get the admin based on the JWT identity (which must be a string)
        auth_admin = Admin.query.get(int(current_user_id))  # convert to int if admin_id is integer
        if not auth_admin:
            return jsonify({'message': 'Unauthorized: Admin not found'}), 401

        try:
            data = request.get_json()

            name = data.get('name')
            email = data.get('email')
            mobile = data.get('mobile')
            gender = data.get('gender')
            dob = data.get('dob')
            is_active = data.get('is_active')

            # Check email duplication
            if email and email != auth_admin.email:
                if Admin.query.filter(Admin.email == email, Admin.admin_id != auth_admin.admin_id).first():
                    return jsonify({'error': 'Email already in use.'}), 400

            # Check mobile duplication
            if mobile and mobile != auth_admin.mobile:
                if Admin.query.filter(Admin.mobile == mobile, Admin.admin_id != auth_admin.admin_id).first():
                    return jsonify({'error': 'Mobile number already in use.'}), 400

            # Update fields only if provided
            if name:
                auth_admin.name = name
            if email:
                auth_admin.email = email
            if mobile:
                auth_admin.mobile = mobile
            if gender:
                auth_admin.gender = gender
            if dob:
                try:
                    auth_admin.dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'DOB must be in YYYY-MM-DD format.'}), 400
            if is_active is not None:
                auth_admin.is_active = bool(is_active)

            auth_admin.updated_at = datetime.now(IST)

            db.session.commit()

            return jsonify({'message': 'Admin profile updated successfully.'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500


class GetAllAdmins(MethodView):
    @jwt_required() # Added JWT protection
    def get(self):
        try:
            # Fetch all admins from the database
            admins = Admin.query.all()

            if not admins:
                return jsonify({'admins': []}), 200 # Return 200 with empty list

            # Serialize the list of admins (you can use a proper schema if needed)
            admin_list = []
            for admin in admins:
                admin_data = {
                    'admin_id': admin.admin_id,
                    'name': admin.name,
                    'email': admin.email,
                    'mobile': admin.mobile,
                    'is_active': admin.is_active,
                    'gender': admin.gender,
                    'dob': admin.dob.isoformat() if admin.dob else None, # type: ignore
                    'created_at': admin.created_at.isoformat() if admin.created_at else None, # type: ignore
                    'updated_at': admin.updated_at.isoformat() if admin.updated_at else None, # type: ignore
                }
                admin_list.append(admin_data)

            return jsonify({'admins': admin_list}), 200

        except Exception as e:
            return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500

class GetAdminByObjectId(MethodView):
    @jwt_required()  # Protect the endpoint with JWT authentication
    def get(self, admin_id):
        # Get the current logged-in user's ID from JWT
        current_user_id = get_jwt_identity()
        
        try:
            # Fetch admin based on the provided admin_id (from URL path parameter)
            # admin_id from path is a string, convert to int for query.get()
            try:
                target_admin_id = int(admin_id)
            except ValueError:
                return jsonify({'message': 'Invalid admin ID format in URL.'}), 400
            
            admin = Admin.query.get(target_admin_id)

            if not admin:
                return jsonify({'message': f'Admin with ID {target_admin_id} not found.'}), 404

            # Authorization: Example - an admin can only get their own details via this specific endpoint.
            # If any admin can get any other admin's details, this check might be different or removed.
            if admin.admin_id != int(current_user_id): # Ensure consistent type for comparison
                return jsonify({'message': 'Unauthorized to access this admin\'s details.'}), 403

            # Serialize the admin data
            admin_data = {
                'admin_id': admin.admin_id,
                'name': admin.name,
                'email': admin.email,
                'mobile': admin.mobile,
                'is_active': admin.is_active,
                'gender': admin.gender,
                'dob': admin.dob.isoformat() if admin.dob else None, # type: ignore
                'created_at': admin.created_at.isoformat() if admin.created_at else None, # type: ignore
                'updated_at': admin.updated_at.isoformat() if admin.updated_at else None, # type: ignore
            }

            return jsonify({'admin': admin_data}), 200

        except Exception as e:
            return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500




import json
from datetime import datetime
from pytz import timezone


IST = timezone('Asia/Kolkata')
filepath = "backend\python_mcqs.json"
def load_mcqs_from_json(filepath, batch_id, admin_id):
    with open(filepath, 'r', encoding='utf-8') as file:
        mcq_data = json.load(file)

    for idx, item in enumerate(mcq_data, start=1):
        question = PythonMCQ(
            batch_id=batch_id,
            question=item['question'],
            options=item['options'],
            answer=item['answer'],
            topic=item['topic'],
            difficulty=item['difficulty'],
            created_at=datetime.fromisoformat(item['created_at']).astimezone(IST),
            created_by=admin_id
        )
        db.session.add(question)

    db.session.commit()
    print(f"✅ {len(mcq_data)} MCQ questions added successfully.")


from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Constants
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = 'madhu.amunik@gmail.com'
SMTP_PASSWORD = 'jwtthzobwzfiwzey'
EXAM_LINK = 'https://yourdomain.com/exam/login'

# Helper: Generate user_id
def generate_user_id(name, number):
    return f"{name.lower().replace(' ', '')[:5]}{number:03d}"

# Helper: Send Email
def send_exam_email(to_email, user_id, raw_password, exam_link, start_date, end_date):
    subject = "Your Exam Login Credentials"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #2E86C1;">Welcome to Your Exam Portal</h2>
        <p>Dear Candidate,</p>
        <p>Your login credentials for the exam are:</p>
        <ul>
            <li><strong>User ID:</strong> {user_id}</li>
            <li><strong>Password:</strong> {raw_password}</li>
            <li><strong>Exam Window:</strong> {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}</li>
        </ul>
        <p>You are allowed to take the exam anytime within the above date range.</p>
        <p>Click the link below to begin the exam:</p>
        <a href="{exam_link}" style="padding: 10px 15px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Start Exam</a>
        <p style="margin-top: 20px;">All the best!</p>
        <p>Regards,<br>Exam Admin Team</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"[Email Error] Failed to send to {to_email}: {e}")

from werkzeug.utils import secure_filename


IST = pytz.timezone('Asia/Kolkata')
class CreateBatch(MethodView):
    @jwt_required()
    def post(self):
        current_admin_id = get_jwt_identity()

        try:
            if 'file' not in request.files:
                return jsonify({"error": "Excel file is required"}), 400

            file = request.files['file']
            candidates_data = parse_candidates_excel(file)

            title = request.form.get('title')
            if not title:
                return jsonify({"error": "Title is required"}), 400

            # Check batch title uniqueness
            if Batch.query.filter_by(title=title).first():
                return jsonify({"error": f"Batch with title '{title}' already exists"}), 400

            keywords = request.form.get('keywords', '[]')
            if isinstance(keywords, str):
                keywords = json.loads(keywords)

            total_candidates = int(request.form.get('total_candidates', len(candidates_data)))
            exam_duration = int(request.form.get('exam_duration', 60))

            start_date = datetime.strptime(request.form.get('start_date'), "%d-%m-%Y").date()
            end_date = datetime.strptime(request.form.get('end_date'), "%d-%m-%Y").date()

            # Create new batch
            batch = Batch(
                title=title,
                keywords=keywords,
                total_candidates=total_candidates,
                exam_duration=exam_duration,
                start_date=start_date,
                end_date=end_date,
                created_by=current_admin_id,
                created_at=datetime.now(IST)
            )
            db.session.add(batch)
            db.session.flush()

            emails_sent = 0
            skipped_emails = []
            used_user_ids = set()

            for i, candidate_info in enumerate(candidates_data):
                name = candidate_info.get('name')
                email = candidate_info.get('email')

                if not name or not email:
                    skipped_emails.append(email)
                    continue

                # Ensure unique user_id
                base_user_id = ''.join(name.lower().split())[:6]
                suffix = 1
                while True:
                    user_id = f"{base_user_id}{str(suffix).zfill(3)}"
                    if user_id not in used_user_ids and not Candidate.query.filter_by(user_id=user_id).first():
                        break
                    suffix += 1
                used_user_ids.add(user_id)

                raw_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                # Store raw password directly (NOT recommended in production)
                candidate = Candidate(
                    name=name,
                    email=email,
                    user_id=user_id,
                    password=raw_password,
                    batch_id=batch.batch_id,
                    created_at=datetime.now(IST)
                )
                db.session.add(candidate)

                try:
                    send_exam_email(
                        to_email=email,
                        user_id=user_id,
                        raw_password=raw_password,
                        exam_link=EXAM_LINK,
                        start_date=start_date,
                        end_date=end_date
                    )
                    emails_sent += 1
                except Exception:
                    skipped_emails.append(email)

            db.session.commit()

            return jsonify({
                "message": f"Batch '{title}' created successfully.",
                "emails_sent": emails_sent,
                "skipped_emails": skipped_emails
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500



from werkzeug.utils import secure_filename

import tempfile
import pandas as pd

def parse_candidates_excel(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp:
        file.save(temp.name)
        df = pd.read_excel(temp.name)
        return df.to_dict(orient="records")

class GetBatchCandidates(MethodView):
    @jwt_required()
    def get(self, batch_id):
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        candidates = Candidate.query.filter_by(batch_id=batch_id).all()

        candidate_list = [
            {
                "name": c.name,
                "email": c.email,
                "user_id": c.user_id,
                "password": c.password,  # ⚠️ raw password if stored in plaintext
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for c in candidates
        ]

        return jsonify({
            "batch_id": batch.batch_id,
            "title": batch.title,
            "exam_duration": batch.exam_duration,
            "start_date": batch.start_date.strftime("%d-%m-%Y"),
            "end_date": batch.end_date.strftime("%d-%m-%Y"),
            "total_candidates": batch.total_candidates,
            "candidates": candidate_list
        }), 200
import math
from sqlalchemy import func
import math
from sqlalchemy import func
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask import request, jsonify

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from datetime import datetime
from sqlalchemy.sql.expression import func

class AssignMCQsToBatch(MethodView):
    @jwt_required()
    def post(self, batch_id):
        try:
            admin_id = get_jwt_identity()

            batch = Batch.query.get(batch_id)
            if not batch:
                return jsonify({"error": "Batch not found"}), 404

            data = request.get_json()
            total_questions = int(data.get('num_questions', 10))

            # Define difficulty distribution
            easy_count = int(total_questions * 0.4)
            medium_count = int(total_questions * 0.3)
            hard_count = total_questions - easy_count - medium_count

            candidates = Candidate.query.filter_by(batch_id=batch_id).all()
            if not candidates:
                return jsonify({"error": "No candidates in this batch"}), 400

            for candidate in candidates:
                # Get random questions by difficulty
                easy_qs = PythonMCQ.query.filter_by(difficulty='Easy').order_by(func.rand()).limit(easy_count).all()
                medium_qs = PythonMCQ.query.filter_by(difficulty='Medium').order_by(func.rand()).limit(medium_count).all()
                hard_qs = PythonMCQ.query.filter_by(difficulty='Hard').order_by(func.rand()).limit(hard_count).all()

                selected = easy_qs + medium_qs + hard_qs
                if len(selected) > total_questions:
                    return jsonify({
                        "error": f"Not enough MCQs available for candidate {candidate.name}"
                    }), 400

                for mcq in selected:
                    if not mcq.batch_id:
                        mcq.batch_id = batch_id
                        db.session.add(mcq)

                    assignment = AssignedMCQ(
                        candidate_id=candidate.candidate_id,
                        question_id=mcq.id,
                        assigned_by=admin_id,
                        assigned_at=datetime.now(IST)
                    )
                    db.session.add(assignment)

            db.session.commit()
            return jsonify({
                "message": f"{total_questions} MCQs assigned to {len(candidates)} candidates in batch '{batch.title}'"
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

class AdminGetResults(MethodView):
    @jwt_required()
    def get(self, batch_id):
        try:
            batch = Batch.query.get(batch_id)
            if not batch:
                return jsonify({"error": "Batch not found"}), 404

            candidates = Candidate.query.filter_by(batch_id=batch_id).all()
            if not candidates:
                return jsonify({"message": "No candidates found for this batch"}), 200

            results = []
            for candidate in candidates:
                answers = CandidateAnswer.query.filter_by(candidate_id=candidate.candidate_id).all()
                
                # Compare selected_option with actual answer
                score = sum(
                    1 for ans in answers 
                    if ans.selected_option and ans.selected_option == ans.question.answer
                )

                total_attempted = len([a for a in answers if a.selected_option])

                # Fetch candidate exam status
                exam_status_record = CandidateExamStatus.query.filter_by(
                    candidate_id=candidate.candidate_id,
                    batch_id=batch_id
                ).first()

                is_submitted = exam_status_record.is_submitted if exam_status_record else False

                results.append({
                    "candidate_name": candidate.name,
                    "user_id": candidate.user_id,
                    "score": score,
                    "attempted": total_attempted,
                    "exam_status": "Submitted" if is_submitted else "Not Submitted"
                })

            return jsonify({
                "batch_title": batch.title,
                "results": results
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500












import json
from datetime import datetime
from pytz import timezone


IST = timezone('Asia/Kolkata')
filepath = "backend\python_mcqs.json"
def load_mcqs_from_json(filepath, batch_id, admin_id):
    with open(filepath, 'r', encoding='utf-8') as file:
        mcq_data = json.load(file)

    for idx, item in enumerate(mcq_data, start=1):
        question = PythonMCQ(
            batch_id=batch_id,
            question=item['question'],
            options=item['options'],
            answer=item['answer'],
            topic=item['topic'],
            difficulty=item['difficulty'],
            created_at=datetime.fromisoformat(item['created_at']).astimezone(IST),
            created_by=admin_id
        )
        db.session.add(question)

    db.session.commit()
    print(f"✅ {len(mcq_data)} MCQ questions added successfully.")

load_mcqs_from_json()