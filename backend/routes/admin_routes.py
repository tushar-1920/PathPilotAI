"""
PathPilot AI — Admin Routes
Complete admin control center with all platform analytics.
"""

from flask import Blueprint, render_template, session, jsonify
from backend.models import User, JobPosting, Application, Resume
from backend.utils.auth_decorator import login_required
from datetime import datetime, timedelta
from collections import Counter
import json

admin_routes = Blueprint("admin_routes", __name__)


def _is_admin():
    user = User.query.get(session.get("user_id"))
    return user and user.role == "admin"


# ─────────────────────────────────────────────
#  MAIN ADMIN PAGE
# ─────────────────────────────────────────────
@admin_routes.route("/admin")
@login_required
def admin_dashboard():
    if not _is_admin():
        return "Unauthorized", 403
    return render_template("admin_dashboard.html")


# ─────────────────────────────────────────────
#  API: CORE STATS
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/stats")
@login_required
def admin_stats():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    # User counts
    total_users  = User.query.count()
    pro_users    = User.query.filter_by(subscription_plan="pro").count()
    free_users   = total_users - pro_users
    monthly_subs = User.query.filter_by(subscription_plan="pro", billing_cycle="monthly").count()
    annual_subs  = User.query.filter_by(subscription_plan="pro", billing_cycle="annual").count()
    verified     = User.query.filter_by(is_verified=True).count()

    # Revenue
    mrr = monthly_subs * 19
    arr = annual_subs * 190

    # Platform data
    total_jobs    = JobPosting.query.count()
    total_apps    = Application.query.count()
    total_resumes = Resume.query.count()

    # Coding practice stats (safe import)
    total_submissions = 0
    total_solved      = 0
    try:
        from backend.models import Submission, SolvedProblem
        total_submissions = Submission.query.count()
        total_solved      = SolvedProblem.query.count()
    except Exception:
        pass

    # New users last 7 days
    week_ago     = datetime.utcnow() - timedelta(days=7)
    new_users_7d = User.query.filter(User.created_at >= week_ago).count()

    # New users last 30 days
    month_ago     = datetime.utcnow() - timedelta(days=30)
    new_users_30d = User.query.filter(User.created_at >= month_ago).count()

    # Growth rate (week over week)
    prev_week_start = datetime.utcnow() - timedelta(days=14)
    prev_week_end   = datetime.utcnow() - timedelta(days=7)
    prev_week_users = User.query.filter(
        User.created_at >= prev_week_start,
        User.created_at < prev_week_end
    ).count()
    growth_rate = 0
    if prev_week_users > 0:
        growth_rate = round(((new_users_7d - prev_week_users) / prev_week_users) * 100, 1)

    return jsonify({
        "users": {
            "total":       total_users,
            "pro":         pro_users,
            "free":        free_users,
            "verified":    verified,
            "monthly_subs":monthly_subs,
            "annual_subs": annual_subs,
            "new_7d":      new_users_7d,
            "new_30d":     new_users_30d,
            "growth_rate": growth_rate,
        },
        "revenue": {
            "mrr":   mrr,
            "arr":   arr,
            "total": mrr + arr,
            "conversion_rate": round(pro_users / max(total_users, 1) * 100, 1),
        },
        "platform": {
            "jobs":        total_jobs,
            "applications":total_apps,
            "resumes":     total_resumes,
            "submissions": total_submissions,
            "solved":      total_solved,
        },
    })


# ─────────────────────────────────────────────
#  API: USER GROWTH CHART (last 30 days)
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/user-growth")
@login_required
def admin_user_growth():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    labels, counts, cumulative = [], [], []
    running = 0
    base    = User.query.filter(
        User.created_at < datetime.utcnow() - timedelta(days=30)
    ).count()
    running = base

    for i in range(29, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end   = day_start + timedelta(days=1)
        cnt = User.query.filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).count()
        labels.append(day_start.strftime("%d %b"))
        counts.append(cnt)
        running += cnt
        cumulative.append(running)

    return jsonify({"labels": labels, "daily": counts, "cumulative": cumulative})


# ─────────────────────────────────────────────
#  API: REVENUE CHART (last 12 months)
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/revenue-chart")
@login_required
def admin_revenue_chart():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    labels, revenue = [], []
    for i in range(11, -1, -1):
        month_start = (datetime.utcnow().replace(day=1, hour=0, minute=0, second=0) - timedelta(days=30*i))
        month_end   = month_start + timedelta(days=31)
        month_end   = month_end.replace(day=1)

        monthly = User.query.filter(
            User.subscription_plan == "pro",
            User.billing_cycle == "monthly",
            User.created_at < month_end
        ).count()
        annual = User.query.filter(
            User.subscription_plan == "pro",
            User.billing_cycle == "annual",
            User.created_at < month_end
        ).count()

        labels.append(month_start.strftime("%b %Y"))
        revenue.append(monthly * 19 + annual * 190)

    return jsonify({"labels": labels, "revenue": revenue})


# ─────────────────────────────────────────────
#  API: SUBSCRIPTION BREAKDOWN (pie)
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/subscription-breakdown")
@login_required
def admin_subscription_breakdown():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    free     = User.query.filter_by(subscription_plan="free").count()
    monthly  = User.query.filter_by(subscription_plan="pro", billing_cycle="monthly").count()
    annual   = User.query.filter_by(subscription_plan="pro", billing_cycle="annual").count()
    enterprise = User.query.filter_by(subscription_plan="enterprise").count()

    return jsonify({
        "labels": ["Free", "Pro Monthly", "Pro Annual", "Enterprise"],
        "values": [free, monthly, annual, enterprise],
        "colors": ["#64748b", "#5b6bff", "#00e5c8", "#a855f7"],
    })


# ─────────────────────────────────────────────
#  API: PLATFORM ACTIVITY (submissions, resumes, jobs per day)
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/platform-activity")
@login_required
def admin_platform_activity():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    labels, resumes_data, subs_data = [], [], []

    for i in range(13, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end   = day_start + timedelta(days=1)

        r = Resume.query.filter(
            Resume.uploaded_at >= day_start,
            Resume.uploaded_at < day_end
        ).count()

        s = 0
        try:
            from backend.models import Submission
            s = Submission.query.filter(
                Submission.created_at >= day_start,
                Submission.created_at < day_end
            ).count()
        except Exception:
            pass

        labels.append(day_start.strftime("%d %b"))
        resumes_data.append(r)
        subs_data.append(s)

    return jsonify({
        "labels":      labels,
        "resumes":     resumes_data,
        "submissions": subs_data,
    })


# ─────────────────────────────────────────────
#  API: TOP SKILLS across all users
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/top-skills")
@login_required
def admin_top_skills():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    all_skills = []
    users = User.query.filter(User.normalized_skills.isnot(None)).all()
    for user in users:
        if user.normalized_skills:
            skills = [s.strip() for s in user.normalized_skills.split(",") if s.strip()]
            all_skills.extend(skills)

    counter = Counter(all_skills)
    top20   = counter.most_common(20)

    return jsonify({
        "labels": [s[0] for s in top20],
        "counts": [s[1] for s in top20],
    })


# ─────────────────────────────────────────────
#  API: RECENT USERS
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/recent-users")
@login_required
def admin_recent_users():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.order_by(User.created_at.desc()).limit(10).all()
    return jsonify([{
        "id":       u.id,
        "name":     u.name,
        "email":    u.email,
        "plan":     u.subscription_plan or "free",
        "verified": u.is_verified,
        "joined":   u.created_at.strftime("%d %b %Y") if u.created_at else "—",
        "role":     u.role or "user",
    } for u in users])


# ─────────────────────────────────────────────
#  API: CODING PRACTICE STATS
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/coding-stats")
@login_required
def admin_coding_stats():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    try:
        from backend.models import Submission, SolvedProblem
        from backend.services.problem_service import get_difficulty_stats

        total_subs    = Submission.query.count()
        accepted_subs = Submission.query.filter_by(status="Accepted").count()
        wrong_subs    = Submission.query.filter_by(status="Wrong Answer").count()
        total_solved  = SolvedProblem.query.count()

        acceptance_rate = round(accepted_subs / max(total_subs, 1) * 100, 1)

        # Top submitters
        from sqlalchemy import func
        from backend.extensions import db
        top_users = db.session.query(
            Submission.user_id,
            func.count(Submission.id).label("cnt")
        ).group_by(Submission.user_id)\
         .order_by(func.count(Submission.id).desc())\
         .limit(5).all()

        top_user_data = []
        for uid, cnt in top_users:
            u = User.query.get(uid)
            if u:
                top_user_data.append({"name": u.name, "submissions": cnt})

        # Status distribution
        tle_subs   = Submission.query.filter_by(status="Time Limit Exceeded").count()
        error_subs = Submission.query.filter_by(status="Runtime Error").count()

        problem_stats = get_difficulty_stats()

        return jsonify({
            "total_submissions": total_subs,
            "accepted":          accepted_subs,
            "wrong_answer":      wrong_subs,
            "tle":               tle_subs,
            "runtime_error":     error_subs,
            "acceptance_rate":   acceptance_rate,
            "total_solved":      total_solved,
            "problem_counts":    problem_stats,
            "top_submitters":    top_user_data,
            "status_labels": ["Accepted", "Wrong Answer", "TLE", "Runtime Error"],
            "status_values": [accepted_subs, wrong_subs, tle_subs, error_subs],
            "status_colors": ["#22c55e", "#ff5757", "#ffb547", "#a855f7"],
        })
    except Exception as e:
        return jsonify({
            "total_submissions": 0, "accepted": 0, "wrong_answer": 0,
            "tle": 0, "runtime_error": 0, "acceptance_rate": 0,
            "total_solved": 0, "problem_counts": {}, "top_submitters": [],
            "status_labels": [], "status_values": [], "status_colors": [],
            "note": f"Coding module error: {str(e)}"
        })


# ─────────────────────────────────────────────
#  API: RESUME STATS
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/resume-stats")
@login_required
def admin_resume_stats():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    total    = Resume.query.count()
    avg_score = 0
    scores   = [r.skill_score for r in Resume.query.all() if r.skill_score]
    if scores:
        avg_score = round(sum(scores) / len(scores), 1)

    # Score distribution buckets
    buckets = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    for s in scores:
        if s <= 25:    buckets["0-25"] += 1
        elif s <= 50:  buckets["26-50"] += 1
        elif s <= 75:  buckets["51-75"] += 1
        else:          buckets["76-100"] += 1

    return jsonify({
        "total":      total,
        "avg_score":  avg_score,
        "buckets":    buckets,
        "high_score": max(scores) if scores else 0,
        "low_score":  min(scores) if scores else 0,
    })


# ─────────────────────────────────────────────
#  API: JOB STATS
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/job-stats")
@login_required
def admin_job_stats():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    total_jobs = JobPosting.query.count()
    total_apps = Application.query.count()

    # Applications by status
    status_counts = {}
    apps = Application.query.all()
    for app in apps:
        s = app.status or "unknown"
        status_counts[s] = status_counts.get(s, 0) + 1

    # Top job sources
    sources = Counter([j.source for j in JobPosting.query.all() if j.source])
    top_sources = [{"source": k, "count": v} for k, v in sources.most_common(5)]

    # Top roles
    roles = Counter([j.role for j in JobPosting.query.all() if j.role])
    top_roles = [{"role": k, "count": v} for k, v in roles.most_common(8)]

    return jsonify({
        "total_jobs":     total_jobs,
        "total_apps":     total_apps,
        "status_counts":  status_counts,
        "top_sources":    top_sources,
        "top_roles":      top_roles,
    })


# ─────────────────────────────────────────────
#  API: PLATFORM HEALTH CHECK
# ─────────────────────────────────────────────
@admin_routes.route("/api/admin/health")
@login_required
def admin_health():
    if not _is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    checks = {}

    # DB check
    try:
        User.query.count()
        checks["database"] = {"status": "ok", "label": "Database"}
    except Exception as e:
        checks["database"] = {"status": "error", "label": "Database", "detail": str(e)}

    # Coding module check
    try:
        from backend.models import Submission
        Submission.query.count()
        checks["coding_module"] = {"status": "ok", "label": "Coding Practice"}
    except Exception:
        checks["coding_module"] = {"status": "warning", "label": "Coding Practice", "detail": "Tables not yet created"}

    # Jobs check
    try:
        JobPosting.query.count()
        checks["jobs"] = {"status": "ok", "label": "Job Engine"}
    except Exception as e:
        checks["jobs"] = {"status": "error", "label": "Job Engine", "detail": str(e)}

    # AI services check
    try:
        from backend.services.resume_service import ResumeService
        checks["ai_service"] = {"status": "ok", "label": "AI Resume Service"}
    except Exception:
        checks["ai_service"] = {"status": "warning", "label": "AI Resume Service", "detail": "Not loaded"}

    all_ok = all(v["status"] == "ok" for v in checks.values())
    return jsonify({
        "overall": "healthy" if all_ok else "degraded",
        "checks":  checks,
        "timestamp": datetime.utcnow().isoformat(),
    })