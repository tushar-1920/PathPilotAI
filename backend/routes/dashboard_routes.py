from flask import Blueprint, jsonify, render_template, session, redirect, request, url_for, current_app
from backend.models import User, Resume
from backend.utils.auth_utils import login_required
from backend.services.elite_scoring_engine import EliteScoringEngine
from backend.services.recommendation_service import RecommendationService
from backend.services.subscription_service import SubscriptionService
from backend.services.stripe_service import StripeService
from datetime import datetime
from collections import Counter

dashboard_routes     = Blueprint("dashboard_routes", __name__)
subscription_service = SubscriptionService()

# ── Shared engine instance ────────────────────────────────────
_elite_engine = EliteScoringEngine()


# ══════════════════════════════════════════════════════════════
#  GLOBAL MARKET DATA  (2025–2026, updated demand + growth)
#  demand = market demand index 0–100
#  growth = YoY growth % in job postings
#  salary = avg USD salary premium index
# ══════════════════════════════════════════════════════════════
MARKET_2026 = {
    # GenAI / LLM
    "generative ai":            {"demand": 98, "growth": 45, "salary": 95},
    "large language models":    {"demand": 97, "growth": 43, "salary": 94},
    "llm":                      {"demand": 97, "growth": 43, "salary": 94},
    "prompt engineering":       {"demand": 95, "growth": 40, "salary": 90},
    "langchain":                {"demand": 93, "growth": 38, "salary": 88},
    "rag":                      {"demand": 93, "growth": 38, "salary": 88},
    "vector database":          {"demand": 90, "growth": 35, "salary": 85},
    "mlops":                    {"demand": 91, "growth": 30, "salary": 87},
    "openai api":               {"demand": 92, "growth": 36, "salary": 86},
    "hugging face":             {"demand": 89, "growth": 32, "salary": 85},
    "fine-tuning":              {"demand": 90, "growth": 33, "salary": 88},
    # Core ML/AI
    "machine learning":         {"demand": 95, "growth": 22, "salary": 92},
    "deep learning":            {"demand": 93, "growth": 20, "salary": 90},
    "pytorch":                  {"demand": 89, "growth": 19, "salary": 88},
    "tensorflow":               {"demand": 85, "growth": 12, "salary": 84},
    "scikit-learn":             {"demand": 82, "growth": 10, "salary": 80},
    "nlp":                      {"demand": 88, "growth": 18, "salary": 86},
    "computer vision":          {"demand": 87, "growth": 17, "salary": 85},
    "data science":             {"demand": 91, "growth": 19, "salary": 89},
    "feature engineering":      {"demand": 80, "growth": 11, "salary": 79},
    "xgboost":                  {"demand": 78, "growth": 9,  "salary": 77},
    # Cloud & DevOps
    "aws":                      {"demand": 92, "growth": 17, "salary": 91},
    "docker":                   {"demand": 91, "growth": 16, "salary": 89},
    "kubernetes":               {"demand": 90, "growth": 22, "salary": 91},
    "terraform":                {"demand": 89, "growth": 20, "salary": 88},
    "ci/cd":                    {"demand": 88, "growth": 18, "salary": 86},
    "devops":                   {"demand": 90, "growth": 17, "salary": 89},
    "github actions":           {"demand": 85, "growth": 21, "salary": 83},
    "argocd":                   {"demand": 83, "growth": 25, "salary": 84},
    "google cloud":             {"demand": 84, "growth": 16, "salary": 83},
    "azure":                    {"demand": 85, "growth": 15, "salary": 83},
    "linux":                    {"demand": 87, "growth": 10, "salary": 84},
    "ansible":                  {"demand": 79, "growth": 11, "salary": 78},
    "prometheus":               {"demand": 78, "growth": 14, "salary": 77},
    "grafana":                  {"demand": 77, "growth": 13, "salary": 76},
    "datadog":                  {"demand": 80, "growth": 16, "salary": 80},
    "helm":                     {"demand": 82, "growth": 18, "salary": 81},
    "platform engineering":     {"demand": 86, "growth": 28, "salary": 87},
    "site reliability engineering": {"demand": 88, "growth": 20, "salary": 90},
    # Backend / Systems
    "python":                   {"demand": 94, "growth": 18, "salary": 90},
    "system design":            {"demand": 92, "growth": 20, "salary": 93},
    "microservices":            {"demand": 88, "growth": 15, "salary": 87},
    "distributed systems":      {"demand": 89, "growth": 17, "salary": 90},
    "fastapi":                  {"demand": 86, "growth": 28, "salary": 85},
    "rest api":                 {"demand": 88, "growth": 12, "salary": 84},
    "graphql":                  {"demand": 80, "growth": 13, "salary": 81},
    "grpc":                     {"demand": 79, "growth": 15, "salary": 80},
    "django":                   {"demand": 78, "growth": 8,  "salary": 77},
    "flask":                    {"demand": 76, "growth": 7,  "salary": 75},
    "node.js":                  {"demand": 85, "growth": 12, "salary": 83},
    "express.js":               {"demand": 78, "growth": 8,  "salary": 77},
    "spring boot":              {"demand": 84, "growth": 11, "salary": 83},
    "java":                     {"demand": 84, "growth": 10, "salary": 83},
    "go":                       {"demand": 86, "growth": 22, "salary": 87},
    "rust":                     {"demand": 82, "growth": 28, "salary": 88},
    "apache kafka":             {"demand": 84, "growth": 16, "salary": 84},
    "redis":                    {"demand": 82, "growth": 12, "salary": 81},
    # Frontend
    "javascript":               {"demand": 91, "growth": 13, "salary": 86},
    "typescript":               {"demand": 91, "growth": 20, "salary": 87},
    "react":                    {"demand": 90, "growth": 15, "salary": 87},
    "next.js":                  {"demand": 87, "growth": 24, "salary": 85},
    "vue.js":                   {"demand": 77, "growth": 10, "salary": 76},
    "angular":                  {"demand": 76, "growth": 7,  "salary": 76},
    "tailwind css":             {"demand": 78, "growth": 20, "salary": 74},
    "html":                     {"demand": 72, "growth": 5,  "salary": 68},
    "css":                      {"demand": 72, "growth": 5,  "salary": 68},
    # Mobile
    "react native":             {"demand": 80, "growth": 12, "salary": 80},
    "flutter":                  {"demand": 81, "growth": 15, "salary": 79},
    "swift":                    {"demand": 80, "growth": 11, "salary": 83},
    "kotlin":                   {"demand": 80, "growth": 12, "salary": 82},
    "android":                  {"demand": 78, "growth": 9,  "salary": 78},
    "ios":                      {"demand": 79, "growth": 10, "salary": 81},
    # Databases
    "sql":                      {"demand": 89, "growth": 11, "salary": 84},
    "postgresql":               {"demand": 87, "growth": 14, "salary": 85},
    "mysql":                    {"demand": 78, "growth": 7,  "salary": 75},
    "mongodb":                  {"demand": 79, "growth": 10, "salary": 77},
    "elasticsearch":            {"demand": 78, "growth": 11, "salary": 79},
    "snowflake":                {"demand": 86, "growth": 22, "salary": 87},
    "bigquery":                 {"demand": 84, "growth": 19, "salary": 85},
    "dynamodb":                 {"demand": 80, "growth": 14, "salary": 81},
    "cassandra":                {"demand": 72, "growth": 6,  "salary": 74},
    # Data Engineering
    "apache spark":             {"demand": 85, "growth": 14, "salary": 87},
    "apache airflow":           {"demand": 82, "growth": 16, "salary": 83},
    "dbt":                      {"demand": 83, "growth": 25, "salary": 84},
    "etl":                      {"demand": 78, "growth": 10, "salary": 78},
    "data pipelines":           {"demand": 83, "growth": 18, "salary": 83},
    "databricks":               {"demand": 86, "growth": 24, "salary": 88},
    "data warehousing":         {"demand": 78, "growth": 10, "salary": 79},
    # Security
    "cybersecurity":            {"demand": 93, "growth": 21, "salary": 91},
    "penetration testing":      {"demand": 88, "growth": 19, "salary": 88},
    "devsecops":                {"demand": 88, "growth": 28, "salary": 89},
    "zero trust":               {"demand": 86, "growth": 25, "salary": 87},
    "application security":     {"demand": 86, "growth": 22, "salary": 87},
    "cloud security":           {"demand": 88, "growth": 22, "salary": 89},
    "ethical hacking":          {"demand": 83, "growth": 17, "salary": 84},
    "network security":         {"demand": 80, "growth": 13, "salary": 80},
    "siem":                     {"demand": 75, "growth": 11, "salary": 76},
    # Analytics / BI
    "data analysis":            {"demand": 85, "growth": 14, "salary": 80},
    "power bi":                 {"demand": 78, "growth": 13, "salary": 76},
    "tableau":                  {"demand": 77, "growth": 11, "salary": 76},
    "data visualization":       {"demand": 78, "growth": 13, "salary": 77},
    "pandas":                   {"demand": 83, "growth": 12, "salary": 80},
    "numpy":                    {"demand": 80, "growth": 10, "salary": 79},
    # Tools
    "git":                      {"demand": 88, "growth": 8,  "salary": 82},
    "agile":                    {"demand": 78, "growth": 7,  "salary": 75},
    "jira":                     {"demand": 72, "growth": 5,  "salary": 70},
    "jupyter notebook":         {"demand": 74, "growth": 7,  "salary": 72},
    # Blockchain
    "solidity":                 {"demand": 74, "growth": 12, "salary": 82},
    "web3":                     {"demand": 73, "growth": 10, "salary": 80},
    "blockchain":               {"demand": 73, "growth": 8,  "salary": 79},
    "smart contracts":          {"demand": 73, "growth": 11, "salary": 81},
    # Testing
    "unit testing":             {"demand": 78, "growth": 9,  "salary": 76},
    "pytest":                   {"demand": 77, "growth": 10, "salary": 75},
    "playwright":               {"demand": 79, "growth": 20, "salary": 77},
    "cypress":                  {"demand": 78, "growth": 17, "salary": 76},
    "selenium":                 {"demand": 72, "growth": 5,  "salary": 71},
    "tdd":                      {"demand": 76, "growth": 8,  "salary": 76},
}

# Global Top 20 Skills 2026 (for trending section)
GLOBAL_TOP_2026 = sorted(
    [{"skill": k.title(), "demand": v["demand"], "growth": v["growth"]}
     for k, v in MARKET_2026.items()],
    key=lambda x: x["demand"], reverse=True
)[:20]

# ── Category Map (mirrors elite engine but used for dashboard breakdown) ──
DASHBOARD_CATEGORY_MAP = {
    "AI / ML / GenAI": {
        "machine learning","deep learning","generative ai","llm","nlp",
        "computer vision","pytorch","tensorflow","scikit-learn","langchain",
        "rag","openai api","mlops","hugging face","prompt engineering",
        "data science","pandas","numpy","xgboost","feature engineering",
    },
    "Cloud / DevOps": {
        "aws","azure","google cloud","gcp","docker","kubernetes","terraform",
        "ansible","jenkins","ci/cd","github actions","argocd","helm","linux",
        "prometheus","grafana","datadog","platform engineering","devops","sre",
        "site reliability engineering","infrastructure as code",
    },
    "Backend / Systems": {
        "python","java","go","rust","node.js","express.js","fastapi","django",
        "flask","spring boot","microservices","rest api","graphql","grpc",
        "system design","distributed systems","redis","apache kafka","scala","c#",
    },
    "Frontend / Web": {
        "javascript","typescript","react","next.js","vue.js","angular","svelte",
        "tailwind css","html","css","redux","webpack","vite","html5","css3",
    },
    "Mobile": {
        "android","ios","flutter","react native","swift","kotlin",
        "swiftui","jetpack compose",
    },
    "Databases / Data Eng": {
        "sql","postgresql","mysql","mongodb","elasticsearch","cassandra",
        "dynamodb","snowflake","bigquery","apache spark","apache airflow",
        "dbt","etl","data pipelines","databricks","data warehousing","redis",
    },
    "Security": {
        "cybersecurity","penetration testing","ethical hacking","zero trust",
        "devsecops","siem","application security","cloud security","owasp",
        "network security","cryptography",
    },
    "Testing / QA": {
        "unit testing","pytest","selenium","playwright","cypress","jest",
        "tdd","bdd","load testing",
    },
    "Analytics / BI": {
        "data analysis","power bi","tableau","data visualization",
        "business intelligence","a/b testing","excel",
    },
}


def _parse_skills(user: User) -> list:
    """Extract normalized skill list from user model."""
    if not user or not user.normalized_skills:
        return []
    return [s.strip() for s in user.normalized_skills.split(",") if s.strip()]


def _tier_label(score: float) -> str:
    if score >= 90: return "Top 5%"
    if score >= 80: return "Elite"
    if score >= 65: return "Competitive"
    if score >= 50: return "Developing"
    if score >= 35: return "Entry Level"
    return "Beginner"


# ══════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════

@dashboard_routes.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html")


# ──────────────────────────────────────────────────────────────
#  MAIN DASHBOARD API  (/api/dashboard)
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/dashboard")
@login_required
def get_dashboard():
    user_id = session.get("user_id")
    user    = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # ── 1. Skills ────────────────────────────────────────────
    resume_skills = _parse_skills(user)
    skills_lower  = {s.lower() for s in resume_skills}

    # ── 2. Elite Scoring Engine ───────────────────────────────
    elite_scores = _elite_engine.compute_score(resume_skills)
    comp_score   = elite_scores["competitive_score"]

    # Override tier with our richer label (engine has its own but we override)
    elite_scores["tier"]       = _tier_label(comp_score)
    elite_scores["tier_color"] = elite_scores.get("tier_color", "#5b6bff")

    # ── 3. ATS Score — realistic, 4 components summing to 100 max ──
    # OLD BUG: ats_core*4 (max 100) + market (max 15) + stack (max 10) = 125 max
    # before the min(100) cap → almost everyone hits 100.
    # FIX: 4 components with strict individual caps that sum to exactly 100.
    n_skills = len(resume_skills)

    # Keyword density (0–40): sweet spot 15–25 skills
    if   n_skills == 0:  kw = 0.0
    elif n_skills <= 5:  kw = n_skills * 3.5             # 0–17.5
    elif n_skills <= 12: kw = 17.5 + (n_skills - 5) * 2.2  # 17.5–33
    elif n_skills <= 22: kw = 33.0 + (n_skills - 12) * 0.7  # 33–40
    elif n_skills <= 35: kw = 40.0
    else:                kw = max(34.0, 40.0 - (n_skills - 35) * 0.3)
    kw = min(40.0, round(kw, 1))

    # Market relevance (0–30): demand quality * quantity factor
    # Prevents 1 high-demand skill (Python) from scoring 30/30 alone
    quality_factor   = elite_scores["market_score"] / 25.0        # 0.0–1.0
    quantity_factor  = min(1.0, n_skills / 15.0)                   # needs 15+ skills for full score
    mkt = round(quality_factor * quantity_factor * 30.0, 1)
    mkt = min(30.0, mkt)

    # Stack completeness (0–20): coherent full stacks score higher
    stk = round((elite_scores["stack_completeness"] / 20.0) * 20.0, 1)
    stk = min(20.0, stk)

    # Domain diversity (0–10): breadth across different domains
    div = round((elite_scores["diversity_score"] / 15.0) * 10.0, 1)
    div = min(10.0, div)

    ats_score = min(100, int(kw + mkt + stk + div))

    # ── 4. Category Breakdown (counts + scores) ───────────────
    category_breakdown = {}
    category_pct       = {}
    for cat, skillset in DASHBOARD_CATEGORY_MAP.items():
        hits = len(skills_lower & skillset)
        category_breakdown[cat] = hits
        category_pct[cat]       = round(min(100, hits / max(len(skillset), 1) * 100), 1)

    best_cat   = max(category_breakdown, key=category_breakdown.get) if resume_skills else "—"
    best_hits  = category_breakdown.get(best_cat, 0)

    # ── 5. Role Fit ───────────────────────────────────────────
    ROLE_MAP = {
        "AI / ML / GenAI":    "AI / ML Engineer",
        "Cloud / DevOps":     "Cloud / DevOps Engineer",
        "Backend / Systems":  "Backend Engineer",
        "Frontend / Web":     "Frontend Developer",
        "Mobile":             "Mobile Developer",
        "Databases / Data Eng": "Data Engineer",
        "Security":           "Cybersecurity Engineer",
        "Testing / QA":       "QA / SDET Engineer",
        "Analytics / BI":     "Data Analyst",
    }

    # Use elite engine's dominant_role if available; else derive from category
    dominant_role = elite_scores.get("dominant_role") or ROLE_MAP.get(best_cat, "Software Engineer")

    # Role fit % = weighted blend of elite score + category depth
    role_fit_pct = min(97, int(
        comp_score * 0.65
        + min(best_hits * 6, 30)
        + (5 if best_hits > 0 else 0)
    ))

    role_fit = {
        "best_role":  dominant_role,
        "percentage": role_fit_pct,
    }

    # ── 6. Market Demand — user's skills vs market ─────────────
    skill_market = []
    for skill in resume_skills:
        data = MARKET_2026.get(skill.lower())
        if data:
            skill_market.append({
                "skill":  skill,
                "demand": data["demand"],
                "growth": data["growth"],
                "salary": data.get("salary", 75),
            })
    # Sort by demand desc, top 12
    skill_market.sort(key=lambda x: x["demand"], reverse=True)
    skill_market = skill_market[:12]

    # ── 7. Readiness Score (overall job readiness) ─────────────
    #  = blended from elite comp score + ats + role fit
    readiness = min(100, int(
        comp_score * 0.5
        + ats_score * 0.3
        + role_fit_pct * 0.2
    ))

    # ── 8. Percentile (realistic, not inflated) ─────────────────
    # Maps score range to percentile with diminishing returns
    if   comp_score >= 90: percentile = 95
    elif comp_score >= 80: percentile = 85
    elif comp_score >= 70: percentile = 72
    elif comp_score >= 60: percentile = 58
    elif comp_score >= 50: percentile = 44
    elif comp_score >= 35: percentile = 28
    else:                  percentile = max(5, int(comp_score * 0.4))

    # ── 9. Skill Volatility (market risk) ─────────────────────
    #  Low volatility = stable skills, High = niche/aging skills
    trending_set    = set(_elite_engine.TRENDING_2026)
    n_trending_held = len(skills_lower & trending_set)
    n_total         = max(len(resume_skills), 1)
    trending_ratio  = n_trending_held / n_total
    volatility      = max(2, int(30 * (1 - trending_ratio)))  # lower is better

    # ── 10. Skill Breakdown per-skill with demand metadata ─────
    skill_breakdown = _elite_engine.get_skill_breakdown(resume_skills)[:15]

    # ── 11. Missing trending skills (quick wins) ───────────────
    missing_trending = sorted(
        [s for s in _elite_engine.TRENDING_2026 if s not in skills_lower],
        key=lambda s: _elite_engine.SKILL_DEMAND.get(s, 5),
        reverse=True
    )[:8]

    # ── 12. Skill History (growth trend) ──────────────────────
    resumes = Resume.query \
        .filter_by(user_id=user_id) \
        .order_by(Resume.uploaded_at.asc()) \
        .all()
    growth_labels = [r.uploaded_at.strftime("%d %b") for r in resumes if r.uploaded_at]
    growth_scores = [r.skill_score or 0 for r in resumes if r.uploaded_at]

    # ── RESPONSE ──────────────────────────────────────────────
    return jsonify({
        # Core scores
        "skill_score":        int(comp_score),
        "ats_score":          ats_score,
        "readiness_score":    readiness,
        "percentile":         percentile,
        "volatility":         volatility,

        # Skills
        "resume_skills":      resume_skills,
        "total_skills":       len(resume_skills),
        "skill_breakdown":    skill_breakdown,
        "missing_trending":   [s.title() for s in missing_trending],

        # Role & Category
        "role_fit":           role_fit,
        "category_breakdown": category_breakdown,
        "category_pct":       category_pct,
        "dominant_role":      dominant_role,

        # Elite engine full output
        "elite":              elite_scores,

        # Market data for user's skills
        "skill_market":       skill_market,

        # Growth history
        "skill_growth": {
            "labels": growth_labels,
            "scores": growth_scores,
        },
    })


# ──────────────────────────────────────────────────────────────
#  SKILL TREND
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/skill-trend")
@login_required
def skill_trend():
    from backend.models import UserSkill
    user_id = session.get("user_id")
    skills  = UserSkill.query.filter_by(user_id=user_id).all()
    skill_names = [us.skill.name for us in skills if us.skill]
    return jsonify(Counter(skill_names))


# ──────────────────────────────────────────────────────────────
#  AI RECOMMENDATIONS
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/recommendations")
@login_required
def recommendations():
    user_id = session.get("user_id")
    service = RecommendationService()
    result  = service.generate_recommendations(user_id)
    return jsonify(result)


# ──────────────────────────────────────────────────────────────
#  SKILL GROWTH HISTORY
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/skill-growth")
@login_required
def skill_growth():
    user_id = session.get("user_id")
    resumes = Resume.query \
        .filter_by(user_id=user_id) \
        .order_by(Resume.uploaded_at.asc()) \
        .all()

    labels = [r.uploaded_at.strftime("%d %b") for r in resumes if r.uploaded_at]
    scores = [r.skill_score or 0 for r in resumes if r.uploaded_at]

    return jsonify({"labels": labels, "scores": scores})


# ──────────────────────────────────────────────────────────────
#  SKILL DEMAND (user's skills vs market)
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/skill-demand")
@login_required
def skill_demand():
    user_id = session.get("user_id")
    user    = User.query.get(user_id)
    if not user or not user.normalized_skills:
        return jsonify([])

    skills = _parse_skills(user)
    results = []
    for skill in skills:
        data = MARKET_2026.get(skill.lower())
        if data:
            results.append({
                "skill":  skill,
                "demand": data["demand"],
                "growth": data["growth"],
                "salary": data.get("salary", 75),
            })

    results.sort(key=lambda x: x["demand"], reverse=True)
    return jsonify(results[:15])


# ──────────────────────────────────────────────────────────────
#  GLOBAL TRENDS (top skills worldwide 2026)
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/global-trends")
@login_required
def global_trends():
    return jsonify(GLOBAL_TOP_2026)


# ──────────────────────────────────────────────────────────────
#  SCORE BREAKDOWN (detailed per-component)
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/score-breakdown")
@login_required
def score_breakdown():
    user_id = session.get("user_id")
    user    = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    skills       = _parse_skills(user)
    elite_scores = _elite_engine.compute_score(skills)
    breakdown    = _elite_engine.get_skill_breakdown(skills)

    return jsonify({
        "score":           elite_scores["competitive_score"],
        "grade":           elite_scores["grade"],
        "tier":            _tier_label(elite_scores["competitive_score"]),
        "tier_color":      elite_scores["tier_color"],
        "components": {
            "ats_core":           {"score": elite_scores["ats_core"],           "max": 25, "label": "ATS & Keyword Density"},
            "market_demand":      {"score": elite_scores["market_score"],       "max": 25, "label": "Market Demand"},
            "stack_completeness": {"score": elite_scores["stack_completeness"], "max": 20, "label": "Stack Completeness"},
            "diversity":          {"score": elite_scores["diversity_score"],    "max": 15, "label": "Domain Diversity"},
            "growth_alignment":   {"score": elite_scores["growth_alignment"],   "max": 15, "label": "2026 Trend Alignment"},
        },
        "skill_breakdown":     breakdown[:20],
        "matched_stacks":      elite_scores["matched_stacks"],
        "trending_matched":    elite_scores["trending_matched"],
        "weak_areas":          elite_scores["weak_areas"],
        "covered_categories":  elite_scores["covered_categories"],
        "improvement_tips":    elite_scores["improvement_tips"],
        "missing_trending":    [
            s.title() for s in _elite_engine.TRENDING_2026
            if s not in {sk.lower() for sk in skills}
        ][:8],
    })


# ──────────────────────────────────────────────────────────────
#  MULTI-SKILL COMPARISON  (benchmark vs peers)
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/market-benchmark")
@login_required
def market_benchmark():
    user_id = session.get("user_id")
    user    = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    skills       = _parse_skills(user)
    elite_scores = _elite_engine.compute_score(skills)
    comp_score   = elite_scores["competitive_score"]

    # Peer benchmark averages (realistic 2026 market data)
    PEER_BENCHMARKS = {
        "Junior Developer (0–2 yrs)":  {"avg_score": 38, "avg_skills": 8,  "avg_ats": 45},
        "Mid-level Developer (2–5 yrs)":{"avg_score": 62, "avg_skills": 18, "avg_ats": 68},
        "Senior Developer (5–8 yrs)":  {"avg_score": 78, "avg_skills": 28, "avg_ats": 82},
        "Staff / Principal (8+ yrs)":  {"avg_score": 89, "avg_skills": 35, "avg_ats": 91},
    }

    # Determine user's peer group
    n_skills = len(skills)
    if   n_skills <= 8:  peer_group = "Junior Developer (0–2 yrs)"
    elif n_skills <= 20: peer_group = "Mid-level Developer (2–5 yrs)"
    elif n_skills <= 32: peer_group = "Senior Developer (5–8 yrs)"
    else:                peer_group = "Staff / Principal (8+ yrs)"

    peer = PEER_BENCHMARKS[peer_group]

    # Gap vs peers
    score_gap  = round(comp_score - peer["avg_score"], 1)
    skills_gap = len(skills) - peer["avg_skills"]

    return jsonify({
        "user_score":     comp_score,
        "user_skills":    n_skills,
        "peer_group":     peer_group,
        "peer_avg_score": peer["avg_score"],
        "peer_avg_skills": peer["avg_skills"],
        "score_vs_peers": score_gap,
        "skills_vs_peers": skills_gap,
        "verdict": (
            "Above your peer group average 🚀" if score_gap > 5 else
            "On par with your peer group ✅"   if score_gap >= -5 else
            "Below peer group average — focus on high-demand skills ⚡"
        ),
        "all_benchmarks": PEER_BENCHMARKS,
    })


# ──────────────────────────────────────────────────────────────
#  USER INFO
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/user-info")
@login_required
def user_info():
    user = User.query.get(session.get("user_id"))
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Auto-downgrade expired subscriptions
    if user.subscription_expiry and user.subscription_expiry < datetime.utcnow():
        user.subscription_plan   = "free"
        user.subscription_status = "active"
        user.subscription_expiry = None

    return jsonify({
        "name":   user.name,
        "plan":   user.subscription_plan,
        "status": user.subscription_status,
        "expiry": user.subscription_expiry.strftime("%Y-%m-%d")
                  if user.subscription_expiry else None,
    })


# ──────────────────────────────────────────────────────────────
#  UPGRADE / BILLING / STRIPE
# ──────────────────────────────────────────────────────────────
@dashboard_routes.route("/api/upgrade-to-pro", methods=["POST"])
@login_required
def upgrade_to_pro():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    subscription_service.upgrade_to_pro(user_id)
    return jsonify({"message": "Upgraded to Pro"})


@dashboard_routes.route("/pricing")
def pricing_page():
    return render_template("pricing.html")


@dashboard_routes.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    data          = request.get_json()
    billing_cycle = data.get("billing_cycle", "monthly")
    stripe_service = StripeService()
    checkout_url  = stripe_service.create_checkout_session(session["user_id"], billing_cycle)
    return jsonify({"url": checkout_url})


@dashboard_routes.route("/stripe-success")
@login_required
def stripe_success():
    session_id = request.args.get("session_id")
    if not session_id:
        return redirect("/pricing")
    StripeService().handle_success(session_id)
    return redirect("/dashboard")


@dashboard_routes.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload    = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        StripeService().handle_webhook(payload, sig_header)
        return "", 200
    except Exception as e:
        print("Webhook error:", e)
        return "", 400


@dashboard_routes.route("/billing-portal")
@login_required
def billing_portal():
    import stripe
    user = User.query.get(session["user_id"])
    if not user.stripe_customer_id:
        return redirect("/pricing")
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    portal = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=url_for("dashboard_routes.dashboard_page", _external=True)
    )
    return redirect(portal.url)


@dashboard_routes.route("/billing")
@login_required
def billing_page():
    return render_template("billing.html")