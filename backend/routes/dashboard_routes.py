from flask import Blueprint, jsonify, render_template, session
from backend.services.skill_score_engine import SkillScoreEngine
from backend.utils.auth_utils import login_required
from backend.services.recommendation_service import RecommendationService
dashboard_routes = Blueprint("dashboard_routes", __name__)

engine = SkillScoreEngine()


# =========================
# Dashboard Page (HTML)
# =========================
@dashboard_routes.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html")


# =========================
# Dashboard API
# =========================
@dashboard_routes.route("/api/dashboard")
@login_required
def get_dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "skill_score": 0,
            "readiness_score": 0,
            "skills": [],
            "breakdown": {}
        })

    try:
        skill_score = engine.calculate_skill_score(user_id)
        readiness_score = engine.calculate_career_readiness(user_id)
        skills = engine.get_user_skills(user_id)
        breakdown = engine.get_skill_category_breakdown(user_id)

        return jsonify({
            "skill_score": skill_score or 0,
            "readiness_score": readiness_score or 0,
            "skills": skills or [],
            "breakdown": breakdown or {}
        })

    except Exception as e:
        print("Dashboard Engine Error:", e)

        return jsonify({
            "skill_score": 0,
            "readiness_score": 0,
            "skills": [],
            "breakdown": {}
        })

@dashboard_routes.route("/api/skill-trend")
@login_required
def skill_trend():

    from flask import session
    from backend.models import UserSkill
    from collections import Counter

    skills = UserSkill.query.filter_by(user_id=session["user_id"]).all()

    skill_names = [us.skill.name for us in skills if us.skill]

    counter = Counter(skill_names)

    return jsonify(counter)

@dashboard_routes.route("/api/recommendations")
@login_required
def recommendations():

    from flask import session

    service = RecommendationService()

    result = service.generate_recommendations(session["user_id"])

    return jsonify(result)

@dashboard_routes.route("/api/skill-growth")
@login_required
def skill_growth():

    from flask import session
    from backend.models import Resume

    resumes = Resume.query\
        .filter_by(user_id=session["user_id"])\
        .order_by(Resume.uploaded_at.asc())\
        .all()

    labels = []
    scores = []

    for r in resumes:
        labels.append(r.uploaded_at.strftime("%d %b"))
        scores.append(r.skill_score or 0)

    return jsonify({
        "labels": labels,
        "scores": scores
    })