from flask import Blueprint, render_template, session, request, jsonify
from backend.utils.auth_decorator import login_required
from backend.services.career_time_machine_service import CareerTimeMachineService
from backend.models import User, Resume

ctm_routes = Blueprint("ctm_routes", __name__)

def svc():
    return CareerTimeMachineService()


@ctm_routes.route("/career-time-machine")
@login_required
def ctm_page():
    user_id = session["user_id"]
    user    = User.query.get(user_id)
    machine = svc().get_machine(user_id)
    resume  = Resume.query.filter_by(user_id=user_id).order_by(Resume.id.desc()).first()
    return render_template("career_time_machine.html",
        user=user, machine=machine, resume=resume)


@ctm_routes.route("/api/ctm/generate", methods=["POST"])
@login_required
def generate():
    d = request.get_json() or {}

    target_role    = (d.get("target_role") or "").strip()
    target_company = (d.get("target_company") or "").strip()
    current_level  = (d.get("current_level") or "mid").strip()

    # ── BUG FIX: safely coerce timeline_months to int ──
    raw_timeline = d.get("timeline_months")
    try:
        timeline = int(raw_timeline) if raw_timeline is not None else 24
    except (ValueError, TypeError):
        timeline = 24

    # Clamp to allowed values
    if timeline not in (12, 24, 36):
        timeline = 24

    if not target_role:
        return jsonify({"success": False, "error": "Target role is required"}), 400

    try:
        result = svc().generate_plan(
            user_id        = session["user_id"],
            target_role    = target_role,
            target_company = target_company,
            timeline_months= timeline,
            current_level  = current_level,
        )
        return jsonify({"success": True, **result})
    except Exception as e:
        print(f"[CTM] Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ctm_routes.route("/api/ctm/toggle-milestone", methods=["POST"])
@login_required
def toggle_milestone():
    d = request.get_json() or {}

    machine_id = d.get("machine_id")
    month_num  = d.get("month_num")
    milestone  = (d.get("milestone") or "").strip()
    note       = (d.get("note") or "").strip()

    if not machine_id or month_num is None:
        return jsonify({"success": False, "error": "Missing machine_id or month_num"}), 400

    try:
        result = svc().toggle_milestone(
            user_id    = session["user_id"],
            machine_id = int(machine_id),
            month_num  = int(month_num),
            milestone  = milestone,
            note       = note,
        )
        return jsonify({"success": True, **result})
    except Exception as e:
        print(f"[CTM] Toggle error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ctm_routes.route("/api/ctm/current")
@login_required
def current():
    try:
        machine = svc().get_machine(session["user_id"])
        if not machine:
            return jsonify({"success": False, "message": "No plan found"})
        return jsonify({"success": True, **machine})
    except Exception as e:
        print(f"[CTM] Current error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500