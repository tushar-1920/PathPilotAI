from flask import Blueprint, render_template, request, send_file, jsonify
import os, traceback

from backend.services.resume_builder_service import generate_resume

resume_builder = Blueprint("resume_builder", __name__)


# ──────────────────────────────────────────────────────────
# PAGE ROUTE
# ──────────────────────────────────────────────────────────

@resume_builder.route("/resume-builder")
def resume_builder_page():
    return render_template("resume_builder.html")


# ──────────────────────────────────────────────────────────
# API — GENERATE PDF
# NOTE: Route is /api/build-resume to avoid conflict with
#       any existing /generate-resume route in your app
# ──────────────────────────────────────────────────────────

@resume_builder.route("/api/build-resume", methods=["POST"])
def generate_resume_api():
    try:
        # Accept JSON — silent=True means it returns None instead of 400 on bad JSON
        data = request.get_json(force=True, silent=True)

        # Fallback: try form data if JSON parsing failed
        if not data:
            data = request.form.to_dict()

        if not data:
            print("[ResumeBuilder] ERROR: No data received in request body")
            return jsonify({"error": "No data received"}), 400

        print(f"[ResumeBuilder] Received keys: {list(data.keys())}")

        # Set safe defaults so empty fields never crash LaTeX
        data.setdefault("name",           "My Resume")
        data.setdefault("title",          "")
        data.setdefault("email",          "")
        data.setdefault("phone",          "")
        data.setdefault("location",       "")
        data.setdefault("linkedin",       "https://linkedin.com")
        data.setdefault("github",         "https://github.com")
        data.setdefault("portfolio",      "https://example.com")
        data.setdefault("hackerrank",     "https://hackerrank.com")
        data.setdefault("leetcode",       "https://leetcode.com")
        data.setdefault("summary",        "")
        data.setdefault("education",      "")
        data.setdefault("internship",     "")
        data.setdefault("projects",       "")
        data.setdefault("skills",         "")
        data.setdefault("honors",         "")
        data.setdefault("certifications", "")

        pdf_path = generate_resume(data)

        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF file was not created"}), 500

        safe_name = (data.get("name") or "Resume").replace(" ", "_").replace("/", "_")
        filename  = f"{safe_name}_Resume.pdf"

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )

    except Exception as e:
        print(f"[ResumeBuilder] EXCEPTION: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500