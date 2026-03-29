"""
backend/routes/recruiter_routes.py

Register in app.py:
    from backend.routes.recruiter_routes import recruiter_routes
    app.register_blueprint(recruiter_routes)
"""
import os
from functools import wraps
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from werkzeug.utils import secure_filename

from backend.extensions import db
from backend.models import (
    User, Profile, Certificate,
    RecruiterJob, JobApplication, RecruiterMessage,
    Post, PostComment, Follow
)
from backend.services.recruiter_service import RecruiterService

recruiter_routes = Blueprint("recruiter_routes", __name__)
svc = RecruiterService()

UPLOAD_FOLDER = os.path.join("frontend", "static", "uploads", "application_resumes")
ALLOWED_EXT   = {"pdf", "doc", "docx"}


# ── Auth decorators ────────────────────────────────────────────
def recruiter_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "recruiter":
            flash("Recruiter access required.")
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def _recruiter_ctx():
    return {
        "recruiter_email":   session.get("recruiter_email", ""),
        "recruiter_company": session.get("recruiter_company", ""),
    }


# ── Score & profile helpers (same formula as profile_routes) ───
def _profile_image_url(p):
    return f"/static/{p.profile_image}" if p and p.profile_image else None


def _safe_skills(user):
    try:
        raw = getattr(user, "normalized_skills", None) or getattr(user, "skills", None) or ""
        return [s.strip() for s in raw.split(",") if s.strip()]
    except Exception:
        return []


def _get_all_scores(user_id):
    """
    Compute live scores via EliteScoringEngine —
    identical to profile_routes._get_all_scores.
    Returns: (ats_score, competitive_score, readiness_score,
              percentile, role_fit_pct, dominant_role)
    """
    try:
        from backend.services.elite_scoring_engine import EliteScoringEngine
        user = User.query.get(user_id)
        if not user or not user.normalized_skills:
            return 0, 0, 0, 0, 0, ""

        skills   = [s.strip() for s in user.normalized_skills.split(",") if s.strip()]
        n_skills = len(skills)
        if n_skills == 0:
            return 0, 0, 0, 0, 0, ""

        engine     = EliteScoringEngine()
        elite      = engine.compute_score(skills)
        comp_score = elite["competitive_score"]

        if   n_skills <= 5:  kw = n_skills * 3.5
        elif n_skills <= 12: kw = 17.5 + (n_skills - 5) * 2.2
        elif n_skills <= 22: kw = 33.0 + (n_skills - 12) * 0.7
        elif n_skills <= 35: kw = 40.0
        else:                kw = max(34.0, 40.0 - (n_skills - 35) * 0.3)
        kw  = min(40.0, round(kw, 1))
        mkt = min(30.0, round((elite["market_score"] / 25.0) * min(1.0, n_skills / 15.0) * 30.0, 1))
        stk = min(20.0, round((elite["stack_completeness"] / 20.0) * 20.0, 1))
        div = min(10.0, round((elite["diversity_score"] / 15.0) * 10.0, 1))
        ats_score = min(100, int(kw + mkt + stk + div))

        role_fit_pct  = min(97, int(comp_score * 0.65 + min(n_skills * 2, 30) + 5))
        dominant_role = elite.get("dominant_role", "")
        readiness     = min(100, int(comp_score * 0.5 + ats_score * 0.3 + role_fit_pct * 0.2))

        if   comp_score >= 90: percentile = 95
        elif comp_score >= 80: percentile = 85
        elif comp_score >= 70: percentile = 72
        elif comp_score >= 60: percentile = 58
        elif comp_score >= 50: percentile = 44
        elif comp_score >= 35: percentile = 28
        else:                  percentile = max(5, int(comp_score * 0.4))

        return ats_score, int(comp_score), readiness, percentile, role_fit_pct, dominant_role

    except Exception as e:
        print(f"[RecruiterScores] {e}")
        return 0, 0, 0, 0, 0, ""


def _get_coding_stats(user_id):
    try:
        from backend.models import SolvedProblem
        return SolvedProblem.query.filter_by(user_id=user_id).count()
    except Exception:
        pass
    try:
        from backend.models import CodingSubmission
        return CodingSubmission.query.filter_by(
            user_id=user_id, status="accepted"
        ).distinct(CodingSubmission.problem_id).count()
    except Exception:
        return 0


# ══════════════════════════════════════════════════════════════
#  RECRUITER PANEL ROUTES
# ══════════════════════════════════════════════════════════════

@recruiter_routes.route("/recruiter/dashboard")
@recruiter_required
def recruiter_dashboard():
    email = session["recruiter_email"]
    stats = svc.get_dashboard_stats(email)
    jobs  = svc.get_recruiter_jobs(email)
    return render_template("recruiter/dashboard.html",
        stats=stats, jobs=jobs, **_recruiter_ctx())


@recruiter_routes.route("/recruiter/post-job", methods=["GET", "POST"])
@recruiter_required
def post_job():
    if request.method == "POST":
        rounds_raw = request.form.getlist("rounds")
        data = {
            "title":           request.form.get("title", ""),
            "description":     request.form.get("description", ""),
            "location":        request.form.get("location", ""),
            "job_type":        request.form.get("job_type", "Full-Time"),
            "ctc":             request.form.get("ctc", ""),
            "deadline":        request.form.get("deadline", ""),
            "stream_required": request.form.get("stream_required", ""),
            "min_cgpa":        request.form.get("min_cgpa", 0),
            "batch":           request.form.get("batch", ""),
            "rounds":          [r.strip() for r in rounds_raw if r.strip()],
            "skills_required": request.form.get("skills_required", ""),
            "allow_messaging": bool(request.form.get("allow_messaging")),
        }
        svc.create_job(
            session["recruiter_email"],
            session["recruiter_company"],
            data
        )
        flash("✅ Job posted successfully!")
        return redirect("/recruiter/dashboard")
    return render_template("recruiter/post_job.html", **_recruiter_ctx())


@recruiter_routes.route("/recruiter/jobs/<int:job_id>/applications")
@recruiter_required
def view_applications(job_id):
    job = svc.get_job(job_id)
    if not job or job.recruiter_email != session["recruiter_email"]:
        flash("Job not found.")
        return redirect("/recruiter/dashboard")

    filters = {
        "min_cgpa": request.args.get("min_cgpa", ""),
        "college":  request.args.get("college", ""),
        "status":   request.args.get("status", ""),
        "timing":   request.args.get("timing", "all"),
    }
    apps = svc.get_applications(job_id, filters)
    return render_template("recruiter/applications.html",
        job=job, apps=apps, filters=filters, **_recruiter_ctx())


@recruiter_routes.route("/recruiter/applications/<int:app_id>/status", methods=["POST"])
@recruiter_required
def update_status(app_id):
    new_status = request.form.get("status", "applied")
    svc.update_application_status(app_id, new_status, session["recruiter_email"])
    return redirect(request.referrer or "/recruiter/dashboard")


# ── FULL STUDENT PROFILE VIEW FOR RECRUITER ─────────────────────
@recruiter_routes.route("/recruiter/student/<int:user_id>")
@recruiter_required
def view_student(user_id):
    """
    Renders the student's complete profile for the recruiter —
    pulls the same live data (scores, skills, posts, certs, social)
    as profile_routes.view_profile, but in a recruiter read-only view.
    """
    user    = User.query.get_or_404(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    certs   = Certificate.query.filter_by(user_id=user_id).order_by(Certificate.id.desc()).all()
    posts   = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).limit(10).all()

    followers_count = Follow.query.filter_by(following_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=user_id).count()

    skills_list   = _safe_skills(user)
    coding_solved = _get_coding_stats(user_id)
    (ats_score, competitive_score,
     readiness_score, percentile,
     role_fit_pct, dominant_role) = _get_all_scores(user_id)

    # Applications this student submitted to THIS recruiter's jobs
    recruiter_email   = session["recruiter_email"]
    recruiter_job_ids = [j.id for j in svc.get_recruiter_jobs(recruiter_email)]
    student_apps = JobApplication.query.filter(
        JobApplication.user_id == user_id,
        JobApplication.job_id.in_(recruiter_job_ids)
    ).all() if recruiter_job_ids else []

    # Comments (top 2 per post — read-only display)
    post_comments = {}
    for p in posts:
        cmts = PostComment.query.filter_by(post_id=p.id)\
                   .order_by(PostComment.created_at.asc()).limit(2).all()
        post_comments[p.id] = cmts

    return render_template("recruiter/view_student.html",
        student_user      = user,
        student_profile   = profile,
        certs             = certs or [],
        posts             = posts or [],
        post_comments     = post_comments,
        followers_count   = followers_count,
        following_count   = following_count,
        resume_skills     = skills_list,
        coding_solved     = coding_solved,
        ats_score         = ats_score,
        competitive_score = competitive_score,
        readiness_score   = readiness_score,
        percentile        = percentile,
        role_fit_pct      = role_fit_pct,
        dominant_role     = dominant_role,
        student_apps      = student_apps,
        profile_image_url = _profile_image_url(profile),
        **_recruiter_ctx()
    )


@recruiter_routes.route("/recruiter/search-students")
@recruiter_required
def search_students():
    q       = request.args.get("q", "").strip()
    results = svc.search_students(q) if q else []
    return render_template("recruiter/search_students.html",
        results=results, query=q, **_recruiter_ctx())


@recruiter_routes.route("/recruiter/send-message", methods=["GET", "POST"])
@recruiter_required
def send_message():
    if request.method == "POST":
        receiver_id = int(request.form.get("receiver_id", 0))
        subject     = request.form.get("subject", "").strip()
        content     = request.form.get("content", "").strip()
        msg_type    = request.form.get("msg_type", "general")
        allow_reply = bool(request.form.get("allow_reply"))
        job_id_raw  = request.form.get("job_id")
        job_id      = int(job_id_raw) if job_id_raw else None

        svc.send_message(
            recruiter_email = session["recruiter_email"],
            company_name    = session["recruiter_company"],
            receiver_id     = receiver_id,
            subject         = subject,
            content         = content,
            job_id          = job_id,
            msg_type        = msg_type,
            allow_reply     = allow_reply,
        )

        if request.form.get("send_email") and receiver_id:
            u = User.query.get(receiver_id)
            if u:
                job_title = ""
                if job_id:
                    j = svc.get_job(job_id)
                    job_title = j.title if j else ""
                svc.send_email(
                    to_email=u.email, student_name=u.name,
                    company_name=session["recruiter_company"],
                    template=msg_type, job_title=job_title, extra=content,
                )

        flash("✅ Message sent!")
        return redirect("/recruiter/messages")

    receiver_id = request.args.get("receiver_id", "")
    job_id      = request.args.get("job_id", "")
    jobs        = svc.get_recruiter_jobs(session["recruiter_email"])
    students    = []
    if receiver_id:
        s = User.query.get(int(receiver_id))
        if s:
            students = [s]
    return render_template("recruiter/send_message.html",
        jobs=jobs, students=students,
        pre_receiver=receiver_id, pre_job=job_id,
        **_recruiter_ctx())


@recruiter_routes.route("/recruiter/messages")
@recruiter_required
def recruiter_messages():
    msgs = svc.get_recruiter_sent_messages(session["recruiter_email"])
    return render_template("recruiter/messages.html",
        msgs=msgs, **_recruiter_ctx())


@recruiter_routes.route("/recruiter/jobs/<int:job_id>/toggle", methods=["POST"])
@recruiter_required
def toggle_job(job_id):
    svc.toggle_job_status(job_id, session["recruiter_email"])
    return redirect("/recruiter/dashboard")


@recruiter_routes.route("/recruiter/jobs/<int:job_id>/delete", methods=["POST"])
@recruiter_required
def delete_job(job_id):
    svc.delete_job(job_id, session["recruiter_email"])
    flash("Job deleted.")
    return redirect("/recruiter/dashboard")


@recruiter_routes.route("/api/recruiter/search-students")
@recruiter_required
def api_search_students():
    q = request.args.get("q", "").strip()
    return jsonify(svc.search_students(q))


# ══════════════════════════════════════════════════════════════
#  USER-FACING JOB ROUTES
# ══════════════════════════════════════════════════════════════

@recruiter_routes.route("/live-jobs")
@login_required
def live_jobs():
    jobs        = svc.get_all_active_jobs()
    user_id     = session["user_id"]
    applied_ids = {a.job_id for a in JobApplication.query.filter_by(user_id=user_id).all()}
    return render_template("jobs/live_jobs.html",
        jobs=jobs, applied_ids=applied_ids)


@recruiter_routes.route("/live-jobs/<int:job_id>/apply", methods=["GET", "POST"])
@login_required
def apply_job(job_id):
    job = svc.get_job(job_id)
    if not job or not job.is_active:
        flash("Job not found.")
        return redirect("/live-jobs")

    if request.method == "POST":
        resume_filename = None
        resume_file = request.files.get("resume_file")
        if resume_file and resume_file.filename:
            ext = resume_file.filename.rsplit(".", 1)[-1].lower()
            if ext in ALLOWED_EXT:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                safe_name = secure_filename(
                    f"{session['user_id']}_{job_id}_{resume_file.filename}"
                )
                resume_file.save(os.path.join(UPLOAD_FOLDER, safe_name))
                resume_filename = safe_name

        result = svc.apply_for_job(
            user_id         = session["user_id"],
            job_id          = job_id,
            form_data       = request.form,
            resume_filename = resume_filename,
        )
        if result["success"]:
            flash("✅ Application submitted successfully!")
            return redirect("/my-applications")
        else:
            flash(result["error"])
            return redirect(f"/live-jobs/{job_id}/apply")

    user = User.query.get(session["user_id"])
    return render_template("jobs/apply_job.html", job=job, user=user)


@recruiter_routes.route("/my-applications")
@login_required
def my_applications():
    apps = svc.get_user_applications(session["user_id"])
    return render_template("jobs/my_applications.html", apps=apps)


@recruiter_routes.route("/my-messages")
@login_required
def my_messages():
    user_id = session["user_id"]
    msgs    = svc.get_user_messages(user_id)
    unread  = svc.get_unread_count(user_id)
    for m in msgs:
        if not m.is_read:
            svc.mark_message_read(m.id, user_id)
    # ← renamed template to job_messages.html to avoid clash with existing messages.html
    return render_template("jobs/job_messages.html", msgs=msgs, unread=unread)


# ── Optional API: unread recruiter message count (used by profile.html badge) ──
@recruiter_routes.route("/api/recruiter-messages/unread-count")
@login_required
def recruiter_msg_unread_count():
    user_id = session["user_id"]
    count   = RecruiterMessage.query.filter_by(receiver_id=user_id, is_read=False).count()
    return jsonify({"count": count})


# ── Serve application resumes ──────────────────────────────────────────────
@recruiter_routes.route("/uploads/application_resumes/<path:filename>")
@recruiter_required
def serve_resume(filename):
    """Serve uploaded resume files for recruiter viewing."""
    from flask import send_from_directory
    folder = os.path.join("frontend", "static", "uploads", "application_resumes")
    abs_folder = os.path.abspath(folder)
    return send_from_directory(abs_folder, filename)


# ── Student reply to recruiter message ────────────────────────────────────
@recruiter_routes.route("/my-messages/<int:msg_id>/reply", methods=["POST"])
@login_required
def reply_to_recruiter(msg_id):
    """Allow student to reply if recruiter enabled allow_reply."""
    user_id = session["user_id"]
    msg     = RecruiterMessage.query.filter_by(id=msg_id, receiver_id=user_id).first()

    if not msg:
        flash("Message not found.")
        return redirect("/my-messages")

    if not msg.allow_reply:
        flash("The recruiter has not enabled replies for this message.")
        return redirect("/my-messages")

    reply_text = request.form.get("reply_content", "").strip()
    if not reply_text:
        flash("Reply cannot be empty.")
        return redirect("/my-messages")

    # Store the reply as a new RecruiterMessage going the other way
    # We repurpose the model: sender is identified by storing user info in subject
    user = User.query.get(user_id)
    reply_msg = RecruiterMessage(
        recruiter_email = msg.recruiter_email,   # still scoped to this recruiter
        company_name    = f"STUDENT_REPLY::{user.name if user else 'Student'}::{user.email if user else ''}",
        receiver_id     = user_id,               # receiver = self (marker for recruiter inbox)
        job_id          = msg.job_id,
        subject         = f"Re: {msg.subject or ''}",
        content         = reply_text,
        message_type    = "reply",
        allow_reply     = False,
        is_read         = False,
    )
    db.session.add(reply_msg)
    db.session.commit()

    flash("✅ Reply sent to recruiter!")
    return redirect("/my-messages")