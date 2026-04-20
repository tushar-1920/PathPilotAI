"""
backend/routes/offer_predictor_routes.py

Offer Predictor — PathPilot AI
Routes:
  GET  /offer-predictor              → main page
  GET  /offer-predictor/history      → prediction history page
  GET  /offer-predictor/result/<id>  → single result detail page
  POST /api/offer-predictor/analyze  → run a new prediction (AJAX)
  GET  /api/offer-predictor/history  → fetch history JSON (AJAX)
  GET  /api/offer-predictor/<id>     → fetch single result JSON (AJAX)
  POST /api/offer-predictor/quick-scan → fast skill-only scan (no DB save)

Register in app.py:
    from backend.routes.offer_predictor_routes import offer_predictor_routes
    app.register_blueprint(offer_predictor_routes)
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from backend.utils.auth_decorator import login_required
from backend.models import User, Resume, Profile, OfferPrediction
from backend.services.offer_predictor_service import OfferPredictorService

offer_predictor_routes = Blueprint("offer_predictor_routes", __name__)

# ── helpers ───────────────────────────────────────────────────
def _svc():
    return OfferPredictorService()

def _get_user_context():
    uid     = session.get("user_id")
    user    = User.query.get(uid) if uid else None
    profile = Profile.query.filter_by(user_id=uid).first() if uid else None
    img     = f"/static/{profile.profile_image}" if profile and profile.profile_image else ""
    name    = user.name if user else "Guest"
    return uid, name, img, user, profile


# ══════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════════════

@offer_predictor_routes.route("/offer-predictor")
@login_required
def offer_predictor_page():
    uid, name, img, user, profile = _get_user_context()
    resume   = Resume.query.filter_by(user_id=uid).order_by(Resume.id.desc()).first()
    history  = _svc().get_history(uid, limit=5)

    has_resume = bool(resume and (getattr(resume, "raw_text", None) or getattr(resume, "normalized_skills", None)))

    return render_template(
        "offer_predictor.html",
        user_name    = name,
        user_image   = img,
        has_resume   = has_resume,
        resume       = resume,
        history      = history,
        skills       = (user.normalized_skills or "") if user else "",
    )


@offer_predictor_routes.route("/offer-predictor/result/<int:pid>")
@login_required
def offer_result_page(pid):
    uid, name, img, user, profile = _get_user_context()
    prediction = OfferPrediction.query.filter_by(id=pid, user_id=uid).first()
    if not prediction:
        return redirect(url_for("offer_predictor_routes.offer_predictor_page"))
    return render_template(
        "offer_predictor_result.html",
        user_name  = name,
        user_image = img,
        prediction = prediction.to_dict(),
        pred_obj   = prediction,
    )


@offer_predictor_routes.route("/offer-predictor/history")
@login_required
def offer_history_page():
    uid, name, img, user, profile = _get_user_context()
    history = _svc().get_history(uid, limit=50)
    return render_template(
        "offer_predictor_history.html",
        user_name  = name,
        user_image = img,
        history    = history,
    )


# ══════════════════════════════════════════════════════════════
#  API ROUTES
# ══════════════════════════════════════════════════════════════

@offer_predictor_routes.route("/api/offer-predictor/analyze", methods=["POST"])
@login_required
def analyze():
    """Run a full Offer Predictor analysis."""
    uid  = session["user_id"]
    data = request.get_json(silent=True) or {}

    job_description = (data.get("job_description") or "").strip()
    job_title       = (data.get("job_title") or "").strip()
    company_name    = (data.get("company_name") or "").strip()
    job_url         = (data.get("job_url") or "").strip()

    if not job_description:
        return jsonify({"success": False, "error": "Job description is required."}), 400

    if len(job_description) < 50:
        return jsonify({"success": False, "error": "Job description is too short. Paste the full JD for accurate results."}), 400

    try:
        result = _svc().predict(
            user_id         = uid,
            job_description = job_description,
            job_title       = job_title,
            company_name    = company_name,
            job_url         = job_url,
        )
        return jsonify({"success": True, **result})
    except RuntimeError as e:
        return jsonify({"success": False, "error": str(e)}), 503
    except Exception as e:
        print(f"[OfferPredictor] Error: {e}")
        return jsonify({"success": False, "error": "Analysis failed. Please try again."}), 500


@offer_predictor_routes.route("/api/offer-predictor/history")
@login_required
def history_api():
    uid     = session["user_id"]
    limit   = min(int(request.args.get("limit", 10)), 50)
    history = _svc().get_history(uid, limit=limit)
    return jsonify({"success": True, "history": history})


@offer_predictor_routes.route("/api/offer-predictor/<int:pid>")
@login_required
def single_prediction_api(pid):
    uid    = session["user_id"]
    result = _svc().get_prediction(pid, uid)
    if not result:
        return jsonify({"success": False, "error": "Prediction not found."}), 404
    return jsonify({"success": True, **result})


@offer_predictor_routes.route("/api/offer-predictor/delete/<int:pid>", methods=["DELETE"])
@login_required
def delete_prediction(pid):
    uid  = session["user_id"]
    pred = OfferPrediction.query.filter_by(id=pid, user_id=uid).first()
    if not pred:
        return jsonify({"success": False, "error": "Not found"}), 404
    from backend.extensions import db
    db.session.delete(pred)
    db.session.commit()
    return jsonify({"success": True})