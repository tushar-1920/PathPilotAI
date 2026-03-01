from backend.models import UserSkill
from backend.services.role_definitions import ROLE_DEFINITIONS
from backend.services.skill_metadata import SKILL_METADATA
from backend.services.ai_explainer import AIExplainer
from backend.services.market_intelligence import MarketIntelligenceEngine


class RoadmapEngine:

    def __init__(self):
        self.explainer = AIExplainer()
        self.market_engine = MarketIntelligenceEngine()

    # ==========================================
    # Get User Skills
    # ==========================================
    def get_user_skill_names(self, user_id):
        user_skills = UserSkill.query.filter_by(user_id=user_id).all()
        return [us.skill.name for us in user_skills]

    # ==========================================
    # Generate Roadmap
    # ==========================================
    def generate_roadmap(self, user_id, target_role):

        if target_role not in ROLE_DEFINITIONS:
            return {"error": "Invalid role selected"}

        role_structure = ROLE_DEFINITIONS[target_role]
        user_skills = self.get_user_skill_names(user_id)

        roadmap = {}
        missing_skills = []

        for stage, skills in role_structure.items():

            roadmap[stage] = []

            for skill in skills:

                if skill in user_skills:
                    roadmap[stage].append({
                        "skill": skill,
                        "status": "Completed"
                    })
                else:
                    roadmap[stage].append({
                        "skill": skill,
                        "status": "Missing"
                    })
                    missing_skills.append(skill)

        return {
            "target_role": target_role,
            "roadmap": roadmap,
            "missing_skills": missing_skills
        }

    # ==========================================
    # Role-Based Score
    # ==========================================
    def calculate_role_based_score(self, user_id, target_role):

        user_skills = self.get_user_skill_names(user_id)
        role_structure = ROLE_DEFINITIONS.get(target_role)

        if not role_structure:
            return 0

        role_skills = []
        for stage in role_structure.values():
            role_skills.extend(stage)

        total_required = len(role_skills)
        if total_required == 0:
            return 0

        matched = len(set(user_skills) & set(role_skills))

        return round((matched / total_required) * 100, 2)

    # ==========================================
    # Detect Best Role
    # ==========================================
    def detect_best_role(self, user_id):

        user_skills = self.get_user_skill_names(user_id)

        best_role = None
        best_score = 0

        for role, structure in ROLE_DEFINITIONS.items():

            role_skills = []
            for stage in structure.values():
                role_skills.extend(stage)

            if not role_skills:
                continue

            matched = len(set(user_skills) & set(role_skills))
            score = matched / len(role_skills)

            if score > best_score:
                best_score = score
                best_role = role

        return best_role, round(best_score * 100, 2)

    # ==========================================
    # Full Intelligent Learning Plan
    # ==========================================
    def generate_learning_plan(self, user_id, target_role):

        roadmap_data = self.generate_roadmap(user_id, target_role)

        if "error" in roadmap_data:
            return roadmap_data

        missing_skills = roadmap_data["missing_skills"]

        # ==========================================
        # Stage Completion Percentage
        # ==========================================
        stage_completion = {}

        for stage, skills in roadmap_data["roadmap"].items():

            total = len(skills)
            completed = len([s for s in skills if s["status"] == "Completed"])

            percentage = round((completed / total) * 100, 2) if total else 0
            stage_completion[stage] = percentage

        # ==========================================
        # Learning Plan with AI Explanation
        # ==========================================
        week_counter = 1
        learning_plan = {}

        for skill in missing_skills:

            metadata = SKILL_METADATA.get(
                skill,
                {"weeks": 2, "difficulty": "Intermediate"}
            )

            duration = metadata["weeks"]

            explanation = self.explainer.explain_skill(skill, target_role)

            week_label = f"Week {week_counter}-{week_counter + duration - 1}"

            learning_plan[week_label] = {
                "skill": skill,
                "difficulty": metadata["difficulty"],
                "duration_weeks": duration,
                "explanation": explanation
            }

            week_counter += duration

        # ==========================================
        # Total Learning Duration
        # ==========================================
        total_duration = sum(
            SKILL_METADATA.get(skill, {"weeks": 2})["weeks"]
            for skill in missing_skills
        )

        # ==========================================
        # Role-Based Score
        # ==========================================
        role_score = self.calculate_role_based_score(user_id, target_role)

        # ==========================================
        # Placement Probability
        # ==========================================
        placement_probability = round(min(role_score * 0.9, 95), 2)

        # ==========================================
        # Market Intelligence Layer
        # ==========================================
        role_structure = ROLE_DEFINITIONS.get(target_role, {})
        role_skills = []

        for stage in role_structure.values():
            role_skills.extend(stage)

        user_skills = self.get_user_skill_names(user_id)

        market_data = self.market_engine.analyze_market_gap(
            user_skills,
            role_skills
        )

        # ==========================================
        # Final Structured Response
        # ==========================================
        return {
            "target_role": target_role,
            "role_score": role_score,
            "placement_probability": placement_probability,
            "total_learning_weeks": total_duration,
            "stage_completion": stage_completion,
            "roadmap": roadmap_data["roadmap"],
            "learning_plan": learning_plan,
            "missing_skills": missing_skills,
            "market_intelligence": market_data
        }