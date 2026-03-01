from backend.models import User, JobPosting


class SkillGapService:

    def analyze_gap(self, user_id, role):

        user = User.query.get(user_id)

        if not user or not user.normalized_skills:
            return {"error": "User has no skills"}

        user_skills = {
            s.strip().lower()
            for s in user.normalized_skills.split(",")
            if s.strip()
        }

        jobs = JobPosting.query.filter(
            JobPosting.role.ilike(f"%{role}%")
        ).all()

        required_skills = set()

        for job in jobs:
            if job.normalized_skills:
                required_skills.update(
                    s.strip().lower()
                    for s in job.normalized_skills.split(",")
                    if s.strip()
                )

        missing = required_skills - user_skills
        matched = user_skills.intersection(required_skills)

        match_percent = 0
        if required_skills:
            match_percent = (len(matched) / len(required_skills)) * 100

        return {
            "match_percent": round(match_percent, 2),
            "missing_skills": list(missing),
            "matched_skills": list(matched)
        }