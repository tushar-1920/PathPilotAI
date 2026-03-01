from backend.models import UserSkill


class RecommendationService:

    def generate_recommendations(self, user_id):

        user_skills = UserSkill.query.filter_by(user_id=user_id).all()

        skill_names = [us.skill.name for us in user_skills if us.skill]

        recommendations = []

        if "Python" in skill_names and "Machine Learning" not in skill_names:
            recommendations.append("Consider learning Machine Learning")

        if "React" in skill_names and "TypeScript" not in skill_names:
            recommendations.append("TypeScript can boost your frontend profile")

        if "Docker" not in skill_names:
            recommendations.append("DevOps skills like Docker increase hiring rate")
        if "SQL" not in skill_names:
            recommendations.append("SQL is essential for data roles")

        if "AWS" not in skill_names:
            recommendations.append("Cloud skills like AWS are in high demand")
        if "NLP" not in skill_names and "Python" in skill_names:
            recommendations.append("NLP is a hot area in AI, consider learning it")
        if "Kubernetes" not in skill_names and "Docker" in skill_names:
            recommendations.append("Kubernetes complements Docker for DevOps roles")
        if "Data Visualization" not in skill_names and "Data Analysis" in skill_names:
            recommendations.append("Data Visualization skills can enhance your data analysis profile")
        if "Deep Learning" not in skill_names and "Machine Learning" in skill_names:
            recommendations.append("Deep Learning is a key skill for advanced AI roles")
        if "Terraform" not in skill_names and "AWS" in skill_names:
            recommendations.append("Infrastructure as Code tools like Terraform are valuable for cloud roles")
        if "GitHub Actions" not in skill_names and "CI/CD" in skill_names:
            recommendations.append("GitHub Actions is a popular CI/CD tool to learn")
        if "Flutter" not in skill_names and "Mobile Development" in skill_names:
            recommendations.append("Flutter is a versatile framework for mobile development")
        if "Next.js" not in skill_names and "React" in skill_names:
            recommendations.append("Next.js can enhance your React skills for full-stack development")
        if "Hugging Face" not in skill_names and "NLP" in skill_names:
            recommendations.append("Hugging Face is a leading platform for NLP models and tools")

        
        return recommendations