from backend.services.job_match_engine import JobMatchEngine


@job_analyzer_routes.route("/api/analyze-job", methods=["POST"])
def analyze_job():

    data = request.json
    description = data.get("description")

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    resume_skills = []

    if user.normalized_skills:
        resume_skills = [
            s.strip()
            for s in user.normalized_skills.split(",")
        ]

    engine = JobMatchEngine()

    job_skills = engine.extract_job_skills(description)

    result = engine.compare(resume_skills, job_skills)

    return jsonify({
        "score": result["score"],
        "matched": result["matched_skills"],
        "missing": result["missing_skills"],
        "eligibility": result["eligibility"],
        "job_skills": job_skills
    })