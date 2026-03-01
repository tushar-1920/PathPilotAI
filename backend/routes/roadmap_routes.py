from flask import Blueprint, request, jsonify, session
from backend.models import User
from backend.services.roadmap_engine import RoadmapEngine
from backend.utils.auth_decorator import login_required
roadmap_routes = Blueprint("roadmap_routes", __name__)

engine = RoadmapEngine()


@roadmap_routes.route("/api/roadmap", methods=["POST"])
def generate_roadmap():

    # 🔐 Ensure user is logged in
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(session["user_id"])

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    role = data.get("role")

    if not role:
        return jsonify({"error": "Role not provided"}), 400


    # ===============================
    # AUTO ROLE DETECTION
    # ===============================
    if role == "AUTO":

        detected_role, match_score = engine.detect_best_role(user.id)

        result = engine.generate_learning_plan(user.id, detected_role)

        result["detected_role"] = detected_role
        result["role_match_score"] = match_score

        return jsonify(result)


    # ===============================
    # MANUAL ROLE SELECTED
    # ===============================
    result = engine.generate_learning_plan(user.id, role)

    return jsonify(result)