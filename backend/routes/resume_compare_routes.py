from flask import Blueprint, request, jsonify
from backend.services.resume_comparison_service import ResumeComparisonService
from backend.utils.auth_decorator import login_required

resume_compare_routes = Blueprint("resume_compare_routes", __name__)

@resume_compare_routes.route("/api/resume-compare", methods=["POST"])
@login_required
def resume_compare():

    data = request.get_json()

    resume_a_id = data.get("resume_a_id")
    resume_b_id = data.get("resume_b_id")

    if not resume_a_id or not resume_b_id:
        return jsonify({"error": "Missing resume IDs"}), 400

    service = ResumeComparisonService()
    result = service.compare(resume_a_id, resume_b_id)

    return jsonify(result)