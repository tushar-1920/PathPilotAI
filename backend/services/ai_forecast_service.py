import os
from openai import OpenAI
from backend.models import Resume, JobPosting
from collections import Counter
from backend.services.forecasting_service import (
    MARKET_DEMAND_BASELINE, SKILL_LIFECYCLE, ForecastingService
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Role definition map for prediction
ROLE_SKILL_MAP = {
    "AI / LLM Engineer":         ["langchain","rag","openai api","vector database","llm","generative ai","mlops","prompt engineering"],
    "Machine Learning Engineer": ["tensorflow","pytorch","deep learning","mlops","model deployment","scikit-learn","feature engineering"],
    "Data Scientist":            ["pandas","numpy","machine learning","data science","scikit-learn","matplotlib","statistics","a/b testing"],
    "Data Engineer":             ["apache spark","apache airflow","dbt","etl","snowflake","bigquery","data pipelines","kafka"],
    "Full Stack Developer":      ["react","node.js","postgresql","rest api","javascript","typescript","docker","mongodb"],
    "Backend Developer":         ["python","flask","django","fastapi","spring boot","rest api","postgresql","redis","microservices"],
    "Frontend Developer":        ["react","next.js","typescript","javascript","tailwind css","html","css","redux"],
    "DevOps / Cloud Engineer":   ["docker","kubernetes","terraform","aws","ci/cd","linux","ansible","prometheus","github actions"],
    "Mobile Developer":          ["flutter","react native","android","ios","swift","kotlin","firebase"],
    "Cybersecurity Engineer":    ["cybersecurity","penetration testing","devsecops","zero trust","siem","owasp","network security"],
    "Data Analyst":              ["sql","power bi","tableau","excel","data analysis","python","data visualization"],
    "Platform Engineer":         ["kubernetes","terraform","argocd","helm","platform engineering","gitops","service mesh"],
    "Blockchain Developer":      ["solidity","ethereum","smart contracts","web3","blockchain","hardhat"],
    "Software Engineer":         ["python","java","git","algorithms","data structures","system design","oop"],
}

# 12-month growth projections by role
ROLE_GROWTH_FORECAST = {
    "AI / LLM Engineer":         {"6m": +28, "12m": +52, "salary_premium": 45},
    "Machine Learning Engineer": {"6m": +18, "12m": +34, "salary_premium": 38},
    "Data Scientist":            {"6m": +15, "12m": +28, "salary_premium": 32},
    "Data Engineer":             {"6m": +16, "12m": +30, "salary_premium": 30},
    "DevOps / Cloud Engineer":   {"6m": +14, "12m": +26, "salary_premium": 28},
    "Full Stack Developer":      {"6m": +12, "12m": +22, "salary_premium": 20},
    "Backend Developer":         {"6m": +11, "12m": +20, "salary_premium": 22},
    "Frontend Developer":        {"6m": +10, "12m": +18, "salary_premium": 18},
    "Mobile Developer":          {"6m": +9,  "12m": +16, "salary_premium": 16},
    "Cybersecurity Engineer":    {"6m": +17, "12m": +32, "salary_premium": 35},
    "Platform Engineer":         {"6m": +15, "12m": +28, "salary_premium": 30},
    "Data Analyst":              {"6m": +8,  "12m": +14, "salary_premium": 14},
    "Software Engineer":         {"6m": +8,  "12m": +15, "salary_premium": 15},
    "Blockchain Developer":      {"6m": +10, "12m": +18, "salary_premium": 22},
}


class AIForecastService:

    def __init__(self):
        self.market_svc = ForecastingService()

    # ══════════════════════════════════════════════════════════
    #  MAIN FORECAST ENGINE
    # ══════════════════════════════════════════════════════════
    def analyze_career_forecast(self, resume_id):
        resume = Resume.query.get(resume_id)
        if not resume or not resume.normalized_skills:
            return self._empty()

        resume_skills = {
            s.strip().lower()
            for s in resume.normalized_skills.split(",") if s.strip()
        }
        resume_skills_list = list(resume_skills)

        # ── Market Counter (DB) ───────────────────────────────
        market_counter = Counter()
        jobs = JobPosting.query.all()
        for job in jobs:
            if job.normalized_skills:
                for sk in job.normalized_skills.split(","):
                    s = sk.strip().lower()
                    if s:
                        market_counter[s] += 1

        # Supplement with global baseline
        for skill, demand in MARKET_DEMAND_BASELINE.items():
            if skill not in market_counter:
                market_counter[skill] = int(demand * 0.3)

        market_skills = set(market_counter.keys())

        # ── Coverage & Alignment ─────────────────────────────
        matched          = resume_skills & market_skills
        coverage         = round(len(matched) / max(len(market_skills), 1) * 100, 2)
        gap              = round(100 - coverage, 2)
        alignment_weight = sum(market_counter[s] for s in matched)
        total_weight     = sum(market_counter.values()) or 1
        alignment        = round((alignment_weight / total_weight) * 100, 2)
        competitive      = round(coverage * 0.35 + alignment * 0.65, 2)

        # ── Role Prediction ──────────────────────────────────
        role = self._predict_role(resume_skills)

        # ── Growth Signals ───────────────────────────────────
        role_fc   = ROLE_GROWTH_FORECAST.get(role, {"6m": 10, "12m": 18, "salary_premium": 15})
        growth_6m = role_fc["6m"]
        growth_12m= role_fc["12m"]
        salary_pm = role_fc["salary_premium"]

        # ── Trending Skills ──────────────────────────────────
        trending_held    = sorted([s for s in resume_skills if s in SKILL_LIFECYCLE["rising"]])
        rising_missing   = sorted([s for s in SKILL_LIFECYCLE["rising"] if s not in resume_skills])[:5]
        high_val_missing = sorted(
            [s for s in market_skills if s not in resume_skills],
            key=lambda s: MARKET_DEMAND_BASELINE.get(s, 0),
            reverse=True
        )[:6]

        # ── Risk Level ───────────────────────────────────────
        risk_score, risk_label = self._compute_risk(competitive, trending_held, gap)

        # ── Skill Saturation Analysis ────────────────────────
        saturation = self.market_svc.skill_saturation_analysis(resume_skills_list)[:6]

        # ── 12-Month Career Projection ───────────────────────
        projection = self._build_projection(competitive, growth_12m)

        # ── AI Narrative ─────────────────────────────────────
        narrative = self._generate_ai_narrative(
            coverage, competitive, role, trending_held,
            high_val_missing, risk_label, growth_12m
        )

        # ── Market Momentum Score ────────────────────────────
        momentum  = min(100, round(competitive * 0.7 + len(trending_held) * 4, 1))
        stability = round(alignment * 0.8, 1)
        growth_rt = round((coverage + alignment) / 2 * 0.9, 1)

        return {
            # Core metrics
            "coverage_percent":     coverage,
            "gap_score":            gap,
            "alignment_index":      alignment,
            "competitive_score":    competitive,
            "risk_score":           risk_score,
            "risk_level":           risk_label,
            "predicted_role":       role,

            # Growth signals
            "growth_score":         min(100, round(competitive * 1.1, 1)),
            "growth_6m":            growth_6m,
            "growth_12m":           growth_12m,
            "salary_premium":       salary_pm,

            # Market pulse
            "momentum_score":       momentum,
            "stability_index":      stability,
            "growth_rate":          growth_rt,

            # Skills intelligence
            "trending_skills_held": trending_held,
            "rising_missing":       rising_missing,
            "high_value_missing":   high_val_missing,
            "skill_saturation":     saturation,

            # AI-generated content
            "ai_narrative":         narrative,

            # Projection data (for chart)
            "projection_labels":    projection["labels"],
            "projection_current":   projection["current"],
            "projection_forecast":  projection["forecast"],
        }

    # ══════════════════════════════════════════════════════════
    #  ROLE PREDICTION
    # ══════════════════════════════════════════════════════════
    def _predict_role(self, skills: set) -> str:
        scores = {}
        for role, role_skills in ROLE_SKILL_MAP.items():
            overlap = len(skills & set(role_skills))
            # Weight by how specific the role skills are
            scores[role] = overlap * (10 / max(len(role_skills), 1))
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "Software Engineer"

    # ══════════════════════════════════════════════════════════
    #  RISK COMPUTATION
    # ══════════════════════════════════════════════════════════
    def _compute_risk(self, competitive: float, trending_held: list, gap: float):
        # Base risk inversely proportional to competitive score
        base_risk = 100 - competitive
        # Trending skills reduce risk
        trend_bonus = min(20, len(trending_held) * 5)
        # High gap increases risk
        gap_penalty = gap * 0.2
        risk_score  = round(max(5, min(95, base_risk + gap_penalty - trend_bonus)), 1)

        if risk_score < 30:   label = "Low"
        elif risk_score < 55: label = "Medium"
        elif risk_score < 75: label = "High"
        else:                 label = "Critical"

        return risk_score, label

    # ══════════════════════════════════════════════════════════
    #  12-MONTH PROJECTION DATA (for chart)
    # ══════════════════════════════════════════════════════════
    def _build_projection(self, competitive: float, growth_12m: int) -> dict:
        from datetime import datetime
        import math

        now    = datetime.now()
        labels = []
        curr   = []
        fore   = []

        base    = competitive
        monthly_growth = growth_12m / 12.0

        for i in range(13):  # now + 12 months
            m = (now.month - 1 + i) % 12 + 1
            y = now.year + (now.month - 1 + i) // 12
            labels.append(f"{datetime(y, m, 1).strftime('%b %Y')}")
            curr.append(round(base, 1))
            fore.append(round(min(100, base + monthly_growth * i * (1 + i * 0.01)), 1))

        return {"labels": labels, "current": curr, "forecast": fore}

    # ══════════════════════════════════════════════════════════
    #  AI NARRATIVE GENERATOR
    # ══════════════════════════════════════════════════════════
    def _generate_ai_narrative(self, coverage, competitive, role,
                                trending_held, missing, risk, growth_12m) -> str:
        trending_str = ", ".join(trending_held[:4]) if trending_held else "none detected"
        missing_str  = ", ".join(missing[:4])        if missing       else "none identified"

        prompt = f"""You are an elite AI career intelligence analyst providing a 2026 market forecast.

Write a 3-paragraph professional career forecast (120-150 words total) for a professional dashboard.

Data:
- Market Coverage: {coverage}%
- Competitive Score: {competitive}%
- Best-fit Role: {role}
- Trending Skills Held: {trending_str}
- High-value Missing Skills: {missing_str}
- Risk Level: {risk}
- 12-Month Growth Forecast: +{growth_12m}%

Paragraph 1: Current market position and competitive standing.
Paragraph 2: Key opportunity areas and highest-ROI skills to add.
Paragraph 3: 12-month strategic outlook and career trajectory.

Tone: Data-driven, direct, motivating. No bullet points. Write as flowing paragraphs."""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an elite career intelligence AI. Be specific and data-driven."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AIForecastService] Narrative error: {e}")
            return (
                f"Your profile shows {coverage}% market coverage with a competitive score of {competitive}%. "
                f"You are best positioned for a {role} role. "
                f"The 12-month market forecast shows +{growth_12m}% growth in your target area. "
                f"To reduce your {risk.lower()} risk level, prioritize adding: {missing_str}."
            )

    # ══════════════════════════════════════════════════════════
    #  EMPTY RESPONSE
    # ══════════════════════════════════════════════════════════
    def _empty(self) -> dict:
        return {
            "coverage_percent": 0, "gap_score": 100,
            "alignment_index": 0, "competitive_score": 0,
            "risk_score": 90, "risk_level": "High",
            "predicted_role": "Unknown",
            "growth_score": 0, "growth_6m": 0, "growth_12m": 0,
            "salary_premium": 0, "momentum_score": 0,
            "stability_index": 0, "growth_rate": 0,
            "trending_skills_held": [], "rising_missing": [],
            "high_value_missing": [], "skill_saturation": [],
            "ai_narrative": "Please upload and analyze a resume first.",
            "projection_labels": [], "projection_current": [], "projection_forecast": [],
        }