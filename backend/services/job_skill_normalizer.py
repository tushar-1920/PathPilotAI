from backend.services.skill_metadata import SKILL_METADATA


class JobSkillNormalizer:

    def normalize(self, skills_list):

        normalized = []

        for skill in skills_list:

            s = skill.strip().lower()

            for canonical in SKILL_METADATA.keys():
                if s in canonical.lower():
                    normalized.append(canonical)

            if s not in normalized:
                normalized.append(skill.strip())

        return list(set(normalized))