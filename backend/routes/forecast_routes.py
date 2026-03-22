from flask import Blueprint, jsonify, session, render_template, request
from backend.services.ai_forecast_service import AIForecastService
from backend.services.forecasting_service import ForecastingService
from backend.utils.auth_decorator import login_required
from backend.models import Resume, User

forecast_routes = Blueprint("forecast_routes", __name__)

ai_service     = AIForecastService()
market_service = ForecastingService()


# ══════════════════════════════════════════════════════════════
#  PAGE
# ══════════════════════════════════════════════════════════════
@forecast_routes.route("/forecast")
@login_required
def forecast_page():
    user_id = session.get("user_id")
    resumes = Resume.query.filter_by(user_id=user_id).all()
    return render_template("forecast.html", resumes=resumes)


# ══════════════════════════════════════════════════════════════
#  AI RESUME FORECAST  — main intelligence endpoint
# ══════════════════════════════════════════════════════════════
@forecast_routes.route("/api/forecast-intelligence")
@login_required
def forecast_intelligence():
    resume_id = request.args.get("resume_id")
    if not resume_id:
        return jsonify({"error": "resume_id required"}), 400
    data = ai_service.analyze_career_forecast(resume_id)
    return jsonify(data)


# ══════════════════════════════════════════════════════════════
#  MARKET DATA — skill + role forecasts
# ══════════════════════════════════════════════════════════════
@forecast_routes.route("/api/forecast-data")
@login_required
def forecast_data():
    skill_forecast = market_service.skill_market_intelligence()
    role_forecast  = market_service.role_market_forecast()
    growth_data    = market_service.market_growth_projection()
    return jsonify({
        "skill_forecast": skill_forecast,
        "role_forecast":  role_forecast,
        "market_growth":  growth_data,
    })


# ══════════════════════════════════════════════════════════════
#  SKILL SATURATION  — per-skill opportunity analysis
# ══════════════════════════════════════════════════════════════
@forecast_routes.route("/api/skill-saturation")
@login_required
def skill_saturation():
    user_id = session.get("user_id")
    user    = User.query.get(user_id)
    if not user or not user.normalized_skills:
        return jsonify([])
    skills = [s.strip() for s in user.normalized_skills.split(",") if s.strip()]
    data   = market_service.skill_saturation_analysis(skills)
    return jsonify(data)


# ══════════════════════════════════════════════════════════════
#  MARKET ALIGNMENT  — quick resume vs market check
# ══════════════════════════════════════════════════════════════
@forecast_routes.route("/api/market-alignment")
@login_required
def market_alignment():
    user_id = session.get("user_id")
    data    = market_service.resume_market_alignment(user_id)
    if not data:
        return jsonify({"error": "No resume data found"}), 404
    return jsonify(data)