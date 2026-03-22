import os, json
from openai import OpenAI
from backend.models import User, Resume, db
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Interview type configurations ─────────────────────────────
INTERVIEW_CONFIGS = {
    "hr": {
        "label":       "HR & Behavioral",
        "icon":        "🤝",
        "color":       "#5b6bff",
        "description": "Behavioral, situational, and cultural fit questions",
        "focus":       "behavioral, leadership, teamwork, communication, situational",
        "levels": {
            "fresher":   "entry-level candidate with 0-1 years experience",
            "mid":       "mid-level professional with 2-4 years experience",
            "senior":    "senior professional with 5+ years experience",
        }
    },
    "technical": {
        "label":       "Technical Deep Dive",
        "icon":        "⚙️",
        "color":       "#00e5c8",
        "description": "CS fundamentals, system design, and domain expertise",
        "focus":       "data structures, algorithms, system design, OOP, databases, networking",
        "levels": {
            "fresher":   "fresh graduate — focus on CS fundamentals and basics",
            "mid":       "working developer — focus on system design and optimization",
            "senior":    "senior engineer — focus on architecture and leadership",
        }
    },
    "ml": {
        "label":       "ML & Data Science",
        "icon":        "🧠",
        "color":       "#a855f7",
        "description": "Machine learning, statistics, and AI concepts",
        "focus":       "machine learning, deep learning, statistics, feature engineering, model evaluation, NLP, computer vision",
        "levels": {
            "fresher":   "ML student — focus on fundamentals and basic algorithms",
            "mid":       "ML practitioner — focus on real-world applications and tuning",
            "senior":    "ML lead — focus on production systems and research",
        }
    },
    "coding": {
        "label":       "Live Coding",
        "icon":        "💻",
        "color":       "#22c55e",
        "description": "Solve real coding problems like top tech company interviews",
        "focus":       "arrays, strings, linked lists, trees, dynamic programming, sorting, searching",
        "levels": {
            "fresher":   "Easy difficulty — basic data structures and simple algorithms",
            "mid":       "Medium difficulty — moderate algorithms and problem solving",
            "senior":    "Hard difficulty — complex algorithms and optimization",
        }
    },
    "system": {
        "label":       "System Design",
        "icon":        "🏗️",
        "color":       "#ffb547",
        "description": "Design scalable systems like FAANG interviews",
        "focus":       "scalability, microservices, databases, caching, load balancing, distributed systems, APIs",
        "levels": {
            "fresher":   "basic system design — simple architectures and components",
            "mid":       "intermediate — distributed systems and scaling",
            "senior":    "advanced — full-scale production architecture and trade-offs",
        }
    },
}

TOTAL_QUESTIONS = 8


class InterviewService:

    # ══════════════════════════════════════════════════════════
    #  START SESSION — personalize from resume if available
    # ══════════════════════════════════════════════════════════
    def start_session(self, user_id: int, interview_type: str, level: str) -> dict:
        config = INTERVIEW_CONFIGS.get(interview_type, INTERVIEW_CONFIGS["hr"])
        level_desc = config["levels"].get(level, config["levels"]["fresher"])

        # Pull resume skills for personalization
        user = User.query.get(user_id)
        skills_context = ""
        if user and hasattr(user, 'normalized_skills') and user.normalized_skills:
            skills = [s.strip() for s in user.normalized_skills.split(",") if s.strip()][:10]
            if skills:
                skills_context = f"\nCandidate's known skills: {', '.join(skills)}. Tailor questions to probe depth in these areas."

        system_prompt = f"""You are an elite interviewer at a top-tier tech company (FAANG level).
You are conducting a {config['label']} interview for a {level_desc}.
Focus areas: {config['focus']}.{skills_context}

Interview rules:
1. Ask ONE clear, specific question per turn
2. Do NOT reveal the answer
3. Be professional but encouraging
4. Track conversation context — don't repeat similar questions
5. For coding questions, provide a clear problem statement with example input/output
6. Vary difficulty — start moderate, escalate based on answers"""

        return {
            "system_prompt":   system_prompt,
            "config":          config,
            "level":           level,
            "level_desc":      level_desc,
            "interview_type":  interview_type,
            "total_questions": TOTAL_QUESTIONS,
        }

    # ══════════════════════════════════════════════════════════
    #  GENERATE QUESTION
    # ══════════════════════════════════════════════════════════
    def generate_question(self, system_prompt: str, history: list,
                          question_num: int, interview_type: str) -> dict:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        if question_num == 1:
            messages.append({"role": "user", "content":
                f"Start the interview. Ask your first question. Be direct — just ask the question, no preamble."})
        else:
            messages.append({"role": "user", "content":
                f"Ask question {question_num} of {TOTAL_QUESTIONS}. Make it different from previous questions. "
                f"Just ask the question directly."})

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )
        question = resp.choices[0].message.content.strip()

        # Generate hint (for coding type only)
        hint = ""
        if interview_type == "coding":
            hint_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":"You are a helpful mentor."},
                          {"role":"user","content":f"Give ONE subtle hint for this problem without revealing the answer:\n{question}"}],
                temperature=0.4, max_tokens=80,
            )
            hint = hint_resp.choices[0].message.content.strip()

        return {"question": question, "hint": hint}

    # ══════════════════════════════════════════════════════════
    #  EVALUATE ANSWER
    # ══════════════════════════════════════════════════════════
    def evaluate_answer(self, question: str, answer: str, interview_type: str,
                        level: str, time_taken: int) -> dict:
        if not answer or len(answer.strip()) < 5:
            return {
                "score": 0, "max_score": 10,
                "verdict": "Skipped",
                "strength": "No answer provided.",
                "improvement": "Always attempt an answer — even partial answers score points.",
                "ideal_points": "—",
                "badge": "⏭️",
            }

        time_penalty = ""
        if time_taken > 180:  # > 3 min
            time_penalty = f" Note: candidate took {time_taken}s — consider time management in feedback."

        prompt = f"""You are an expert interviewer evaluating a candidate's answer.

Interview Type: {interview_type.upper()}
Level: {level}
Question: {question}
Candidate's Answer: {answer}{time_penalty}

Evaluate strictly and return ONLY valid JSON:
{{
  "score": <integer 0-10>,
  "verdict": "<Excellent|Good|Average|Weak|Poor>",
  "strength": "<one sentence: what they did well>",
  "improvement": "<one sentence: what to improve>",
  "ideal_points": "<2-3 bullet points of what a perfect answer covers, separated by |>",
  "follow_up": "<one follow-up question to probe deeper>"
}}

Be honest — don't inflate scores. Score 0-3 for wrong/incomplete, 4-6 for partial, 7-8 for good, 9-10 for excellent."""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
                temperature=0.2,
                response_format={"type":"json_object"},
            )
            result = json.loads(resp.choices[0].message.content)
            result["max_score"] = 10
            result["badge"] = self._score_badge(result.get("score", 0))
            return result
        except Exception as e:
            print(f"[InterviewService] Eval error: {e}")
            return {
                "score": 5, "max_score": 10, "verdict": "Average",
                "strength": "Answer recorded.", "improvement": "Could not fully evaluate.",
                "ideal_points": "—", "follow_up": "", "badge": "⭐",
            }

    # ══════════════════════════════════════════════════════════
    #  FINAL REPORT
    # ══════════════════════════════════════════════════════════
    def generate_final_report(self, interview_type: str, level: str,
                               qa_history: list, total_time: int) -> dict:
        scores  = [qa["score"] for qa in qa_history if "score" in qa]
        avg     = round(sum(scores) / max(len(scores), 1), 1)
        total   = sum(scores)
        max_total = len(qa_history) * 10

        # Summary prompt
        summary_prompt = f"""You are an elite hiring manager giving final interview feedback.

Interview: {interview_type.upper()} | Level: {level}
Questions answered: {len(qa_history)}
Average score: {avg}/10
Total score: {total}/{max_total}

Q&A Summary:
{chr(10).join([f"Q{i+1}: {qa.get('question','')[:80]} → Score: {qa.get('score',0)}/10" for i, qa in enumerate(qa_history)])}

Return ONLY valid JSON:
{{
  "overall_verdict": "<Hire|Strong Hire|Maybe|No Hire>",
  "performance_summary": "<2-3 sentence overall assessment>",
  "top_strength": "<biggest strength observed>",
  "critical_gap": "<most important area to improve>",
  "next_steps": ["<action 1>", "<action 2>", "<action 3>"],
  "readiness_percent": <integer 0-100>
}}"""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":summary_prompt}],
                temperature=0.3,
                response_format={"type":"json_object"},
            )
            report = json.loads(resp.choices[0].message.content)
        except Exception:
            report = {
                "overall_verdict": "Average",
                "performance_summary": f"Completed {len(qa_history)} questions with an average score of {avg}/10.",
                "top_strength": "Attempted all questions.",
                "critical_gap": "Focus on depth and clarity of explanations.",
                "next_steps": ["Practice more mock interviews", "Review weak topics", "Build projects"],
                "readiness_percent": int((avg / 10) * 100),
            }

        report["avg_score"]   = avg
        report["total_score"] = total
        report["max_score"]   = max_total
        report["total_time"]  = total_time
        report["qa_history"]  = qa_history
        report["verdict_color"] = {
            "Strong Hire": "#22c55e", "Hire": "#00e5c8",
            "Maybe": "#ffb547", "No Hire": "#ff5757",
        }.get(report.get("overall_verdict","Maybe"), "#ffb547")

        return report

    # ══════════════════════════════════════════════════════════
    #  TTS — text to speech via OpenAI
    # ══════════════════════════════════════════════════════════
    def text_to_speech(self, text: str) -> bytes:
        resp = client.audio.speech.create(
            model="tts-1", voice="nova",
            input=text[:500],  # limit length
        )
        return resp.content

    # ══════════════════════════════════════════════════════════
    #  STT — speech to text via Whisper
    # ══════════════════════════════════════════════════════════
    def speech_to_text(self, audio_file) -> str:
        resp = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file,
        )
        return resp.text

    # ── helpers ──
    def _score_badge(self, score: int) -> str:
        if score >= 9:  return "🏆"
        if score >= 7:  return "⭐"
        if score >= 5:  return "✅"
        if score >= 3:  return "⚠️"
        return "❌"

    def get_configs(self) -> dict:
        return INTERVIEW_CONFIGS

    def get_total_questions(self) -> int:
        return TOTAL_QUESTIONS