from backend.models import UserSkill, Skill, SkillCategory, User

from backend.extensions import db



class SkillScoreEngine:


    # =========================================

    # Calculate Skill Score

    # =========================================

    def calculate_skill_score(self, user_id):


        user_skills = UserSkill.query.filter_by(user_id=user_id).all()

        total_skills = Skill.query.count()


        if total_skills == 0:

            return 0


        score = (len(user_skills) / total_skills) * 100


        return round(score, 2)



    # =========================================

    # Get User Skills

    # =========================================

    def get_user_skills(self, user_id):


        user_skills = UserSkill.query.filter_by(user_id=user_id).all()


        skills = []


        for us in user_skills:

            if us.skill:

                skills.append(us.skill.name)

        return skills



    # =========================================

    # Skill Category Breakdown

    # =========================================

    def get_skill_category_breakdown(self, user_id):


        breakdown = {}


        user_skills = UserSkill.query.filter_by(user_id=user_id).all()


        for us in user_skills:


            if not us.skill:
                continue


            category_name = (

                us.skill.category.name

                if us.skill.category

                else "General"

            )


            if category_name not in breakdown:

                breakdown[category_name] = []


            breakdown[category_name].append(us.skill.name)


        return breakdown



    # =========================================

    # Career Readiness

    # =========================================

    def calculate_career_readiness(self, user_id):


        skill_score = self.calculate_skill_score(user_id)


        # Simple logic (upgrade later with AI)

        readiness = min(skill_score * 1.5, 100)


        return round(readiness, 2)

