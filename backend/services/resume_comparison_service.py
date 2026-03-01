from backend.models import Resume, UserSkill


class ResumeComparisonService:

    def compare_versions(self, user_id):

        resumes = Resume.query\
            .filter_by(user_id=user_id)\
            .order_by(Resume.uploaded_at.desc())\
            .limit(2).all()

        if len(resumes) < 2:
            return {"error": "Upload at least 2 resumes"}

        # Get current skills
        latest_skills = UserSkill.query.filter_by(user_id=user_id).all()
        latest = {us.skill.name for us in latest_skills if us.skill}

        # Fake previous version for now (next phase = store per resume)
        previous = set()

        added = list(latest - previous)
        removed = list(previous - latest)

        return {
            "added": added,
            "removed": removed,
            "total": len(latest)
        }