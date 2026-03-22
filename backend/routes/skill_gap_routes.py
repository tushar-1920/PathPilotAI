from flask import Blueprint, jsonify, request, render_template, session
from backend.services.skill_gap_service import SkillGapService
from backend.utils.auth_decorator import login_required
from backend.utils.subscription_required import pro_required
from backend.services.ai_salary_engine import AISalaryEngine
skill_gap_routes = Blueprint("skill_gap_routes", __name__)
service = SkillGapService()


@skill_gap_routes.route("/skill-gap")
@login_required
def skill_gap_page():
    return render_template("skill_gap.html")


# Free Version
@skill_gap_routes.route("/api/skill-gap", methods=["POST"])
@login_required
def analyze_gap():

    role = request.json.get("role")
    result = service.analyze_gap(session["user_id"], role)

    return jsonify(result)


# PRO Version
@skill_gap_routes.route("/api/skill-gap-pro", methods=["POST"])
@login_required
@pro_required("skill_gap_pro")
def analyze_gap_pro():

    role = request.json.get("role")
    result = service.analyze_gap_pro(session["user_id"], role)

    return jsonify(result)