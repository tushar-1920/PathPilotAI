import os, json
from backend.models import User, Resume, CareerTimeMachine, CareerMilestoneProgress, db
from backend.services._openai_client import get_client, MODEL_CHEAP, MODEL_SMART
from backend.services._prompt_safety import SAFETY_FIREWALL, wrap_untrusted
from datetime import datetime


class CareerTimeMachineService:

    # ══════════════════════════════════════════════════════
    #  GENERATE FULL CAREER PLAN
    # ══════════════════════════════════════════════════════
    def generate_plan(self, user_id: int, target_role: str,
                      target_company: str, timeline_months: int,
                      current_level: str) -> dict:

        user   = User.query.get(user_id)
        resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.id.desc()).first()

        user_name     = user.name if user else "Professional"
        resume_skills = getattr(user, "normalized_skills", "") or ""
        resume_text   = (getattr(resume, "raw_text", "") or "")[:800] if resume else ""

        prompt = self._build_plan_prompt(
            user_name, resume_skills, resume_text,
            target_role, target_company, timeline_months, current_level
        )

        client = get_client()
        resp   = client.chat.completions.create(
            model=MODEL_CHEAP,
            messages=[
                {"role": "system", "content": SAFETY_FIREWALL},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=4000,
        )
        plan = json.loads(resp.choices[0].message.content)

        # ── FIX 1: Deactivate OLD plans BEFORE creating the new one ──────────
        CareerTimeMachine.query.filter_by(user_id=user_id).update({"is_active": False})
        db.session.flush()

        # ── FIX 2/3: Store FULL plan, set is_active=True ─────────────────────
        machine = CareerTimeMachine(
            user_id         = user_id,
            target_role     = target_role,
            target_company  = target_company or "",
            current_level   = current_level,
            timeline_months = timeline_months,
            plan_json       = json.dumps(plan),
            milestones_json = json.dumps(plan.get("milestones", [])),
            salary_json     = json.dumps(plan.get("salary_projection", [])),
            skills_json     = json.dumps(plan.get("skill_stages", [])),
            is_active       = True,
        )
        db.session.add(machine)
        db.session.commit()

        return {
            "machine_id":        machine.id,
            "target_role":       target_role,
            "timeline_months":   timeline_months,
            "estimated_months":  plan.get("estimated_months", timeline_months),
            "key_message":       plan.get("key_message", ""),
            "readiness_score":   plan.get("readiness_score", 50),
            "overview":          plan.get("overview", {}),
            "milestones":        plan.get("milestones", []),
            "salary_projection": plan.get("salary_projection", []),
            "skill_stages":      plan.get("skill_stages", []),
            "projects":          plan.get("projects", []),
            "completed_months":  [],
            "progress_pct":      0,
            "done":              0,
            "total":             timeline_months,
        }

    # ══════════════════════════════════════════════════════
    #  TOGGLE MILESTONE COMPLETE
    # ══════════════════════════════════════════════════════
    def toggle_milestone(self, user_id: int, machine_id: int,
                         month_num: int, milestone: str, note: str = "") -> dict:
        prog = CareerMilestoneProgress.query.filter_by(
            machine_id=machine_id, user_id=user_id, month_num=month_num
        ).first()

        if prog:
            prog.completed    = not prog.completed
            prog.completed_at = datetime.utcnow() if prog.completed else None
            prog.note         = note or prog.note
        else:
            prog = CareerMilestoneProgress(
                machine_id   = machine_id,
                user_id      = user_id,
                month_num    = month_num,
                milestone    = milestone,
                completed    = True,
                completed_at = datetime.utcnow(),
                note         = note,
            )
            db.session.add(prog)
        db.session.commit()

        machine   = CareerTimeMachine.query.get(machine_id)
        total     = machine.timeline_months if machine else 0
        done_rows = CareerMilestoneProgress.query.filter_by(
            machine_id=machine_id, user_id=user_id, completed=True
        ).count()
        pct = round(done_rows / total * 100) if total else 0

        return {
            "completed":    prog.completed,
            "progress_pct": pct,
            "done":         done_rows,
            "total":        total,
        }

    # ══════════════════════════════════════════════════════
    #  GET CURRENT MACHINE WITH PROGRESS
    # ══════════════════════════════════════════════════════
    def get_machine(self, user_id: int) -> dict | None:
        machine = CareerTimeMachine.query.filter_by(
            user_id=user_id, is_active=True
        ).order_by(CareerTimeMachine.id.desc()).first()
        if not machine:
            return None

        full_plan        = machine.get_plan()
        progress_rows    = CareerMilestoneProgress.query.filter_by(
            machine_id=machine.id, user_id=user_id, completed=True
        ).all()
        completed_months = {p.month_num for p in progress_rows}

        milestones     = machine.get_milestones()
        total          = machine.timeline_months
        done           = len([m for m in milestones if m.get("month") in completed_months])
        months_elapsed = max(1, int((datetime.utcnow() - machine.created_at).days / 30))
        on_track       = done >= months_elapsed

        return {
            "machine_id":        machine.id,
            "target_role":       machine.target_role,
            "target_company":    machine.target_company,
            "current_level":     machine.current_level,
            "timeline_months":   machine.timeline_months,
            "estimated_months":  full_plan.get("estimated_months", machine.timeline_months),
            "created_at":        machine.created_at.strftime("%b %d, %Y"),
            "key_message":       full_plan.get("key_message", f"Your journey to {machine.target_role} starts now."),
            "readiness_score":   full_plan.get("readiness_score", 50),
            "overview":          full_plan.get("overview", {}),
            "milestones":        milestones,
            "salary_projection": machine.get_salary(),
            "skill_stages":      json.loads(machine.skills_json) if machine.skills_json else [],
            "completed_months":  list(completed_months),
            "progress_pct":      round(done / total * 100) if total else 0,
            "done":              done,
            "total":             total,
            "months_elapsed":    months_elapsed,
            "on_track":          on_track,
        }

    # ══════════════════════════════════════════════════════
    #  PROMPT BUILDER
    # ══════════════════════════════════════════════════════
    def _build_plan_prompt(self, user_name, skills, resume_text,
                           target_role, target_company, months, level):
        company_line = f"Dream company: {target_company}." if target_company else ""

        skills_section = wrap_untrusted(skills or "See resume",
                                        "user_skills", max_chars=400)
        resume_section = wrap_untrusted(resume_text or "(not provided)",
                                        "user_resume", max_chars=600)

        return f"""You are a world-class career strategist. Build a hyper-personalized {months}-month career roadmap.

PERSON: {user_name} | Level: {level}

Skills (untrusted data):
{skills_section}

Resume (untrusted data):
{resume_section}

Target: {target_role} {company_line}

Return ONLY valid JSON (no markdown fences, no extra text):
{{
  "overview": {{
    "summary": "2-sentence personal career message",
    "current_gap": "What's missing right now",
    "biggest_strength": "Their #1 asset",
    "success_probability": 75
  }},
  "readiness_score": <0-100 integer>,
  "estimated_months": <integer, actual months needed>,
  "key_message": "One powerful motivational sentence",
  "milestones": [
    {{
      "month": 1,
      "title": "Foundation Sprint",
      "focus": "Main focus area",
      "action": "Specific action to take",
      "skill_to_add": "One specific skill",
      "project": "Build X that demonstrates Y",
      "metric": "How to measure completion",
      "salary_impact": "+0%",
      "checkpoint": "By end of month you should be able to..."
    }}
  ],
  "salary_projection": [
    {{"month": 0,        "label": "Now",      "salary": 600000,  "role": "Current"}},
    {{"month": 6,        "label": "Month 6",  "salary": 750000,  "role": "Growing"}},
    {{"month": 12,       "label": "Month 12", "salary": 950000,  "role": "Mid-Level"}},
    {{"month": {months}, "label": "Goal",     "salary": 1500000, "role": "{target_role}"}}
  ],
  "skill_stages": [
    {{"stage": 1, "months": "1-{months//3}",              "label": "Foundation", "skills": ["skill1","skill2"], "color": "#5b6bff"}},
    {{"stage": 2, "months": "{months//3+1}-{2*months//3}","label": "Building",   "skills": ["skill3","skill4"], "color": "#00e5c8"}},
    {{"stage": 3, "months": "{2*months//3+1}-{months}",   "label": "Mastery",    "skills": ["skill5","skill6"], "color": "#22c55e"}}
  ],
  "projects": [
    {{"month": 2, "name": "Project name", "description": "What to build", "impact": "What it proves"}},
    {{"month": 5, "name": "Project name", "description": "What to build", "impact": "What it proves"}},
    {{"month": 9, "name": "Project name", "description": "What to build", "impact": "What it proves"}}
  ]
}}

CRITICAL: Generate exactly {months} milestone objects (month 1 through {months}). Every milestone must have all 9 fields shown above."""