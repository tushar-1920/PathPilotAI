from backend.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# SKILL CATEGORY
# =========================================================
class SkillCategory(db.Model):
    __tablename__ = "skill_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))

    skills = db.relationship("Skill", backref="category", lazy=True)


# =========================================================
# SKILL
# =========================================================
class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("skill_categories.id"),
        nullable=True
    )

    demand_score = db.Column(db.Float, default=0)
    future_score = db.Column(db.Float, default=0)
    description = db.Column(db.String(500))


# =========================================================
# SKILL ALIAS
# =========================================================
class SkillAlias(db.Model):
    __tablename__ = "skill_aliases"

    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(200), unique=True, nullable=False)

    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"))
    skill = db.relationship("Skill", backref="aliases")


# =========================================================
# USER (UPDATED FOR AUTH SYSTEM)
# =========================================================
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)

    email = db.Column(db.String(200), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=True)

    role = db.Column(db.String(50), default="user")

    is_verified = db.Column(db.Boolean, default=False)

    normalized_skills = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # SaaS Fields
    subscription_plan = db.Column(db.String(50), default="free")  # free | pro | enterprise
    subscription_status = db.Column(db.String(50), default="active")  # active | cancelled
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    billing_cycle = db.Column(db.String(20))

    # ── Helper: always returns the profile photo URL (or None) ──
    # Used by auth_routes and app.py before_request to populate session
    @property
    def profile_photo_url(self):
        """
        Returns '/static/uploads/profile_images/...' if the user has
        uploaded a profile photo, otherwise None.
        Safe to call even if no Profile row exists yet.
        """
        try:
            if self.profile and self.profile.profile_image:
                img = self.profile.profile_image
                if img.startswith('/static/'):
                    return img
                return f"/static/{img}"
        except Exception:
            pass
        return None

    @property
    def display_initial(self):
        """Returns the first letter of the user's name, uppercased. Fallback: 'U'."""
        try:
            return (self.name or 'U')[0].upper()
        except Exception:
            return 'U'


# =========================================================
# RESUME (ONLY ONE DEFINITION)
# =========================================================
class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    filename = db.Column(db.String(300))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    skill_score = db.Column(db.Float)

    user = db.relationship("User", backref="resumes")
    normalized_skills = db.Column(db.Text)


# =========================================================
# USER SKILL
# =========================================================
class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"))

    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="user_skills")
    skill = db.relationship("Skill")


# =========================================================
# JOB POSTING
# =========================================================
class JobPosting(db.Model):
    __tablename__ = "job_postings"

    id = db.Column(db.Integer, primary_key=True)

    external_id = db.Column(db.String(200), index=True)
    title = db.Column(db.String(300), index=True)
    company = db.Column(db.String(300), index=True)
    location = db.Column(db.String(200), index=True)

    role = db.Column(db.String(200), index=True)

    skills_required = db.Column(db.Text)
    normalized_skills = db.Column(db.Text)

    salary = db.Column(db.String(100))
    source = db.Column(db.String(100), index=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "external_id",
            "source",
            name="unique_job_source"
        ),
    )


# =========================================================
# APPLICATION TRACKER
# =========================================================
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("job_postings.id"))

    status = db.Column(db.String(50), default="saved")
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="applications")
    job = db.relationship("JobPosting")

class SavedJob(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    title = db.Column(db.String(200))

    description = db.Column(db.Text)

    job_skills = db.Column(db.Text)

    score = db.Column(db.Integer)

    eligibility = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    job_level = db.Column(db.String(50))

# =========================================================
# CODING PRACTICE MODELS
# Add these 3 classes at the BOTTOM of your existing models.py
# =========================================================

class Problem(db.Model):
    """
    Optional DB-backed problem storage.
    The master list also lives in problem_service.py (dict-based).
    Use this when you want an admin panel to add/edit problems.
    """
    __tablename__ = "problems"

    id              = db.Column(db.Integer, primary_key=True)
    title           = db.Column(db.String(200), nullable=False)
    difficulty      = db.Column(db.String(20), nullable=False)   # Easy | Medium | Hard
    description     = db.Column(db.Text, nullable=False)
    input_format    = db.Column(db.Text, nullable=True)
    output_format   = db.Column(db.Text, nullable=True)
    constraints     = db.Column(db.Text, nullable=True)
    hints           = db.Column(db.Text, nullable=True)
    test_cases      = db.Column(db.JSON, nullable=True)
    boilerplate     = db.Column(db.JSON, nullable=True)
    topics          = db.Column(db.JSON, nullable=True)
    plans           = db.Column(db.JSON, nullable=True)
    acceptance_rate = db.Column(db.Float, default=0.0)
    time_limit_ms   = db.Column(db.Integer, default=2000)
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submissions     = db.relationship("Submission",    backref="problem", lazy="dynamic")
    solved_by       = db.relationship("SolvedProblem", backref="problem", lazy="dynamic")

    def __repr__(self):
        return f"<Problem id={self.id} title={self.title!r} difficulty={self.difficulty}>"


class Submission(db.Model):
    """
    Every Run-Code and Submit-Code call creates one row.
    status: Accepted | Wrong Answer | Time Limit Exceeded | Runtime Error
    """
    __tablename__ = "submissions"

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    problem_id    = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False, index=True)
    code          = db.Column(db.Text, nullable=False)
    language      = db.Column(db.String(30), nullable=False)
    status        = db.Column(db.String(40), nullable=False)
    runtime_ms    = db.Column(db.Float, default=0.0)
    memory_kb     = db.Column(db.Integer, default=0)
    passed_cases  = db.Column(db.Integer, default=0)
    total_cases   = db.Column(db.Integer, default=0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Submission id={self.id} user={self.user_id} problem={self.problem_id} status={self.status}>"

    def to_dict(self, include_code=False):
        d = {
            "id":           self.id,
            "user_id":      self.user_id,
            "problem_id":   self.problem_id,
            "language":     self.language,
            "status":       self.status,
            "runtime_ms":   self.runtime_ms,
            "memory_kb":    self.memory_kb,
            "passed_cases": self.passed_cases,
            "total_cases":  self.total_cases,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }
        if include_code:
            d["code"] = self.code
        return d


class SolvedProblem(db.Model):
    """
    One row per (user_id, problem_id) — written only on first Accepted.
    Drives: solved count, difficulty stats, leaderboard, activity calendar.
    """
    __tablename__ = "solved_problems"
    __table_args__ = (
        db.UniqueConstraint("user_id", "problem_id", name="uq_user_problem"),
    )

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    solved_at  = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SolvedProblem user={self.user_id} problem={self.problem_id}>"

    def to_dict(self):
        return {
            "id":         self.id,
            "user_id":    self.user_id,
            "problem_id": self.problem_id,
            "solved_at":  self.solved_at.isoformat() if self.solved_at else None,
        }



# ─────────────────────────────────────────────────────────────
# ADD username column to Profile model:
#
#   username      = db.Column(db.String(30), unique=True, nullable=True)
#   username_set  = db.Column(db.Boolean, default=False)
#   post_image    = already on Post below
#
# ADD image_url column to Certificate model:
#   image_url = db.Column(db.String(500))
#
# ADD image_url, image_path to Post model:
#   image_url  = db.Column(db.String(500))
#
# ─────────────────────────────────────────────────────────────
# FULL UPGRADED MODELS — replace your existing 5 models with these:

class Profile(db.Model):
    __tablename__ = "profiles"
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    username       = db.Column(db.String(30), unique=True, nullable=True)   # @username — set once
    username_set   = db.Column(db.Boolean, default=False)                   # can only set once
    headline       = db.Column(db.String(220))
    bio            = db.Column(db.Text)
    profile_image  = db.Column(db.String(400))
    cover_image    = db.Column(db.String(400))
    location       = db.Column(db.String(120))
    skills_summary = db.Column(db.Text)
    github         = db.Column(db.String(300))
    linkedin       = db.Column(db.String(300))
    portfolio      = db.Column(db.String(300))
    twitter        = db.Column(db.String(300))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user           = db.relationship("User", backref=db.backref("profile", uselist=False))


class Certificate(db.Model):
    __tablename__ = "certificates"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title         = db.Column(db.String(250), nullable=False)
    issuer        = db.Column(db.String(200))
    issued_date   = db.Column(db.String(50))
    credential_id = db.Column(db.String(200))
    link          = db.Column(db.String(500))
    image_url     = db.Column(db.String(500))   # certificate image / badge
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    user          = db.relationship("User", backref="certificates")


class Follow(db.Model):
    __tablename__ = "follows"
    id           = db.Column(db.Integer, primary_key=True)
    follower_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("follower_id","following_id",name="unique_follow"),)
    follower  = db.relationship("User", foreign_keys=[follower_id],  backref="following_rel")
    following = db.relationship("User", foreign_keys=[following_id], backref="followers_rel")


class Post(db.Model):
    __tablename__ = "posts"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    post_type  = db.Column(db.String(20), default="text")  # text/achievement/milestone/image
    image_url  = db.Column(db.String(500))                  # optional image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship("User", backref="posts")
    likes      = db.relationship("PostLike", backref="post", cascade="all, delete-orphan")
    comments   = db.relationship("PostComment", backref="post", cascade="all, delete-orphan")


class PostLike(db.Model):
    __tablename__ = "post_likes"
    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("post_id","user_id",name="unique_post_like"),)


class PostComment(db.Model):
    __tablename__ = "post_comments"
    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship("User", backref="comments")


# ─────────────────────────────────────────────────────────────
# NEW: Direct Messages
# ─────────────────────────────────────────────────────────────
class Message(db.Model):
    __tablename__ = "messages"
    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    sender      = db.relationship("User", foreign_keys=[sender_id],   backref="sent_messages")
    receiver    = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")


# ── APPEND THESE TO backend/models.py ──────────────────────────────────────
# Make sure `from datetime import datetime` is already at the top of models.py


class AIInterviewSession(db.Model):
    """One interview session per attempt."""
    __tablename__ = "ai_interview_sessions"

    id            = db.Column(db.Integer,   primary_key=True)
    user_id       = db.Column(db.Integer,   db.ForeignKey("users.id"), nullable=False)
    role          = db.Column(db.String(150),  default="Software Engineer")
    level         = db.Column(db.String(50),   default="intermediate")     # fresher/intermediate/advanced/faang
    personality   = db.Column(db.String(50),   default="balanced")         # friendly/strict/faang/startup/balanced
    resume_text   = db.Column(db.Text,         default="")
    status        = db.Column(db.String(20),   default="active")           # active / ended
    question_num  = db.Column(db.Integer,      default=0)
    live_score    = db.Column(db.Float,        default=0.0)                # 0–100, updated silently
    decision      = db.Column(db.String(20),   nullable=True)              # hire / reject / maybe
    final_report  = db.Column(db.Text,         nullable=True)              # JSON string
    face_flags    = db.Column(db.Text,         default="[]")               # JSON list of face events
    created_at    = db.Column(db.DateTime,     default=datetime.utcnow)
    ended_at      = db.Column(db.DateTime,     nullable=True)


class AIInterviewMessage(db.Model):
    """Every message exchanged in an interview session."""
    __tablename__ = "ai_interview_messages"

    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("ai_interview_sessions.id"), nullable=False)
    sender     = db.Column(db.String(10),  nullable=False)   # "ai" or "user"
    message    = db.Column(db.Text,        nullable=False)
    face_data  = db.Column(db.Text,        default="{}")      # JSON face snapshot at time of message
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

"""
ADD THESE TO YOUR backend/models.py
Two new model classes for Career Time Machine + Blind Spot Detector
"""
from backend.extensions import db
from datetime import datetime
import json

# ══════════════════════════════════════════════════════════════
#  CAREER TIME MACHINE MODELS
# ══════════════════════════════════════════════════════════════

class CareerTimeMachine(db.Model):
    """Stores each user's career journey plan + progress tracking."""
    __tablename__ = "career_time_machines"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_role     = db.Column(db.String(200), nullable=False)
    target_company  = db.Column(db.String(200))          # dream company (optional)
    current_level   = db.Column(db.String(100))          # junior/mid/senior
    timeline_months = db.Column(db.Integer, default=24)  # 12, 24, or 36 months
    plan_json       = db.Column(db.Text)                 # full AI-generated plan
    milestones_json = db.Column(db.Text)                 # list of monthly milestones
    salary_json     = db.Column(db.Text)                 # salary projections per milestone
    skills_json     = db.Column(db.Text)                 # skills at each stage
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active       = db.Column(db.Boolean, default=True)

    # Relationships
    progress        = db.relationship("CareerMilestoneProgress", backref="machine",
                                       lazy=True, cascade="all,delete-orphan")

    def get_plan(self):
        try: return json.loads(self.plan_json) if self.plan_json else {}
        except: return {}

    def get_milestones(self):
        try: return json.loads(self.milestones_json) if self.milestones_json else []
        except: return []

    def get_salary(self):
        try: return json.loads(self.salary_json) if self.salary_json else []
        except: return []


class CareerMilestoneProgress(db.Model):
    """Tracks which milestones a user has completed."""
    __tablename__ = "career_milestone_progress"

    id          = db.Column(db.Integer, primary_key=True)
    machine_id  = db.Column(db.Integer, db.ForeignKey("career_time_machines.id"), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    month_num   = db.Column(db.Integer, nullable=False)   # which month (1-36)
    milestone   = db.Column(db.String(500))               # milestone text
    completed   = db.Column(db.Boolean, default=False)
    completed_at= db.Column(db.DateTime)
    note        = db.Column(db.Text)                      # user's own note
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


# ══════════════════════════════════════════════════════════════
#  BLIND SPOT DETECTOR MODELS
# ══════════════════════════════════════════════════════════════

class BlindSpotReport(db.Model):
    """Stores each AI blind spot analysis for a user."""
    __tablename__ = "blind_spot_reports"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    overall_score   = db.Column(db.Integer, default=0)      # 0-100 self-awareness score
    blind_spots_json= db.Column(db.Text)                    # list of detected blind spots
    strengths_json  = db.Column(db.Text)                    # hidden strengths found
    patterns_json   = db.Column(db.Text)                    # behavioral patterns detected
    language_json   = db.Column(db.Text)                    # language analysis
    gaps_json       = db.Column(db.Text)                    # credibility gaps
    fixes_json      = db.Column(db.Text)                    # exact fix for each blind spot
    coach_message   = db.Column(db.Text)                    # personal message from AI coach
    shock_factor    = db.Column(db.Integer, default=5)      # 1-10 how surprising the findings are
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def get_blind_spots(self):
        try: return json.loads(self.blind_spots_json) if self.blind_spots_json else []
        except: return []

    def get_strengths(self):
        try: return json.loads(self.strengths_json) if self.strengths_json else []
        except: return []

    def get_patterns(self):
        try: return json.loads(self.patterns_json) if self.patterns_json else []
        except: return []

    def get_fixes(self):
        try: return json.loads(self.fixes_json) if self.fixes_json else []
        except: return []

"""
ADD/REPLACE in backend/models.py
New additions: PostCommentReply, ProfileStats
"""
from backend.extensions import db
from datetime import datetime


# ── ADD THIS NEW MODEL ──────────────────────────────────────
class PostCommentReply(db.Model):
    """Replies to comments (nested comments)."""
    __tablename__ = "post_comment_replies"
    id         = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("post_comments.id"), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship("User", backref="comment_replies")
    comment    = db.relationship("PostComment",
                    backref=db.backref("replies", cascade="all,delete-orphan", lazy=True))


# ── ADD THIS NEW MODEL ──────────────────────────────────────
class ProfileStats(db.Model):
    """Cached stats for profile — ATS score, coding score, etc."""
    __tablename__ = "profile_stats"
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    ats_score       = db.Column(db.Integer, default=0)
    coding_score    = db.Column(db.Integer, default=0)
    problems_solved = db.Column(db.Integer, default=0)
    skills_count    = db.Column(db.Integer, default=0)
    resume_updated  = db.Column(db.DateTime)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user            = db.relationship("User", backref=db.backref("profile_stats", uselist=False))


# ── UPGRADE PostComment (add parent_id for nested) ──────────
# Add this column to post_comments table via migration:
# parent_id = db.Column(db.Integer, db.ForeignKey("post_comments.id"), nullable=True)

# ═══════════════════════════════════════════════════════════════════════
#  RECRUITER SYSTEM MODELS
#  APPEND these 3 classes to the BOTTOM of backend/models.py
#  Do NOT touch any existing model above.
# ═══════════════════════════════════════════════════════════════════════
import json


class RecruiterJob(db.Model):
    """
    Jobs posted by recruiters through the recruiter panel.
    Separate from JobPosting (which is for scraped/external jobs).
    """
    __tablename__ = "recruiter_jobs"

    id              = db.Column(db.Integer, primary_key=True)
    recruiter_email = db.Column(db.String(200), nullable=False, index=True)
    company_name    = db.Column(db.String(200), nullable=False)
    title           = db.Column(db.String(300), nullable=False)
    description     = db.Column(db.Text,        nullable=False)
    location        = db.Column(db.String(200))
    job_type        = db.Column(db.String(100))        # Full-Time / Intern / Contract
    ctc             = db.Column(db.String(100))        # e.g. "8.44 LPA" or "₹20,000/month"
    deadline        = db.Column(db.DateTime)
    stream_required = db.Column(db.String(300))        # CSE, AIML, etc.
    min_cgpa        = db.Column(db.Float, default=0.0)
    batch           = db.Column(db.String(50))         # 2025, 2026, 2027
    rounds          = db.Column(db.Text)               # JSON list of rounds
    skills_required = db.Column(db.Text)               # comma-separated
    is_active       = db.Column(db.Boolean, default=True)
    allow_messaging = db.Column(db.Boolean, default=False)  # can students reply?
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    applications = db.relationship(
        "JobApplication", backref="job",
        lazy=True, cascade="all, delete-orphan"
    )

    def get_rounds(self):
        try:    return json.loads(self.rounds) if self.rounds else []
        except: return []

    def get_skills(self):
        if not self.skills_required:
            return []
        return [s.strip() for s in self.skills_required.split(",") if s.strip()]

    @property
    def is_expired(self):
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline

    @property
    def applicant_count(self):
        return len(self.applications)


class JobApplication(db.Model):
    """
    Student application to a RecruiterJob.
    Captures all form fields the recruiter asked for.
    """
    __tablename__ = "job_applications"

    id              = db.Column(db.Integer, primary_key=True)
    job_id          = db.Column(db.Integer, db.ForeignKey("recruiter_jobs.id"), nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"),          nullable=False)

    # Academic details
    tenth_percent   = db.Column(db.Float)
    twelfth_percent = db.Column(db.Float)
    cgpa            = db.Column(db.Float)
    degree          = db.Column(db.String(200))
    college         = db.Column(db.String(300))
    school_name     = db.Column(db.String(300))
    batch           = db.Column(db.String(50))
    stream          = db.Column(db.String(200))

    # Extra info
    strengths       = db.Column(db.Text)
    why_hire        = db.Column(db.Text)
    contact_email   = db.Column(db.String(200))
    phone           = db.Column(db.String(20))

    # Resume
    resume_filename = db.Column(db.String(400))   # stored filename
    resume_url      = db.Column(db.String(500))   # path or cloud URL

    # Status & tracking
    status          = db.Column(db.String(50), default="applied")
    # applied | under_review | shortlisted | selected | rejected
    applied_at      = db.Column(db.DateTime, default=datetime.utcnow)
    is_before_deadline = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship("User", backref="job_applications")

    __table_args__ = (
        db.UniqueConstraint("job_id", "user_id", name="unique_job_user_application"),
    )

    @property
    def status_color(self):
        return {
            "applied":       "blue",
            "under_review":  "yellow",
            "shortlisted":   "purple",
            "selected":      "green",
            "rejected":      "red",
        }.get(self.status, "gray")


class RecruiterMessage(db.Model):
    """
    Messages sent FROM recruiter TO a student (or reply if allowed).
    Recruiter is identified by email string, not a User row.
    """
    __tablename__ = "recruiter_messages"

    id               = db.Column(db.Integer, primary_key=True)
    recruiter_email  = db.Column(db.String(200), nullable=False, index=True)
    company_name     = db.Column(db.String(200))
    receiver_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id           = db.Column(db.Integer, db.ForeignKey("recruiter_jobs.id"), nullable=True)
    subject          = db.Column(db.String(300))
    content          = db.Column(db.Text, nullable=False)
    message_type     = db.Column(db.String(50), default="general")
    # general | selected | rejected | interview | offer
    is_read          = db.Column(db.Boolean, default=False)
    allow_reply      = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    receiver = db.relationship("User", backref="recruiter_messages")
    job      = db.relationship("RecruiterJob", backref="messages")

class BattleProfile(db.Model):
    """Per-user Battle Mode stats, XP, trophies, league."""
    __tablename__ = "battle_profiles"
 
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    # XP & Trophy system
    total_xp        = db.Column(db.Integer, default=0)
    battle_xp       = db.Column(db.Integer, default=0)   # XP this season
    trophies        = db.Column(db.Integer, default=0)    # trophy count (wins give +15, loss -3)
    # Win/Loss record
    total_battles   = db.Column(db.Integer, default=0)
    wins            = db.Column(db.Integer, default=0)
    losses          = db.Column(db.Integer, default=0)
    draws           = db.Column(db.Integer, default=0)
    # Streaks
    current_streak  = db.Column(db.Integer, default=0)
    best_streak     = db.Column(db.Integer, default=0)
    # Per-difficulty wins
    easy_wins       = db.Column(db.Integer, default=0)
    medium_wins     = db.Column(db.Integer, default=0)
    hard_wins       = db.Column(db.Integer, default=0)
    # Test cases
    total_tests_passed = db.Column(db.Integer, default=0)
    total_tests_attempted = db.Column(db.Integer, default=0)
    # Timestamps
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 
    user = db.relationship("User", backref=db.backref("battle_profile", uselist=False))
 
 
class BattleHistory(db.Model):
    """Record of every completed battle for a user."""
    __tablename__ = "battle_history"
 
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # Opponent info
    opponent_id     = db.Column(db.Integer, nullable=True)
    opponent_name   = db.Column(db.String(200), default="Unknown")
    # Battle info
    duel_code       = db.Column(db.String(20), nullable=False)
    difficulty      = db.Column(db.String(20), default="easy")
    language        = db.Column(db.String(30), default="python")
    # Problem info
    problem_id      = db.Column(db.String(20), nullable=True)
    problem_title   = db.Column(db.String(300), nullable=True)
    # Result
    result          = db.Column(db.String(20), default="unknown")   # win | loss | draw
    xp_earned       = db.Column(db.Integer, default=0)
    trophies_change = db.Column(db.Integer, default=0)
    tests_passed    = db.Column(db.Integer, default=0)
    total_tests     = db.Column(db.Integer, default=0)
    submitted       = db.Column(db.Boolean, default=False)
    accepted        = db.Column(db.Boolean, default=False)
    # Multi-question data (JSON: list of per-question results)
    questions_data  = db.Column(db.Text, nullable=True)  # JSON
    # Timestamps
    played_at       = db.Column(db.DateTime, default=datetime.utcnow)
 
    user = db.relationship("User", backref="battle_history")


# ══════════════════════════════════════════════════════════════
# APPEND THESE TWO CLASSES TO THE BOTTOM OF backend/models.py
# ══════════════════════════════════════════════════════════════

class Notification(db.Model):
    """
    Universal notification hub.
    types:
      recruiter_message  — a recruiter sent you a message
      job_match          — a new job matches your skills
      battle_invite      — someone challenged you to a battle
      application_update — your application status changed
      hiring_alert       — a company you follow posted a new job
    """
    __tablename__ = "notifications"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    notif_type  = db.Column(db.String(50), nullable=False)   # see types above
    title       = db.Column(db.String(300), nullable=False)
    body        = db.Column(db.Text)
    link        = db.Column(db.String(500))                  # where to go on click
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref="notifications")

    def to_dict(self):
        return {
            "id":         self.id,
            "type":       self.notif_type,
            "title":      self.title,
            "body":       self.body,
            "link":       self.link,
            "is_read":    self.is_read,
            "created_at": self.created_at.strftime("%b %d, %I:%M %p") if self.created_at else "",
        }


class CompanyFollow(db.Model):
    """
    User follows a company to get hiring alerts whenever
    a new RecruiterJob from that company_name is posted.
    """
    __tablename__ = "company_follows"
    __table_args__ = (
        db.UniqueConstraint("user_id", "company_name", name="uq_user_company_follow"),
    )

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company_name = db.Column(db.String(300), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="company_follows")

"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OFFER PREDICTOR — Add these classes to backend/models.py
  Place them at the END of the existing models.py file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ══════════════════════════════════════════════════════════════
#  OFFER PREDICTOR MODELS
# ══════════════════════════════════════════════════════════════

class OfferPrediction(db.Model):
    """Stores each Offer Predictor analysis run by a user."""
    __tablename__ = "offer_predictions"

    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Input
    job_title           = db.Column(db.String(300))
    company_name        = db.Column(db.String(300))
    job_description     = db.Column(db.Text)          # raw JD text or scraped from URL
    job_url             = db.Column(db.String(1000))   # original URL (optional)

    # Core result
    offer_probability   = db.Column(db.Float, default=0.0)   # 0–100 %
    readiness_tier      = db.Column(db.String(50))            # "Strong", "Possible", "Long Shot", "Not Ready"
    verdict_headline    = db.Column(db.String(500))

    # Detailed JSON blobs
    blockers_json       = db.Column(db.Text)    # top 3 things blocking the offer
    strengths_json      = db.Column(db.Text)    # what's already impressive
    gap_plan_json       = db.Column(db.Text)    # 30-day close-the-gap plan
    skill_match_json    = db.Column(db.Text)    # matched vs missing skills
    resume_audit_json   = db.Column(db.Text)    # resume-specific issues
    company_intel_json  = db.Column(db.Text)    # company culture / what they look for
    interview_tips_json = db.Column(db.Text)    # predicted interview questions
    salary_intel_json   = db.Column(db.Text)    # salary data for this role/company
    score_breakdown_json= db.Column(db.Text)    # sub-scores: skills, resume, projects, experience

    # Meta
    coach_message       = db.Column(db.Text)    # personalised brutally honest message
    risk_level          = db.Column(db.String(30))  # "Low", "Medium", "High", "Critical"
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="offer_predictions")

    # ── JSON helpers ──────────────────────────────────────────
    def get_blockers(self):
        try: return json.loads(self.blockers_json) if self.blockers_json else []
        except: return []

    def get_strengths(self):
        try: return json.loads(self.strengths_json) if self.strengths_json else []
        except: return []

    def get_gap_plan(self):
        try: return json.loads(self.gap_plan_json) if self.gap_plan_json else []
        except: return []

    def get_skill_match(self):
        try: return json.loads(self.skill_match_json) if self.skill_match_json else {}
        except: return {}

    def get_resume_audit(self):
        try: return json.loads(self.resume_audit_json) if self.resume_audit_json else []
        except: return []

    def get_company_intel(self):
        try: return json.loads(self.company_intel_json) if self.company_intel_json else {}
        except: return {}

    def get_interview_tips(self):
        try: return json.loads(self.interview_tips_json) if self.interview_tips_json else []
        except: return []

    def get_salary_intel(self):
        try: return json.loads(self.salary_intel_json) if self.salary_intel_json else {}
        except: return {}

    def get_score_breakdown(self):
        try: return json.loads(self.score_breakdown_json) if self.score_breakdown_json else {}
        except: return {}

    def to_dict(self):
        return {
            "id":                self.id,
            "job_title":         self.job_title,
            "company_name":      self.company_name,
            "job_url":           self.job_url,
            "offer_probability": self.offer_probability,
            "readiness_tier":    self.readiness_tier,
            "verdict_headline":  self.verdict_headline,
            "blockers":          self.get_blockers(),
            "strengths":         self.get_strengths(),
            "gap_plan":          self.get_gap_plan(),
            "skill_match":       self.get_skill_match(),
            "resume_audit":      self.get_resume_audit(),
            "company_intel":     self.get_company_intel(),
            "interview_tips":    self.get_interview_tips(),
            "salary_intel":      self.get_salary_intel(),
            "score_breakdown":   self.get_score_breakdown(),
            "coach_message":     self.coach_message,
            "risk_level":        self.risk_level,
            "created_at":        self.created_at.strftime("%d %b %Y, %I:%M %p") if self.created_at else "",
        }