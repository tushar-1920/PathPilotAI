from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User, Profile
from backend.extensions import db
from backend.extensions import limiter
from flask_limiter.util import get_remote_address
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import os
auth_routes = Blueprint("auth_routes", __name__)

# ── Init Firebase Admin once ──
if not firebase_admin._apps:
    import json
    firebase_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if firebase_json:
        # Production — load from environment variable
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
    else:
        # Local development — load from file
        cred_path = os.path.join(os.path.dirname(__file__), "..", "..", "firebase-admin-key.json")
        cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def _set_user_session(user):
    session["user_id"]       = user.id
    session["role"]          = user.role
    session["user_name"]     = user.name or ""
    session["user_email"]    = user.email or ""
    session["profile_photo"] = user.profile_photo_url
    session["is_verified"]   = bool(user.is_verified)


def _set_recruiter_session(user):
    """
    Recruiters bypass OTP and use a slightly different session shape so
    that all the downstream recruiter routes keep working unchanged.
    `recruiter_email` and `recruiter_company` are the keys those routes
    read — preserved from the previous hardcoded-dict flow.
    """
    session["user_id"]            = user.id
    session["user_name"]          = user.name or ""
    session["user_email"]         = user.email or ""
    session["recruiter_email"]    = user.email
    session["recruiter_company"]  = user.name
    session["role"]               = "recruiter"
    session["is_verified"]        = True
    session["profile_photo"]      = user.profile_photo_url


# ================= GOOGLE LOGIN =================
@auth_routes.route("/auth/google", methods=["POST"])
def google_login():
    id_token = request.json.get("idToken")
    try:
        decoded   = firebase_auth.verify_id_token(id_token)
        email     = decoded["email"]
        name      = decoded.get("name", email.split("@")[0])
        google_id = decoded["uid"]

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
                google_id=google_id,
                auth_provider="google",
                role="user"
            )
            db.session.add(user)
            db.session.commit()
        elif not user.google_id:
            user.google_id    = google_id
            user.auth_provider = "google"
            db.session.commit()

        # Google users are already verified by Google
        user.is_verified = True
        db.session.commit()

        _set_user_session(user)
        return jsonify({"success": True, "redirect": "/dashboard"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401


# ================= REGISTER =================
@auth_routes.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"], key_func=get_remote_address)
def register():
    if request.method == "POST":
        name     = request.form.get("name")
        email    = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields required")
            return redirect(url_for("auth_routes.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for("auth_routes.register"))

        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role="user"
        )
        db.session.add(new_user)
        db.session.commit()

        # Send OTP email
        from backend.services.email_service import generate_otp, send_otp_email
        from datetime import datetime, timedelta

        otp = generate_otp()
        new_user.otp_code       = otp
        new_user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        new_user.otp_attempts   = 0
        db.session.commit()

        send_otp_email(new_user.email, otp, new_user.name)
        _set_user_session(new_user)
        return redirect("/verify-email")

    return render_template("register.html")


# ================= LOGIN =================
@auth_routes.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"], key_func=get_remote_address)
def login():
    if request.method == "POST":
        email    = request.form.get("email")
        password = request.form.get("password")

        # Unified password check — recruiters now live in the User table too
        user = User.query.filter_by(email=email).first()
        if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials")
            return redirect(url_for("auth_routes.login"))

        # Recruiter accounts: skip OTP, go straight to recruiter dashboard.
        # Preserves the exact behavior of the old hardcoded-dict flow.
        if user.role == "recruiter":
            _set_recruiter_session(user)
            return redirect("/recruiter/dashboard")

        # Normal users: go through OTP verification (unchanged)
        from backend.services.email_service import generate_otp, send_otp_email
        from datetime import datetime, timedelta

        otp = generate_otp()
        user.is_verified    = False
        user.otp_code       = otp
        user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        user.otp_attempts   = 0
        db.session.commit()

        send_otp_email(user.email, otp, user.name)
        _set_user_session(user)
        return redirect("/verify-email")

    return render_template("login.html")


# ================= LOGOUT =================
@auth_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= EMAIL OTP VERIFY =================
@auth_routes.route("/verify-email")
def verify_email_page():
    if not session.get("user_id"):
        return redirect("/login")
    user = User.query.get(session["user_id"])
    if user and user.is_verified:
        return redirect("/dashboard")
    return render_template("verify_email.html")


@auth_routes.route("/verify-email", methods=["POST"])
@limiter.limit("10 per minute")
def verify_email():
    if not session.get("user_id"):
        return jsonify({"success": False, "error": "Not logged in"}), 401

    data = request.get_json()
    otp_entered = data.get("otp", "").strip()

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    from datetime import datetime

    # Check attempts
    if user.otp_attempts >= 5:
        return jsonify({"success": False, "error": "Too many attempts. Please register again."}), 429

    # Check expiry
    if not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:
        return jsonify({"success": False, "error": "OTP expired. Please request a new one."}), 400

    # Check OTP
    if user.otp_code != otp_entered:
        user.otp_attempts += 1
        db.session.commit()
        remaining = 5 - user.otp_attempts
        return jsonify({"success": False, "error": f"Wrong OTP. {remaining} attempts left."}), 400

    # OTP correct
    user.is_verified    = True
    user.otp_code       = None
    user.otp_expires_at = None
    user.otp_attempts   = 0
    db.session.commit()

    session["is_verified"] = True
    return jsonify({"success": True, "redirect": "/dashboard"})

@auth_routes.route("/verify-email/resend", methods=["POST"])
@limiter.limit("3 per minute")
def resend_otp():

    if not session.get("user_id"):
        return jsonify({"success": False, "error": "Not logged in"}), 401

    from backend.services.email_service import generate_otp, send_otp_email
    from datetime import datetime, timedelta

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    otp = generate_otp()
    user.otp_code       = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    user.otp_attempts   = 0
    db.session.commit()

    sent = send_otp_email(user.email, otp, user.name)
    if sent:
        return jsonify({"success": True, "message": "OTP resent to your email!"})
    else:
        return jsonify({"success": False, "error": "Failed to send email. Check mail config."}), 500