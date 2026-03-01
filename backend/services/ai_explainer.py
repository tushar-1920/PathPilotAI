from backend.services.role_definitions import ROLE_DEFINITIONS


class AIExplainer:

    def explain_skill(self, skill, target_role):

        explanation = {}

        explanation["why_important"] = (
            f"{skill} is a core skill required to become a {target_role}. "
            f"It is commonly used in real-world production environments."
        )

        explanation["real_world_usage"] = (
            f"In industry, {skill} is used to build scalable systems, "
            f"optimize performance, and deliver reliable applications."
        )

        explanation["career_impact"] = (
            f"If you skip {skill}, your ability to perform as a "
            f"{target_role} will be limited in interviews and real projects."
        )

        explanation["project_suggestion"] = (
            f"Build a real-world project focusing on {skill} "
            f"to demonstrate practical experience."
        )

        return explanation