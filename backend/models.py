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

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), default="user")

    is_verified = db.Column(db.Boolean, default=False)

    normalized_skills = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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