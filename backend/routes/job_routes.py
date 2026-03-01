from flask import Blueprint, request, jsonify, render_template
from backend.services.job_match_engine import JobMatchEngine
from backend.services.job_ingest_service import JobIngestService
from backend.models import JobPosting, User
from backend.extensions import db
from backend.utils.auth_decorator import login_required
job_routes = Blueprint("job_routes", __name__)

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