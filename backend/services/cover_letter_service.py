import os, json
from openai import OpenAI
from backend.models import User, Resume, db
from backend.services._openai_client import get_client, MODEL_CHEAP, MODEL_SMART

TONES = {
    "professional": {
        "label": "Professional", "icon": "🎩",
        "desc": "Formal, polished, corporate-ready",
        "instruction": "Write in a formal, professional tone. Confident but respectful. Suitable for large corporations and traditional industries.",
        "color": "#5b6bff"
    },
    "confident": {
        "label": "Confident", "icon": "🔥",
        "desc": "Bold, assertive, results-driven",
        "instruction": "Write in a bold, confident tone. Lead with achievements. Show ambition. Make them feel they would be missing out by not hiring this person.",
        "color": "#ff5757"
    },
    "friendly": {
        "label": "Friendly", "icon": "😊",
        "desc": "Warm, personable, startup-ready",
        "instruction": "Write in a warm, friendly, conversational tone. Show personality. Perfect for startups and creative companies.",
        "color": "#22c55e"
    },
    "creative": {
        "label": "Creative", "icon": "🎨",
        "desc": "Unique, storytelling, memorable",
        "instruction": "Write creatively. Open with a compelling hook or story. Make it memorable and completely different from every other cover letter.",
        "color": "#a855f7"
    },
    "concise": {
        "label": "Concise", "icon": "⚡",
        "desc": "Short, sharp, maximum impact",
        "instruction": "Write a SHORT cover letter — maximum 3 paragraphs. Every sentence must earn its place. No fluff. Pure impact.",
        "color": "#ffb547"
    },
}

LENGTHS = {
    "short":  {"label": "Short",  "words": "150-200 words", "paragraphs": 3},
    "medium": {"label": "Medium", "words": "250-300 words", "paragraphs": 4},
    "long":   {"label": "Long",   "words": "380-420 words", "paragraphs": 5},
}


class CoverLetterService:

    def __init__(self):
        self.client = get_client()

    # ══════════════════════════════════════════════════
    #  MAIN GENERATE
    # ══════════════════════════════════════════════════
    def generate(self, user_id, job_description, company_name,
                 role_name, hiring_manager, tone, length,
                 extra_notes="", resume_id=None):

        user = User.query.get(user_id)

        # Pick resume — specific or latest
        if resume_id:
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        else:
            resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.id.desc()).first()

        user_name     = user.name if user else "Candidate"
        resume_text   = ""
        resume_skills = ""
        resume_fname  = ""

        if resume:
            resume_text  = getattr(resume, "raw_text", "") or ""
            resume_fname = getattr(resume, "filename", "") or ""
            # Try to get skills from resume's normalized_skills or user's
            skills_raw = getattr(resume, "normalized_skills", "") or ""
            if not skills_raw and user:
                skills_raw = getattr(user, "normalized_skills", "") or ""
            resume_skills = skills_raw

        tone_cfg   = TONES.get(tone, TONES["professional"])
        length_cfg = LENGTHS.get(length, LENGTHS["medium"])

        prompt = self._build_prompt(
            user_name=user_name,
            resume_text=resume_text,
            resume_skills=resume_skills,
            job_description=job_description,
            company_name=company_name,
            role_name=role_name,
            hiring_manager=hiring_manager,
            tone_instruction=tone_cfg["instruction"],
            word_count=length_cfg["words"],
            paragraphs=length_cfg["paragraphs"],
            extra_notes=extra_notes,
        )

        resp = self.client.chat.completions.create(
            model=MODEL_CHEAP,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.78,
            max_tokens=900,
        )
        letter = resp.choices[0].message.content.strip()

        score_data   = self._score_letter(letter, job_description, resume_skills)
        matches      = self._extract_matches(letter, job_description)
        missing_kw   = self._missing_keywords(letter, job_description)
        suggestions  = self._improvement_tips(score_data["breakdown"])

        return {
            "letter":       letter,
            "score":        score_data["score"],
            "score_label":  score_data["label"],
            "score_color":  score_data["color"],
            "breakdown":    score_data["breakdown"],
            "key_matches":  matches,
            "missing_kw":   missing_kw,
            "suggestions":  suggestions,
            "word_count":   len(letter.split()),
            "tone":         tone_cfg["label"],
            "tone_color":   tone_cfg["color"],
            "company":      company_name,
            "role":         role_name,
            "resume_used":  resume_fname or "Latest resume",
        }

    # ══════════════════════════════════════════════════
    #  REGENERATE PARAGRAPH
    # ══════════════════════════════════════════════════
    def regenerate_paragraph(self, paragraph, instruction, tone, context):
        tone_cfg = TONES.get(tone, TONES["professional"])
        prompt = f"""Rewrite this cover letter paragraph.

Original:
{paragraph}

Instruction: {instruction}
Tone to use: {tone_cfg["instruction"]}
Full letter context: {context[:600]}

Return ONLY the rewritten paragraph. No quotes, no labels, no explanation."""

        resp = self.client.chat.completions.create(
            model=MODEL_CHEAP,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.72, max_tokens=220,
        )
        return resp.choices[0].message.content.strip()

    # ══════════════════════════════════════════════════
    #  SCORE
    # ══════════════════════════════════════════════════
    def _score_letter(self, letter, jd, skills):
        prompt = f"""Score this cover letter on exactly 4 dimensions (each 0-10).

Cover Letter:
{letter[:1200]}

Job Description:
{jd[:600]}

Candidate Skills: {skills[:300]}

Return ONLY this JSON (no markdown):
{{
  "personalization": <int 0-10>,
  "keyword_match": <int 0-10>,
  "clarity": <int 0-10>,
  "impact": <int 0-10>
}}"""
        try:
            resp = self.client.chat.completions.create(
                model=MODEL_CHEAP,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            data   = json.loads(resp.choices[0].message.content)
            scores = [
                max(0, min(10, int(data.get("personalization", 7)))),
                max(0, min(10, int(data.get("keyword_match",   7)))),
                max(0, min(10, int(data.get("clarity",         7)))),
                max(0, min(10, int(data.get("impact",          7)))),
            ]
            avg = round(sum(scores) / 4 * 10)
            return {
                "score": avg,
                "label": "Excellent" if avg >= 85 else "Good" if avg >= 70 else "Average" if avg >= 55 else "Needs Work",
                "color": "#22c55e"  if avg >= 85 else "#00e5c8" if avg >= 70 else "#ffb547" if avg >= 55 else "#ff5757",
                "breakdown": {
                    "Personalization": scores[0],
                    "Keyword Match":   scores[1],
                    "Clarity":         scores[2],
                    "Impact":          scores[3],
                }
            }
        except Exception as e:
            print(f"[Score] Error: {e}")
            return {
                "score": 74, "label": "Good", "color": "#00e5c8",
                "breakdown": {"Personalization": 7, "Keyword Match": 8, "Clarity": 7, "Impact": 7}
            }

    # ══════════════════════════════════════════════════
    #  KEYWORD HELPERS
    # ══════════════════════════════════════════════════
    def _extract_matches(self, letter, jd):
        ll, jl = letter.lower(), jd.lower()
        techs  = [
            "python","java","javascript","react","node.js","sql","aws","docker",
            "kubernetes","machine learning","deep learning","tensorflow","pytorch",
            "flask","django","fastapi","data science","nlp","computer vision",
            "git","agile","scrum","leadership","communication","problem solving",
            "typescript","mongodb","postgresql","redis","spark","kafka","excel",
            "power bi","tableau","scikit-learn","pandas","numpy","langchain",
        ]
        return [t.title() for t in techs if t in jl and t in ll][:10]

    def _missing_keywords(self, letter, jd):
        ll, jl = letter.lower(), jd.lower()
        techs  = [
            "python","java","javascript","react","node.js","sql","aws","docker",
            "kubernetes","machine learning","tensorflow","pytorch","flask","django",
            "fastapi","data science","nlp","agile","typescript","mongodb",
            "postgresql","spark","kafka","excel","power bi","tableau",
        ]
        return [t.title() for t in techs if t in jl and t not in ll][:5]

    def _improvement_tips(self, breakdown):
        tips = []
        if breakdown.get("Personalization", 10) < 7:
            tips.append("Add more specific details about why THIS company excites you")
        if breakdown.get("Keyword Match", 10) < 7:
            tips.append("Include more technical keywords directly from the job description")
        if breakdown.get("Clarity", 10) < 7:
            tips.append("Simplify sentences — aim for one idea per sentence")
        if breakdown.get("Impact", 10) < 7:
            tips.append("Lead with your biggest achievement and quantify results with numbers")
        return tips

    # ══════════════════════════════════════════════════
    #  PROMPT BUILDER
    # ══════════════════════════════════════════════════
    def _build_prompt(self, user_name, resume_text, resume_skills,
                      job_description, company_name, role_name,
                      hiring_manager, tone_instruction,
                      word_count, paragraphs, extra_notes):

        manager_line = f"Dear {hiring_manager}," if hiring_manager else "Dear Hiring Manager,"
        extra        = f"\nExtra context from candidate: {extra_notes}" if extra_notes else ""

        return f"""You are a world-class career coach and professional writer. Write a highly personalized, human-sounding cover letter.

CANDIDATE:
Name: {user_name}
Skills: {resume_skills[:400] if resume_skills else "See resume below"}
Resume: {resume_text[:800] if resume_text else "Not provided"}

TARGET JOB:
Company: {company_name}
Role: {role_name}
Job Description:
{job_description[:1100]}
{extra}

WRITING RULES:
- Tone: {tone_instruction}
- Length: EXACTLY {word_count} ({paragraphs} paragraphs)
- Salutation: "{manager_line}"
- Closing: "Sincerely,\\n{user_name}"
- STRICTLY connect specific resume skills/achievements to specific JD requirements
- Use numbers and metrics wherever possible (%, years, team sizes, results)
- NEVER start with "I am writing to apply" or "I am excited to apply"
- NEVER use "I believe I would be a great fit" or generic phrases
- Each sentence must add value — zero filler
- Sound like a real, passionate, qualified human — not AI
- Paragraph structure:
  Para 1: Compelling hook + specific reason for THIS company/role
  Middle: 2-3 concrete achievements mapped to JD requirements
  Final: Strong call to action + genuine enthusiasm

Output ONLY the cover letter text. Start with the salutation. End with the closing."""