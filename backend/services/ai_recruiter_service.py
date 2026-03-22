"""
PathPilot AI — AI Recruiter Service
Handles interview logic, AI prompting, face data analysis, scoring, reports.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


def _db():
    from backend.extensions import db
    return db


def _models():
    from backend.models import AIInterviewSession, AIInterviewMessage
    return AIInterviewSession, AIInterviewMessage


# ─────────────────────────────────────────────────────────
#  RECRUITER PERSONALITIES
# ─────────────────────────────────────────────────────────

PERSONALITIES = {
    "friendly": {
        "name":  "Sarah (Friendly Recruiter)",
        "tone":  "warm, encouraging, supportive",
        "style": "You ask questions gently, give hints when the candidate struggles, "
                 "and praise good answers. You have a calm, welcoming tone.",
        "emoji": "😊",
        "color": "#22c55e",
    },
    "strict": {
        "name":  "Mr. Sharma (Strict Recruiter)",
        "tone":  "direct, no-nonsense, challenging",
        "style": "You are very demanding. You interrupt incorrect answers, push back on "
                 "vague responses, and don't accept surface-level answers. You say things like "
                 "'That's not precise enough' or 'Why? Explain the reasoning.'",
        "emoji": "😐",
        "color": "#ff5757",
    },
    "faang": {
        "name":  "Alex (FAANG Interviewer)",
        "tone":  "technical, deep, relentless",
        "style": "You ask FAANG-level questions. After every answer, you drill deeper. "
                 "You ask about time complexity, edge cases, scalability. You challenge every "
                 "assumption. You say 'Can you do better?' frequently.",
        "emoji": "💀",
        "color": "#a855f7",
    },
    "startup": {
        "name":  "Rahul (Startup Founder)",
        "tone":  "fast, practical, execution-focused",
        "style": "You care about speed, ownership, and real-world impact. You ask "
                 "'Have you shipped this to production?', 'How fast can you build this?', "
                 "'What would you do with zero resources?'. You value builders over talkers.",
        "emoji": "🚀",
        "color": "#ffb547",
    },
    "balanced": {
        "name":  "Priya (Senior Recruiter)",
        "tone":  "professional, fair, thorough",
        "style": "You are a balanced professional interviewer. You ask a mix of HR and "
                 "technical questions, dig into projects, and evaluate both hard and soft skills.",
        "emoji": "🎯",
        "color": "#5b6bff",
    },
}

# ─────────────────────────────────────────────────────────
#  LEVEL CONFIGS
# ─────────────────────────────────────────────────────────

LEVELS = {
    "fresher": {
        "label":       "Fresher / Entry Level",
        "questions":   6,
        "description": "Basic CS, projects, motivation, communication",
        "focus":       "fundamentals, learning ability, attitude",
    },
    "intermediate": {
        "label":       "Intermediate (2–5 years)",
        "questions":   8,
        "description": "System design basics, past projects, technical depth",
        "focus":       "technical skills, problem solving, project depth",
    },
    "advanced": {
        "label":       "Senior / Advanced (5+ years)",
        "questions":   10,
        "description": "Architecture, leadership, complex problems",
        "focus":       "architecture, leadership, deep technical knowledge",
    },
    "faang": {
        "label":       "FAANG Level 💀",
        "questions":   12,
        "description": "Coding, system design, behavioral, case studies",
        "focus":       "algorithms, scalability, leadership principles, culture fit",
    },
}


class AIRecruiterService:

    # ─────────────────────────────────────────────────────
    #  SESSION MANAGEMENT
    # ─────────────────────────────────────────────────────

    def create_session(
        self,
        user_id:     int,
        role:        str,
        level:       str,
        personality: str,
        resume_text: str = "",
    ):
        db = _db()
        AIInterviewSession, _ = _models()

        sess = AIInterviewSession(
            user_id       = user_id,
            role          = role,
            level         = level,
            personality   = personality,
            resume_text   = resume_text[:5000],   # cap resume
            status        = "active",
            question_num  = 0,
            live_score    = 0.0,
            face_flags    = json.dumps([]),        # list of face events
            created_at    = datetime.utcnow(),
        )
        db.session.add(sess)
        db.session.commit()
        logger.info(f"Interview session {sess.id} created for user {user_id}")
        return sess

    def get_session(self, session_id: int):
        AIInterviewSession, _ = _models()
        return AIInterviewSession.query.get(session_id)

    def get_session_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        AIInterviewSession, _ = _models()
        sessions = (
            AIInterviewSession.query
            .filter_by(user_id=user_id)
            .order_by(AIInterviewSession.created_at.desc())
            .limit(limit)
            .all()
        )
        result = []
        for s in sessions:
            result.append({
                "id":         s.id,
                "role":       s.role,
                "level":      s.level,
                "personality":s.personality,
                "status":     s.status,
                "score":      round(s.live_score or 0, 1),
                "decision":   s.decision or "pending",
                "date":       s.created_at.strftime("%d %b %Y") if s.created_at else "—",
            })
        return result

    def get_full_result(self, session_id: int) -> Dict:
        AIInterviewSession, AIInterviewMessage = _models()
        sess = AIInterviewSession.query.get(session_id)
        if not sess:
            return {}
        messages = (
            AIInterviewMessage.query
            .filter_by(session_id=session_id)
            .order_by(AIInterviewMessage.created_at)
            .all()
        )
        return {
            "session":  {
                "id":          sess.id,
                "role":        sess.role,
                "level":       sess.level,
                "personality": sess.personality,
                "score":       round(sess.live_score or 0, 1),
                "decision":    sess.decision or "pending",
                "report":      sess.final_report or "{}",
            },
            "messages": [
                {"sender": m.sender, "text": m.message,
                 "timestamp": m.created_at.strftime("%H:%M") if m.created_at else ""}
                for m in messages
            ],
        }

    # ─────────────────────────────────────────────────────
    #  OPENING MESSAGE
    # ─────────────────────────────────────────────────────

    def get_opening_message(self, sess) -> str:
        p    = PERSONALITIES.get(sess.personality, PERSONALITIES["balanced"])
        lvl  = LEVELS.get(sess.level, LEVELS["intermediate"])

        prompt = f"""You are {p['name']}, a professional interviewer.
Your tone is {p['tone']}.
{p['style']}

You are interviewing a candidate for the role of: {sess.role}
Interview level: {lvl['label']}

Start the interview RIGHT NOW with a professional opening.
Introduce yourself briefly (1 sentence), then immediately ask the first question.
The first question should be an opener like "Tell me about yourself" or resume-based.
Keep it to 2-3 sentences maximum.
Do NOT add any meta text or explanations — speak directly as the recruiter."""

        return self._call_claude(prompt, max_tokens=200)

    # ─────────────────────────────────────────────────────
    #  PROCESS ANSWER + GENERATE FOLLOW-UP
    # ─────────────────────────────────────────────────────

    def process_answer(
        self,
        session,
        user_msg:   str,
        face_data:  Dict,
        audio_data: Dict,
    ) -> Dict:
        db = _db()
        AIInterviewSession, AIInterviewMessage = _models()

        # Save user message
        user_msg_obj = AIInterviewMessage(
            session_id = session.id,
            sender     = "user",
            message    = user_msg,
            face_data  = json.dumps(face_data),
            created_at = datetime.utcnow(),
        )
        db.session.add(user_msg_obj)

        # Update question counter
        session.question_num = (session.question_num or 0) + 1
        db.session.commit()

        # Track face events (cheating / looking away)
        face_flags = json.loads(session.face_flags or "[]")
        if face_data.get("looking_away"):
            face_flags.append({"q": session.question_num, "event": "looking_away", "ts": datetime.utcnow().isoformat()})
        if face_data.get("suspicious"):
            face_flags.append({"q": session.question_num, "event": "suspicious_behavior", "ts": datetime.utcnow().isoformat()})
        session.face_flags = json.dumps(face_flags[-20:])  # keep last 20

        # Get conversation history
        history = self._get_history(session.id)

        p   = PERSONALITIES.get(session.personality, PERSONALITIES["balanced"])
        lvl = LEVELS.get(session.level, LEVELS["intermediate"])
        max_questions = lvl["questions"]
        q_num = session.question_num

        # ── SCORE THIS ANSWER SILENTLY ──
        answer_score = self._score_answer(user_msg, face_data, audio_data, p)
        new_score = ((session.live_score or 0) * (q_num - 1) + answer_score) / q_num
        session.live_score = round(new_score, 2)

        # ── DECIDE: interrupt, follow-up, or next question ──
        is_final_question = q_num >= max_questions

        # Should AI interrupt? (if answer is wrong/vague and personality is strict/faang)
        should_interrupt = (
            answer_score < 45 and
            session.personality in ("strict", "faang") and
            q_num < max_questions
        )

        interrupt_msg = ""
        if should_interrupt:
            interrupt_msg = self._generate_interrupt(user_msg, p, session.role)

        # Generate main AI response
        ai_response = self._generate_response(
            session       = session,
            user_msg      = user_msg,
            history       = history,
            personality   = p,
            level         = lvl,
            q_num         = q_num,
            max_questions = max_questions,
            face_data     = face_data,
            answer_score  = answer_score,
            is_final      = is_final_question,
        )

        # Save AI message
        ai_msg_obj = AIInterviewMessage(
            session_id = session.id,
            sender     = "ai",
            message    = ai_response,
            created_at = datetime.utcnow(),
        )
        db.session.add(ai_msg_obj)
        db.session.commit()

        return {
            "ai_response":   ai_response,
            "interview_over": is_final_question,
            "live_score":    session.live_score,
            "question_num":  q_num,
            "interrupt":     should_interrupt,
            "interrupt_msg": interrupt_msg,
        }

    def _generate_response(self, session, user_msg, history, personality, level,
                           q_num, max_questions, face_data, answer_score, is_final):
        p = personality

        # Build conversation context
        conv_text = "\n".join([
            f"{'CANDIDATE' if m['sender']=='user' else 'YOU (RECRUITER)'}: {m['text']}"
            for m in history[-8:]  # last 8 messages for context
        ])

        face_note = ""
        if face_data.get("looking_away"):
            face_note = "\n[NOTE: Candidate was looking away while answering. You may mention maintaining eye contact.]"
        if face_data.get("hesitation_detected"):
            face_note += "\n[NOTE: Candidate showed hesitation. You can probe deeper.]"

        if is_final:
            prompt = f"""You are {p['name']}.
Your interview style: {p['style']}
Role being interviewed for: {session.role}
Interview level: {level['label']}

CONVERSATION SO FAR:
{conv_text}

CANDIDATE'S FINAL ANSWER: {user_msg}
{face_note}

This was the last question. Wrap up the interview professionally.
Thank the candidate, give ONE brief general observation (positive or constructive),
and say you will be in touch. Keep it to 3 sentences maximum.
Speak directly as the recruiter — no meta text."""
        else:
            questions_left = max_questions - q_num
            follow_up_chance = answer_score < 65  # probe if answer was weak

            if follow_up_chance and q_num < max_questions - 1:
                instruction = f"""The candidate's answer was {'weak/vague' if answer_score < 45 else 'decent but needs more depth'}.
Ask ONE sharp follow-up question that drills deeper into what they just said.
Don't accept the surface answer. Push for specifics, reasoning, or examples.
Keep your response to 2 sentences maximum."""
            else:
                instruction = f"""The candidate answered adequately.
Give a very brief reaction (1 sentence max, can be neutral or brief acknowledgment),
then immediately ask the next interview question.
You have {questions_left} questions left. Focus on: {level['focus']}.
Keep total response under 3 sentences."""

            prompt = f"""You are {p['name']}.
Your interview style: {p['style']}
Role: {session.role} | Level: {level['label']}

CONVERSATION SO FAR:
{conv_text}

CANDIDATE JUST SAID: {user_msg}
{face_note}

{instruction}

IMPORTANT: Speak directly as the recruiter. No meta text. No lists. Pure conversational interview."""

        return self._call_claude(prompt, max_tokens=250)

    def _generate_interrupt(self, user_msg: str, personality: Dict, role: str) -> str:
        p = personality
        prompt = f"""You are {p['name']}, a {p['tone']} interviewer.
The candidate just said: "{user_msg}"
Their answer is incorrect, incomplete, or too vague.

Generate ONE sharp interruption (1 sentence) that:
- Stops them politely but firmly
- Points out what's wrong or missing
- Is in character as a {p['tone']} interviewer

Example: "Hold on — that explanation isn't quite right. What do you actually mean by that?"

Give ONLY the interruption sentence, nothing else."""
        return self._call_claude(prompt, max_tokens=80)

    # ─────────────────────────────────────────────────────
    #  SILENT SCORING
    # ─────────────────────────────────────────────────────

    def _score_answer(self, answer: str, face_data: Dict, audio_data: Dict, personality: Dict) -> float:
        """Score an answer 0-100 silently."""
        base_score = 60.0

        # Length heuristic
        words = len(answer.split())
        if words < 10:   base_score -= 20
        elif words < 25: base_score -= 10
        elif words > 50: base_score += 5

        # Face penalties
        if face_data.get("looking_away"):       base_score -= 8
        if face_data.get("suspicious"):         base_score -= 15
        if face_data.get("hesitation_detected"): base_score -= 5

        # Audio features
        if audio_data.get("long_pauses"):       base_score -= 5
        if audio_data.get("very_slow_speech"):  base_score -= 3

        # Quality keywords (very basic heuristic)
        quality_words = ["because", "therefore", "specifically", "example", "result",
                         "implemented", "designed", "optimized", "reduced", "improved",
                         "architecture", "approach", "challenge", "solution", "achieved"]
        matches = sum(1 for w in quality_words if w.lower() in answer.lower())
        base_score += min(matches * 3, 15)

        return max(0, min(100, base_score))

    # ─────────────────────────────────────────────────────
    #  FINAL REPORT GENERATION
    # ─────────────────────────────────────────────────────

    def generate_final_report(self, session) -> Dict:
        db = _db()
        AIInterviewSession, AIInterviewMessage = _models()

        messages = (
            AIInterviewMessage.query
            .filter_by(session_id=session.id)
            .order_by(AIInterviewMessage.created_at)
            .all()
        )

        user_answers = [m.message for m in messages if m.sender == "user"]
        all_conv = "\n".join([
            f"{'CANDIDATE' if m.sender=='user' else 'INTERVIEWER'}: {m.message}"
            for m in messages
        ])

        face_flags = json.loads(session.face_flags or "[]")
        p = PERSONALITIES.get(session.personality, PERSONALITIES["balanced"])

        prompt = f"""You are {p['name']}, a professional recruiter.
You just finished interviewing a candidate for: {session.role}
Interview level: {session.level}

FULL INTERVIEW TRANSCRIPT:
{all_conv}

BEHAVIORAL FLAGS:
- Times looking away: {sum(1 for f in face_flags if f.get('event')=='looking_away')}
- Suspicious behaviors: {sum(1 for f in face_flags if f.get('event')=='suspicious_behavior')}

Based on this complete interview, generate a detailed recruiter evaluation report in JSON format.
Return ONLY valid JSON, no other text.

{{
  "hire_decision": "HIRE" or "REJECT" or "MAYBE",
  "overall_score": <number 0-100>,
  "confidence_score": <number 0-100>,
  "scores": {{
    "communication": <0-10>,
    "technical_depth": <0-10>,
    "problem_solving": <0-10>,
    "confidence": <0-10>,
    "cultural_fit": <0-10>,
    "project_depth": <0-10>
  }},
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "brutal_feedback": "2-3 sentences of direct, honest feedback",
  "improvement_plan": ["action 1", "action 2", "action 3"],
  "salary_offer": "estimated salary range based on performance",
  "summary": "2-3 sentence executive summary of the candidate"
}}"""

        try:
            raw = self._call_claude(prompt, max_tokens=800)
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                report = json.loads(json_match.group())
            else:
                report = self._default_report(session.live_score or 0)
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            report = self._default_report(session.live_score or 0)

        # Determine hire decision from score if not set
        score = report.get("overall_score", session.live_score or 0)
        decision_map = {
            "HIRE":   score >= 70,
            "MAYBE":  50 <= score < 70,
            "REJECT": score < 50,
        }
        if score >= 70:     report["hire_decision"] = "HIRE"
        elif score >= 50:   report["hire_decision"] = "MAYBE"
        else:               report["hire_decision"] = "REJECT"

        # Save to session
        session.final_report = json.dumps(report)
        session.decision     = report["hire_decision"].lower()
        session.live_score   = report.get("overall_score", session.live_score)
        session.status       = "ended"
        db.session.commit()

        return report

    def _default_report(self, score: float) -> Dict:
        return {
            "hire_decision":     "MAYBE" if score >= 50 else "REJECT",
            "overall_score":     round(score, 1),
            "confidence_score":  round(score * 0.9, 1),
            "scores": {"communication": 6, "technical_depth": 5, "problem_solving": 6,
                       "confidence": 5, "cultural_fit": 6, "project_depth": 5},
            "strengths":         ["Showed up on time", "Attempted all questions"],
            "weaknesses":        ["Needs more depth", "Improve communication clarity"],
            "brutal_feedback":   "The candidate showed some potential but needs significant improvement in technical depth and clarity of communication.",
            "improvement_plan":  ["Practice explaining concepts out loud", "Build 1-2 production projects", "Study system design basics"],
            "salary_offer":      "₹6-10 LPA (based on current skill level)",
            "summary":           "Average candidate. Needs focused improvement before re-attempting.",
        }

    # ─────────────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────────────

    def _get_history(self, session_id: int) -> List[Dict]:
        _, AIInterviewMessage = _models()
        msgs = (
            AIInterviewMessage.query
            .filter_by(session_id=session_id)
            .order_by(AIInterviewMessage.created_at)
            .all()
        )
        return [{"sender": m.sender, "text": m.message} for m in msgs]

    
    def _call_claude(self, prompt: str, max_tokens: int = 400) -> str:
        try:
            from openai import OpenAI
            from backend.config import Config
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": "You are a professional AI recruiter conducting real interviews. Be direct, realistic and conversational."},
                    {"role": "user",   "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return "I apologize, there was a technical issue. Please repeat your answer."