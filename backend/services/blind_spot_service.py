import os, json
from openai import OpenAI
from backend.models import User, Resume, BlindSpotReport, db

client_holder = {}

def get_client():
    if "c" not in client_holder:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in your .env file")
        client_holder["c"] = OpenAI(api_key=api_key)
    return client_holder["c"]


# ── Safe JSON parser ───────────────────────────────────────────
def _safe_json(text: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    t = text.strip()
    if "```json" in t:
        t = t.split("```json", 1)[1]
    if "```" in t:
        t = t.split("```", 1)[0]
    t = t.strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        start, end = t.find("{"), t.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(t[start:end])
            except Exception:
                pass
    return {}


class BlindSpotService:

    # ══════════════════════════════════════════════════════
    #  FULL ANALYSIS
    # ══════════════════════════════════════════════════════
    def analyze(self, user_id: int, extra_context: str = "") -> dict:
        user   = User.query.get(user_id)
        resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.id.desc()).first()

        user_name     = (user.name if user else None) or "Professional"
        resume_text   = (getattr(resume, "raw_text", "") or "")[:1500] if resume else ""
        resume_skills = (getattr(user, "normalized_skills", "") or "") if user else ""
        resume_fname  = (getattr(resume, "filename", "") or "") if resume else ""

        prompt = self._build_prompt(user_name, resume_text, resume_skills, extra_context)

        client = get_client()
        resp   = client.chat.completions.create(
            model="gpt-4o",                  # upgraded from mini for brutal accuracy
            messages=[{"role": "user", "content": prompt}],
            temperature=0.75,
            response_format={"type": "json_object"},
            max_tokens=3500,
        )
        data = _safe_json(resp.choices[0].message.content)

        if not data:
            raise ValueError("AI returned empty or unparseable response. Please try again.")

        # ── Persist ──────────────────────────────────────────────────────────
        report = BlindSpotReport(
            user_id          = user_id,
            overall_score    = int(data.get("self_awareness_score", 60)),
            blind_spots_json = json.dumps(data.get("blind_spots", [])),
            strengths_json   = json.dumps(data.get("hidden_strengths", [])),
            patterns_json    = json.dumps(data.get("patterns", [])),
            language_json    = json.dumps(data.get("language_analysis", {})),
            gaps_json        = json.dumps(data.get("credibility_gaps", [])),
            fixes_json       = json.dumps(data.get("fixes", [])),
            coach_message    = data.get("coach_message", ""),
            shock_factor     = int(data.get("shock_factor", 5)),
        )
        db.session.add(report)
        db.session.commit()

        return self._report_to_dict(report, data, resume_fname)

    # ══════════════════════════════════════════════════════
    #  GET LATEST REPORT  ← FIX: now returns ALL fields
    # ══════════════════════════════════════════════════════
    def get_latest(self, user_id: int) -> dict | None:
        report = (
            BlindSpotReport.query
            .filter_by(user_id=user_id)
            .order_by(BlindSpotReport.id.desc())
            .first()
        )
        if not report:
            return None

        # Deserialise all JSON columns
        language_raw = {}
        try:
            language_raw = json.loads(report.language_json) if report.language_json else {}
        except Exception:
            pass

        gaps_raw = []
        try:
            gaps_raw = json.loads(report.gaps_json) if report.gaps_json else []
        except Exception:
            pass

        # Build a synthetic "data" dict identical to what analyze() returns
        data = {
            "self_awareness_score": report.overall_score,
            "score_label":          self._score_label(report.overall_score),
            "blind_spots":          report.get_blind_spots(),
            "hidden_strengths":     report.get_strengths(),
            "patterns":             report.get_patterns(),
            "language_analysis":    language_raw,
            "credibility_gaps":     gaps_raw,
            "fixes":                report.get_fixes(),
            "coach_message":        report.coach_message,
            "shock_factor":         report.shock_factor,
        }
        return self._report_to_dict(report, data, "", report.created_at.strftime("%b %d, %Y"))

    # ══════════════════════════════════════════════════════
    #  DEEP DIVE ON ONE BLIND SPOT
    # ══════════════════════════════════════════════════════
    def deep_dive(self, blind_spot: str, user_context: str) -> dict:
        prompt = f"""You are an elite career coach giving a BRUTALLY honest deep-dive on this exact blind spot:

BLIND SPOT: "{blind_spot}"
CONTEXT: {user_context[:600] or "Not provided"}

Be specific, psychological, and transformative. Don't be gentle.

Return ONLY valid JSON (no markdown):
{{
  "root_cause": "Deep psychological or behavioral reason WHY this blind spot exists — be specific and direct",
  "real_world_impact": "EXACTLY how this is costing them in money, lost offers, missed promotions — be brutally concrete. Use numbers if possible.",
  "fix_steps": [
    "Step 1: Specific action with exact example",
    "Step 2: Specific action",
    "Step 3: Specific action",
    "Step 4: How to measure improvement"
  ],
  "rewrite_example": "BEFORE: their actual weak language → AFTER: powerful rewrite",
  "timeline_to_fix": "Realistic timeline e.g. '3 weeks of daily 15-min practice'",
  "motivational_truth": "The one uncomfortable truth they need to hear that will finally make them change — make it hit hard"
}}"""

        client = get_client()
        resp   = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.72,
            response_format={"type": "json_object"},
            max_tokens=1000,
        )
        data = _safe_json(resp.choices[0].message.content)
        if not data:
            raise ValueError("Deep dive returned no data")
        return data

    # ══════════════════════════════════════════════════════
    #  PRIVATE HELPERS
    # ══════════════════════════════════════════════════════
    def _report_to_dict(self, report, data: dict, resume_fname: str, created_at: str = None) -> dict:
        score = int(data.get("self_awareness_score", report.overall_score))
        return {
            "report_id":            report.id,
            "self_awareness_score": score,
            "score_label":          data.get("score_label") or self._score_label(score),
            "shock_factor":         int(data.get("shock_factor", report.shock_factor)),
            "coach_message":        data.get("coach_message", report.coach_message) or "",
            "blind_spots":          data.get("blind_spots", []),
            "hidden_strengths":     data.get("hidden_strengths", []),
            "patterns":             data.get("patterns", []),
            "language_analysis":    data.get("language_analysis", {}),
            "credibility_gaps":     data.get("credibility_gaps", []),
            "fixes":                data.get("fixes", []),
            "resume_used":          resume_fname or "Your resume",
            "created_at":           created_at or "",
        }

    def _score_label(self, score: int) -> str:
        if score >= 80: return "Highly Self-Aware"
        if score >= 65: return "Aware"
        if score >= 45: return "Developing"
        return "Unaware"

    # ══════════════════════════════════════════════════════
    #  PROMPT — upgraded to be more powerful
    # ══════════════════════════════════════════════════════
    def _build_prompt(self, user_name: str, resume_text: str,
                      skills: str, extra: str) -> str:
        extra_line = f"\nExtra context from the user: {extra}" if extra else ""
        no_resume  = not resume_text.strip()
        resume_section = (
            f"Resume content:\n{resume_text}"
            if not no_resume
            else "No resume provided — infer patterns from skills and extra context. Still produce a full, specific report."
        )
        return f"""You are the world's most brutally honest, hyper-specific, compassionate career intelligence AI. You have 20 years of experience coaching professionals at Google, McKinsey, and top startups. You are performing a ₹50,000 career diagnostic session.

CANDIDATE NAME: {user_name}
Skills on file: {skills[:600] if skills else "Not provided"}
{resume_section}{extra_line}

Your job: Find the REAL reasons this person isn't getting the offers, salary, or recognition they deserve. Not generic advice — specific, evidence-based, psychological findings.

Return ONLY valid JSON (no markdown fences):
{{
  "self_awareness_score": <0–100 integer — how self-aware they are about their career blind spots>,
  "score_label": "Unaware / Developing / Aware / Highly Self-Aware",
  "shock_factor": <1–10 — how surprising/uncomfortable your findings are>,
  "coach_message": "A 3-sentence personal, direct, compassionate message TO THIS SPECIFIC PERSON by name. Make it hit emotionally. Address what you actually found.",

  "blind_spots": [
    {{
      "id": 1,
      "category": "Language / Positioning / Visibility / Confidence / Strategy / Skills / Salary",
      "title": "Short punchy title — e.g. 'You Sound Like an Executor, Not a Leader'",
      "severity": "Critical / High / Medium",
      "icon": "single emoji",
      "finding": "SPECIFIC finding — 2-3 sentences. Reference actual patterns from their resume/skills. Be direct.",
      "evidence": "Direct quote or specific pattern from their actual profile that proves this",
      "impact": "Concrete impact — lost salary, missed promotions, fewer callbacks — be specific with numbers where possible",
      "fix": "Exact, 1-sentence actionable fix they can apply TODAY"
    }}
  ],

  "hidden_strengths": [
    {{
      "title": "A strength they clearly have but are NOT leveraging",
      "icon": "single emoji",
      "description": "What it is and WHY it's valuable in the market right now",
      "how_to_use": "Exact tactical way to use this strength in interviews, resume, or salary negotiation"
    }}
  ],

  "patterns": [
    {{
      "pattern": "Short behavioral pattern name",
      "icon": "single emoji",
      "description": "What they keep doing — be specific and personal",
      "fix": "Exactly how to break this pattern — specific action"
    }}
  ],

  "language_analysis": {{
    "passive_count": <number of passive-voice or weak phrases detected>,
    "tone": "Apologetic / Neutral / Confident / Assertive",
    "summary": "2 sentences — specific assessment of how their language is working against them",
    "words_to_remove": ["weak word 1", "weak word 2", "weak word 3", "weak word 4"],
    "words_to_add": ["power word 1", "power word 2", "power word 3", "power word 4"],
    "power_words_missing": ["word1", "word2"]
  }},

  "credibility_gaps": [
    {{
      "gap": "What they CLAIM vs what they actually PROVE — be specific",
      "impact": "Why this specific gap is hurting their credibility with hiring managers",
      "fix": "Exact way to close this gap — what proof to add, what to change"
    }}
  ],

  "fixes": [
    {{
      "blind_spot_id": 1,
      "before": "Exact example of their current weak language or behavior",
      "after": "Powerful transformed version",
      "effort": "15 minutes / 1 hour / 1 week"
    }}
  ]
}}

RULES:
- Generate 4–6 blind spots minimum
- Generate 3–4 hidden strengths
- Generate 3–4 patterns
- Generate 2–4 credibility gaps
- Generate one fix per blind spot
- Everything must be SPECIFIC to THIS person, not generic career advice
- If no resume provided, still produce a full report based on skills and context
- severity distribution: at least 1 Critical, 2 High, rest Medium"""