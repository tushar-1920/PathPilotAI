from flask import Blueprint, request, jsonify, render_template, session
from backend.services.job_match_engine import JobMatchEngine
from backend.services.job_ingest_service import JobIngestService
from backend.models import JobPosting, User
from backend.extensions import db
from backend.utils.auth_decorator import login_required
job_routes = Blueprint("job_routes", __name__)
from backend.models import SavedJob, Resume
from datetime import datetime
engine = JobMatchEngine()


# ===============================
# JOBS PAGE
# ===============================
@job_routes.route("/jobs")
def jobs_page():
    return render_template("jobs.html")


# ===============================
# GET JOB MATCHES
# ===============================
@job_routes.route("/api/job-matches")
@login_required
def get_job_matches():

    from flask import request, session

    role = request.args.get("role", "").strip()
    fit = request.args.get("fit", "").strip()
    sort = request.args.get("sort", "desc")

    results = engine.get_job_matches(
        user_id=session["user_id"],
        role_filter=role if role else None,
        fit_filter=fit if fit else None,
        sort=sort
    )

    return jsonify(results)


# ===============================
# GET DISTINCT ROLES
# ===============================
@job_routes.route("/api/job-roles")
def get_roles():

    roles = db.session.query(JobPosting.role).distinct().all()

    role_list = [r[0] for r in roles if r[0]]

    return jsonify(role_list)


# ===============================
# REFRESH LIVE JOBS
# ===============================
@job_routes.route("/api/refresh-jobs")
def refresh_jobs():

    result = JobIngestService().fetch_remoteok_jobs()

    return jsonify(result)

@job_routes.route("/api/save-job", methods=["POST"])
@login_required
def save_job():

    from flask import request, session
    from backend.models import Application

    job_id = request.json.get("job_id")

    existing = Application.query.filter_by(
        user_id=session["user_id"],
        job_id=job_id
    ).first()

    if existing:
        return jsonify({"message": "Already saved"})

    new = Application(
        user_id=session["user_id"],
        job_id=job_id,
        status="saved"
    )

    db.session.add(new)
    db.session.commit()

    return jsonify({"message": "Job saved"})

@job_routes.route("/applications")
@login_required
def applications_page():
    return render_template("applications.html")

@job_routes.route("/api/analyze-job", methods=["POST"])
@login_required
def analyze_job():

    data = request.json

    description = data.get("description")
    job_title = data.get("title")
    job_level = data.get("job_level")   # NEW FIELD

    if not description:
        return jsonify({"error": "No job description provided"}), 400

    user = User.query.get(session.get("user_id"))

    resume_skills = []

    if user and user.normalized_skills:
        resume_skills = [
            s.strip().lower()
            for s in user.normalized_skills.split(",")
            if s.strip()
        ]

    engine = JobMatchEngine()

    result = engine.deep_job_match(resume_skills, description)

    saved_job = SavedJob(
        user_id=user.id,
        title=job_title,
        job_level=job_level,   # SAVE JOB LEVEL
        description=description,
        job_skills=",".join(result["job_skills"]),
        score=result["score"],
        eligibility=result["eligibility"],
        created_at=datetime.utcnow()
    )

    db.session.add(saved_job)
    db.session.commit()

    return jsonify({
        "score": result["score"],
        "matched": result["matched_skills"],
        "missing": result["missing_skills"],
        "eligibility": result["eligibility"]
    })

@job_routes.route("/job-analyzer")
@login_required
def job_analyzer_page():
    return render_template("job_analyzer.html")

@job_routes.route("/api/saved-jobs")
@login_required
def get_saved_jobs():

    jobs = SavedJob.query.filter_by(
        user_id=session.get("user_id")
    ).all()

    data = []

    for job in jobs:

        data.append({

            "id": job.id,

            "title": job.title,

            "job_level": job.job_level,   # NEW FIELD

            "score": job.score,

            "eligibility": job.eligibility,

            "date": job.created_at.strftime("%Y-%m-%d")

        })

    return jsonify(data)

@job_routes.route("/saved-jobs")
@login_required
def saved_jobs_page():
    return render_template("saved_jobs.html")

@job_routes.route("/api/compare-resume-job", methods=["POST"])
@login_required
def compare_resume_job():

    data = request.json

    resume_id = data.get("resume_id")
    job_id = data.get("job_id")

    resume = Resume.query.get(resume_id)
    job = SavedJob.query.get(job_id)

    if not resume or not job:
        return jsonify({"error": "Invalid resume or job"}), 400

    # --------------------------
    # Resume Skills
    # --------------------------

    resume_skills = []

    if resume.normalized_skills:
        resume_skills = [
            s.strip().lower()
            for s in resume.normalized_skills.split(",")
            if s.strip()
        ]

    # --------------------------
    # Job Skills
    # --------------------------

    job_skills = []

    if job.job_skills:
        job_skills = [
            s.strip().lower()
            for s in job.job_skills.split(",")
            if s.strip()
        ]

    engine = JobMatchEngine()

    score = engine.calculate_match_score(
        resume_skills,
        job_skills,
        False
    )

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    return jsonify({

        "score": score,

        "resume_name": resume.filename,

        "job_title": job.title,

        "matched_skills": matched,

        "missing_skills": missing,

        "total_job_skills": len(job_skills),

        "matched_count": len(matched)

    })


@job_routes.route("/api/delete-saved-job/<int:job_id>", methods=["DELETE"])
@login_required
def delete_saved_job(job_id):

    job = SavedJob.query.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job deleted"})