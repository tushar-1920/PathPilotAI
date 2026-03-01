from backend.models import UserSkill, Skill
from collections import defaultdict


class CareerIdentityService:

    # Global role templates (can expand later)
    ROLE_TEMPLATES = {
        "Data Scientist": [
            "Python", "Machine Learning", "Deep Learning",
            "Pandas", "NumPy", "Scikit-learn",
            "Data Analysis", "Data Visualization",
            "Statistics", "SQL"
        ],
        "AI Engineer": [
            "Python", "TensorFlow", "PyTorch",
            "Deep Learning", "NLP",
            "Computer Vision", "Transformers"
        ],
        "Frontend Developer": [
            "HTML", "CSS", "JavaScript",
            "React", "Next.js", "Tailwind CSS"
        ],
        "Backend Developer": [
            "Python", "Django", "Flask",
            "Node.js", "REST API",
            "PostgreSQL", "MongoDB"
        ],
        "DevOps Engineer": [
            "Docker", "Kubernetes",
            "AWS", "CI/CD",
            "Linux", "Terraform"
        ]
    }

    def detect_identity(self, user_id):

        user_skills = UserSkill.query.filter_by(user_id=user_id).all()

        user_skill_names = [
            us.skill.name for us in user_skills if us.skill
        ]

        role_scores = defaultdict(int)

        for role, template_skills in self.ROLE_TEMPLATES.items():

            match_count = 0

            for skill in template_skills:
                if skill in user_skill_names:
                    match_count += 1

            score = (match_count / len(template_skills)) * 100
            role_scores[role] = round(score, 2)

        sorted_roles = sorted(
            role_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        primary = sorted_roles[0]
        secondary = sorted_roles[1]

        return {
            "primary_role": primary[0],
            "primary_score": primary[1],
            "secondary_role": secondary[0],
            "secondary_score": secondary[1]
        }