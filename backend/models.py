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