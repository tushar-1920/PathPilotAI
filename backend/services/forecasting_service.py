from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
from backend.models import JobPosting, User


# ── 2025-26 Global Market Demand Baseline ────────────────────
# These weights ensure meaningful scores even with sparse DB data
MARKET_DEMAND_BASELINE = {
    "generative ai": 98, "llm": 97, "large language models": 97,
    "prompt engineering": 95, "langchain": 93, "rag": 93,
    "vector database": 90, "mlops": 91, "openai api": 92,
    "machine learning": 95, "deep learning": 93, "pytorch": 89,
    "tensorflow": 85, "scikit-learn": 82, "nlp": 88,
    "computer vision": 87, "data science": 91,
    "aws": 92, "docker": 91, "kubernetes": 90, "terraform": 89,
    "ci/cd": 88, "devops": 90, "github actions": 85, "linux": 87,
    "python": 94, "system design": 92, "microservices": 88,
    "distributed systems": 89, "fastapi": 86, "rest api": 88,
    "node.js": 85, "spring boot": 84, "go": 86, "rust": 82,
    "javascript": 91, "typescript": 91, "react": 90, "next.js": 87,
    "sql": 89, "postgresql": 87, "mongodb": 79, "redis": 82,
    "snowflake": 86, "bigquery": 84, "apache spark": 85, "dbt": 83,
    "apache kafka": 84, "apache airflow": 82,
    "cybersecurity": 93, "penetration testing": 88, "devsecops": 88,
    "android": 78, "ios": 79, "flutter": 81, "react native": 80,
    "data analysis": 85, "power bi": 78, "tableau": 77,
    "git": 88, "agile": 78, "java": 84, "c#": 77, "scala": 76,
}

# Skill lifecycle classification
SKILL_LIFECYCLE = {
    "rising":   {"generative ai","llm","langchain","rag","mlops","argocd",
                 "rust","go","typescript","next.js","dbt","platform engineering",
                 "devsecops","zero trust","vector database","prompt engineering"},
    "peak":     {"python","docker","kubernetes","aws","react","machine learning",
                 "deep learning","system design","fastapi","terraform","ci/cd",
                 "postgresql","apache kafka","apache spark","pytorch","nlp"},
    "stable":   {"javascript","sql","git","java","node.js","linux","agile",
                 "rest api","mysql","mongodb","spring boot","flask","django",
                 "html","css","android","ios","flutter"},
    "declining":{"jquery","angularjs","svn","php","monolith","perl",
                 "cobol","vb.net","flash","coffeescript"},
}


class ForecastingService:

    # ══════════════════════════════════════════════════════════
    #  SKILL MARKET INTELLIGENCE
    # ══════════════════════════════════════════════════════════
    def skill_market_intelligence(self):
        """
        Returns top skills ranked by composite score:
        DB frequency + global baseline + lifecycle multiplier
        """
        skill_counts = defaultdict(int)
        jobs = JobPosting.query.all()

        for job in jobs:
            if job.normalized_skills:
                for skill in job.normalized_skills.split(","):
                    s = skill.strip().lower()
                    if s:
                        skill_counts[s] += 1

        # Merge DB counts with global baseline
        all_skills = set(skill_counts.keys()) | set(MARKET_DEMAND_BASELINE.keys())

        max_count = max(skill_counts.values()) if skill_counts else 1

        results = []
        for skill in all_skills:
            db_count  = skill_counts.get(skill, 0)
            baseline  = MARKET_DEMAND_BASELINE.get(skill, 40)

            # Weighted composite demand score
            db_score   = (db_count / max_count) * 100 if max_count > 0 else 0
            demand_idx = round(db_score * 0.45 + baseline * 0.55, 2)

            # Lifecycle multiplier
            lc_mult = self._lifecycle_multiplier(skill)

            # Momentum = demand velocity (how fast it's growing)
            momentum = round(min(100, demand_idx * lc_mult), 2)

            # Growth percent (annualized estimate)
            if skill in SKILL_LIFECYCLE["rising"]:    growth = round(demand_idx * 0.35, 2)
            elif skill in SKILL_LIFECYCLE["peak"]:    growth = round(demand_idx * 0.18, 2)
            elif skill in SKILL_LIFECYCLE["stable"]:  growth = round(demand_idx * 0.08, 2)
            elif skill in SKILL_LIFECYCLE["declining"]:growth = round(-demand_idx * 0.12, 2)
            else:                                      growth = round(demand_idx * 0.12, 2)

            # Salary premium index
            salary_premium = round(min(100, demand_idx * lc_mult * 0.9), 1)

            # Lifecycle label
            lifecycle = self._get_lifecycle(skill)

            results.append({
                "skill":          skill,
                "demand_index":   demand_idx,
                "momentum_score": momentum,
                "growth_percent": growth,
                "salary_premium": salary_premium,
                "lifecycle":      lifecycle,
                "db_postings":    db_count,
            })

        # Sort by momentum (combines demand + trend)
        return sorted(results, key=lambda x: x["momentum_score"], reverse=True)[:20]

    # ══════════════════════════════════════════════════════════
    #  ROLE DEMAND FORECAST
    # ══════════════════════════════════════════════════════════
    def role_market_forecast(self):
        """Role demand with 12-month projection and growth rate."""
        role_counts = defaultdict(int)
        jobs = JobPosting.query.all()

        for job in jobs:
            if job.role:
                role_counts[job.role.strip()] += 1

        # Supplement with baseline if DB is sparse
        ROLE_BASELINE = {
            "AI Engineer": 95, "ML Engineer": 92, "Data Scientist": 91,
            "DevOps Engineer": 89, "Full Stack Developer": 88,
            "Backend Developer": 86, "Frontend Developer": 84,
            "Data Engineer": 87, "Cloud Engineer": 85,
            "Cybersecurity Engineer": 83, "Platform Engineer": 82,
        }

        all_roles = set(role_counts.keys()) | set(ROLE_BASELINE.keys())
        max_count = max(role_counts.values()) if role_counts else 1

        results = []
        for role in all_roles:
            count    = role_counts.get(role, 0)
            base     = ROLE_BASELINE.get(role, 50)
            db_score = (count / max_count) * 100 if max_count > 0 else 0
            current  = round(db_score * 0.4 + base * 0.6, 1)
            # 12-month projection with role-specific growth
            growth_m = 1.22 if "AI" in role or "ML" in role else \
                       1.18 if "DevOps" in role or "Cloud" in role else \
                       1.14 if "Data" in role else 1.10
            projected = round(current * growth_m, 1)
            yoy_growth = round((projected - current), 1)
            results.append({
                "role":         role,
                "current_demand":  current,
                "projected_demand": projected,
                "yoy_growth":   yoy_growth,
                "db_postings":  count,
            })

        return sorted(results, key=lambda x: x["current_demand"], reverse=True)[:12]

    # ══════════════════════════════════════════════════════════
    #  USER vs MARKET ALIGNMENT
    # ══════════════════════════════════════════════════════════
    def resume_market_alignment(self, user_id):
        user = User.query.get(user_id)
        if not user or not user.normalized_skills:
            return None

        user_skills = {s.strip().lower()
                       for s in user.normalized_skills.split(",") if s.strip()}

        market = self.skill_market_intelligence()
        market_skills = {i["skill"] for i in market}

        matched   = user_skills & market_skills
        coverage  = round(len(matched) / max(len(market_skills), 1) * 100, 2)
        gap       = round(100 - coverage, 2)

        # Weighted alignment (high-demand matches count more)
        alignment_weight = sum(i["demand_index"] for i in market if i["skill"] in user_skills)
        total_weight     = sum(i["demand_index"] for i in market) or 1
        alignment_index  = round((alignment_weight / total_weight) * 100, 2)

        competitive = round(coverage * 0.4 + alignment_index * 0.6, 2)

        # Trending skills user holds
        trending_held = [s for s in user_skills if s in SKILL_LIFECYCLE["rising"]]
        # High-value missing
        missing_high  = sorted(
            [i for i in market if i["skill"] not in user_skills],
            key=lambda x: x["demand_index"], reverse=True
        )[:5]

        return {
            "coverage_percent":   coverage,
            "gap_score":          gap,
            "alignment_index":    alignment_index,
            "competitive_score":  competitive,
            "trending_skills_held": trending_held,
            "top_missing_skills": [m["skill"] for m in missing_high],
        }

    # ══════════════════════════════════════════════════════════
    #  MARKET GROWTH PROJECTION (time series)
    # ══════════════════════════════════════════════════════════
    def market_growth_projection(self):
        monthly_counts = defaultdict(int)
        jobs = JobPosting.query.all()

        for job in jobs:
            if job.created_at:
                month = job.created_at.strftime("%Y-%m")
                monthly_counts[month] += 1

        months = sorted(monthly_counts.keys())
        counts = [monthly_counts[m] for m in months]

        if len(counts) < 2:
            return {"growth_rate": 12.5, "trend": "Growing", "months": [], "values": []}

        x = np.arange(len(counts))
        y = np.array(counts, dtype=float)
        slope = np.polyfit(x, y, 1)[0]
        growth_rate = round((slope / (np.mean(y) + 1)) * 100, 2)
        trend = "Growing" if slope > 0 else "Declining"

        return {
            "growth_rate": growth_rate,
            "trend":       trend,
            "months":      months,
            "values":      counts,
        }

    # ══════════════════════════════════════════════════════════
    #  SKILL SATURATION ANALYSIS
    # ══════════════════════════════════════════════════════════
    def skill_saturation_analysis(self, user_skills: list) -> list:
        """
        For each user skill, returns:
        - market demand score
        - saturation level (how many people have it)
        - opportunity score (demand / saturation → niche advantage)
        """
        market = {i["skill"]: i for i in self.skill_market_intelligence()}
        results = []

        for skill in user_skills:
            s = skill.lower().strip()
            m = market.get(s)
            if not m:
                demand = MARKET_DEMAND_BASELINE.get(s, 40)
                m = {"demand_index": demand, "momentum_score": demand, "growth_percent": 5}

            # Saturation estimate (inverse of lifecycle momentum)
            if s in SKILL_LIFECYCLE["rising"]:    saturation = 25
            elif s in SKILL_LIFECYCLE["peak"]:    saturation = 70
            elif s in SKILL_LIFECYCLE["stable"]:  saturation = 85
            elif s in SKILL_LIFECYCLE["declining"]:saturation = 45
            else:                                  saturation = 55

            opportunity = round(min(100, m["demand_index"] / max(saturation, 1) * 60), 1)

            results.append({
                "skill":       skill,
                "demand":      m["demand_index"],
                "saturation":  saturation,
                "opportunity": opportunity,
                "lifecycle":   self._get_lifecycle(s),
            })

        return sorted(results, key=lambda x: x["opportunity"], reverse=True)

    # ══════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════
    def _lifecycle_multiplier(self, skill: str) -> float:
        if skill in SKILL_LIFECYCLE["rising"]:    return 1.35
        if skill in SKILL_LIFECYCLE["peak"]:      return 1.15
        if skill in SKILL_LIFECYCLE["stable"]:    return 0.95
        if skill in SKILL_LIFECYCLE["declining"]: return 0.60
        return 1.00

    def _get_lifecycle(self, skill: str) -> str:
        if skill in SKILL_LIFECYCLE["rising"]:    return "Rising"
        if skill in SKILL_LIFECYCLE["peak"]:      return "Peak Demand"
        if skill in SKILL_LIFECYCLE["stable"]:    return "Stable"
        if skill in SKILL_LIFECYCLE["declining"]: return "Declining"
        return "Emerging"