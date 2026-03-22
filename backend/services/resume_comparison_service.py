from backend.models import Resume
from collections import defaultdict

class ResumeComparisonService:

    GLOBAL_SKILL_MAP = {
        "Data & AI": {"python","machine learning","deep learning","tensorflow",
                      "pytorch","nlp","data science","pandas","numpy","sql"},
        "Frontend": {"html","css","javascript","react","angular","vue"},
        "Backend": {"node.js","django","flask","spring","express.js",
                    "mongodb","postgresql","mysql","api"},
        "DevOps & Cloud": {"aws","azure","gcp","docker","kubernetes"},
        "Mobile": {"flutter","react native","android","ios"},
        "Cybersecurity": {"cybersecurity","penetration testing","network security"}
    }

    def extract_skills(self, resume):
        if not resume.normalized_skills:
            return []
        return list(set([
            s.strip().lower()
            for s in resume.normalized_skills.split(",")
            if s.strip()
        ]))

    def compute_category_scores(self, skills):
        scores = {}
        for category, skillset in self.GLOBAL_SKILL_MAP.items():
            scores[category] = len(set(skills) & skillset)
        return scores

    def compute_ats(self, skills):
        keyword_component = min(40, len(skills) * 3)
        diversity_component = min(30, len(set(skills)) * 2)
        depth_component = min(30, len(skills) // 2)
        return min(100, keyword_component + diversity_component + depth_component)

    def compare(self, resume_a_id, resume_b_id):

        resume_a = Resume.query.get(resume_a_id)
        resume_b = Resume.query.get(resume_b_id)

        if not resume_a or not resume_b:
            return {"error": "Invalid resume IDs"}

        skills_a = set(self.extract_skills(resume_a))
        skills_b = set(self.extract_skills(resume_b))

        intersection = skills_a & skills_b
        union = skills_a | skills_b
        overlap = round((len(intersection) / len(union)) * 100, 2) if union else 0

        unique_a = list(skills_a - skills_b)
        unique_b = list(skills_b - skills_a)

        cat_a = self.compute_category_scores(skills_a)
        cat_b = self.compute_category_scores(skills_b)

        ats_a = self.compute_ats(skills_a)
        ats_b = self.compute_ats(skills_b)

        best_a = max(cat_a, key=cat_a.get)
        best_b = max(cat_b, key=cat_b.get)

        demand_a = sum(cat_a.values()) * 8
        demand_b = sum(cat_b.values()) * 8

        competitiveness_gap = abs(ats_a - ats_b)

        if ats_a > ats_b:
            verdict = f"{resume_a.filename} is {competitiveness_gap}% more competitive in 2026 AI market."
        elif ats_b > ats_a:
            verdict = f"{resume_b.filename} is {competitiveness_gap}% more competitive in 2026 AI market."
        else:
            verdict = "Both resumes are equally competitive."

        return {
            "overlap": overlap,
            "unique_a": unique_a,
            "unique_b": unique_b,
            "category_a": cat_a,
            "category_b": cat_b,
            "ats_a": ats_a,
            "ats_b": ats_b,
            "role_a": best_a,
            "role_b": best_b,
            "demand_a": demand_a,
            "demand_b": demand_b,
            "verdict": verdict,
            "resume_a_name": resume_a.filename,
            "resume_b_name": resume_b.filename
        }