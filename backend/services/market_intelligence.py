from backend.models import Skill


class MarketIntelligenceEngine:

    # ==========================================
    # Get Trending Skills (Based on frequency)
    # ==========================================
    def get_trending_skills(self, limit=20):

        # For now, return top skills alphabetically
        # Later we can connect to real job data

        skills = Skill.query.limit(limit).all()

        return [skill.name for skill in skills]

    # ==========================================
    # Compare User vs Market
    # ==========================================
    def analyze_market_gap(self, user_skills, role_skills):

        trending_skills = self.get_trending_skills()

        high_demand_missing = [
            skill for skill in trending_skills
            if skill not in user_skills
        ]

        role_market_overlap = list(
            set(role_skills) & set(trending_skills)
        )

        return {
            "trending_skills": trending_skills,
            "high_demand_missing": high_demand_missing,
            "role_market_overlap": role_market_overlap
        }