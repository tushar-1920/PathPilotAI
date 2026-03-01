from flask import Blueprint, request, jsonify, session, render_template
import os
from datetime import datetime

from backend.services.resume_parser import ResumeParser
from backend.extensions import db
from backend.models import User, Resume, UserSkill, Skill
from backend.utils.auth_decorator import login_required
from backend.services.career_identity_service import CareerIdentityService
from backend.services.resume_comparison_service import ResumeComparisonService
# ============================
# Blueprint
# ============================
resume_routes = Blueprint("resume_routes", __name__)

parser = ResumeParser()

# ============================
# Upload Folder Setup
# ============================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================
# Upload Resume Route
# ============================
@resume_routes.route("/api/upload-resume", methods=["POST"])
def upload_resume():

    file = request.files.get("resume")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # 🔐 Must be logged in
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(session["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 400

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Parse resume
    extracted_skills = parser.parse_resume(filepath)

    print("Extracted skills:", extracted_skills)

    # ==============================
    # 1️⃣ Save Resume Record
    # ==============================
    new_resume = Resume(
        user_id=user.id,
        filename=file.filename,
        uploaded_at=datetime.utcnow()
    )

    db.session.add(new_resume)

    # ==============================
    # 2️⃣ Update normalized_skills
    # ==============================
    user.normalized_skills = ",".join(extracted_skills)
    from backend.services.skill_score_engine import SkillScoreEngine

    score_engine = SkillScoreEngine()
    skill_score = score_engine.calculate_skill_score(user.id)

    new_resume = Resume(
        user_id=user.id,
        filename=file.filename,
        skill_score=skill_score
    )

    db.session.add(new_resume)
    db.session.commit()

    # ==============================
    # 3️⃣ Clear old UserSkill entries
    # ==============================
    UserSkill.query.filter_by(user_id=user.id).delete()

    # ==============================
    # 4️⃣ Insert fresh UserSkill records
    # ==============================
    for skill_name in extracted_skills:

        skill = Skill.query.filter_by(name=skill_name).first()

        if skill:
            user_skill = UserSkill(
                user_id=user.id,
                skill_id=skill.id
            )
            db.session.add(user_skill)

    identity_service = CareerIdentityService()
    identity = identity_service.detect_identity(user.id)

    db.session.commit()

    return jsonify({

        "message": "Resume processed successfully",
        "skills": extracted_skills,
        "identity": identity
    })

@resume_routes.route("/api/resume-compare")
@login_required
def compare_resumes():

    from flask import session
    service = ResumeComparisonService()

    result = service.compare_versions(session["user_id"])

    return jsonify(result)

@resume_routes.route("/api/resume-history")
@login_required
def resume_history():

    from flask import session

    resumes = Resume.query\
        .filter_by(user_id=session["user_id"])\
        .order_by(Resume.uploaded_at.desc())\
        .all()

    result = []

    for r in resumes:
        result.append({
            "id": r.id,
            "filename": r.filename,
            "uploaded_at": r.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "skill_score": r.skill_score or 0
        })

    return jsonify(result)

@resume_routes.route("/resume-history")
@login_required
def resume_history_page():
    return render_template("resume_history.html")