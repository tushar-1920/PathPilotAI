from flask import Blueprint, render_template, session, request, jsonify
from backend.utils.auth_decorator import login_required
from backend.services.blind_spot_service import BlindSpotService
from backend.models import User, Resume

blind_spot_routes = Blueprint("blind_spot_routes", __name__)

def svc():
    return BlindSpotService()


@blind_spot_routes.route("/blind-spot-detector")
@login_required
def blind_spot_page():
    user_id = session["user_id"]
    user    = User.query.get(user_id)
    report  = svc().get_latest(user_id)
    resume  = Resume.query.filter_by(user_id=user_id).order_by(Resume.id.desc()).first()
    return render_template("blind_spot_detector.html",
        user=user, report=report, resume=resume)


@blind_spot_routes.route("/blind-spot/deep-dive")
@login_required
def deep_dive_page():
    return render_template("blind_spot_deep_dive.html")


@blind_spot_routes.route("/api/blind-spot/analyze", methods=["POST"])
@login_required
def analyze():
    d     = request.get_json() or {}
    extra = (d.get("extra_context") or "").strip()
    try:
        result = svc().analyze(session["user_id"], extra)
        return jsonify({"success": True, **result})
    except Exception as e:
        print(f"[BlindSpot] Analyze error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blind_spot_routes.route("/api/blind-spot/deep-dive", methods=["POST"])
@login_required
def deep_dive_api():
    d          = request.get_json() or {}
    blind_spot = (d.get("blind_spot") or "").strip()
    context    = (d.get("context") or "").strip()
    if not blind_spot:
        return jsonify({"success": False, "error": "No blind spot provided"}), 400
    try:
        result = svc().deep_dive(blind_spot, context)
        return jsonify({"success": True, **result})
    except Exception as e:
        print(f"[BlindSpot] Deep dive error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blind_spot_routes.route("/api/blind-spot/latest")
@login_required
def latest():
    try:
        report = svc().get_latest(session["user_id"])
        if not report:
            return jsonify({"success": False, "message": "No report found"})
        return jsonify({"success": True, **report})
    except Exception as e:
        print(f"[BlindSpot] Latest error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500