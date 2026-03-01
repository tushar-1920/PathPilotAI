from flask import Blueprint, render_template
from backend.models import User, JobPosting, Application
from backend.utils.auth_decorator import login_required
from flask import session

admin_routes = Blueprint("admin_routes", __name__)


@admin_routes.route("/admin")
@login_required
def admin_dashboard():

    user = User.query.get(session["user_id"])

    if user.role != "admin":
        return "Unauthorized", 403

    return render_template(
        "admin_dashboard.html",
        total_users=User.query.count(),
        total_jobs=JobPosting.query.count(),
        total_apps=Application.query.count()
    )