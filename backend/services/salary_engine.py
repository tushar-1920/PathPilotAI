# backend/services/salary_engine.py

SALARY_DATA = {
    "India": {
        "currency": "₹",
        "Fresher": {
            "Full Stack Developer": 450000,
            "Backend Developer": 400000,
            "AI Engineer": 700000
        },
        "Intermediate": {
            "Full Stack Developer": 800000,
            "Backend Developer": 750000,
            "AI Engineer": 1200000
        },
        "Senior": {
            "Full Stack Developer": 1500000,
            "Backend Developer": 1400000,
            "AI Engineer": 2200000
        }
    },
    "USA": {
        "currency": "$",
        "Fresher": {
            "Full Stack Developer": 85000,
            "Backend Developer": 80000,
            "AI Engineer": 110000
        },
        "Intermediate": {
            "Full Stack Developer": 120000,
            "Backend Developer": 115000,
            "AI Engineer": 150000
        },
        "Senior": {
            "Full Stack Developer": 170000,
            "Backend Developer": 160000,
            "AI Engineer": 210000
        }
    }
}

STATE_MULTIPLIER = {
    "Karnataka": 1.25,
    "Maharashtra": 1.20,
    "Delhi": 1.18,
    "Other": 1.0
}


class SalaryEngine:

    def get_base_salary(self, role, experience_level, country, state=None):

        if country not in SALARY_DATA:
            country = "USA"  # Safe fallback

        country_data = SALARY_DATA[country]

        if experience_level not in country_data:
            experience_level = "Fresher"

        level_data = country_data[experience_level]

        if role not in level_data:
            # fallback to first role in that level
            role = list(level_data.keys())[0]

        base_salary = level_data[role]

        # Apply state multiplier only for India
        if country == "India" and state:
            multiplier = STATE_MULTIPLIER.get(state, 1.0)
            base_salary *= multiplier

        return int(base_salary)

    def predict_salary(
        self,
        role,
        experience_level,
        country,
        state=None,
        role_score=0
    ):

        base_salary = self.get_base_salary(
            role,
            experience_level,
            country,
            state
        )

        currency = SALARY_DATA.get(country, {}).get("currency", "$")

        # Small role score multiplier
        skill_multiplier = 1 + (role_score / 200)

        predicted_salary = base_salary * skill_multiplier

        company_tiers = {
            "startup": int(predicted_salary * 0.85),
            "product": int(predicted_salary),
            "mnc": int(predicted_salary * 1.25),
            "faang": int(predicted_salary * 1.6)
        }

        growth_projection = []
        current = predicted_salary

        for year in range(1, 6):
            current *= 1.12
            growth_projection.append({
                "year": year,
                "salary": int(current)
            })

        return {
            "currency": currency,
            "predicted_salary": int(predicted_salary),
            "salary_range_min": int(predicted_salary * 0.9),
            "salary_range_max": int(predicted_salary * 1.1),
            "growth_projection": growth_projection,
            "company_tiers": company_tiers,
            "top_paying_skills": ["AI", "Cloud", "System Design"],
            "negotiation_advice": "You can negotiate 10–15% above base salary."
        }