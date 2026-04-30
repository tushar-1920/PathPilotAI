from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User, Profile
from backend.extensions import db
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import os

auth_routes = Blueprint("auth_routes", __name__)

# ── Init Firebase Admin once ──
if not firebase_admin._apps:
    cred_path = os.path.join(os.path.dirname(__file__), "..", "..", "firebase-admin-key.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

RECRUITER_ACCOUNTS = {
    "recruiter@pathpilot.com":   ("recruit123",  "PathPilot Hiring"),
    "google@recruiter.com":      ("google@123",  "Google"),
    "microsoft@recruiter.com":   ("msft@123",    "Microsoft"),
    "amazon@recruiter.com":      ("amzn@123",    "Amazon"),
    "startup@recruiter.com":     ("start@123",   "TechStartup Inc"),
    "tcs@recruiter.com":         ("tcs@123",     "TCS"),
    "infosys@recruiter.com":     ("infy@123",    "Infosys"),
    "wipro@recruiter.com":       ("wipro@123",   "Wipro"),
    "caelius@recruiter.com":     ("caelius@123", "Caelius Consulting"),
}


def _set_user_session(user):
    session["user_id"]       = user.id
    session["role"]          = user.role
    session["user_name"]     = user.name or ""
    session["user_email"]    = user.email or ""
    session["profile_photo"] = user.profile_photo_url


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

        _set_user_session(user)
        return jsonify({"success": True, "redirect": "/dashboard"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401


# ================= REGISTER =================
@auth_routes.route("/register", methods=["GET", "POST"])
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

        _set_user_session(new_user)
        return redirect("/verify-phone")

    return render_template("register.html")


# ================= LOGIN =================
@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email")
        password = request.form.get("password")

        if email in RECRUITER_ACCOUNTS:
            stored_pass, company_name = RECRUITER_ACCOUNTS[email]
            if password == stored_pass:
                session["recruiter_email"]   = email
                session["recruiter_company"] = company_name
                session["role"]              = "recruiter"
                return redirect("/recruiter/dashboard")
            else:
                flash("Invalid recruiter credentials")
                return redirect(url_for("auth_routes.login"))

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials")
            return redirect(url_for("auth_routes.login"))

        _set_user_session(user)
        return redirect("/dashboard")

    return render_template("login.html")


# ================= LOGOUT =================
@auth_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================= PHONE VERIFY =================
@auth_routes.route("/verify-phone")
def verify_phone_page():
    if not session.get("user_id"):
        return redirect("/login")
    return render_template("verify_phone.html")


@auth_routes.route("/verify-phone", methods=["POST"])
def verify_phone():
    if not session.get("user_id"):
        return jsonify({"success": False, "error": "Not logged in"}), 401

    id_token = request.json.get("idToken")
    try:
        decoded      = firebase_auth.verify_id_token(id_token)
        phone_number = decoded.get("phone_number")

        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        user.is_verified = True
        db.session.commit()

        session["is_verified"] = True
        return jsonify({"success": True, "redirect": "/dashboard"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401


@auth_routes.route("/verify-phone/skip", methods=["POST"])
def skip_phone_verify():
    session["is_verified"] = False
    return jsonify({"success": True})