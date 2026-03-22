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
@login_required
def upload_resume():

    file = request.files.get("resume")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    extracted_skills = parser.parse_resume(filepath) or []

    print("Extracted skills:", extracted_skills)

    # Update user normalized skills ONLY
    user.normalized_skills = ",".join(extracted_skills)

    # Clear old skills
    UserSkill.query.filter_by(user_id=user.id).delete()

    # Insert fresh skills
    for skill_name in extracted_skills:

        skill = Skill.query.filter_by(name=skill_name).first()

        if skill:
            db.session.add(UserSkill(
                user_id=user.id,
                skill_id=skill.id
            ))

    # Calculate skill score
    from backend.services.skill_score_engine import SkillScoreEngine
    score_engine = SkillScoreEngine()
    skill_score = score_engine.calculate_skill_score(user.id)

    resume = Resume(
        user_id=user.id,
        filename=file.filename,
        uploaded_at=datetime.utcnow(),
        skill_score=skill_score,
        normalized_skills=",".join(extracted_skills)
    )

    db.session.add(resume)
    db.session.commit()

    return jsonify({
        "message": "Resume processed successfully",
        "skills": extracted_skills
    })

@resume_routes.route("/api/resume-history")
@login_required
def resume_history():

    from flask import session, jsonify
    from backend.models import Resume

    user_id = session.get("user_id")

    if not user_id:
        return jsonify([])

    resumes = Resume.query\
        .filter_by(user_id=user_id)\
        .order_by(Resume.uploaded_at.desc())\
        .all()

    result = []

    for r in resumes:
        result.append({
            "id": r.id,
            "filename": r.filename,
            "uploaded_at": r.uploaded_at.strftime("%Y-%m-%d %H:%M") if r.uploaded_at else "",
            "skill_score": r.skill_score or 0
        })

    return jsonify(result)

@resume_routes.route("/resume-history")
@login_required
def resume_history_page():
    return render_template("resume_history.html")