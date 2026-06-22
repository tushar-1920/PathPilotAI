from flask import Blueprint, request, jsonify, session, render_template
import os
from datetime import datetime
from werkzeug.utils import secure_filename

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
# Security Constants
# ============================
ALLOWED_EXTS = {".pdf", ".docx"}
MAX_RESUME_BYTES = 5 * 1024 * 1024  # 5 MB


# ============================
# Upload Resume Route
# ============================
@resume_routes.route("/api/upload-resume", methods=["POST"])
@login_required
def upload_resume():

    file = request.files.get("resume")
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400

    # 1. Whitelist extensions — block .py, .exe, .sh, .php, anything else
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        return jsonify({"error": "Only PDF or DOCX files are allowed"}), 400

    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 2. Sanitize the user's filename — strips path components, special chars.
    #    Then prepend a server-controlled prefix (user_id + timestamp) so the
    #    name is unique AND the user-visible portion stays recognizable.
    user_part = secure_filename(file.filename) or f"resume{ext}"
    safe_name = f"u{user_id}_{int(datetime.utcnow().timestamp())}_{user_part}"
    filepath = os.path.join(UPLOAD_FOLDER, safe_name)

    # 3. Defense-in-depth: the resolved absolute path MUST stay inside
    #    UPLOAD_FOLDER. Blocks any leftover traversal attempts.
    if not os.path.abspath(filepath).startswith(
        os.path.abspath(UPLOAD_FOLDER) + os.sep
    ):
        return jsonify({"error": "Invalid file path"}), 400

    file.save(filepath)

    # 4. Size check post-save (defense alongside Flask's MAX_CONTENT_LENGTH)
    if os.path.getsize(filepath) > MAX_RESUME_BYTES:
        os.remove(filepath)
        return jsonify({"error": "File too large (max 5MB)"}), 413

    # ===== Existing parsing logic — UNCHANGED =====
    extracted_skills = parser.parse_resume(filepath) or []
    print("Extracted skills:", extracted_skills)

    # Update user normalized skills
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

    # Calculate skill score (SkillScoreEngine — unchanged for now)
    from backend.services.skill_score_engine import SkillScoreEngine
    score_engine = SkillScoreEngine()
    skill_score = score_engine.calculate_skill_score(user.id)

    # 5. Store the safe name in DB
    resume = Resume(
        user_id=user.id,
        filename=safe_name,
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


# ============================
# Resume History API — UNCHANGED
# ============================
@resume_routes.route("/api/resume-history")
@login_required
def resume_history():
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