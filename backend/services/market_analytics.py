from backend.models import JobPosting


class MarketAnalytics:

    def skill_demand_stats(self):

        jobs = JobPosting.query.all()

        frequency = {}

        for job in jobs:
            if not job.normalized_skills:
                continue

            for skill in job.normalized_skills.split(","):
                s = skill.strip()
                frequency[s] = frequency.get(s, 0) + 1

        sorted_skills = sorted(
            frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_skills[:20]