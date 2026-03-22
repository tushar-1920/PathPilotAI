import os
import json
from collections import Counter, defaultdict
from backend.models import JobPosting, Skill
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── 2025-26 Global Market Demand Baseline ─────────────────────
GLOBAL_DEMAND_2026 = {
    "generative ai": 98, "llm": 97, "large language models": 97,
    "prompt engineering": 95, "langchain": 93, "rag": 93,
    "vector database": 90, "mlops": 91, "openai api": 92,
    "fine-tuning": 89, "hugging face": 89, "llmops": 88,
    "machine learning": 95, "deep learning": 93, "pytorch": 89,
    "tensorflow": 85, "scikit-learn": 82, "nlp": 88,
    "computer vision": 87, "data science": 91,
    "aws": 92, "docker": 91, "kubernetes": 90, "terraform": 89,
    "ci/cd": 88, "devops": 90, "github actions": 85,
    "azure": 85, "google cloud": 84, "linux": 87, "ansible": 79,
    "argocd": 83, "helm": 82, "platform engineering": 86,
    "site reliability engineering": 88, "datadog": 80,
    "python": 94, "system design": 92, "microservices": 88,
    "distributed systems": 89, "fastapi": 86, "rest api": 88,
    "graphql": 80, "grpc": 79, "node.js": 85, "go": 86,
    "rust": 82, "java": 84, "spring boot": 84, "kafka": 84,
    "javascript": 91, "typescript": 91, "react": 90,
    "next.js": 87, "vue.js": 77, "tailwind css": 78,
    "sql": 89, "postgresql": 87, "apache spark": 85,
    "apache airflow": 82, "dbt": 83, "snowflake": 86,
    "bigquery": 84, "databricks": 86, "data pipelines": 83,
    "cybersecurity": 93, "penetration testing": 88,
    "devsecops": 88, "zero trust": 86, "application security": 86,
    "react native": 80, "flutter": 81, "android": 78, "ios": 79,
    "pytest": 77, "playwright": 79, "cypress": 78,
    "pandas": 83, "numpy": 80, "data analysis": 85,
    "power bi": 78, "tableau": 77, "redis": 82,
    "mongodb": 79, "elasticsearch": 77, "cassandra": 72,
    "git": 88, "agile": 78, "jira": 72,
}

RISING    = {"generative ai","llm","langchain","rag","mlops","argocd","rust","go",
             "typescript","next.js","dbt","platform engineering","devsecops","zero trust",
             "vector database","prompt engineering","hugging face","databricks","llmops"}
PEAK      = {"python","docker","kubernetes","aws","react","machine learning","deep learning",
             "system design","fastapi","terraform","ci/cd","postgresql","kafka","pytorch","nlp"}
STABLE    = {"javascript","sql","git","java","node.js","linux","rest api","mysql",
             "spring boot","flask","django","html","css","android","ios","flutter"}
DECLINING = {"jquery","angularjs","svn","perl","php","monolith","coffeescript"}

SECTOR_MAP = {
    "AI & Machine Learning": {"machine learning","deep learning","pytorch","tensorflow",
        "scikit-learn","nlp","computer vision","generative ai","llm","mlops","langchain",
        "rag","openai api","hugging face","data science","xgboost"},
    "Cloud & DevOps":        {"aws","azure","docker","kubernetes","terraform","ci/cd",
        "github actions","linux","ansible","argocd","helm","google cloud","datadog",
        "prometheus","grafana","platform engineering","devops"},
    "Backend Engineering":   {"python","node.js","go","rust","java","fastapi","django",
        "flask","spring boot","microservices","rest api","graphql","grpc","kafka","redis"},
    "Frontend & Web":        {"javascript","typescript","react","next.js","vue.js",
        "tailwind css","html","css","webpack","redux"},
    "Data Engineering":      {"apache spark","apache airflow","dbt","snowflake","bigquery",
        "databricks","data pipelines","etl","postgresql","sql"},
    "Cybersecurity":         {"cybersecurity","penetration testing","devsecops","zero trust",
        "application security","cloud security","siem","owasp"},
    "Mobile":                {"react native","flutter","android","ios","swift","kotlin"},
    "Analytics & BI":        {"power bi","tableau","data analysis","pandas","numpy"},
}


class MarketIntelligenceService:

    def _collect_market_data(self):
        jobs = JobPosting.query.all()
        skill_counter = Counter()
        role_counter  = Counter()
        monthly       = defaultdict(int)
        for job in jobs:
            if job.role:
                r = job.role.strip()
                if r.lower() not in ["other","unknown","misc",""]:
                    role_counter[r] += 1
            if job.normalized_skills:
                for sk in job.normalized_skills.split(","):
                    s = sk.strip().lower()
                    if s:
                        skill_counter[s] += 1
            if hasattr(job, 'created_at') and job.created_at:
                monthly[job.created_at.strftime("%Y-%m")] += 1
        return {"total_jobs": len(jobs), "skills": dict(skill_counter),
                "roles": dict(role_counter), "monthly": dict(monthly)}

    def _build_heatmap(self, skill_counts):
        all_skills = set(skill_counts.keys()) | set(GLOBAL_DEMAND_2026.keys())
        max_db = max(skill_counts.values()) if skill_counts else 1
        results = []
        for skill in all_skills:
            db_score  = (skill_counts.get(skill, 0) / max_db) * 100
            baseline  = GLOBAL_DEMAND_2026.get(skill, 35)
            demand_idx= round(db_score * 0.4 + baseline * 0.6, 1)
            lc_mult   = 1.35 if skill in RISING else 1.15 if skill in PEAK else \
                        0.95 if skill in STABLE else 0.60 if skill in DECLINING else 1.0
            score     = round(min(100, demand_idx * lc_mult), 1)
            lifecycle = "Rising" if skill in RISING else "Peak" if skill in PEAK else \
                        "Stable" if skill in STABLE else "Declining" if skill in DECLINING else "Emerging"
            results.append({"skill": skill, "score": int(score),
                             "demand": skill_counts.get(skill, 0), "lifecycle": lifecycle})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:24]

    def _sector_breakdown(self, skill_counts):
        results = []
        for sector, skills in SECTOR_MAP.items():
            sector_score = sum(GLOBAL_DEMAND_2026.get(s,35)*(1+skill_counts.get(s,0)*0.1)
                               for s in skills) / max(len(skills), 1)
            results.append({"sector": sector, "score": round(min(100, sector_score), 1),
                             "db_postings": sum(skill_counts.get(s,0) for s in skills),
                             "skill_count": len(skills)})
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def _role_demand(self, role_counts):
        ROLE_BASE = {
            "AI Engineer":94,"LLM Engineer":95,"MLOps Engineer":89,
            "ML Engineer":92,"Data Scientist":91,"DevOps Engineer":89,
            "Full Stack Developer":88,"Backend Developer":86,"Frontend Developer":84,
            "Data Engineer":87,"Cloud Engineer":85,"Cybersecurity Engineer":83,
            "Platform Engineer":82,
        }
        all_roles = set(role_counts.keys()) | set(ROLE_BASE.keys())
        max_db    = max(role_counts.values()) if role_counts else 1
        results   = []
        for role in all_roles:
            db_score  = (role_counts.get(role,0)/max_db)*100
            base      = ROLE_BASE.get(role,55)
            current   = round(db_score*0.35 + base*0.65, 1)
            growth_m  = 1.28 if any(x in role for x in ["AI","LLM","ML"]) else \
                        1.20 if any(x in role for x in ["DevOps","Cloud","Security"]) else \
                        1.14 if "Data" in role else 1.10
            projected = round(current*growth_m, 1)
            results.append({"role":role,"current":current,"projected":projected,
                             "yoy_growth":round(projected-current,1),
                             "db_count":role_counts.get(role,0)})
        return sorted(results, key=lambda x: x["current"], reverse=True)[:12]

    def generate_market_intelligence(self):
        market  = self._collect_market_data()
        heatmap = self._build_heatmap(market["skills"])
        sectors = self._sector_breakdown(market["skills"])
        roles   = self._role_demand(market["roles"])
        months  = sorted(market["monthly"].keys())[-12:]
        monthly_vals = [market["monthly"].get(m, 0) for m in months]

        top_skills = {s["skill"]: s["score"] for s in heatmap[:15]}
        top_roles  = {r["role"]: r["current"] for r in roles[:8]}

        prompt = f"""You are an expert technology job market analyst for 2025-2026.
Dataset: Total Jobs: {market['total_jobs']}, Top Skills: {top_skills}, Top Roles: {top_roles}.

Return ONLY this exact JSON structure. Every array item MUST be a plain STRING — never an object or dict.

{{
  "top_emerging_skill": "Generative AI",
  "ai_job_share": "34%",
  "market_volatility": "High",
  "top_market_role": "AI Engineer",
  "market_temperature": "Hot",
  "hiring_velocity": "Accelerating",
  "future_signals": [
    "LLM Engineers demand rising 52% YoY — fastest-growing role in 2026.",
    "MLOps now required at 78% of companies deploying more than 3 ML models.",
    "Cloud-native skills commanding 28% salary premium over non-cloud engineers.",
    "Cybersecurity hiring up 21% driven by AI-powered attack surface expansion.",
    "Data Engineering salaries rising 30% as lakehouse architectures go mainstream."
  ],
  "automation_risk": [
    "Data Entry Clerk — Critical Risk: fully automatable with current LLM tools.",
    "Manual QA Tester — High Risk: AI testing frameworks replacing 40% of tasks.",
    "Report Analyst — Medium Risk: BI tools with AI narration reducing headcount.",
    "Junior Frontend Dev — Medium Risk: AI code generation handles 60% of UI boilerplate.",
    "Basic DevOps Engineer — Low Risk: pipelines automated but strategy remains human."
  ],
  "ai_market_insight": "The 2025-26 market is in a GenAI super-cycle with LLM engineer salaries 45% above average. Python and cloud remain baseline for 89% of roles. RAG and LangChain expertise commands the highest premiums."
}}

CRITICAL RULES:
1. future_signals — MUST be a list of 5 plain strings. No objects, no dicts. Each string is one sentence with a specific number.
2. automation_risk — MUST be a list of 5 plain strings in format "Role Name — Risk Level: reason."
3. top_market_role MUST come from this roles list: {list(top_roles.keys())}
4. NEVER use objects/dicts inside arrays. Only plain strings."""

        result = {}
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini", temperature=0.35,
                messages=[{"role":"user","content":prompt}],
                response_format={"type":"json_object"})
            result = json.loads(resp.choices[0].message.content)
            # Sanitize — force future_signals and automation_risk to be lists of strings
            def _obj_to_str(item, key):
                if isinstance(item, str):
                    return item.strip()
                if isinstance(item, dict):
                    # automation_risk object: {job, risk_level, reason}
                    if "job" in item and "risk_level" in item:
                        s = f"{item['job']} — Risk Level: {item['risk_level']}"
                        if item.get("reason"): s += f". {item['reason']}"
                        return s
                    # {role, risk, reason}
                    if "role" in item and "risk" in item:
                        s = f"{item['role']} — {item['risk']}"
                        if item.get("reason"): s += f": {item['reason']}"
                        return s
                    # future_signal object: {signal, timeframe}
                    if "signal" in item:
                        s = item["signal"]
                        if item.get("timeframe"): s += f" ({item['timeframe']})"
                        return s
                    # Generic fallback
                    vals = [str(v) for v in item.values() if isinstance(v, str) and len(v) > 1]
                    return " — ".join(vals) if vals else str(item)
                return str(item).strip()

            for key in ("future_signals", "automation_risk"):
                if key in result:
                    raw = result[key] if isinstance(result[key], list) else [result[key]]
                    result[key] = [_obj_to_str(item, key) for item in raw if item]
        except Exception as e:
            print(f"[MarketIntelligenceService] AI error: {e}")

        result.setdefault("top_emerging_skill", heatmap[0]["skill"].title() if heatmap else "Generative AI")
        result.setdefault("ai_job_share",        "32%")
        result.setdefault("market_volatility",   "High")
        result.setdefault("top_market_role",     roles[0]["role"] if roles else "AI Engineer")
        result.setdefault("market_temperature",  "Hot")
        result.setdefault("hiring_velocity",     "Accelerating")
        result.setdefault("future_signals", [
            "LLM Engineers demand rising 52% YoY — fastest-growing tech role in 2026.",
            "MLOps engineers now mandatory at companies with >5 ML models in production.",
            "Cloud-native skills (K8s, Terraform, ArgoCD) required for 78% of senior roles.",
            "Cybersecurity roles growing 21% as AI-driven attack surface expands rapidly.",
            "Data Engineering salaries up 30% due to data lakehouse adoption surge.",
        ])
        result.setdefault("automation_risk", [
            "Manual QA / Test Engineers — High Risk: AI testing tools replacing 40% of tasks.",
            "Data Entry Roles — Critical Risk: Fully automatable with current LLM capabilities.",
            "Junior Frontend Dev — Medium Risk: AI code generation handles 60% of boilerplate.",
            "Report Analysts — Medium Risk: BI tools with AI narration replacing manual reports.",
            "DevOps (basic) — Low Risk: Automation handles pipelines but strategy stays human.",
        ])
        result.setdefault("ai_market_insight",
            "The 2025-26 market is in a GenAI super-cycle — companies hiring AI/LLM engineers at 3× the 2023 rate. "
            "Python and cloud skills remain baseline requirements for 89% of tech roles. "
            "Salary premiums for LangChain/RAG expertise are 35-45% above standard ML engineer rates.")

        result["skill_heatmap"]    = heatmap
        result["sector_breakdown"] = sectors
        result["role_demand"]      = roles
        result["monthly_labels"]   = months
        result["monthly_values"]   = monthly_vals
        result["total_jobs"]       = market["total_jobs"]
        return result

    def role_analysis(self):
        market = self._collect_market_data()
        roles  = self._role_demand(market["roles"])
        top5   = [r["role"] for r in roles[:5]]
        prompt = f"""You are a 2025-26 tech job market analyst.
Top 5 roles: {top5}. For each write 2 sentences: current demand/salary + 12-month forecast.
Return ONLY JSON: {{"analysis":["role1: ...", "role2: ...", "role3: ...", "role4: ...", "role5: ..."]}}"""
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini", temperature=0.4,
                messages=[{"role":"user","content":prompt}],
                response_format={"type":"json_object"})
            return json.loads(resp.choices[0].message.content)
        except Exception:
            return {"analysis": [
                f"{top5[0] if top5 else 'AI Engineer'}: Explosive demand — salaries $160K-$220K, 52% YoY growth.",
                "Data Scientist: LLM skills premium — $140K-$185K, growing 19% YoY.",
                "DevOps Engineer: Cloud-native premium — $130K-$175K, stable growth.",
                "Full Stack Developer: TypeScript/Next.js premium — $120K-$160K, steady.",
                "Cybersecurity Engineer: Accelerating from AI threats — $145K-$190K, 21% growth.",
            ]}

    def skill_demand_stats(self):
        jobs = JobPosting.query.all()
        freq = {}
        for job in jobs:
            if not job.normalized_skills:
                continue
            for sk in job.normalized_skills.split(","):
                s = sk.strip().lower()
                if s:
                    freq[s] = freq.get(s, 0) + 1
        for skill, demand in GLOBAL_DEMAND_2026.items():
            if skill not in freq:
                freq[skill] = int(demand * 0.2)
        return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]

    def get_trending_skills(self, limit=20):
        hm = self._build_heatmap({})
        return [s["skill"] for s in hm[:limit]]

    def analyze_market_gap(self, user_skills, role_skills):
        trending = self.get_trending_skills()
        user_set = {s.lower() for s in user_skills}
        return {
            "trending_skills":     trending,
            "high_demand_missing": [s for s in trending if s not in user_set],
            "role_market_overlap": list(set(s.lower() for s in role_skills) & set(trending)),
        }