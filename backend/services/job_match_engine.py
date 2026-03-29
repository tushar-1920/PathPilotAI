import os, re, json
from openai import OpenAI
from backend.models import JobPosting, User
from backend.extensions import db
from backend.services.global_skill_library import GLOBAL_SKILLS_LOWER, SKILL_ALIASES

# ── OpenAI client (lazy init) ──────────────────────────────────
_client = None
def _get_client():
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        _client = OpenAI(api_key=key)
    return _client


class JobMatchEngine:

    # ══════════════════════════════════════════════════════════
    #  SKILL NORMALIZER  — uses your 1000+ global library
    # ══════════════════════════════════════════════════════════
    def _normalize(self, skill: str) -> str:
        """Map raw skill string → canonical name from global library."""
        s = skill.strip().lower()
        # 1. direct alias lookup
        if s in SKILL_ALIASES:
            return SKILL_ALIASES[s]
        # 2. exact lowercase match in global library
        if s in GLOBAL_SKILLS_LOWER:
            return GLOBAL_SKILLS_LOWER[s]
        # 3. return title-cased original as fallback
        return skill.strip().title()

    def _normalize_set(self, skills: list) -> set:
        return {self._normalize(s).lower() for s in skills if s.strip()}

    # ══════════════════════════════════════════════════════════
    #  AI-POWERED SKILL EXTRACTION  (replaces dumb regex)
    # ══════════════════════════════════════════════════════════
    def extract_job_skills(self, description: str) -> list:
        """
        Use GPT to extract ALL skills from a job description —
        technical, domain, tools, frameworks, soft skills, standards.
        Falls back to regex on API failure.
        """
        if not description or not description.strip():
            return []

        prompt = f"""Extract every skill, technology, tool, framework, programming language, 
domain knowledge, standard, or qualification mentioned in this job description.

Include things like: OOP, REST, HTTP, JSON, XML, SOA, MuleSoft, Salesforce, APIs, 
CGPA requirements turned into skills, communication skills, Java ecosystem tools, etc.

Job Description:
\"\"\"
{description[:3000]}
\"\"\"

Return ONLY a JSON array of skill strings. No explanation. No markdown. Example:
["Java", "OOP", "REST API", "JSON", "XML", "MuleSoft", "Salesforce", "Communication"]"""

        try:
            client = _get_client()
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,        # low temp = consistent extraction
                max_tokens=600,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content.strip()
            # GPT sometimes wraps in {"skills": [...]}
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                skills = parsed
            elif isinstance(parsed, dict):
                # grab the first list value found
                skills = next((v for v in parsed.values() if isinstance(v, list)), [])
            else:
                skills = []

            # Normalize each extracted skill against global library
            normalized = []
            seen = set()
            for s in skills:
                norm = self._normalize(str(s))
                key  = norm.lower()
                if key not in seen and len(key) > 1:
                    seen.add(key)
                    normalized.append(norm)
            return normalized

        except Exception as e:
            print(f"[JobMatchEngine] AI extraction failed, using regex fallback: {e}")
            return self._regex_extract(description)

    # ══════════════════════════════════════════════════════════
    #  REGEX FALLBACK  (used when OpenAI is unavailable)
    # ══════════════════════════════════════════════════════════
    def _regex_extract(self, description: str) -> list:
        """
        Regex-based extraction using the full 1000+ global skill library.
        Much better than the old 50-skill hardcoded set.
        """
        text = description.lower()
        found = []
        seen  = set()

        # Sort longest first to match "machine learning" before "machine"
        sorted_skills = sorted(GLOBAL_SKILLS_LOWER.keys(), key=len, reverse=True)

        for skill_lower in sorted_skills:
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text):
                canonical = GLOBAL_SKILLS_LOWER[skill_lower]
                key = canonical.lower()
                if key not in seen:
                    seen.add(key)
                    found.append(canonical)

        # Also check aliases
        for alias, canonical in SKILL_ALIASES.items():
            pattern = r'\b' + re.escape(alias.lower()) + r'\b'
            if re.search(pattern, text):
                key = canonical.lower()
                if key not in seen:
                    seen.add(key)
                    found.append(canonical)

        return found

    # ══════════════════════════════════════════════════════════
    #  CALCULATE MATCH SCORE
    # ══════════════════════════════════════════════════════════
    def calculate_match_score(self, user_skills: list, job_skills: list,
                               role_match: bool = False) -> int:
        if not job_skills:
            return 0

        user_set = self._normalize_set(user_skills)
        job_set  = self._normalize_set(job_skills)

        if not job_set:
            return 0

        overlap      = user_set & job_set
        skill_score  = (len(overlap) / len(job_set)) * 100
        role_bonus   = 10 if role_match else 0
        return int(min(skill_score + role_bonus, 100))

    # ══════════════════════════════════════════════════════════
    #  FIT LEVEL
    # ══════════════════════════════════════════════════════════
    def get_fit_level(self, score: int) -> str:
        if score >= 80: return "Strong"
        if score >= 60: return "Competitive"
        if score >= 40: return "Medium"
        return "Weak"

    # ══════════════════════════════════════════════════════════
    #  DEEP JOB MATCH  (called by /api/analyze-job)
    # ══════════════════════════════════════════════════════════
    def deep_job_match(self, resume_skills: list, job_description: str) -> dict:
        # Extract skills from job description using AI
        job_skills = self.extract_job_skills(job_description)

        # Normalize both sets for comparison
        resume_set = self._normalize_set(resume_skills)
        job_set    = self._normalize_set(job_skills)

        matched = resume_set & job_set
        missing = job_set - resume_set

        score       = round((len(matched) / len(job_set)) * 100, 1) if job_set else 0
        eligibility = self.get_fit_level(int(score))

        # Return display-friendly canonical names
        # Map back from lowercase to canonical for display
        lower_to_canonical = {s.lower(): s for s in job_skills}
        resume_lower_to_canonical = {}
        for s in resume_skills:
            norm = self._normalize(s)
            resume_lower_to_canonical[norm.lower()] = norm

        matched_display = [
            resume_lower_to_canonical.get(s, s.title()) for s in matched
        ]
        missing_display = [
            lower_to_canonical.get(s, s.title()) for s in missing
        ]

        return {
            "score":          score,
            "matched_skills": sorted(matched_display),
            "missing_skills": sorted(missing_display),
            "job_skills":     job_skills,
            "eligibility":    eligibility,
        }

    # ══════════════════════════════════════════════════════════
    #  GET JOB MATCHES  (called by /api/job-matches — UNCHANGED)
    # ══════════════════════════════════════════════════════════
    def get_job_matches(self, user_id: int, role_filter=None,
                        fit_filter=None, sort="desc") -> list:
        user = User.query.get(user_id)
        if not user:
            return []

        user_skills = []
        if user.normalized_skills:
            user_skills = [s.strip() for s in user.normalized_skills.split(",") if s.strip()]

        query = JobPosting.query
        if role_filter:
            query = query.filter(JobPosting.role.ilike(f"%{role_filter}%"))
        jobs = query.all()

        results = []
        for job in jobs:
            job_skills = []
            if job.normalized_skills:
                job_skills = [s.strip() for s in job.normalized_skills.split(",") if s.strip()]

            role_match = bool(role_filter and job.role and role_filter.lower() in job.role.lower())
            score      = self.calculate_match_score(user_skills, job_skills, role_match)
            fit_level  = self.get_fit_level(score)

            if fit_filter and fit_filter != fit_level:
                continue

            results.append({
                "id":             job.id,
                "title":          job.title,
                "company":        job.company,
                "location":       job.location,
                "skills_required":job.skills_required,
                "match_score":    score,
                "fit_level":      fit_level,
                "source":         job.source,
            })

        return sorted(results, key=lambda x: x["match_score"], reverse=(sort == "desc"))