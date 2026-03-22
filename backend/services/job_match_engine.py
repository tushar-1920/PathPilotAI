from backend.models import JobPosting, User
from backend.extensions import db
import re


class JobMatchEngine:

    # ==========================================
    # GLOBAL SKILL LIBRARY (for job description parsing)
    # ==========================================
    GLOBAL_SKILLS = {

        # Programming
        "python","java","c++","c","javascript","typescript","go","rust",

        # Data / AI
        "machine learning","deep learning","data science","pandas","numpy",
        "tensorflow","pytorch","scikit-learn","nlp","matplotlib","seaborn",

        # Backend
        "flask","django","spring","node.js","express","fastapi",

        # Frontend
        "html","css","react","angular","vue","next.js","tailwind","bootstrap",

        # Database
        "mysql","postgresql","mongodb","sqlite","oracle","redis",

        # Cloud
        "aws","azure","gcp","docker","kubernetes","terraform",

        # DevOps
        "jenkins","ci/cd","linux","bash","git","github","gitlab",

        # Big Data
        "spark","hadoop","kafka","airflow","databricks","snowflake"
    }

    # ==========================================
    # Extract Skills from Job Description
    # ==========================================
    def extract_job_skills(self, description):

        text = description.lower()

        extracted = set()

        for skill in self.GLOBAL_SKILLS:

            if re.search(r"\b" + re.escape(skill) + r"\b", text):
                extracted.add(skill)

        return list(extracted)

    # ==========================================
    # Calculate Match Score
    # ==========================================
    def calculate_match_score(self, user_skills, job_skills, role_match):

        if not job_skills:
            return 0

        user_set = {s.strip().lower() for s in user_skills}
        job_set = {s.strip().lower() for s in job_skills if s.strip()}

        if not job_set:
            return 0

        overlap = user_set.intersection(job_set)

        skill_score = (len(overlap) / len(job_set)) * 100

        # Role match boost
        role_bonus = 15 if role_match else 0

        final_score = min(skill_score + role_bonus, 100)

        return int(final_score)

    # ==========================================
    # Fit Level
    # ==========================================
    def get_fit_level(self, score):

        if score >= 80:
            return "Strong"
        elif score >= 60:
            return "Competitive"
        elif score >= 40:
            return "Medium"
        else:
            return "Weak"

    # ==========================================
    # Deep Resume vs Job Comparison
    # ==========================================
    def deep_job_match(self, resume_skills, job_description):

        job_skills = self.extract_job_skills(job_description)

        resume_set = {s.lower() for s in resume_skills}
        job_set = {s.lower() for s in job_skills}

        matched = resume_set.intersection(job_set)
        missing = job_set - resume_set

        if len(job_set) == 0:
            score = 0
        else:
            score = round((len(matched) / len(job_set)) * 100, 2)

        eligibility = self.get_fit_level(score)

        return {
            "score": score,
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "job_skills": job_skills,
            "eligibility": eligibility
        }

    # ==========================================
    # Get Job Matches (MAIN METHOD - UNCHANGED)
    # ==========================================
    def get_job_matches(self, user_id, role_filter=None, fit_filter=None, sort="desc"):

        user = User.query.get(user_id)

        if not user:
            return []

        # Extract user skills safely
        user_skills = []

        if user.normalized_skills:
            user_skills = [
                s.strip().lower()
                for s in user.normalized_skills.split(",")
                if s.strip()
            ]

        query = JobPosting.query

        # Safe role filtering
        if role_filter:
            query = query.filter(JobPosting.role.ilike(f"%{role_filter}%"))

        jobs = query.all()

        results = []

        for job in jobs:

            job_skills = []

            if job.normalized_skills:
                job_skills = [
                    s.strip().lower()
                    for s in job.normalized_skills.split(",")
                    if s.strip()
                ]

            role_match = False

            if role_filter and job.role:
                role_match = role_filter.lower() in job.role.lower()

            score = self.calculate_match_score(
                user_skills,
                job_skills,
                role_match
            )

            fit_level = self.get_fit_level(score)

            # Apply fit filter safely
            if fit_filter and fit_filter != fit_level:
                continue

            results.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "skills_required": job.skills_required,
                "match_score": score,
                "fit_level": fit_level,
                "source": job.source
            })

        reverse = True if sort == "desc" else False

        results = sorted(
            results,
            key=lambda x: x["match_score"],
            reverse=reverse
        )

        return results