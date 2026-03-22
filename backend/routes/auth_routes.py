from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User
from backend.extensions import db

# IMPORTANT: This name MUST match import in app.py
auth_routes = Blueprint("auth_routes", __name__)


# ================= REGISTER =================
@auth_routes.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
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

        session["user_id"] = new_user.id
        session["role"] = new_user.role

        return redirect("/dashboard")

    return render_template("register.html")


# ================= LOGIN =================
@auth_routes.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials")
            return redirect(url_for("auth_routes.login"))

        session["user_id"] = user.id
        session["role"] = user.role
        

        return redirect("/dashboard")

    return render_template("login.html")


# ================= LOGOUT =================
@auth_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/")