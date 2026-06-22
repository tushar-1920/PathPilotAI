"""
backend/services/offer_predictor_service.py

The Offer Predictor Engine — PathPilot AI's most dangerous feature.
Takes a student's full profile + a job description and returns:
  • Offer probability (0–100%)
  • Top 3 blockers
  • 30-day gap-closing plan
  • Skill match breakdown
  • Resume audit
  • Company intel
  • Predicted interview questions
  • Salary intelligence
  • Score breakdown across 6 dimensions
"""

import os, json, re
from openai import OpenAI
from backend.models import User, Resume, Profile, Certificate, UserSkill, OfferPrediction, db
from datetime import datetime
from backend.services._openai_client import get_client, MODEL_CHEAP, MODEL_SMART

# ── Lazy OpenAI client ────────────────────────────────────────
_client_holder = {}

def _get_client():
    if "c" not in _client_holder:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in your .env file")
        _client_holder["c"] = get_client()
    return _client_holder["c"]


# ── Safe JSON parser ──────────────────────────────────────────
def _safe_json(text: str) -> dict:
    t = text.strip()
    for fence in ("```json", "```"):
        if fence in t:
            t = t.split(fence, 1)[1]
            break
    if "```" in t:
        t = t.split("```", 1)[0]
    t = t.strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        s, e = t.find("{"), t.rfind("}") + 1
        if s != -1 and e > s:
            try:
                return json.loads(t[s:e])
            except Exception:
                pass
    return {}


# ── Readiness tier mapping ─────────────────────────────────────
def _tier(prob: float) -> str:
    if prob >= 72:  return "Strong Candidate"
    if prob >= 50:  return "Possible"
    if prob >= 30:  return "Long Shot"
    return "Not Ready Yet"

def _risk(prob: float) -> str:
    if prob >= 72:  return "Low"
    if prob >= 50:  return "Medium"
    if prob >= 30:  return "High"
    return "Critical"


# ═══════════════════════════════════════════════════════════════
#  MAIN SERVICE CLASS
# ═══════════════════════════════════════════════════════════════

class OfferPredictorService:

    # ──────────────────────────────────────────────────────────
    #  PUBLIC: Run a full prediction
    # ──────────────────────────────────────────────────────────
    def predict(self, user_id: int, job_description: str,
                job_title: str = "", company_name: str = "",
                job_url: str = "") -> dict:

        # ── 1. Collect everything we know about the user ──────
        profile_data = self._collect_profile(user_id)

        # ── 2. Build the master prompt ────────────────────────
        prompt = self._build_prompt(profile_data, job_description, job_title, company_name)

        # ── 3. Call GPT-4o ────────────────────────────────────
        client = _get_client()
        resp = client.chat.completions.create(
            model=MODEL_SMART,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.65,
            response_format={"type": "json_object"},
            max_tokens=5000,
        )
        data = _safe_json(resp.choices[0].message.content)

        if not data:
            raise ValueError("AI returned empty response. Please try again.")

        # ── 4. Extract values ─────────────────────────────────
        prob    = float(data.get("offer_probability", 40))
        prob    = max(1.0, min(99.0, prob))   # clamp 1–99

        # ── 5. Persist to DB ──────────────────────────────────
        prediction = OfferPrediction(
            user_id             = user_id,
            job_title           = job_title or data.get("detected_job_title", ""),
            company_name        = company_name or data.get("detected_company", ""),
            job_description     = job_description[:3000],
            job_url             = job_url,
            offer_probability   = round(prob, 1),
            readiness_tier      = _tier(prob),
            verdict_headline    = data.get("verdict_headline", ""),
            blockers_json       = json.dumps(data.get("blockers", [])),
            strengths_json      = json.dumps(data.get("strengths", [])),
            gap_plan_json       = json.dumps(data.get("gap_plan", [])),
            skill_match_json    = json.dumps(data.get("skill_match", {})),
            resume_audit_json   = json.dumps(data.get("resume_audit", [])),
            company_intel_json  = json.dumps(data.get("company_intel", {})),
            interview_tips_json = json.dumps(data.get("interview_tips", [])),
            salary_intel_json   = json.dumps(data.get("salary_intel", {})),
            score_breakdown_json= json.dumps(data.get("score_breakdown", {})),
            coach_message       = data.get("coach_message", ""),
            risk_level          = _risk(prob),
        )
        db.session.add(prediction)
        db.session.commit()

        return prediction.to_dict()

    # ──────────────────────────────────────────────────────────
    #  GET HISTORY
    # ──────────────────────────────────────────────────────────
    def get_history(self, user_id: int, limit: int = 10) -> list:
        rows = (
            OfferPrediction.query
            .filter_by(user_id=user_id)
            .order_by(OfferPrediction.id.desc())
            .limit(limit)
            .all()
        )
        return [r.to_dict() for r in rows]

    # ──────────────────────────────────────────────────────────
    #  GET SINGLE PREDICTION
    # ──────────────────────────────────────────────────────────
    def get_prediction(self, prediction_id: int, user_id: int) -> dict | None:
        row = OfferPrediction.query.filter_by(id=prediction_id, user_id=user_id).first()
        return row.to_dict() if row else None

    # ──────────────────────────────────────────────────────────
    #  COLLECT USER PROFILE (all data sources)
    # ──────────────────────────────────────────────────────────
    def _collect_profile(self, user_id: int) -> dict:
        user    = User.query.get(user_id)
        resume  = Resume.query.filter_by(user_id=user_id).order_by(Resume.id.desc()).first()
        profile = Profile.query.filter_by(user_id=user_id).first()
        certs   = Certificate.query.filter_by(user_id=user_id).all()

        name          = user.name if user else "Student"
        skills_raw    = (getattr(user, "normalized_skills", "") or "").strip()
        resume_text   = (getattr(resume, "raw_text", "") or "")[:2000] if resume else ""
        skill_score   = getattr(resume, "skill_score", None) if resume else None
        github        = (getattr(profile, "github", "") or "") if profile else ""
        linkedin      = (getattr(profile, "linkedin", "") or "") if profile else ""
        headline      = (getattr(profile, "headline", "") or "") if profile else ""
        bio           = (getattr(profile, "bio", "") or "") if profile else ""
        location      = (getattr(profile, "location", "") or "") if profile else ""
        cert_list     = [f"{c.title} by {c.issuer}" for c in certs] if certs else []
        sub_plan      = getattr(user, "subscription_plan", "free") if user else "free"

        return {
            "name":         name,
            "skills":       skills_raw,
            "resume_text":  resume_text,
            "skill_score":  skill_score,
            "github":       github,
            "linkedin":     linkedin,
            "headline":     headline,
            "bio":          bio,
            "location":     location,
            "certificates": cert_list,
            "plan":         sub_plan,
        }

    # ──────────────────────────────────────────────────────────
    #  BUILD THE MASTER PROMPT
    # ──────────────────────────────────────────────────────────
    def _build_prompt(self, p: dict, jd: str,
                       job_title: str, company: str) -> str:

        certs_str = ", ".join(p["certificates"]) if p["certificates"] else "None listed"
        skill_score_str = f"{p['skill_score']:.1f}/100" if p["skill_score"] else "Not computed"

        return f"""
You are an elite career intelligence AI with 20+ years of recruiting experience at top companies
(Google, Microsoft, Amazon, startups, MNCs). You are brutally honest and data-driven.

Your task: Analyze this student's profile against the job description and return a COMPREHENSIVE
offer prediction in strict JSON format.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CANDIDATE PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {p['name']}
Headline: {p['headline'] or 'Not set'}
Location: {p['location'] or 'Not specified'}
Skills Listed: {p['skills'] or 'None detected'}
Platform Skill Score: {skill_score_str}
GitHub: {'Yes - ' + p['github'] if p['github'] else 'Not linked'}
LinkedIn: {'Yes - ' + p['linkedin'] if p['linkedin'] else 'Not linked'}
Certifications: {certs_str}
Bio / Summary: {p['bio'] or 'None'}

Resume Text (first 2000 chars):
{p['resume_text'] or 'No resume uploaded yet'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TARGET JOB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Job Title: {job_title or 'Not specified — detect from JD'}
Company: {company or 'Not specified — detect from JD'}
Job Description:
{jd[:3000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR OUTPUT (strict JSON, no markdown)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY a JSON object with these exact keys:

{{
  "detected_job_title": "string — if not provided, detect from JD",
  "detected_company": "string — if not provided, detect from JD",

  "offer_probability": <number 1–99, be REALISTIC not generous>,

  "verdict_headline": "One killer sentence summarising the situation (max 120 chars)",

  "score_breakdown": {{
    "skill_match":     <0–100>,
    "resume_quality":  <0–100>,
    "project_depth":   <0–100>,
    "experience_fit":  <0–100>,
    "cultural_signal": <0–100>,
    "overall":         <0–100>
  }},

  "blockers": [
    {{
      "rank": 1,
      "title": "short title (max 6 words)",
      "detail": "2-3 sentences explaining exactly what's wrong and why it hurts",
      "severity": "Critical | High | Medium",
      "quick_fix": "The single most impactful thing they can do this week"
    }},
    {{
      "rank": 2,
      "title": "...",
      "detail": "...",
      "severity": "...",
      "quick_fix": "..."
    }},
    {{
      "rank": 3,
      "title": "...",
      "detail": "...",
      "severity": "...",
      "quick_fix": "..."
    }}
  ],

  "strengths": [
    {{
      "title": "short title",
      "detail": "Why this is actually impressive to recruiters at this company"
    }}
  ],

  "skill_match": {{
    "matched": ["list of skills candidate HAS that job needs"],
    "missing": ["list of skills job needs that candidate LACKS"],
    "bonus": ["skills candidate has that give extra edge"],
    "match_percentage": <0–100>
  }},

  "resume_audit": [
    {{
      "issue": "specific resume issue",
      "impact": "how this hurts their chances",
      "fix": "exact wording / action to fix it"
    }}
  ],

  "gap_plan": [
    {{
      "week": 1,
      "title": "Week 1 goal (5 words max)",
      "actions": ["specific action 1", "specific action 2", "specific action 3"],
      "milestone": "What they should have completed by end of this week",
      "hours_required": <number>
    }},
    {{
      "week": 2,
      "title": "...",
      "actions": ["..."],
      "milestone": "...",
      "hours_required": <number>
    }},
    {{
      "week": 3,
      "title": "...",
      "actions": ["..."],
      "milestone": "...",
      "hours_required": <number>
    }},
    {{
      "week": 4,
      "title": "...",
      "actions": ["..."],
      "milestone": "...",
      "hours_required": <number>
    }}
  ],

  "company_intel": {{
    "culture_tags": ["3-5 words describing company culture"],
    "what_they_value": "2-3 sentences on what this company specifically looks for in candidates",
    "red_flags_for_them": "What profile traits would immediately disqualify a candidate here",
    "insider_tip": "One thing most candidates don't know about getting hired here"
  }},

  "interview_tips": [
    {{
      "type": "Technical | Behavioral | System Design | HR",
      "question": "Likely interview question for THIS role at THIS company",
      "why_asked": "Why this company asks this",
      "how_to_answer": "Exact strategy for answering this based on candidate's profile"
    }}
  ],

  "salary_intel": {{
    "range_low":  <number in INR lakhs per annum>,
    "range_high": <number in INR lakhs per annum>,
    "median":     <number in INR lakhs per annum>,
    "negotiation_tip": "One specific salary negotiation tip for this role/company",
    "context": "brief note on salary landscape for this role"
  }},

  "coach_message": "A brutally honest, personal, motivating 3-4 sentence message addressed
                    directly to the candidate. Name them. Reference specific things from their
                    profile. Be the career coach they never had."
}}

RULES:
- Be REALISTIC about offer_probability. Average fresh grad at Google = 12%. Don't inflate.
- blockers must be SPECIFIC to THIS candidate vs THIS job. No generic advice.
- gap_plan must be actionable TODAY — no vague "learn React", say "complete React crash course
  on freeCodeCamp (18 hours), build a todo app and push to GitHub by Sunday"
- interview_tips questions should reflect THIS company's known interview style
- salary_intel should be realistic for Indian market unless company is clearly foreign
- coach_message must feel personal, not generic. Reference their actual name and skills.
""".strip()