"""
PathPilot AI — AI Recruiter Engine Routes
Real interview simulation with face detection, voice, follow-ups, evaluation.
"""

from flask import Blueprint, render_template, request, jsonify, session
from backend.services.ai_recruiter_service import AIRecruiterService
from backend.utils.auth_decorator import login_required
import logging

logger = logging.getLogger(__name__)

ai_recruiter_routes = Blueprint("ai_recruiter_routes", __name__)
recruiter_service   = AIRecruiterService()


# ─────────────────────────────────────────────────────────
#  PAGE ROUTES
# ─────────────────────────────────────────────────────────

@ai_recruiter_routes.route("/ai-recruiter")
@login_required
def ai_recruiter_home():
    """Landing page — choose level, role, personality."""
    user_id  = session.get("user_id")
    history  = recruiter_service.get_session_history(user_id, limit=5)
    return render_template("ai_recruiter.html", history=history)


@ai_recruiter_routes.route("/ai-recruiter/room/<int:session_id>")
@login_required
def interview_room(session_id):
    """Live interview room."""
    user_id = session.get("user_id")
    iv_sess = recruiter_service.get_session(session_id)
    if not iv_sess or iv_sess.user_id != user_id:
        from flask import redirect, url_for
        return redirect(url_for("ai_recruiter_routes.ai_recruiter_home"))
    return render_template("ai_recruiter_room.html", iv_session=iv_sess)


@ai_recruiter_routes.route("/ai-recruiter/result/<int:session_id>")
@login_required
def interview_result(session_id):
    """Final recruiter report page."""
    user_id = session.get("user_id")
    iv_sess = recruiter_service.get_session(session_id)
    if not iv_sess or iv_sess.user_id != user_id:
        from flask import redirect, url_for
        return redirect(url_for("ai_recruiter_routes.ai_recruiter_home"))
    result = recruiter_service.get_full_result(session_id)
    return render_template("ai_recruiter_result.html", result=result, iv_session=iv_sess)


# ─────────────────────────────────────────────────────────
#  API ROUTES
# ─────────────────────────────────────────────────────────

@ai_recruiter_routes.route("/api/ai-recruiter/start", methods=["POST"])
@login_required
def start_session():
    """Create a new interview session."""
    try:
        user_id = session.get("user_id")
        data    = request.get_json(force=True) or {}

        role         = data.get("role", "Software Engineer")
        level        = data.get("level", "intermediate")       # fresher / intermediate / advanced / faang
        personality  = data.get("personality", "balanced")     # friendly / strict / faang / startup
        resume_text  = data.get("resume_text", "")

        iv_sess = recruiter_service.create_session(
            user_id     = user_id,
            role        = role,
            level       = level,
            personality = personality,
            resume_text = resume_text,
        )

        # Get opening message from AI
        opening = recruiter_service.get_opening_message(iv_sess)

        return jsonify({
            "success":    True,
            "session_id": iv_sess.id,
            "room_url":   f"/ai-recruiter/room/{iv_sess.id}",
            "opening":    opening,
        })
    except Exception as e:
        logger.error(f"start_session error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_recruiter_routes.route("/api/ai-recruiter/message", methods=["POST"])
@login_required
def send_message():
    """
    User sends an answer. AI responds with follow-up or next question.
    Also processes face expression data sent from frontend.
    """
    try:
        user_id = session.get("user_id")
        data    = request.get_json(force=True) or {}

        session_id     = data.get("session_id")
        user_message   = data.get("message", "").strip()
        face_data      = data.get("face_data", {})   # { expression, confidence, eye_contact, hesitation }
        audio_features = data.get("audio_features", {})  # { pauses, speed, confidence }

        if not session_id or not user_message:
            return jsonify({"success": False, "error": "Missing fields"}), 400

        iv_sess = recruiter_service.get_session(session_id)
        if not iv_sess or iv_sess.user_id != user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        if iv_sess.status == "ended":
            return jsonify({"success": False, "error": "Interview ended"}), 400

        result = recruiter_service.process_answer(
            session    = iv_sess,
            user_msg   = user_message,
            face_data  = face_data,
            audio_data = audio_features,
        )

        return jsonify({
            "success":       True,
            "ai_response":   result["ai_response"],
            "interview_over": result["interview_over"],
            "live_score":    result["live_score"],      # hidden score updated silently
            "question_num":  result["question_num"],
            "interrupt":     result["interrupt"],       # True if AI interrupts
            "interrupt_msg": result.get("interrupt_msg", ""),
        })

    except Exception as e:
        logger.error(f"send_message error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_recruiter_routes.route("/api/ai-recruiter/evaluate", methods=["POST"])
@login_required
def evaluate_session():
    """End the interview and generate the full recruiter report."""
    try:
        user_id    = session.get("user_id")
        data       = request.get_json(force=True) or {}
        session_id = data.get("session_id")

        iv_sess = recruiter_service.get_session(session_id)
        if not iv_sess or iv_sess.user_id != user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        report = recruiter_service.generate_final_report(iv_sess)

        return jsonify({
            "success":    True,
            "report":     report,
            "result_url": f"/ai-recruiter/result/{session_id}",
        })
    except Exception as e:
        logger.error(f"evaluate_session error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_recruiter_routes.route("/api/ai-recruiter/history")
@login_required
def get_history():
    """Past interview sessions for this user."""
    try:
        user_id = session.get("user_id")
        history = recruiter_service.get_session_history(user_id, limit=10)
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_recruiter_routes.route("/api/ai-recruiter/tts", methods=["POST"])
@login_required
def text_to_speech():
    """
    Convert AI message to speech using browser TTS (no external API needed).
    Returns the text back — frontend uses Web Speech API.
    """
    data = request.get_json(force=True) or {}
    return jsonify({"success": True, "text": data.get("text", "")})