from flask import Blueprint, jsonify, render_template, session, request
from backend.utils.auth_decorator import login_required
from backend.services.cover_letter_service import CoverLetterService, TONES, LENGTHS
from backend.models import User, Resume

cover_letter_routes = Blueprint("cover_letter_routes", __name__)


def get_svc():
    return CoverLetterService()


def _get_unique_resumes(user_id, limit=6):
    """Deduplicated by filename, latest first, max 6."""
    all_resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.id.desc()).all()
    seen, result = set(), []
    for r in all_resumes:
        key = (r.filename or f"Resume #{r.id}").strip().lower()
        if key not in seen:
            seen.add(key)
            result.append(r)
        if len(result) >= limit:
            break
    return result


@cover_letter_routes.route("/cover-letter")
@login_required
def cover_letter_page():
    user_id = session["user_id"]
    user    = User.query.get(user_id)
    resumes = _get_unique_resumes(user_id)
    return render_template("cover_letter.html",
        user=user, resumes=resumes,
        tones=TONES, lengths=LENGTHS)


@cover_letter_routes.route("/api/cover-letter/generate", methods=["POST"])
@login_required
def generate():
    data      = request.get_json() or {}
    jd        = (data.get("job_description") or "").strip()
    company   = (data.get("company_name") or "").strip()
    role      = (data.get("role_name") or "").strip()
    manager   = (data.get("hiring_manager") or "").strip()
    tone      = data.get("tone", "professional")
    length    = data.get("length", "medium")
    notes     = (data.get("extra_notes") or "").strip()
    resume_id = data.get("resume_id")

    if not jd:      return jsonify({"error": "Job description is required"}), 400
    if not company: return jsonify({"error": "Company name is required"}), 400
    if not role:    return jsonify({"error": "Role name is required"}), 400

    try:
        result = get_svc().generate(
            user_id=session["user_id"],
            job_description=jd,
            company_name=company,
            role_name=role,
            hiring_manager=manager,
            tone=tone,
            length=length,
            extra_notes=notes,
            resume_id=int(resume_id) if resume_id else None,
        )
        return jsonify({"success": True, **result})
    except Exception as e:
        print(f"[CoverLetter] Error: {e}")
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500


@cover_letter_routes.route("/api/cover-letter/regenerate-paragraph", methods=["POST"])
@login_required
def regenerate_paragraph():
    data        = request.get_json() or {}
    paragraph   = (data.get("paragraph") or "").strip()
    instruction = (data.get("instruction") or "Make it stronger").strip()
    tone        = data.get("tone", "professional")
    context     = (data.get("context") or "").strip()

    if not paragraph:
        return jsonify({"error": "No paragraph provided"}), 400
    try:
        result = get_svc().regenerate_paragraph(paragraph, instruction, tone, context)
        return jsonify({"success": True, "paragraph": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cover_letter_routes.route("/api/cover-letter/tones")
@login_required
def get_tones():
    return jsonify(TONES)