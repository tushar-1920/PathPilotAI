import json
import re

from openai import OpenAI
from flask import current_app


class ResumeAIService:
    """
    AI-powered resume analysis using GPT-4o-mini.
    Returns both raw text (for display) and structured JSON (for processing).
    """

    # ── MAIN ANALYZE (returns formatted string for backward compat) ──
    @staticmethod
    def analyze_resume(resume_text: str) -> str:
        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

        prompt = f"""You are a world-class AI career analyst and resume expert.

Analyze the following resume carefully and respond in this EXACT structured format.
Be specific, actionable, and brutally honest.

ROLE: <Best matching career role based on skills and experience>
ROLE_SCORE: <percentage 0-100 estimating how strong this resume is for that role>

1. Resume Strengths
List 3-5 specific strengths with brief explanations. Reference actual skills/projects from the resume.

2. Resume Weaknesses
List 3-5 specific weaknesses. Be direct — what's missing or poorly presented?

3. Missing Skills
List the top 8-12 skills that are missing for modern tech jobs in this person's domain.
Format: skill1, skill2, skill3, ...

4. ATS Optimization Suggestions
List 5-7 specific keyword and formatting improvements to boost ATS score.

5. Career Growth Suggestions
Suggest 3-5 specific projects, certifications, or improvements the person should pursue next.
Be realistic based on their current level.

6. Market Competitiveness
Rate their market competitiveness: [Strong / Moderate / Developing]
Explain where they stand vs. the current job market for their role.

7. Quick Wins (Do These This Week)
List 3-4 things they can do RIGHT NOW to improve their resume immediately.

Resume:
{resume_text[:6000]}
"""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional resume reviewer and career strategist with 20 years of experience in tech hiring."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.65,
                max_tokens=2000
            )
            return resp.choices[0].message.content

        except Exception as e:
            return f"Analysis failed: {str(e)}"

    # ── STRUCTURED ANALYZE (returns dict for API responses) ────────
    @staticmethod
    def analyze_resume_structured(resume_text: str) -> dict:
        """
        Returns a structured dict with all analysis fields.
        Used by API routes that need parsed data.
        """
        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

        prompt = f"""You are a world-class AI career analyst and resume expert.

Analyze this resume and return ONLY a valid JSON object (no markdown, no extra text).

JSON format:
{{
  "best_role": "string — best matching role",
  "role_score": number (0-100),
  "ats_score": number (0-100),
  "market_rating": "Strong | Moderate | Developing",
  "strengths": ["string", "string", "string"],
  "weaknesses": ["string", "string", "string"],
  "missing_skills": ["skill1", "skill2", "skill3", "...up to 12"],
  "ats_suggestions": ["string", "...up to 7"],
  "career_suggestions": ["string", "...up to 5"],
  "quick_wins": ["string", "...up to 4"],
  "market_competitiveness_explanation": "string — 2-3 sentences",
  "summary": "string — one paragraph overall assessment"
}}

Resume:
{resume_text[:5000]}
"""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional resume reviewer. Always respond with valid JSON only."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.55,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            raw = resp.choices[0].message.content
            return json.loads(raw)

        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the response
            try:
                m = re.search(r'\{[\s\S]+\}', raw)
                if m:
                    return json.loads(m.group(0))
            except Exception:
                pass
            return {"error": "Failed to parse AI response as JSON"}

        except Exception as e:
            return {"error": str(e)}

    # ── ATS SCORE ONLY ──────────────────────────────────────────
    @staticmethod
    def get_ats_score(resume_text: str, job_description: str = None) -> dict:
        """Fast ATS score check — optional job description for role-specific scoring."""
        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

        jd_section = ""
        if job_description:
            jd_section = f"\n\nJob Description to match against:\n{job_description[:2000]}"

        prompt = f"""Rate this resume's ATS (Applicant Tracking System) compatibility.
Return ONLY JSON with this exact structure:
{{
  "ats_score": number (0-100),
  "keyword_density": "Low | Medium | High",
  "formatting_score": number (0-100),
  "top_missing_keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
  "formatting_issues": ["issue1", "issue2"],
  "quick_fixes": ["fix1", "fix2", "fix3"]
}}

Resume:
{resume_text[:4000]}{jd_section}"""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            return json.loads(resp.choices[0].message.content)

        except Exception as e:
            return {"ats_score": 0, "error": str(e)}

    # ── SKILL EXTRACTION VIA AI (fallback) ─────────────────────
    @staticmethod
    def extract_skills_ai(resume_text: str) -> list:
        """
        Uses AI to extract skills when the regex parser misses something.
        Returns a list of skill strings.
        """
        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

        prompt = f"""Extract ALL technical and professional skills from this resume.
Return ONLY a JSON array of skill strings. No explanations, no markdown.
Example: ["Python", "Machine Learning", "AWS", "React", "SQL"]

Resume:
{resume_text[:4000]}"""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return valid JSON array only."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            raw = resp.choices[0].message.content
            parsed = json.loads(raw)
            # Handle both {"skills": [...]} and direct array
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                for key in ['skills', 'data', 'result', 'extracted']:
                    if key in parsed and isinstance(parsed[key], list):
                        return parsed[key]
            return []

        except Exception as e:
            print(f"[ResumeAIService] extract_skills_ai error: {e}")
            return []

    # ── CAREER PATH SUGGESTIONS ──────────────────────────────────
    @staticmethod
    def suggest_career_paths(resume_text: str, current_skills: list) -> dict:
        """Suggests 3 best-fit career paths based on resume + skills."""
        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

        skills_str = ", ".join(current_skills[:30]) if current_skills else "not provided"

        prompt = f"""Based on this resume and skill set, suggest the 3 best career paths.
Return ONLY JSON:
{{
  "paths": [
    {{
      "role": "string",
      "match_score": number (0-100),
      "reason": "string — why this role fits",
      "top_gaps": ["skill1", "skill2", "skill3"],
      "estimated_readiness": "Ready Now | 3-6 months | 6-12 months | 1+ year"
    }}
  ]
}}

Current Skills: {skills_str}
Resume (truncated): {resume_text[:3000]}"""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            return json.loads(resp.choices[0].message.content)

        except Exception as e:
            return {"paths": [], "error": str(e)}