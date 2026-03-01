from flask import Blueprint, request, jsonify, render_template, session
from backend.models import User
from backend.services.salary_engine import SalaryEngine
from backend.services.roadmap_engine import RoadmapEngine
from backend.utils.auth_decorator import login_required


salary_routes = Blueprint("salary_routes", __name__)

salary_engine = SalaryEngine()
roadmap_engine = RoadmapEngine()


# ==============================
# Salary Page
# ==============================
@salary_routes.route("/salary")
@login_required
def salary_page():
    return render_template("salary.html")


# ==============================
# Salary Prediction API
# ==============================
@salary_routes.route("/api/salary-predict", methods=["POST"])
@login_required
def predict_salary():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    role = data.get("role")
    experience_level = data.get("experience_level")
    country = data.get("country")
    state = data.get("state")

    if not role:
        return jsonify({"error": "Role is required"}), 400

    # 🔐 Get logged-in user
    user = User.query.get(session["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    # 🔥 Calculate role match score from roadmap engine
    role_score = roadmap_engine.calculate_role_based_score(user.id, role)

    # 🔥 Predict salary
    result = salary_engine.predict_salary(
        role=role,
        experience_level=experience_level,
        country=country,
        state=state,
        role_score=role_score
    )

    return jsonify(result)