from openai import OpenAI

client = OpenAI(
    api_key="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"
)

class AISalaryEngine:

    def predict_salary(self, role, experience, country, state, company):

        prompt = f"""
You are an expert salary intelligence AI.

Predict a realistic salary range.

Role: {role}
Experience: {experience}
Country: {country}
State: {state}
Company: {company}

Explain:
1. Expected salary range
2. Market demand
3. Company salary impact
4. Career advice
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a global salary market expert."},
                {"role":"user","content":prompt}
            ]
        )

        return response.choices[0].message.content