from flask import Blueprint, request, jsonify, render_template, session
from backend.models import User
from backend.utils.auth_decorator import login_required

from backend.services.ai_salary_engine import AISalaryEngine

salary_routes = Blueprint("salary_routes", __name__)

ai_engine = AISalaryEngine()

# ==================================
# Salary Intelligence Page
# ==================================

@salary_routes.route("/api/ai-salary", methods=["POST"])
@login_required
def ai_salary():

    data = request.get_json()

    role = data.get("role")
    country = data.get("country")
    experience = data.get("experience")
    company = data.get("company")
    state = data.get("state")

    if not role:
        return jsonify({"error":"Role required"}),400

    ai_response = ai_engine.predict_salary(
        role,
        experience,
        country,
        state,
        company
    )

    return jsonify({
        "ai_result": ai_response
    })

@salary_routes.route("/salary")
@login_required
def salary_page():
    return render_template("salary.html")