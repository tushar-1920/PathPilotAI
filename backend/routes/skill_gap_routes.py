from flask import Blueprint, jsonify, request, render_template, session
from backend.services.skill_gap_service import SkillGapService
from backend.utils.auth_decorator import login_required

skill_gap_routes = Blueprint("skill_gap_routes", __name__)

service = SkillGapService()


@skill_gap_routes.route("/skill-gap")
@login_required
def skill_gap_page():
    return render_template("skill_gap.html")


@skill_gap_routes.route("/api/skill-gap", methods=["POST"])
@login_required
def analyze_gap():

    role = request.json.get("role")

    result = service.analyze_gap(session["user_id"], role)

    return jsonify(result)