from flask import Blueprint, jsonify, render_template, session, request, Response
from backend.utils.auth_decorator import login_required
from backend.services.interview_service import InterviewService, INTERVIEW_CONFIGS, TOTAL_QUESTIONS
from backend.models import User, db
import io
from backend.services._openai_client import get_client, MODEL_CHEAP, MODEL_SMART

interview_routes = Blueprint("interview_routes", __name__)
service          = InterviewService()

# ── In-memory session store (use Redis in production) ──────────
_sessions = {}   # { user_id: { system_prompt, history, qa_history, ... } }


def _get_sess(user_id):
    return _sessions.get(user_id, {})

def _set_sess(user_id, data):
    _sessions[user_id] = data


# ══════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════

@interview_routes.route("/interview")
@login_required
def interview_home():
    """Landing page — pick type and level."""
    return render_template("interview.html", configs=INTERVIEW_CONFIGS)


@interview_routes.route("/interview/session")
@login_required
def interview_session():
    """Live interview page."""
    user_id = session["user_id"]
    sess    = _get_sess(user_id)
    if not sess:
        return render_template("interview.html", configs=INTERVIEW_CONFIGS,
                               error="No active session. Please start a new interview.")
    return render_template("interview_session.html",
        interview_type = sess.get("interview_type","hr"),
        level          = sess.get("level","fresher"),
        config         = sess.get("config", {}),
        total_questions= TOTAL_QUESTIONS)


@interview_routes.route("/interview/result")
@login_required
def interview_result():
    """Results page after interview."""
    user_id = session["user_id"]
    sess    = _get_sess(user_id)
    report  = sess.get("report")
    if not report:
        return render_template("interview.html", configs=INTERVIEW_CONFIGS,
                               error="No results found. Please complete an interview first.")
    interview_type = sess.get("interview_type","hr")
    config = INTERVIEW_CONFIGS.get(interview_type, {})
    return render_template("interview_result.html", report=report, config=config,
                           interview_type=interview_type, level=sess.get("level","fresher"))


# ══════════════════════════════════════════════════════════════
#  API — SESSION MANAGEMENT
# ══════════════════════════════════════════════════════════════

@interview_routes.route("/api/interview/start", methods=["POST"])
@login_required
def start_interview():
    """Initialize a new interview session."""
    data   = request.get_json() or {}
    itype  = data.get("interview_type", "hr")
    level  = data.get("level", "fresher")
    uid    = session["user_id"]

    if itype not in INTERVIEW_CONFIGS:
        return jsonify({"error": "Invalid interview type"}), 400

    sess_data = service.start_session(uid, itype, level)
    sess_data.update({
        "interview_type": itype,
        "level":          level,
        "history":        [],       # OpenAI message history
        "qa_history":     [],       # Q&A with scores
        "question_num":   0,
        "current_question": "",
        "started_at":     __import__("time").time(),
    })
    _set_sess(uid, sess_data)
    return jsonify({"success": True, "redirect": "/interview/session"})


@interview_routes.route("/api/interview/question", methods=["POST"])
@login_required
def get_question():
    """Get next interview question."""
    uid  = session["user_id"]
    sess = _get_sess(uid)
    if not sess:
        return jsonify({"error": "No active session"}), 400

    sess["question_num"] += 1
    qnum = sess["question_num"]

    if qnum > TOTAL_QUESTIONS:
        return jsonify({"done": True, "message": "Interview complete!"})

    result = service.generate_question(
        system_prompt  = sess["system_prompt"],
        history        = sess["history"],
        question_num   = qnum,
        interview_type = sess["interview_type"],
    )
    question = result["question"]
    hint     = result.get("hint", "")

    sess["current_question"] = question
    sess["current_hint"]     = hint
    sess["question_start_time"] = __import__("time").time()
    sess["history"].append({"role": "assistant", "content": question})
    _set_sess(uid, sess)

    return jsonify({
        "question":      question,
        "hint":          hint,
        "question_num":  qnum,
        "total":         TOTAL_QUESTIONS,
        "done":          False,
    })


@interview_routes.route("/api/interview/answer", methods=["POST"])
@login_required
def submit_answer():
    """Submit answer and get AI evaluation."""
    uid    = session["user_id"]
    sess   = _get_sess(uid)
    if not sess:
        return jsonify({"error": "No active session"}), 400

    data       = request.get_json() or {}
    answer     = (data.get("answer") or "").strip()
    time_taken = int(data.get("time_taken", 60))
    question   = sess.get("current_question", "")

    # Add to OpenAI history
    sess["history"].append({"role": "user", "content": answer or "[No answer — skipped]"})

    # Evaluate
    evaluation = service.evaluate_answer(
        question       = question,
        answer         = answer,
        interview_type = sess["interview_type"],
        level          = sess["level"],
        time_taken     = time_taken,
    )

    # Store Q&A record
    qa_record = {
        "question":    question,
        "answer":      answer,
        "time_taken":  time_taken,
        "question_num": sess["question_num"],
        **evaluation,
    }
    sess["qa_history"].append(qa_record)
    _set_sess(uid, sess)

    return jsonify({
        "evaluation":    evaluation,
        "question_num":  sess["question_num"],
        "total":         TOTAL_QUESTIONS,
        "questions_left": TOTAL_QUESTIONS - sess["question_num"],
    })


@interview_routes.route("/api/interview/finish", methods=["POST"])
@login_required
def finish_interview():
    """Generate final report."""
    uid    = session["user_id"]
    sess   = _get_sess(uid)
    if not sess:
        return jsonify({"error": "No session"}), 400

    import time
    total_time = int(time.time() - sess.get("started_at", time.time()))

    report = service.generate_final_report(
        interview_type = sess["interview_type"],
        level          = sess["level"],
        qa_history     = sess["qa_history"],
        total_time     = total_time,
    )
    sess["report"] = report
    _set_sess(uid, sess)

    return jsonify({"success": True, "redirect": "/interview/result"})


# ══════════════════════════════════════════════════════════════
#  API — VOICE
# ══════════════════════════════════════════════════════════════

@interview_routes.route("/api/interview/tts", methods=["POST"])
@login_required
def text_to_speech():
    """Convert question text to speech audio."""
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400
    try:
        audio_bytes = service.text_to_speech(text)
        return Response(audio_bytes, mimetype="audio/mpeg",
                        headers={"Content-Disposition": "inline; filename=question.mp3"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@interview_routes.route("/api/interview/stt", methods=["POST"])
@login_required
def speech_to_text():
    """Convert recorded audio to text via Whisper."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files["audio"]

    try:
        import io, os, tempfile
        from openai import OpenAI
        client = get_client()

        # Read raw bytes from the uploaded file
        audio_bytes = audio_file.read()
        if not audio_bytes:
            return jsonify({"error": "Empty audio file"}), 400

        # Write to a temp file with .wav extension — Whisper accepts wav/mp3/webm/mp4/m4a
        # We try webm first, fallback naming ensures Whisper can detect format
        suffix = ".webm"
        original_name = audio_file.filename or "audio.webm"
        if "mp4" in original_name or "mp4" in (audio_file.content_type or ""):
            suffix = ".mp4"
        elif "ogg" in original_name or "ogg" in (audio_file.content_type or ""):
            suffix = ".ogg"
        elif "wav" in original_name:
            suffix = ".wav"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="en",   # force English for speed + accuracy
                )
            text = transcript.text.strip()
            if not text:
                return jsonify({"error": "No speech detected. Please speak clearly."}), 400
            return jsonify({"success": True, "text": text})
        finally:
            os.unlink(tmp_path)   # always clean up temp file

    except Exception as e:
        print(f"[STT Error] {e}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


# ══════════════════════════════════════════════════════════════
#  API — UTILITIES
# ══════════════════════════════════════════════════════════════

@interview_routes.route("/api/interview/status")
@login_required
def interview_status():
    """Check if active session exists."""
    sess = _get_sess(session["user_id"])
    return jsonify({
        "active":   bool(sess),
        "question": sess.get("question_num", 0),
        "total":    TOTAL_QUESTIONS,
        "type":     sess.get("interview_type"),
        "level":    sess.get("level"),
    })


@interview_routes.route("/api/interview/abandon", methods=["POST"])
@login_required
def abandon_interview():
    """Clear active session."""
    uid = session["user_id"]
    if uid in _sessions:
        del _sessions[uid]
    return jsonify({"success": True})