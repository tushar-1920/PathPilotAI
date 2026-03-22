from backend.models import User, JobPosting
from backend.services.global_skill_library import GLOBAL_SKILLS_LOWER, SKILL_ALIASES
from backend.services.skill_metadata import SKILL_METADATA


# ── SKILL IMPORTANCE WEIGHTS ─────────────────────────────────
# Higher = more important in the market right now
SKILL_WEIGHTS = {
    # AI/ML — very high demand
    "Python":                    10,
    "Machine Learning":          10,
    "Deep Learning":              9,
    "TensorFlow":                 8,
    "PyTorch":                    9,
    "Large Language Models":     10,
    "LangChain":                  9,
    "Generative AI":             10,
    "Prompt Engineering":         9,
    "RAG":                        9,
    "Hugging Face":               8,
    "MLOps":                      9,
    "NLP":                        8,
    "Computer Vision":            8,
    "Scikit-learn":               8,
    "OpenAI API":                 9,
    "Vector Database":            8,

    # Cloud / DevOps — very high demand
    "AWS":                       10,
    "Docker":                    10,
    "Kubernetes":                 9,
    "Terraform":                  9,
    "CI/CD":                      9,
    "GitHub Actions":             8,
    "Azure":                      8,
    "Google Cloud":               8,
    "DevOps":                     9,
    "Linux":                      8,

    # Web — high demand
    "JavaScript":                 9,
    "TypeScript":                  9,
    "React":                       9,
    "Node.js":                     8,
    "Next.js":                     8,
    "REST API":                    8,
    "GraphQL":                     7,

    # Backend — high demand
    "FastAPI":                     8,
    "Django":                      7,
    "Flask":                       7,
    "Spring Boot":                 8,
    "Microservices":               8,
    "System Design":               9,
    "Distributed Systems":         9,

    # Data — high demand
    "SQL":                         9,
    "PostgreSQL":                  8,
    "Apache Spark":                8,
    "Apache Kafka":                8,
    "Apache Airflow":              7,
    "dbt":                         7,
    "Snowflake":                   7,
    "BigQuery":                    7,
    "Data Pipelines":              7,
    "Pandas":                      8,
    "NumPy":                       7,

    # Security
    "Cybersecurity":               7,
    "Penetration Testing":         7,
    "Zero Trust":                  7,

    # Testing
    "pytest":                      7,
    "Unit Testing":                7,
    "Selenium":                    6,
    "Playwright":                  7,

    # Git / Tooling
    "Git":                         8,
    "Agile":                       7,
    "Jira":                        6,
}

DEFAULT_WEIGHT = 5  # fallback weight for any skill not in the map


class SkillGapService:

    def _normalize_skill_set(self, skills_raw: list) -> set:
        """Normalize a list of skill strings for robust comparison."""
        normalized = set()
        for s in skills_raw:
            s_clean = s.strip().lower()
            # Check alias map
            if s_clean in SKILL_ALIASES:
                normalized.add(SKILL_ALIASES[s_clean].lower())
            # Check global library
            elif s_clean in GLOBAL_SKILLS_LOWER:
                normalized.add(GLOBAL_SKILLS_LOWER[s_clean].lower())
            else:
                normalized.add(s_clean)
        return normalized

    def _parse_skills_string(self, skills_str: str) -> set:
        """Parse comma-separated skills string from DB."""
        if not skills_str:
            return set()
        raw = [s.strip() for s in skills_str.split(',') if s.strip()]
        return self._normalize_skill_set(raw)

    # ── WEIGHTED SCORE ───────────────────────────────────────
    def _weighted_score(self, user_skills: set, required_skills: set) -> float:
        """Calculate weighted match score (0-100)."""
        if not required_skills:
            return 0.0

        total_weight   = 0
        matched_weight = 0

        for skill in required_skills:
            weight = SKILL_WEIGHTS.get(skill.title(), DEFAULT_WEIGHT)
            # Also try exact match
            for k, v in SKILL_WEIGHTS.items():
                if k.lower() == skill.lower():
                    weight = v
                    break
            total_weight += weight
            if skill in user_skills:
                matched_weight += weight

        if total_weight == 0:
            return 0.0
        return round((matched_weight / total_weight) * 100, 2)

    # ── PRIORITY SCORE FOR MISSING SKILL ────────────────────
    def _priority_score(self, skill: str) -> int:
        """Higher = more urgent to learn."""
        for k, v in SKILL_WEIGHTS.items():
            if k.lower() == skill.lower():
                return v
        return DEFAULT_WEIGHT

    # ──────────────────────────────────────────────────────────
    # FREE VERSION
    # ──────────────────────────────────────────────────────────
    def analyze_gap(self, user_id: int, role: str) -> dict:
        user = User.query.get(user_id)

        if not user or not user.normalized_skills:
            return {"error": "User has no skills. Please upload your resume first."}

        user_skills = self._parse_skills_string(user.normalized_skills)

        jobs = JobPosting.query.filter(
            JobPosting.role.ilike(f"%{role}%")
        ).all()

        required_skills = set()
        for job in jobs:
            if job.normalized_skills:
                required_skills.update(self._parse_skills_string(job.normalized_skills))

        if not required_skills:
            return {
                "error": f"No job postings found for '{role}'. Try a different role name.",
                "role": role,
            }

        missing = required_skills - user_skills
        matched = user_skills.intersection(required_skills)
        match_pct = self._weighted_score(user_skills, required_skills)

        # Sort missing by priority
        missing_sorted = sorted(
            list(missing),
            key=lambda s: self._priority_score(s),
            reverse=True
        )

        return {
            "role":             role,
            "match_percent":    match_pct,
            "missing_skills":   missing_sorted,
            "matched_skills":   sorted(list(matched)),
            "total_required":   len(required_skills),
            "total_matched":    len(matched),
            "total_missing":    len(missing),
        }

    # ──────────────────────────────────────────────────────────
    # PRO VERSION — Advanced Weighted Scoring
    # ──────────────────────────────────────────────────────────
    def analyze_gap_pro(self, user_id: int, role: str) -> dict:
        base = self.analyze_gap(user_id, role)

        if "error" in base:
            return base

        gap_score    = round(100 - base["match_percent"], 2)
        missing      = base["missing_skills"]

        # Prioritized top-5 missing skills
        priority_missing = missing[:5]

        # Bucket missing into urgency tiers
        critical  = [s for s in missing if self._priority_score(s) >= 9]
        important = [s for s in missing if 7 <= self._priority_score(s) < 9]
        nice      = [s for s in missing if self._priority_score(s) < 7]

        # Time-to-fill estimate
        total_weeks = sum(
            SKILL_METADATA.get(s, {}).get('weeks', 2) for s in missing
        )

        # Profile completeness
        profile_score = self._profile_completeness(user_id)

        return {
            "role":                     role,
            "match_percent":            base["match_percent"],
            "gap_score":                gap_score,
            "career_risk_level":        self._risk_level(gap_score),
            "priority_missing_skills":  priority_missing,
            "critical_gaps":            critical,
            "important_gaps":           important,
            "nice_to_have_gaps":        nice,
            "all_missing_skills":       missing,
            "matched_skills":           base["matched_skills"],
            "total_required":           base["total_required"],
            "total_matched":            base["total_matched"],
            "total_missing":            base["total_missing"],
            "estimated_weeks_to_fill":  total_weeks,
            "profile_completeness":     profile_score,
            "recommendation":           self._recommendation(base["match_percent"], critical),
        }

    # ──────────────────────────────────────────────────────────
    # MULTI-ROLE COMPARISON
    # ──────────────────────────────────────────────────────────
    def compare_roles(self, user_id: int, roles: list) -> list:
        """Compare user's fit across multiple roles at once."""
        results = []
        for role in roles:
            base = self.analyze_gap(user_id, role)
            if "error" not in base:
                results.append({
                    "role":         role,
                    "match":        base["match_percent"],
                    "missing":      base["total_missing"],
                    "matched":      base["total_matched"],
                    "risk":         self._risk_level(100 - base["match_percent"]),
                    "top_gaps":     base["missing_skills"][:3],
                })
        # Sort by best match
        return sorted(results, key=lambda x: x["match"], reverse=True)

    # ──────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────
    def _risk_level(self, gap_score: float) -> str:
        if gap_score > 65:   return "High Risk"
        elif gap_score > 40: return "Moderate Risk"
        elif gap_score > 20: return "Low Risk"
        else:                return "Market Ready"

    def _profile_completeness(self, user_id: int) -> int:
        """Score 0-100 for how complete the user's profile is."""
        try:
            user  = User.query.get(user_id)
            score = 0
            if user.normalized_skills:        score += 40
            if user.email:                    score += 15
            if getattr(user, 'bio', None):    score += 15
            if getattr(user, 'linkedin', None): score += 15
            if getattr(user, 'github', None): score += 15
            return score
        except Exception:
            return 0

    def _recommendation(self, match_pct: float, critical_gaps: list) -> str:
        if match_pct >= 80:
            return "You are highly competitive for this role. Focus on polishing your resume and preparing for interviews."
        elif match_pct >= 60:
            if critical_gaps:
                return f"You're a solid candidate. Prioritize learning: {', '.join(critical_gaps[:3])} to become highly competitive."
            return "You're a solid candidate. Strengthen your portfolio with 1-2 strong projects."
        elif match_pct >= 40:
            return f"You need focused upskilling. Start with the critical gaps: {', '.join(critical_gaps[:3])} — these will have the highest ROI."
        else:
            return "This role requires significant skill development. Consider a structured learning plan over 3-6 months before applying."