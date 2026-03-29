"""
backend/services/recruiter_service.py
Full service layer for the Recruiter System.
"""
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.extensions import db
from backend.models import (
    User, Profile, RecruiterJob, JobApplication, RecruiterMessage
)


# ── Email templates ────────────────────────────────────────────
EMAIL_TEMPLATES = {
    "selected": {
        "subject": "🎉 Congratulations! You're Selected — {company}",
        "body": """Dear {name},

We are thrilled to inform you that you have been SELECTED for the position of {job_title} at {company}.

{extra}

Please reply to this email or check your PathPilot messages for next steps.

Best regards,
{company} Hiring Team
""",
    },
    "rejected": {
        "subject": "Application Update — {company}",
        "body": """Dear {name},

Thank you for applying to {company} for the role of {job_title}.

After careful consideration, we regret to inform you that we will not be moving forward with your application at this time.

{extra}

We wish you the very best in your career journey.

Best regards,
{company} Hiring Team
""",
    },
    "interview": {
        "subject": "Interview Invitation — {company} | {job_title}",
        "body": """Dear {name},

We are pleased to invite you for an interview for the position of {job_title} at {company}.

{extra}

Please confirm your availability by replying to this email or via PathPilot messages.

Best regards,
{company} Hiring Team
""",
    },
    "offer": {
        "subject": "Offer Letter — {company} | {job_title}",
        "body": """Dear {name},

We are delighted to extend a formal offer for the position of {job_title} at {company}.

{extra}

Kindly review the attached details and confirm your acceptance.

Best regards,
{company} Hiring Team
""",
    },
    "general": {
        "subject": "Message from {company} — PathPilot",
        "body": """Dear {name},

You have a new message from {company} regarding {job_title}.

{extra}

Best regards,
{company} Hiring Team
""",
    },
}


class RecruiterService:

    # ── Jobs ──────────────────────────────────────────────────

    def create_job(self, recruiter_email: str, company_name: str, data: dict) -> RecruiterJob:
        deadline = None
        if data.get("deadline"):
            try:
                deadline = datetime.strptime(data["deadline"], "%Y-%m-%d")
            except Exception:
                pass

        job = RecruiterJob(
            recruiter_email  = recruiter_email,
            company_name     = company_name,
            title            = data.get("title", ""),
            description      = data.get("description", ""),
            location         = data.get("location", ""),
            job_type         = data.get("job_type", "Full-Time"),
            ctc              = data.get("ctc", ""),
            deadline         = deadline,
            stream_required  = data.get("stream_required", ""),
            min_cgpa         = float(data.get("min_cgpa") or 0),
            batch            = data.get("batch", ""),
            rounds           = json.dumps(data.get("rounds", [])),
            skills_required  = data.get("skills_required", ""),
            is_active        = True,
            allow_messaging  = bool(data.get("allow_messaging")),
        )
        db.session.add(job)
        db.session.commit()
        return job

    def get_job(self, job_id: int):
        return RecruiterJob.query.get(job_id)

    def get_recruiter_jobs(self, recruiter_email: str):
        return RecruiterJob.query.filter_by(recruiter_email=recruiter_email)\
                   .order_by(RecruiterJob.created_at.desc()).all()

    def get_all_active_jobs(self):
        return RecruiterJob.query.filter_by(is_active=True)\
                   .order_by(RecruiterJob.created_at.desc()).all()

    def toggle_job_status(self, job_id: int, recruiter_email: str):
        job = RecruiterJob.query.get(job_id)
        if job and job.recruiter_email == recruiter_email:
            job.is_active = not job.is_active
            db.session.commit()

    def delete_job(self, job_id: int, recruiter_email: str):
        job = RecruiterJob.query.get(job_id)
        if job and job.recruiter_email == recruiter_email:
            db.session.delete(job)
            db.session.commit()

    # ── Applications ──────────────────────────────────────────

    def apply_for_job(self, user_id: int, job_id: int, form_data, resume_filename=None) -> dict:
        # Check duplicate
        existing = JobApplication.query.filter_by(user_id=user_id, job_id=job_id).first()
        if existing:
            return {"success": False, "error": "You have already applied for this job."}

        job = RecruiterJob.query.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found."}

        app = JobApplication(
            job_id           = job_id,
            user_id          = user_id,
            tenth_percent    = _safe_float(form_data.get("tenth_percent")),
            twelfth_percent  = _safe_float(form_data.get("twelfth_percent")),
            cgpa             = _safe_float(form_data.get("cgpa")),
            degree           = form_data.get("degree", ""),
            college          = form_data.get("college", ""),
            school_name      = form_data.get("school_name", ""),
            batch            = form_data.get("batch", ""),
            stream           = form_data.get("stream", ""),
            strengths        = form_data.get("strengths", ""),
            why_hire         = form_data.get("why_hire", ""),
            contact_email    = form_data.get("contact_email", ""),
            phone            = form_data.get("phone", ""),
            resume_filename  = resume_filename,
            applied_at       = datetime.utcnow(),
            status           = "applied",
        )
        db.session.add(app)
        db.session.commit()
        return {"success": True, "app_id": app.id}

    def get_applications(self, job_id: int, filters: dict = None):
        q = JobApplication.query.filter_by(job_id=job_id)
        if filters:
            if filters.get("min_cgpa"):
                try:
                    q = q.filter(JobApplication.cgpa >= float(filters["min_cgpa"]))
                except Exception:
                    pass
            if filters.get("college"):
                q = q.filter(JobApplication.college.ilike(f"%{filters['college']}%"))
            if filters.get("status"):
                q = q.filter(JobApplication.status == filters["status"])
            if filters.get("timing") == "before_deadline":
                job = RecruiterJob.query.get(job_id)
                if job and job.deadline:
                    q = q.filter(JobApplication.applied_at <= job.deadline)
            elif filters.get("timing") == "after_deadline":
                job = RecruiterJob.query.get(job_id)
                if job and job.deadline:
                    q = q.filter(JobApplication.applied_at > job.deadline)
        return q.order_by(JobApplication.applied_at.desc()).all()

    def update_application_status(self, app_id: int, new_status: str, recruiter_email: str):
        app = JobApplication.query.get(app_id)
        if app:
            app.status = new_status
            db.session.commit()

    def get_user_applications(self, user_id: int):
        return (
            db.session.query(JobApplication, RecruiterJob)
            .join(RecruiterJob, JobApplication.job_id == RecruiterJob.id)
            .filter(JobApplication.user_id == user_id)
            .order_by(JobApplication.applied_at.desc())
            .all()
        )

    # ── Dashboard stats ───────────────────────────────────────

    def get_dashboard_stats(self, recruiter_email: str) -> dict:
        jobs        = RecruiterJob.query.filter_by(recruiter_email=recruiter_email).all()
        job_ids     = [j.id for j in jobs]
        total_apps  = 0
        selected    = 0
        active_jobs = 0
        for j in jobs:
            if j.is_active:
                active_jobs += 1
            cnt = JobApplication.query.filter_by(job_id=j.id).count()
            total_apps += cnt
            sel = JobApplication.query.filter_by(job_id=j.id, status="selected").count()
            selected += sel
        msgs = RecruiterMessage.query.filter_by(recruiter_email=recruiter_email).count()
        return {
            "total_jobs":  len(jobs),
            "active_jobs": active_jobs,
            "total_apps":  total_apps,
            "selected":    selected,
            "msgs_sent":   msgs,
        }

    # ── Student search ────────────────────────────────────────

    def search_students(self, query: str):
        if not query:
            return []
        results = User.query.filter(
            (User.name.ilike(f"%{query}%")) |
            (User.email.ilike(f"%{query}%"))
        ).filter(User.role == "user").limit(20).all()
        out = []
        for u in results:
            p = Profile.query.filter_by(user_id=u.id).first()
            out.append({
                "id":       u.id,
                "name":     u.name,
                "email":    u.email,
                "headline": p.headline if p else "",
                "username": p.username if p else "",
                "image":    f"/static/{p.profile_image}" if p and p.profile_image else None,
            })
        return out

    # ── Messages ──────────────────────────────────────────────

    def send_message(self, recruiter_email, company_name, receiver_id,
                     subject, content, job_id=None, msg_type="general",
                     allow_reply=False):
        msg = RecruiterMessage(
            recruiter_email = recruiter_email,
            company_name    = company_name,
            receiver_id     = receiver_id,
            job_id          = job_id,
            subject         = subject,
            content         = content,
            message_type    = msg_type,
            allow_reply     = allow_reply,
            is_read         = False,
        )
        db.session.add(msg)
        db.session.commit()
        return msg

    def get_recruiter_sent_messages(self, recruiter_email: str):
        return RecruiterMessage.query.filter_by(recruiter_email=recruiter_email)\
                   .order_by(RecruiterMessage.created_at.desc()).all()

    def get_user_messages(self, user_id: int):
        return RecruiterMessage.query.filter_by(receiver_id=user_id)\
                   .order_by(RecruiterMessage.created_at.desc()).all()

    def get_unread_count(self, user_id: int) -> int:
        return RecruiterMessage.query.filter_by(receiver_id=user_id, is_read=False).count()

    def mark_message_read(self, msg_id: int, user_id: int):
        msg = RecruiterMessage.query.filter_by(id=msg_id, receiver_id=user_id).first()
        if msg:
            msg.is_read = True
            db.session.commit()

    # ── Email sender ──────────────────────────────────────────

    def send_email(self, to_email: str, student_name: str, company_name: str,
                   template: str, job_title: str = "", extra: str = ""):
        """
        Sends an email using SMTP.
        Set MAIL_SERVER / MAIL_USERNAME / MAIL_PASSWORD in config.
        Falls back gracefully if not configured.
        """
        try:
            from flask import current_app
            server   = current_app.config.get("MAIL_SERVER")
            port     = int(current_app.config.get("MAIL_PORT", 587))
            username = current_app.config.get("MAIL_USERNAME")
            password = current_app.config.get("MAIL_PASSWORD")

            if not (server and username and password):
                print("[Email] SMTP not configured — skipping email send.")
                return False

            tmpl = EMAIL_TEMPLATES.get(template, EMAIL_TEMPLATES["general"])
            subject = tmpl["subject"].format(
                company=company_name, job_title=job_title, name=student_name
            )
            body = tmpl["body"].format(
                name=student_name, company=company_name,
                job_title=job_title, extra=extra
            )

            msg = MIMEMultipart()
            msg["From"]    = username
            msg["To"]      = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(server, port) as smtp:
                smtp.starttls()
                smtp.login(username, password)
                smtp.sendmail(username, to_email, msg.as_string())

            return True
        except Exception as e:
            print(f"[Email Error] {e}")
            return False


# ── Helpers ───────────────────────────────────────────────────

def _safe_float(val):
    try:
        return float(val) if val else None
    except Exception:
        return None