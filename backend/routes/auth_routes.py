from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User, Profile
from backend.extensions import db

auth_routes = Blueprint("auth_routes", __name__)

# ═══════════════════════════════════════════════════════════
#  HARDCODED RECRUITER ACCOUNTS
#  Add / remove entries here to manage recruiter access.
#  Format: "email": ("password", "Company Display Name")
# ═══════════════════════════════════════════════════════════
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
    """Helper: populate all session keys for a logged-in user."""
    session["user_id"]   = user.id
    session["role"]      = user.role
    session["user_name"] = user.name or ""
    session["user_email"] = user.email or ""

    # Load profile photo using the model property — always correct path format
    session["profile_photo"] = user.profile_photo_url


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
        return redirect("/dashboard")

    return render_template("register.html")


# ================= LOGIN =================
@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email")
        password = request.form.get("password")

        # ── RECRUITER CHECK (runs first, before normal user logic) ──
        if email in RECRUITER_ACCOUNTS:
            stored_pass, company_name = RECRUITER_ACCOUNTS[email]
            if password == stored_pass:
                session["recruiter_email"]   = email
                session["recruiter_company"] = company_name
                session["role"]              = "recruiter"
                # We do NOT set session["user_id"] for recruiters
                return redirect("/recruiter/dashboard")
            else:
                flash("Invalid recruiter credentials")
                return redirect(url_for("auth_routes.login"))

        # ── NORMAL USER LOGIN ──
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