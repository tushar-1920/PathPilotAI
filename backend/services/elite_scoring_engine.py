from collections import defaultdict
import math


class EliteScoringEngine:
    """
    Elite Resume Scoring Engine — v3.0
    
    Scoring Components (total = 100 points):
    ─────────────────────────────────────────
    1. ATS Core Score          (0–25 pts)  — skill count, keyword density
    2. Market Demand Score     (0–25 pts)  — how in-demand your skills are
    3. Stack Completeness      (0–20 pts)  — how complete your tech stack is
    4. Diversity Score         (0–15 pts)  — breadth across domains
    5. Growth Alignment        (0–15 pts)  — alignment with 2025-2026 trends
    ─────────────────────────────────────────
    Final = weighted combination, capped at 100
    """

    # ══════════════════════════════════════════════════════════
    #  MARKET DEMAND WEIGHTS (1–10 scale, updated for 2025-26)
    #  10 = extremely hot, 1 = very niche / declining
    # ══════════════════════════════════════════════════════════
    SKILL_DEMAND = {
        # ── AI / ML / LLM ── (hottest market 2025-26)
        "generative ai":              10,
        "large language models":      10,
        "llm":                        10,
        "prompt engineering":         10,
        "langchain":                   9,
        "rag":                         9,
        "vector database":             9,
        "mlops":                       9,
        "machine learning":           10,
        "deep learning":               9,
        "transformers":                9,
        "hugging face":                9,
        "openai api":                  9,
        "fine-tuning":                 9,
        "llmops":                      9,
        "pytorch":                     9,
        "tensorflow":                  8,
        "scikit-learn":                8,
        "nlp":                         8,
        "natural language processing": 8,
        "computer vision":             8,
        "reinforcement learning":      8,
        "xgboost":                     7,
        "lightgbm":                    7,
        "feature engineering":         7,
        "model deployment":            8,
        "keras":                       7,
        "data science":                8,
        "statistical analysis":        7,
        "a/b testing":                 7,
        "bayesian methods":            7,
        "anomaly detection":           7,
        "recommendation systems":      7,
        "time series analysis":        7,
        "pandas":                      8,
        "numpy":                       7,
        "matplotlib":                  6,
        "seaborn":                     6,
        "scipy":                       6,

        # ── Cloud / DevOps / Infra ──
        "aws":                        10,
        "docker":                     10,
        "kubernetes":                  9,
        "terraform":                   9,
        "ci/cd":                       9,
        "devops":                      9,
        "github actions":              8,
        "google cloud":                8,
        "gcp":                         8,
        "azure":                       8,
        "linux":                       8,
        "bash":                        7,
        "ansible":                     7,
        "jenkins":                     7,
        "gitlab ci":                   7,
        "argocd":                      8,
        "helm":                        8,
        "prometheus":                  7,
        "grafana":                     7,
        "datadog":                     7,
        "elk stack":                   6,
        "infrastructure as code":      8,
        "serverless":                  7,
        "site reliability engineering":8,
        "sre":                         8,
        "platform engineering":        8,
        "observability":               7,

        # ── Backend Development ──
        "python":                     10,
        "system design":               9,
        "microservices":               8,
        "distributed systems":         8,
        "rest api":                    8,
        "graphql":                     7,
        "grpc":                        7,
        "fastapi":                     8,
        "django":                      7,
        "flask":                       7,
        "node.js":                     8,
        "express.js":                  7,
        "nestjs":                      7,
        "spring boot":                 8,
        "java":                        8,
        "go":                          8,
        "rust":                        7,
        "scala":                       6,
        "c#":                          7,
        ".net":                        7,
        "php":                         5,
        "ruby":                        5,
        "ruby on rails":               5,
        "event-driven architecture":   7,
        "message queues":              7,
        "redis":                       7,
        "rabbitmq":                    6,
        "apache kafka":                8,
        "caching":                     7,

        # ── Frontend / Full Stack ──
        "javascript":                  9,
        "typescript":                  9,
        "react":                       9,
        "next.js":                     8,
        "vue.js":                      7,
        "angular":                     7,
        "svelte":                      6,
        "tailwind css":                7,
        "html":                        6,
        "css":                         6,
        "html5":                       6,
        "css3":                        6,
        "redux":                       6,
        "graphql client":              7,
        "web performance":             7,
        "webpack":                     6,
        "vite":                        7,

        # ── Mobile ──
        "react native":                7,
        "flutter":                     7,
        "swift":                       7,
        "kotlin":                      7,
        "android":                     7,
        "ios":                         7,
        "swiftui":                     7,
        "jetpack compose":             7,

        # ── Databases ──
        "sql":                         9,
        "postgresql":                  8,
        "mysql":                       7,
        "mongodb":                     7,
        "elasticsearch":               7,
        "cassandra":                   6,
        "dynamodb":                    7,
        "neo4j":                       6,
        "snowflake":                   8,
        "bigquery":                    8,
        "sqlite":                      5,
        "database design":             7,
        "query optimization":          7,

        # ── Data Engineering ──
        "apache spark":                8,
        "apache airflow":              7,
        "apache flink":                7,
        "dbt":                         7,
        "etl":                         7,
        "data pipelines":              8,
        "data warehousing":            7,
        "data lake":                   7,
        "databricks":                  8,

        # ── Data Analytics / BI ──
        "data analysis":               7,
        "power bi":                    7,
        "tableau":                     7,
        "looker":                      6,
        "data visualization":          7,
        "excel":                       5,
        "business intelligence":       6,

        # ── Security ──
        "cybersecurity":               7,
        "penetration testing":         7,
        "ethical hacking":             7,
        "zero trust":                  7,
        "devsecops":                   8,
        "siem":                        6,
        "application security":        7,
        "cloud security":              7,
        "owasp":                       7,
        "network security":            6,
        "cryptography":                6,

        # ── Blockchain / Web3 ──
        "solidity":                    6,
        "ethereum":                    6,
        "smart contracts":             6,
        "web3":                        6,
        "blockchain":                  6,
        "defi":                        5,

        # ── Testing ──
        "pytest":                      7,
        "unit testing":                7,
        "selenium":                    6,
        "playwright":                  7,
        "cypress":                     7,
        "jest":                        7,
        "tdd":                         7,
        "bdd":                         6,
        "load testing":                6,
        "performance testing":         6,

        # ── Tooling ──
        "git":                         8,
        "github":                      7,
        "jira":                        6,
        "agile":                       7,
        "scrum":                       6,
        "figma":                       6,
        "postman":                     6,
        "vs code":                     5,
        "jupyter notebook":            6,
        "google colab":                6,

        # ── Soft / Professional ──
        "communication":               5,
        "leadership":                  6,
        "problem solving":             6,
        "teamwork":                    5,
        "project management":          5,
        "critical thinking":           5,
    }

    DEFAULT_DEMAND = 4  # fallback for any skill not in SKILL_DEMAND

    # ══════════════════════════════════════════════════════════
    #  2025–2026 TRENDING SKILLS (HIGHEST MARKET VELOCITY)
    # ══════════════════════════════════════════════════════════
    TRENDING_2026 = {
        # GenAI / LLM wave
        "generative ai", "large language models", "llm", "prompt engineering",
        "langchain", "rag", "vector database", "openai api", "mlops", "llmops",
        "fine-tuning", "hugging face", "transformers",
        # Cloud-native
        "kubernetes", "terraform", "argocd", "platform engineering",
        "infrastructure as code", "devops", "site reliability engineering",
        # Hot languages & runtimes
        "rust", "go", "typescript",
        # Full-stack modern
        "next.js", "react", "fastapi",
        # Data-at-scale
        "apache spark", "databricks", "snowflake", "dbt", "data pipelines",
        # Security
        "devsecops", "zero trust", "application security",
    }

    # ══════════════════════════════════════════════════════════
    #  DOMAIN CATEGORIES (expanded)
    # ══════════════════════════════════════════════════════════
    CATEGORY_MAP = {
        "AI / ML / GenAI": {
            "machine learning", "deep learning", "generative ai",
            "large language models", "llm", "nlp", "computer vision",
            "reinforcement learning", "pytorch", "tensorflow", "keras",
            "scikit-learn", "xgboost", "lightgbm", "transformers",
            "hugging face", "langchain", "rag", "openai api", "mlops",
            "vector database", "prompt engineering", "feature engineering",
            "data science", "statistical analysis", "pandas", "numpy",
        },
        "Cloud / DevOps / Infra": {
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
            "terraform", "ansible", "jenkins", "ci/cd", "github actions",
            "gitlab ci", "argocd", "helm", "linux", "bash", "serverless",
            "prometheus", "grafana", "datadog", "elk stack", "sre",
            "platform engineering", "observability", "infrastructure as code",
        },
        "Backend / Systems": {
            "python", "java", "go", "rust", "node.js", "express.js",
            "fastapi", "django", "flask", "spring boot", "nestjs",
            "microservices", "rest api", "graphql", "grpc", "system design",
            "distributed systems", "redis", "apache kafka", "rabbitmq",
            "event-driven architecture", "c#", ".net", "scala",
        },
        "Frontend / Web": {
            "javascript", "typescript", "react", "next.js", "vue.js",
            "angular", "svelte", "tailwind css", "html", "css",
            "redux", "webpack", "vite", "web performance", "html5", "css3",
        },
        "Mobile": {
            "android", "ios", "flutter", "react native", "swift", "kotlin",
            "swiftui", "jetpack compose",
        },
        "Databases / Data Eng": {
            "sql", "postgresql", "mysql", "mongodb", "elasticsearch",
            "cassandra", "dynamodb", "snowflake", "bigquery",
            "apache spark", "apache airflow", "dbt", "etl",
            "data pipelines", "data warehousing", "databricks",
            "database design", "query optimization",
        },
        "Security": {
            "cybersecurity", "penetration testing", "ethical hacking",
            "zero trust", "devsecops", "siem", "application security",
            "cloud security", "owasp", "network security", "cryptography",
        },
        "Testing / QA": {
            "unit testing", "pytest", "selenium", "playwright", "cypress",
            "jest", "tdd", "bdd", "load testing", "performance testing",
        },
        "Analytics / BI": {
            "data analysis", "power bi", "tableau", "looker",
            "data visualization", "business intelligence", "excel", "a/b testing",
        },
        "Blockchain / Web3": {
            "solidity", "ethereum", "smart contracts", "web3", "blockchain",
        },
    }

    # ══════════════════════════════════════════════════════════
    #  COMPLETE STACK DEFINITIONS (bonus if user has ≥ threshold)
    # ══════════════════════════════════════════════════════════
    TECH_STACKS = {
        "Full Stack Web": {
            "skills": {"react", "node.js", "postgresql", "rest api", "docker", "git"},
            "threshold": 4, "bonus": 8,
        },
        "AI / ML Engineer": {
            "skills": {"python", "machine learning", "pandas", "numpy", "scikit-learn", "sql"},
            "threshold": 4, "bonus": 10,
        },
        "Data Engineer": {
            "skills": {"python", "apache spark", "sql", "apache airflow", "etl", "docker"},
            "threshold": 4, "bonus": 9,
        },
        "LLM / GenAI Engineer": {
            "skills": {"python", "langchain", "openai api", "rag", "vector database", "fastapi"},
            "threshold": 3, "bonus": 12,
        },
        "Cloud / DevOps": {
            "skills": {"aws", "docker", "kubernetes", "terraform", "ci/cd", "linux"},
            "threshold": 4, "bonus": 10,
        },
        "Mobile Developer": {
            "skills": {"react native", "javascript", "rest api", "git", "firebase"},
            "threshold": 3, "bonus": 7,
        },
        "Cybersecurity": {
            "skills": {"cybersecurity", "penetration testing", "linux", "network security", "python"},
            "threshold": 3, "bonus": 8,
        },
        "Data Scientist": {
            "skills": {"python", "machine learning", "statistics", "pandas", "matplotlib", "sql"},
            "threshold": 4, "bonus": 9,
        },
        "Backend Engineer": {
            "skills": {"python", "postgresql", "rest api", "docker", "git", "system design"},
            "threshold": 4, "bonus": 8,
        },
        "MLOps Engineer": {
            "skills": {"mlops", "docker", "kubernetes", "ci/cd", "python", "aws"},
            "threshold": 3, "bonus": 10,
        },
    }

    # ══════════════════════════════════════════════════════════
    #  MAIN SCORING FUNCTION
    # ══════════════════════════════════════════════════════════
    def compute_score(self, skills: list) -> dict:
        if not skills:
            return self.empty_response()

        skills_lower = [s.lower().strip() for s in skills if s.strip()]
        skills_set   = set(skills_lower)
        n            = len(skills_lower)
        n_unique     = len(skills_set)

        # ── Component 1: ATS Core (0–25) ──────────────────────
        ats_raw = self._ats_core(n, n_unique)

        # ── Component 2: Market Demand (0–25) ─────────────────
        market_raw = self._market_demand(skills_set)

        # ── Component 3: Stack Completeness (0–20) ────────────
        stack_raw, matched_stacks = self._stack_completeness(skills_set)

        # ── Component 4: Diversity (0–15) ─────────────────────
        diversity_raw, covered_categories = self._diversity(skills_set)

        # ── Component 5: Growth Alignment (0–15) ──────────────
        growth_raw, trending_matched = self._growth_alignment(skills_set)

        # ── Weighted Total (normalized to 100) ────────────────
        # Each component already scaled to its max allocation above.
        total = ats_raw + market_raw + stack_raw + diversity_raw + growth_raw
        competitive_score = min(100, round(total, 2))

        # ── Tier & Letter Grade ───────────────────────────────
        tier, grade, tier_color = self._tier(competitive_score)

        # ── Dominant Role Detection ───────────────────────────
        dominant_role = self._detect_dominant_role(skills_set)

        # ── Weak Areas ────────────────────────────────────────
        weak_areas    = self._weak_areas(covered_categories)

        # ── Improvement Tips ──────────────────────────────────
        tips = self._improvement_tips(
            competitive_score, skills_set,
            trending_matched, stack_raw, ats_raw
        )

        return {
            # Final Score
            "competitive_score":   competitive_score,
            "grade":               grade,
            "tier":                tier,
            "tier_color":          tier_color,

            # Components (for UI breakdown bars)
            "ats_core":            round(ats_raw, 2),
            "market_score":        round(market_raw, 2),
            "stack_completeness":  round(stack_raw, 2),
            "diversity_score":     round(diversity_raw, 2),
            "growth_alignment":    round(growth_raw, 2),

            # Context
            "total_skills":        n_unique,
            "dominant_role":       dominant_role,
            "matched_stacks":      matched_stacks,
            "trending_matched":    sorted(list(trending_matched)),
            "weak_areas":          weak_areas,
            "covered_categories":  covered_categories,
            "improvement_tips":    tips,
        }

    # ══════════════════════════════════════════════════════════
    #  COMPONENT CALCULATORS
    # ══════════════════════════════════════════════════════════

    def _ats_core(self, n: int, n_unique: int) -> float:
        """
        ATS Core: rewards skill count (up to a sweet spot) + uniqueness.
        Max = 25 points.
        Sweet spot is 15–30 skills.  <8 = thin resume, >40 = keyword stuffing.
        """
        # Skill count score (0–15)
        if n_unique < 5:
            count_score = n_unique * 1.0
        elif n_unique <= 15:
            count_score = 5 + (n_unique - 5) * 0.9      # 5 → 14
        elif n_unique <= 30:
            count_score = 14 + (n_unique - 15) * 0.067  # 14 → 15
        else:
            count_score = 15 - max(0, (n_unique - 30) * 0.1)  # slight penalty for bloat

        count_score = max(0, min(15, count_score))

        # Uniqueness ratio score (0–10)
        uniqueness_ratio = n_unique / max(n, 1)
        uniqueness_score = uniqueness_ratio * 10
        uniqueness_score = max(0, min(10, uniqueness_score))

        return round(count_score + uniqueness_score, 2)

    def _market_demand(self, skills_set: set) -> float:
        """
        Market Demand: score based on weighted demand of each skill.
        Max = 25 points.
        Uses log-based averaging to prevent a few 10/10 skills from dominating.
        """
        if not skills_set:
            return 0.0

        demand_scores = []
        for skill in skills_set:
            demand = self.SKILL_DEMAND.get(skill, self.DEFAULT_DEMAND)
            demand_scores.append(demand)

        if not demand_scores:
            return 0.0

        # Weighted average (top skills count more)
        demand_scores_sorted = sorted(demand_scores, reverse=True)

        # Give diminishing weight to lower-ranked skills
        weighted_sum = 0.0
        weight_total = 0.0
        for i, score in enumerate(demand_scores_sorted):
            w = 1.0 / math.log(i + 2)     # diminishing log weight
            weighted_sum += score * w
            weight_total += w

        avg_demand = weighted_sum / weight_total if weight_total > 0 else 5.0

        # Scale: avg_demand is 1–10, map to 0–25
        raw = (avg_demand / 10.0) * 25.0
        return min(25.0, round(raw, 2))

    def _stack_completeness(self, skills_set: set) -> tuple:
        """
        Stack Completeness: bonus for having coherent, complete technology stacks.
        Max = 20 points.
        """
        total_bonus    = 0.0
        matched_stacks = []

        for stack_name, config in self.TECH_STACKS.items():
            required  = config["skills"]
            threshold = config["threshold"]
            bonus     = config["bonus"]

            overlap = len(skills_set & required)

            if overlap >= threshold:
                # Partial credit: scale by how complete the stack is
                completeness = overlap / len(required)
                earned       = bonus * completeness
                total_bonus += earned
                matched_stacks.append({
                    "name":         stack_name,
                    "matched":      overlap,
                    "total":        len(required),
                    "completeness": round(completeness * 100, 1),
                })

        return min(20.0, round(total_bonus, 2)), matched_stacks

    def _diversity(self, skills_set: set) -> tuple:
        """
        Diversity: rewards breadth across different tech domains.
        Max = 15 points.
        Penalty for being too narrow (1 category).
        """
        category_hits  = {}
        covered        = []

        for cat, skillset in self.CATEGORY_MAP.items():
            overlap = len(skills_set & skillset)
            if overlap > 0:
                category_hits[cat] = overlap
                covered.append(cat)

        n_covered = len(covered)
        n_total   = len(self.CATEGORY_MAP)

        if n_covered == 0:
            return 0.0, []

        # Base: covered ratio × 15
        base_score = (n_covered / n_total) * 15.0

        # Depth bonus: categories with 3+ skills add a small extra
        depth_bonus = sum(
            min(1.5, hits * 0.3)
            for hits in category_hits.values()
            if hits >= 3
        )

        # Single-category penalty
        if n_covered == 1:
            base_score *= 0.4

        total = min(15.0, base_score + depth_bonus)
        return round(total, 2), covered

    def _growth_alignment(self, skills_set: set) -> tuple:
        """
        Growth Alignment: measures how aligned the skill set is with 2025-26 trends.
        Max = 15 points.
        """
        matched      = skills_set & self.TRENDING_2026
        n_matched    = len(matched)
        n_trending   = len(self.TRENDING_2026)

        if n_matched == 0:
            return 0.0, set()

        # Linear scale with a cap
        raw = (n_matched / n_trending) * 15.0 * 2.5   # 2.5× amplifier so even 2-3 trending gives good score
        return min(15.0, round(raw, 2)), matched

    # ══════════════════════════════════════════════════════════
    #  TIER / GRADE SYSTEM
    # ══════════════════════════════════════════════════════════
    def _tier(self, score: float) -> tuple:
        if score >= 88:   return "Elite",       "S",  "#00e5c8"
        elif score >= 75: return "Strong",       "A",  "#22c55e"
        elif score >= 62: return "Competitive",  "B",  "#5b6bff"
        elif score >= 50: return "Developing",   "C",  "#ffb547"
        elif score >= 35: return "Entry Level",  "D",  "#ff8c42"
        else:             return "Needs Work",   "F",  "#ff5757"

    # ══════════════════════════════════════════════════════════
    #  DOMINANT ROLE DETECTION
    # ══════════════════════════════════════════════════════════
    def _detect_dominant_role(self, skills_set: set) -> str:
        best_role  = "General Developer"
        best_count = 0

        for cat, skillset in self.CATEGORY_MAP.items():
            overlap = len(skills_set & skillset)
            if overlap > best_count:
                best_count = overlap
                best_role  = cat

        # Finer-grained role from stacks
        for stack_name, config in self.TECH_STACKS.items():
            required  = config["skills"]
            threshold = config["threshold"]
            if len(skills_set & required) >= threshold:
                # Pick the stack with highest match ratio
                ratio = len(skills_set & required) / len(required)
                if ratio >= 0.6:
                    return stack_name

        return best_role

    # ══════════════════════════════════════════════════════════
    #  WEAK AREAS
    # ══════════════════════════════════════════════════════════
    def _weak_areas(self, covered_categories: list) -> list:
        all_cats = list(self.CATEGORY_MAP.keys())
        return [c for c in all_cats if c not in covered_categories]

    # ══════════════════════════════════════════════════════════
    #  IMPROVEMENT TIPS
    # ══════════════════════════════════════════════════════════
    def _improvement_tips(
        self,
        score: float,
        skills_set: set,
        trending_matched: set,
        stack_raw: float,
        ats_raw: float,
    ) -> list:
        tips = []

        # ATS tips
        n = len(skills_set)
        if n < 8:
            tips.append("Add more skills — aim for at least 12–15 specific technical skills.")
        elif n < 12:
            tips.append("Expand your skill list to 15–20 targeted skills for better ATS visibility.")

        # Trending tips
        missing_trending = self.TRENDING_2026 - skills_set
        high_value_missing = [
            s for s in missing_trending
            if self.SKILL_DEMAND.get(s, 0) >= 9
        ][:4]
        if high_value_missing:
            tips.append(
                f"Add high-demand 2025–26 skills: {', '.join(t.title() for t in high_value_missing)}."
            )

        # Stack tips
        if stack_raw < 8:
            tips.append(
                "Build a complete tech stack (e.g. Python + SQL + Docker + REST API) "
                "to unlock Stack Completeness bonuses."
            )

        # Cloud tip
        cloud_skills = {"aws", "azure", "gcp", "google cloud", "docker", "kubernetes"}
        if not (skills_set & cloud_skills):
            tips.append("Add at least one Cloud skill (AWS, GCP, or Azure) — it's required for 80%+ of tech jobs.")

        # Gen AI tip
        ai_skills = {"langchain", "openai api", "rag", "vector database", "llm", "generative ai"}
        if not (skills_set & ai_skills):
            tips.append("Add GenAI/LLM skills (LangChain, RAG, OpenAI API) — the fastest-growing demand area in 2025.")

        # DevOps tip
        devops_skills = {"docker", "kubernetes", "ci/cd", "terraform", "github actions"}
        if not (skills_set & devops_skills):
            tips.append("Add DevOps skills (Docker, CI/CD) — essential for any modern tech role.")

        # Score-based tip
        if score < 50:
            tips.append("Focus on 3–4 high-demand areas and build at least one project for each to boost your score significantly.")
        elif score < 70:
            tips.append("You're on the right track. Add 1–2 more high-demand skills and strengthen your weakest domain.")
        elif score >= 88:
            tips.append("Elite profile! Stay updated with new LLM frameworks and contribute to open source to maintain your edge.")

        return tips[:5]   # Return top 5 tips

    # ══════════════════════════════════════════════════════════
    #  STANDALONE COMPONENT METHODS (backward compatible)
    # ══════════════════════════════════════════════════════════

    def compute_ats_core(self, skills: list) -> float:
        skills_lower = [s.lower().strip() for s in skills]
        return self._ats_core(len(skills_lower), len(set(skills_lower)))

    def compute_market_score(self, skills: list) -> float:
        return self._market_demand({s.lower().strip() for s in skills})

    def compute_diversity_score(self, skills: list) -> float:
        score, _ = self._diversity({s.lower().strip() for s in skills})
        return score

    def compute_growth_alignment(self, skills: list) -> float:
        score, _ = self._growth_alignment({s.lower().strip() for s in skills})
        return score

    def compute_stack_completeness(self, skills: list) -> float:
        score, _ = self._stack_completeness({s.lower().strip() for s in skills})
        return score

    # ══════════════════════════════════════════════════════════
    #  DETAILED SKILL BREAKDOWN
    # ══════════════════════════════════════════════════════════
    def get_skill_breakdown(self, skills: list) -> list:
        """
        Returns each skill with its demand score, tier, and trending status.
        Useful for skill-level insight in the UI.
        """
        result = []
        for skill in skills:
            s_lower = skill.lower().strip()
            demand  = self.SKILL_DEMAND.get(s_lower, self.DEFAULT_DEMAND)
            is_trending = s_lower in self.TRENDING_2026

            # Determine category
            category = "Other"
            for cat, skillset in self.CATEGORY_MAP.items():
                if s_lower in skillset:
                    category = cat
                    break

            tier = "Hot" if demand >= 9 else "Strong" if demand >= 7 else "Good" if demand >= 5 else "Niche"
            result.append({
                "skill":       skill,
                "demand":      demand,
                "tier":        tier,
                "category":    category,
                "is_trending": is_trending,
            })

        return sorted(result, key=lambda x: x["demand"], reverse=True)

    # ══════════════════════════════════════════════════════════
    #  EMPTY RESPONSE
    # ══════════════════════════════════════════════════════════
    def empty_response(self) -> dict:
        return {
            "competitive_score":   0,
            "grade":               "F",
            "tier":                "Needs Work",
            "tier_color":          "#ff5757",
            "ats_core":            0,
            "market_score":        0,
            "stack_completeness":  0,
            "diversity_score":     0,
            "growth_alignment":    0,
            "total_skills":        0,
            "dominant_role":       "Unknown",
            "matched_stacks":      [],
            "trending_matched":    [],
            "weak_areas":          list(self.CATEGORY_MAP.keys()),
            "covered_categories":  [],
            "improvement_tips":    ["Upload your resume to get a full skills analysis."],
        }