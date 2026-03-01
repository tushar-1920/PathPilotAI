from flask import Blueprint, render_template

main_routes = Blueprint("main_routes", __name__)

@main_routes.route("/")
def home():
    return render_template("index.html")
@main_routes.route("/upload")
def upload_page():
    return render_template("upload_resume.html")
@main_routes.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
@main_routes.route("/roadmap")
def roadmap_page():
    return render_template("roadmap.html")