from collections import defaultdict
from datetime import datetime
from backend.models import JobPosting, User


class ForecastingService:

    def skill_growth_forecast(self):

        skill_frequency = defaultdict(int)

        jobs = JobPosting.query.all()

        for job in jobs:
            if job.normalized_skills:
                for skill in job.normalized_skills.split(","):
                    skill_frequency[skill.strip().lower()] += 1

        sorted_skills = sorted(
            skill_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return [
            {"skill": skill, "demand": count}
            for skill, count in sorted_skills
        ]


    def role_growth_forecast(self):

        role_frequency = defaultdict(int)

        jobs = JobPosting.query.all()

        for job in jobs:
            if job.role:
                role_frequency[job.role] += 1

        sorted_roles = sorted(
            role_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return [
            {"role": role, "demand": count}
            for role, count in sorted_roles
        ]


    def personalized_future_skills(self, user_id):

        user = User.query.get(user_id)

        if not user or not user.normalized_skills:
            return []

        user_skills = set(user.normalized_skills.split(","))

        forecast = self.skill_growth_forecast()

        suggestions = [
            f["skill"]
            for f in forecast
            if f["skill"] not in user_skills
        ]

        return suggestions[:5]