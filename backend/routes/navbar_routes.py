"""
backend/routes/navbar_routes.py

Handles:
  - Notification bell  (GET /api/notifications, POST /api/notifications/mark-read)
  - Hiring alerts      (GET /hiring-alerts, POST /api/company-follow, DELETE /api/company-unfollow)
  - Global search      (GET /api/search?q=...)

Register in app.py:
    from backend.routes.navbar_routes import navbar_routes
    app.register_blueprint(navbar_routes)
"""

from flask import Blueprint, jsonify, request, render_template, session
from backend.extensions import db
from backend.models import (
    Notification, CompanyFollow,
    RecruiterJob, JobPosting, User, Profile,
)
from functools import wraps
from datetime import datetime

navbar_routes = Blueprint("navbar_routes", __name__)


# ── auth decorator ────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return wrapper


# ══════════════════════════════════════════════════════════════
#  NOTIFICATION BELL
# ══════════════════════════════════════════════════════════════

@navbar_routes.route("/api/notifications")
@login_required
def get_notifications():
    """Return last 20 notifications + unread count for the bell badge."""
    uid = session["user_id"]
    notifs = (
        Notification.query
        .filter_by(user_id=uid)
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )
    unread = Notification.query.filter_by(user_id=uid, is_read=False).count()
    return jsonify({
        "unread": unread,
        "notifications": [n.to_dict() for n in notifs],
    })


@navbar_routes.route("/api/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications_read():
    """Mark all (or a specific) notification as read."""
    uid  = session["user_id"]
    data = request.get_json(silent=True) or {}
    nid  = data.get("id")          # pass id to mark single; omit to mark all

    if nid:
        n = Notification.query.filter_by(id=nid, user_id=uid).first()
        if n:
            n.is_read = True
    else:
        Notification.query.filter_by(user_id=uid, is_read=False).update({"is_read": True})

    db.session.commit()
    return jsonify({"ok": True})


# ══════════════════════════════════════════════════════════════
#  HIRING ALERTS PAGE  +  COMPANY FOLLOW / UNFOLLOW
# ══════════════════════════════════════════════════════════════

@navbar_routes.route("/hiring-alerts")
@login_required
def hiring_alerts_page():
    uid = session["user_id"]

    # Companies the user is already following
    follows = CompanyFollow.query.filter_by(user_id=uid).all()
    followed_names = {f.company_name for f in follows}

    # Latest jobs from followed companies (up to 50)
    hiring_jobs = []
    if followed_names:
        hiring_jobs = (
            RecruiterJob.query
            .filter(
                RecruiterJob.company_name.in_(followed_names),
                RecruiterJob.is_active == True,
            )
            .order_by(RecruiterJob.created_at.desc())
            .limit(50)
            .all()
        )

    # All companies available to follow (distinct from recruiter_jobs)
    all_companies_q = (
        db.session.query(
            RecruiterJob.company_name,
            db.func.count(RecruiterJob.id).label("job_count"),
            db.func.max(RecruiterJob.created_at).label("last_posted"),
        )
        .filter(RecruiterJob.is_active == True)
        .group_by(RecruiterJob.company_name)
        .order_by(db.func.max(RecruiterJob.created_at).desc())
        .limit(100)
        .all()
    )

    all_companies = [
        {
            "name":        row.company_name,
            "job_count":   row.job_count,
            "last_posted": row.last_posted.strftime("%b %d, %Y") if row.last_posted else "",
            "following":   row.company_name in followed_names,
        }
        for row in all_companies_q
    ]

    # Hiring alerts from notifications
    alerts = (
        Notification.query
        .filter_by(user_id=uid, notif_type="hiring_alert")
        .order_by(Notification.created_at.desc())
        .limit(30)
        .all()
    )

    return render_template(
        "hiring_alerts.html",
        follows=follows,
        followed_names=followed_names,
        hiring_jobs=hiring_jobs,
        all_companies=all_companies,
        alerts=alerts,
    )


@navbar_routes.route("/api/company-follow", methods=["POST"])
@login_required
def follow_company():
    uid  = session["user_id"]
    data = request.get_json(silent=True) or {}
    name = (data.get("company_name") or "").strip()

    if not name:
        return jsonify({"error": "company_name required"}), 400

    existing = CompanyFollow.query.filter_by(user_id=uid, company_name=name).first()
    if existing:
        return jsonify({"ok": True, "action": "already_following"})

    db.session.add(CompanyFollow(user_id=uid, company_name=name))
    db.session.commit()
    return jsonify({"ok": True, "action": "followed"})


@navbar_routes.route("/api/company-unfollow", methods=["POST"])
@login_required
def unfollow_company():
    uid  = session["user_id"]
    data = request.get_json(silent=True) or {}
    name = (data.get("company_name") or "").strip()

    CompanyFollow.query.filter_by(user_id=uid, company_name=name).delete()
    db.session.commit()
    return jsonify({"ok": True, "action": "unfollowed"})


# ══════════════════════════════════════════════════════════════
#  GLOBAL SEARCH  (⌘K)
# ══════════════════════════════════════════════════════════════

@navbar_routes.route("/api/search")
@login_required
def global_search():
    """
    Searches jobs, users, and problems.
    Returns JSON with sections: jobs, users, tools.
    """
    q = (request.args.get("q") or "").strip()
    if not q or len(q) < 2:
        return jsonify({"jobs": [], "users": [], "tools": []})

    like = f"%{q}%"

    # ── Jobs ──────────────────────────────────────────────────
    job_rows = (
        RecruiterJob.query
        .filter(
            RecruiterJob.is_active == True,
            db.or_(
                RecruiterJob.title.ilike(like),
                RecruiterJob.company_name.ilike(like),
                RecruiterJob.skills_required.ilike(like),
            )
        )
        .limit(5)
        .all()
    )
    jobs = [
        {
            "title":   j.title,
            "company": j.company_name,
            "type":    j.job_type or "Full-Time",
            "link":    "/live-jobs",
        }
        for j in job_rows
    ]

    # ── Users ─────────────────────────────────────────────────
    user_rows = (
        User.query
        .filter(User.name.ilike(like))
        .limit(5)
        .all()
    )
    users = []
    for u in user_rows:
        p = Profile.query.filter_by(user_id=u.id).first()
        users.append({
            "name":     u.name,
            "headline": p.headline if p else "PathPilot User",
            "link":     f"/profile/{u.id}",
        })

    # ── Built-in Tools (static list, filtered by query) ──────
    ALL_TOOLS = [
        {"name": "Career Roadmap",       "link": "/roadmap",              "icon": "🗺️"},
        {"name": "Salary Insights",      "link": "/salary",               "icon": "💰"},
        {"name": "Market Intelligence",  "link": "/market",               "icon": "📊"},
        {"name": "Resume Builder",       "link": "/resume-builder",       "icon": "📄"},
        {"name": "AI Resume Analyzer",   "link": "/resume-ai",            "icon": "🤖"},
        {"name": "Cover Letter",         "link": "/cover-letter",         "icon": "✉️"},
        {"name": "Interview Simulator",  "link": "/interview",            "icon": "🎯"},
        {"name": "AI Recruiter Room",    "link": "/ai-recruiter",         "icon": "🎙️"},
        {"name": "Code Practice",        "link": "/practice",             "icon": "⚡"},
        {"name": "Battle Mode",          "link": "/battle",               "icon": "⚔️"},
        {"name": "VidCode",              "link": "/vidcode",              "icon": "🎥"},
        {"name": "Career Time Machine",  "link": "/career-time-machine",  "icon": "⏳"},
        {"name": "Blind Spot Detector",  "link": "/blind-spot-detector",  "icon": "🔍"},
        {"name": "Job Analyzer",         "link": "/job-analyzer",         "icon": "🔬"},
        {"name": "Career Forecast",      "link": "/forecast",             "icon": "📈"},
        {"name": "Hiring Alerts",        "link": "/hiring-alerts",        "icon": "🔔"},
        {"name": "Live Jobs",            "link": "/live-jobs",            "icon": "🔴"},
        {"name": "Saved Jobs",           "link": "/saved-jobs",           "icon": "🔖"},
        {"name": "Dashboard",            "link": "/dashboard",            "icon": "🏠"},
        {"name": "My Profile",           "link": "/profile",              "icon": "👤"},
    ]
    ql = q.lower()
    tools = [t for t in ALL_TOOLS if ql in t["name"].lower()][:5]

    return jsonify({"jobs": jobs, "users": users, "tools": tools})


# ══════════════════════════════════════════════════════════════
#  HELPER  — call this from recruiter_routes when a job is posted
#  so all followers get a hiring alert notification instantly.
# ══════════════════════════════════════════════════════════════

def fire_hiring_alerts(company_name: str, job_title: str, job_link: str = "/hiring-alerts"):
    """
    Create Notification rows for every user who follows `company_name`.
    Call this after saving a new RecruiterJob.
    Usage:
        from backend.routes.navbar_routes import fire_hiring_alerts
        fire_hiring_alerts(job.company_name, job.title)
    """
    followers = CompanyFollow.query.filter_by(company_name=company_name).all()
    for f in followers:
        notif = Notification(
            user_id    = f.user_id,
            notif_type = "hiring_alert",
            title      = f"{company_name} is hiring!",
            body       = f"New role: {job_title}",
            link       = job_link,
        )
        db.session.add(notif)
    if followers:
        db.session.commit()