from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from backend.models import Application, JobPosting, User
from backend.extensions import db
from backend.utils.auth_decorator import login_required
from datetime import datetime


# ==============================
# Blueprint Definition
# ==============================
application_routes = Blueprint("application_routes", __name__)


# ==============================
# Applications Page
# ==============================
@application_routes.route("/applications")
@login_required
def applications_page():
    return render_template("applications.html")


# ==============================
# Get All Applications (API)
# ==============================
@application_routes.route("/api/applications")
@login_required
def get_applications():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify([])

    applications = Application.query.filter_by(user_id=user_id).all()

    results = []

    for app in applications:

        job = JobPosting.query.get(app.job_id)

        results.append({
            "id": app.id,
            "title": job.title if job else "Unknown",
            "company": job.company if job else "",
            "status": app.status,
            "date": app.applied_at.strftime("%d %b %Y") if app.applied_at else ""
        })

    return jsonify(results)


# ==============================
# Save Job (Create Application)
# ==============================
@application_routes.route("/api/save-job", methods=["POST"])
@login_required
def save_job():

    user_id = session.get("user_id")
    job_id = request.json.get("job_id")

    if not user_id or not job_id:
        return jsonify({"error": "Invalid request"}), 400

    existing = Application.query.filter_by(
        user_id=user_id,
        job_id=job_id
    ).first()

    if existing:
        return jsonify({"message": "Already saved"})

    new_application = Application(
        user_id=user_id,
        job_id=job_id,
        status="Saved",
        applied_at=datetime.utcnow()
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify({"message": "Job saved successfully"})


# ==============================
# Update Application Status
# ==============================
@application_routes.route("/api/update-application", methods=["POST"])
@login_required
def update_application():

    user_id = session.get("user_id")
    app_id = request.json.get("id")
    new_status = request.json.get("status")

    application = Application.query.filter_by(
        id=app_id,
        user_id=user_id
    ).first()

    if not application:
        return jsonify({"error": "Application not found"}), 404

    application.status = new_status
    db.session.commit()

    return jsonify({"message": "Status updated"})


# ==============================
# Delete Application
# ==============================
@application_routes.route("/api/delete-application", methods=["POST"])
@login_required
def delete_application():

    user_id = session.get("user_id")
    app_id = request.json.get("id")

    application = Application.query.filter_by(
        id=app_id,
        user_id=user_id
    ).first()

    if not application:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(application)
    db.session.commit()

    return jsonify({"message": "Application removed"})