from flask import Blueprint, render_template, request, jsonify, session
from backend.utils.auth_utils import login_required
from backend.services.resume_ai_service import ResumeAIService
from backend.models import Resume
import pdfplumber
import docx

resume_ai_routes = Blueprint("resume_ai_routes", __name__)


@resume_ai_routes.route("/resume-ai")
@login_required
def resume_ai_page():
    user_id = session.get("user_id")
    resumes = Resume.query.filter_by(user_id=user_id).all()
    return render_template("resume_ai.html", resumes=resumes)


@resume_ai_routes.route("/api/resume-ai/analyze", methods=["POST"])
@login_required
def analyze_resume():

    resume_text = ""

    # 1️⃣ if file uploaded
    if "resume_file" in request.files:

        file = request.files["resume_file"]

        if file.filename.endswith(".pdf"):

            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    resume_text += page.extract_text() or ""

        elif file.filename.endswith(".docx"):

            doc = docx.Document(file)
            for p in doc.paragraphs:
                resume_text += p.text + "\n"

        elif file.filename.endswith(".txt"):

            resume_text = file.read().decode("utf-8")

    # 2️⃣ if pasted text
    else:
        data = request.json
        resume_text = data.get("resume_text", "")

    if not resume_text:
        return jsonify({"analysis": "No resume content found."})

    result = ResumeAIService.analyze_resume(resume_text)

    return jsonify({"analysis": result})