from backend.models import JobPosting
from collections import Counter
from datetime import datetime


class MarketIntelligenceService:

    # ===============================
    # Top Skills Demand
    # ===============================
    def get_top_skills(self, limit=10):

        jobs = JobPosting.query.all()

        skill_counter = Counter()

        for job in jobs:
            if job.normalized_skills:
                skills = [
                    s.strip().lower()
                    for s in job.normalized_skills.split(",")
                    if s.strip()
                ]
                skill_counter.update(skills)

        top = skill_counter.most_common(limit)

        return {
            "labels": [t[0] for t in top],
            "values": [t[1] for t in top]
        }

    # ===============================
    # Role Demand
    # ===============================
    def get_role_demand(self):

        jobs = JobPosting.query.all()

        role_counter = Counter()

        for job in jobs:
            if job.role:
                role_counter[job.role] += 1

        top = role_counter.most_common(10)

        return {
            "labels": [t[0] for t in top],
            "values": [t[1] for t in top]
        }

    # ===============================
    # Hiring Trend Over Time
    # ===============================
    def get_hiring_trend(self):

        jobs = JobPosting.query.all()

        trend = Counter()

        for job in jobs:
            if job.created_at:
                date = job.created_at.strftime("%d %b")
                trend[date] += 1

        sorted_dates = sorted(trend.keys())

        return {
            "labels": sorted_dates,
            "values": [trend[d] for d in sorted_dates]
        }