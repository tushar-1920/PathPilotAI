from flask import Blueprint, jsonify, session, render_template
from backend.services.forecasting_service import ForecastingService
from backend.utils.auth_decorator import login_required

forecast_routes = Blueprint("forecast_routes", __name__)
service = ForecastingService()


@forecast_routes.route("/forecast")
@login_required
def forecast_page():
    return render_template("forecast.html")


@forecast_routes.route("/api/forecast-data")
@login_required
def forecast_data():

    skill_forecast = service.skill_growth_forecast()
    role_forecast = service.role_growth_forecast()
    suggestions = service.personalized_future_skills(session["user_id"])

    return jsonify({
        "skill_forecast": skill_forecast,
        "role_forecast": role_forecast,
        "suggestions": suggestions
    })