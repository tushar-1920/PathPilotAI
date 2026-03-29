"""
PathPilot AI — Admin Routes (MASSIVE EDITION)
Complete admin control center — every model, every feature, every stat.
"""

from flask import Blueprint, render_template, session, jsonify, request
from backend.extensions import db
from backend.models import (
    User, Resume, JobPosting, Application, SavedJob,
    Skill, SkillCategory, UserSkill,
    Profile, Certificate, Follow, Post, PostLike, PostComment, PostCommentReply,
    Message, Problem, Submission, SolvedProblem,
    AIInterviewSession, AIInterviewMessage,
    CareerTimeMachine, CareerMilestoneProgress,
    BlindSpotReport, ProfileStats,
    RecruiterJob, JobApplication, RecruiterMessage,
)
from backend.utils.auth_decorator import login_required
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func, desc
import json

admin_routes = Blueprint("admin_routes", __name__)


def _is_admin():
    user = User.query.get(session.get("user_id"))
    return user and user.role == "admin"

def _safe(fn, default=0):
    try: return fn()
    except: return default


# ── MAIN PAGE ──────────────────────────────────────────────
@admin_routes.route("/admin")
@login_required
def admin_dashboard():
    if not _is_admin(): return "Unauthorized", 403
    return render_template("admin_dashboard.html")


# ── CORE STATS ─────────────────────────────────────────────
@admin_routes.route("/api/admin/stats")
@login_required
def admin_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403

    total_users  = User.query.count()
    pro_users    = User.query.filter_by(subscription_plan="pro").count()
    monthly_subs = User.query.filter_by(subscription_plan="pro", billing_cycle="monthly").count()
    annual_subs  = User.query.filter_by(subscription_plan="pro", billing_cycle="annual").count()
    verified     = User.query.filter_by(is_verified=True).count()
    admin_count  = User.query.filter_by(role="admin").count()
    mrr = monthly_subs * 19
    arr = annual_subs  * 190

    week_ago      = datetime.utcnow() - timedelta(days=7)
    month_ago     = datetime.utcnow() - timedelta(days=30)
    new_7d        = User.query.filter(User.created_at >= week_ago).count()
    new_30d       = User.query.filter(User.created_at >= month_ago).count()
    prev_w_start  = datetime.utcnow() - timedelta(days=14)
    prev_w_end    = datetime.utcnow() - timedelta(days=7)
    prev_w        = User.query.filter(User.created_at >= prev_w_start, User.created_at < prev_w_end).count()
    growth_rate   = round(((new_7d - prev_w) / max(prev_w,1)) * 100, 1)

    return jsonify({
        "users": {
            "total": total_users, "pro": pro_users,
            "free": total_users - pro_users, "verified": verified,
            "admins": admin_count, "monthly_subs": monthly_subs,
            "annual_subs": annual_subs, "new_7d": new_7d,
            "new_30d": new_30d, "growth_rate": growth_rate,
        },
        "revenue": {
            "mrr": mrr, "arr": arr, "total": mrr + arr,
            "conversion_rate": round(pro_users/max(total_users,1)*100, 1),
        },
        "platform": {
            "resumes":     Resume.query.count(),
            "jobs":        JobPosting.query.count(),
            "applications":Application.query.count(),
            "submissions": _safe(lambda: Submission.query.count()),
            "solved":      _safe(lambda: SolvedProblem.query.count()),
            "posts":       _safe(lambda: Post.query.count()),
            "likes":       _safe(lambda: PostLike.query.count()),
            "comments":    _safe(lambda: PostComment.query.count()),
            "follows":     _safe(lambda: Follow.query.count()),
            "messages":    _safe(lambda: Message.query.count()),
            "certificates":_safe(lambda: Certificate.query.count()),
            "profiles":    _safe(lambda: Profile.query.count()),
        },
        "ai": {
            "interviews_total": _safe(lambda: AIInterviewSession.query.count()),
            "interviews_done":  _safe(lambda: AIInterviewSession.query.filter_by(status="ended").count()),
            "hired":            _safe(lambda: AIInterviewSession.query.filter_by(decision="hire").count()),
            "career_time_machines": _safe(lambda: CareerTimeMachine.query.count()),
            "blind_spot_reports":   _safe(lambda: BlindSpotReport.query.count()),
        },
        "recruiter": {
            "jobs_total":       _safe(lambda: RecruiterJob.query.count()),
            "jobs_active":      _safe(lambda: RecruiterJob.query.filter_by(is_active=True).count()),
            "applications":     _safe(lambda: JobApplication.query.count()),
            "messages_sent":    _safe(lambda: RecruiterMessage.query.count()),
            "students_selected":_safe(lambda: JobApplication.query.filter_by(status="selected").count()),
        },
    })


# ── USER GROWTH (30 days) ──────────────────────────────────
@admin_routes.route("/api/admin/user-growth")
@login_required
def admin_user_growth():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    labels, counts, cumulative = [], [], []
    base = User.query.filter(User.created_at < datetime.utcnow()-timedelta(days=30)).count()
    running = base
    for i in range(29,-1,-1):
        day_start = datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=i)
        day_end   = day_start + timedelta(days=1)
        cnt = User.query.filter(User.created_at >= day_start, User.created_at < day_end).count()
        labels.append(day_start.strftime("%d %b"))
        counts.append(cnt); running += cnt; cumulative.append(running)
    return jsonify({"labels":labels,"daily":counts,"cumulative":cumulative})


# ── REVENUE CHART ──────────────────────────────────────────
@admin_routes.route("/api/admin/revenue-chart")
@login_required
def admin_revenue_chart():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    labels, revenue = [], []
    for i in range(11,-1,-1):
        ms = (datetime.utcnow().replace(day=1,hour=0,minute=0,second=0)-timedelta(days=30*i))
        me = (ms+timedelta(days=31)).replace(day=1)
        m  = User.query.filter(User.subscription_plan=="pro",User.billing_cycle=="monthly",User.created_at<me).count()
        a  = User.query.filter(User.subscription_plan=="pro",User.billing_cycle=="annual", User.created_at<me).count()
        labels.append(ms.strftime("%b %Y")); revenue.append(m*19+a*190)
    return jsonify({"labels":labels,"revenue":revenue})


# ── SUBSCRIPTION BREAKDOWN ─────────────────────────────────
@admin_routes.route("/api/admin/subscription-breakdown")
@login_required
def admin_subscription_breakdown():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    return jsonify({
        "labels":["Free","Pro Monthly","Pro Annual","Enterprise"],
        "values":[User.query.filter_by(subscription_plan="free").count(),
                  User.query.filter_by(subscription_plan="pro",billing_cycle="monthly").count(),
                  User.query.filter_by(subscription_plan="pro",billing_cycle="annual").count(),
                  User.query.filter_by(subscription_plan="enterprise").count()],
        "colors":["#64748b","#5b6bff","#00e5c8","#a855f7"],
    })


# ── PLATFORM ACTIVITY (14 days) ────────────────────────────
@admin_routes.route("/api/admin/platform-activity")
@login_required
def admin_platform_activity():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    labels,res,subs,posts,ivs=[],[],[],[],[]
    for i in range(13,-1,-1):
        ds = datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=i)
        de = ds+timedelta(days=1)
        labels.append(ds.strftime("%d %b"))
        res.append(Resume.query.filter(Resume.uploaded_at>=ds,Resume.uploaded_at<de).count())
        subs.append(_safe(lambda: Submission.query.filter(Submission.created_at>=ds,Submission.created_at<de).count()))
        posts.append(_safe(lambda: Post.query.filter(Post.created_at>=ds,Post.created_at<de).count()))
        ivs.append(_safe(lambda: AIInterviewSession.query.filter(AIInterviewSession.created_at>=ds,AIInterviewSession.created_at<de).count()))
    return jsonify({"labels":labels,"resumes":res,"submissions":subs,"posts":posts,"interviews":ivs})


# ── TOP SKILLS ─────────────────────────────────────────────
@admin_routes.route("/api/admin/top-skills")
@login_required
def admin_top_skills():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    all_skills = []
    for u in User.query.filter(User.normalized_skills.isnot(None)).all():
        all_skills.extend([s.strip() for s in u.normalized_skills.split(",") if s.strip()])
    top20 = Counter(all_skills).most_common(20)
    return jsonify({"labels":[s[0] for s in top20],"counts":[s[1] for s in top20]})


# ── ALL USERS (paginated + search) ────────────────────────
@admin_routes.route("/api/admin/users")
@login_required
def admin_users_list():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    page = int(request.args.get("page",1))
    q    = request.args.get("q","").strip()
    plan = request.args.get("plan","")
    per  = 20
    query = User.query
    if q:    query = query.filter((User.name.ilike(f"%{q}%"))|(User.email.ilike(f"%{q}%")))
    if plan: query = query.filter_by(subscription_plan=plan)
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page-1)*per).limit(per).all()
    result = []
    for u in users:
        p = _safe(lambda: Profile.query.filter_by(user_id=u.id).first(), None)
        skill_count = len([s.strip() for s in (u.normalized_skills or "").split(",") if s.strip()])
        result.append({
            "id":u.id,"name":u.name,"email":u.email,
            "plan":u.subscription_plan or "free","verified":u.is_verified,
            "joined":u.created_at.strftime("%d %b %Y") if u.created_at else "—",
            "role":u.role or "user","skills":skill_count,
            "headline":p.headline if p else "",
            "resumes":_safe(lambda: Resume.query.filter_by(user_id=u.id).count()),
            "posts":_safe(lambda: Post.query.filter_by(user_id=u.id).count()),
            "interviews":_safe(lambda: AIInterviewSession.query.filter_by(user_id=u.id).count()),
            "solved":_safe(lambda: SolvedProblem.query.filter_by(user_id=u.id).count()),
        })
    return jsonify({"users":result,"total":total,"page":page,"pages":(total+per-1)//per})


# ── RECENT USERS ───────────────────────────────────────────
@admin_routes.route("/api/admin/recent-users")
@login_required
def admin_recent_users():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    users = User.query.order_by(User.created_at.desc()).limit(15).all()
    result = []
    for u in users:
        p = _safe(lambda: Profile.query.filter_by(user_id=u.id).first(), None)
        skill_count = len([s.strip() for s in (u.normalized_skills or "").split(",") if s.strip()])
        result.append({
            "id":u.id,"name":u.name,"email":u.email,
            "plan":u.subscription_plan or "free","verified":u.is_verified,
            "joined":u.created_at.strftime("%d %b %Y") if u.created_at else "—",
            "role":u.role or "user","skills":skill_count,
            "headline":p.headline if p else "",
            "resumes":_safe(lambda: Resume.query.filter_by(user_id=u.id).count()),
        })
    return jsonify(result)


# ── SINGLE USER DEEP DIVE ──────────────────────────────────
@admin_routes.route("/api/admin/user/<int:uid>")
@login_required
def admin_user_detail(uid):
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    u  = User.query.get_or_404(uid)
    p  = _safe(lambda: Profile.query.filter_by(user_id=uid).first(), None)
    resumes    = Resume.query.filter_by(user_id=uid).all()
    posts      = Post.query.filter_by(user_id=uid).order_by(Post.created_at.desc()).limit(10).all()
    certs      = Certificate.query.filter_by(user_id=uid).all()
    followers  = _safe(lambda: Follow.query.filter_by(following_id=uid).count())
    following  = _safe(lambda: Follow.query.filter_by(follower_id=uid).count())
    solved     = _safe(lambda: SolvedProblem.query.filter_by(user_id=uid).count())
    submissions= _safe(lambda: Submission.query.filter_by(user_id=uid).count())
    ivs        = _safe(lambda: AIInterviewSession.query.filter_by(user_id=uid).order_by(AIInterviewSession.created_at.desc()).limit(5).all(), [])
    ctm        = _safe(lambda: CareerTimeMachine.query.filter_by(user_id=uid).first(), None)
    blind      = _safe(lambda: BlindSpotReport.query.filter_by(user_id=uid).order_by(BlindSpotReport.created_at.desc()).first(), None)
    rec_apps   = _safe(lambda: JobApplication.query.filter_by(user_id=uid).all(), [])
    rec_msgs   = _safe(lambda: RecruiterMessage.query.filter_by(receiver_id=uid).count())
    skills_list= [s.strip() for s in (u.normalized_skills or "").split(",") if s.strip()]

    ats=comp=readiness=percentile=0; dominant_role=""
    try:
        from backend.services.elite_scoring_engine import EliteScoringEngine
        if skills_list:
            e=EliteScoringEngine(); el=e.compute_score(skills_list); n=len(skills_list)
            comp=int(el["competitive_score"])
            kw=min(40.0,round(n*3.5 if n<=5 else 17.5+(n-5)*2.2 if n<=12 else 33+(n-12)*0.7 if n<=22 else 40.0, 1))
            mkt=min(30.0,round((el["market_score"]/25)*min(1,n/15)*30,1))
            stk=min(20.0,round((el["stack_completeness"]/20)*20,1))
            div=min(10.0,round((el["diversity_score"]/15)*10,1))
            ats=min(100,int(kw+mkt+stk+div)); readiness=min(100,int(comp*0.5+ats*0.3))
            dominant_role=el.get("dominant_role","")
            percentile=(95 if comp>=90 else 85 if comp>=80 else 72 if comp>=70 else 58 if comp>=60
                        else 44 if comp>=50 else 28 if comp>=35 else max(5,int(comp*0.4)))
    except: pass

    return jsonify({
        "user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role,
                "plan":u.subscription_plan or "free","verified":u.is_verified,
                "joined":u.created_at.strftime("%d %b %Y %H:%M") if u.created_at else "—"},
        "profile":{"headline":p.headline if p else "","bio":p.bio if p else "",
                   "location":p.location if p else "","username":p.username if p else "",
                   "github":p.github if p else "","linkedin":p.linkedin if p else "",
                   "has_image":bool(p and p.profile_image)} if p else {},
        "scores":{"ats":ats,"competitive":comp,"readiness":readiness,
                  "percentile":percentile,"dominant_role":dominant_role},
        "activity":{"resumes":len(resumes),"posts":len(posts),"certs":len(certs),
                    "followers":followers,"following":following,
                    "submissions":submissions,"solved":solved,
                    "interviews":len(ivs) if isinstance(ivs,list) else 0,
                    "recruiter_apps":len(rec_apps),"recruiter_msgs":rec_msgs,
                    "has_ctm":bool(ctm),"blind_spots":bool(blind)},
        "skills":skills_list[:30],
        "resumes":[{"filename":r.filename,"score":r.skill_score,
                    "uploaded":r.uploaded_at.strftime("%d %b %Y") if r.uploaded_at else "—"} for r in resumes],
        "posts":[{"content":po.content[:120],"type":po.post_type,
                  "likes":len(po.likes),"created":po.created_at.strftime("%d %b") if po.created_at else ""} for po in posts],
        "certs":[{"title":c.title,"issuer":c.issuer} for c in certs],
        "interviews":[{"role":s.role,"level":s.level,"status":s.status,
                       "decision":s.decision or "—","score":round(s.live_score,1),
                       "date":s.created_at.strftime("%d %b %Y") if s.created_at else ""} for s in (ivs if isinstance(ivs,list) else [])],
        "ctm":{"target_role":ctm.target_role,"target_company":ctm.target_company,"timeline":ctm.timeline_months} if ctm else None,
        "recruiter_apps":[{"job":a.job.title if a.job else "—","status":a.status,
                           "cgpa":a.cgpa,"college":a.college,
                           "applied":a.applied_at.strftime("%d %b %Y") if a.applied_at else "—"} for a in rec_apps],
    })


# ── SOCIAL ANALYTICS ───────────────────────────────────────
@admin_routes.route("/api/admin/social-stats")
@login_required
def admin_social_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    total_posts  = _safe(lambda: Post.query.count())
    total_likes  = _safe(lambda: PostLike.query.count())
    total_cmts   = _safe(lambda: PostComment.query.count())
    total_replies= _safe(lambda: PostCommentReply.query.count())
    total_follows= _safe(lambda: Follow.query.count())
    total_msgs   = _safe(lambda: Message.query.count())

    post_types = {}
    try:
        for pt in ["text","achievement","milestone","image"]:
            post_types[pt] = Post.query.filter_by(post_type=pt).count()
    except: pass

    top_posters = []
    try:
        rows = db.session.query(Post.user_id,func.count(Post.id).label("cnt"))\
               .group_by(Post.user_id).order_by(func.count(Post.id).desc()).limit(5).all()
        for uid,cnt in rows:
            u=User.query.get(uid)
            if u: top_posters.append({"name":u.name,"posts":cnt})
    except: pass

    top_followed = []
    try:
        rows = db.session.query(Follow.following_id,func.count(Follow.id).label("cnt"))\
               .group_by(Follow.following_id).order_by(func.count(Follow.id).desc()).limit(5).all()
        for uid,cnt in rows:
            u=User.query.get(uid)
            if u: top_followed.append({"name":u.name,"followers":cnt})
    except: pass

    posts_daily,labels_14=[],[]
    try:
        for i in range(13,-1,-1):
            ds=datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=i)
            de=ds+timedelta(days=1)
            posts_daily.append(Post.query.filter(Post.created_at>=ds,Post.created_at<de).count())
            labels_14.append(ds.strftime("%d %b"))
    except: pass

    return jsonify({
        "totals":{"posts":total_posts,"likes":total_likes,"comments":total_cmts,
                  "replies":total_replies,"follows":total_follows,"messages":total_msgs},
        "post_types":post_types,"top_posters":top_posters,"top_followed":top_followed,
        "posts_daily":posts_daily,"labels_14":labels_14,
        "avg_likes_per_post":round(total_likes/max(total_posts,1),2),
    })


# ── AI INTERVIEW ANALYTICS ─────────────────────────────────
@admin_routes.route("/api/admin/interview-stats")
@login_required
def admin_interview_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    total     = _safe(lambda: AIInterviewSession.query.count())
    completed = _safe(lambda: AIInterviewSession.query.filter_by(status="ended").count())
    active    = _safe(lambda: AIInterviewSession.query.filter_by(status="active").count())
    hired     = _safe(lambda: AIInterviewSession.query.filter_by(decision="hire").count())
    rejected  = _safe(lambda: AIInterviewSession.query.filter_by(decision="reject").count())
    maybe     = _safe(lambda: AIInterviewSession.query.filter_by(decision="maybe").count())

    avg_score=0
    try:
        scores=[s.live_score for s in AIInterviewSession.query.filter_by(status="ended").all() if s.live_score]
        avg_score=round(sum(scores)/len(scores),1) if scores else 0
    except: pass

    role_counts={}
    try:
        rows=db.session.query(AIInterviewSession.role,func.count(AIInterviewSession.id))\
             .group_by(AIInterviewSession.role).order_by(func.count(AIInterviewSession.id).desc()).limit(8).all()
        role_counts={r:c for r,c in rows}
    except: pass

    level_counts={}
    try:
        rows=db.session.query(AIInterviewSession.level,func.count(AIInterviewSession.id))\
             .group_by(AIInterviewSession.level).all()
        level_counts={l:c for l,c in rows}
    except: pass

    personality_counts={}
    try:
        rows=db.session.query(AIInterviewSession.personality,func.count(AIInterviewSession.id))\
             .group_by(AIInterviewSession.personality).all()
        personality_counts={p:c for p,c in rows}
    except: pass

    labels,daily=[],[]
    try:
        for i in range(13,-1,-1):
            ds=datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=i)
            de=ds+timedelta(days=1)
            labels.append(ds.strftime("%d %b"))
            daily.append(AIInterviewSession.query.filter(AIInterviewSession.created_at>=ds,AIInterviewSession.created_at<de).count())
    except: pass

    recent=[]
    try:
        sessions=AIInterviewSession.query.order_by(AIInterviewSession.created_at.desc()).limit(8).all()
        for s in sessions:
            u=User.query.get(s.user_id)
            recent.append({"name":u.name if u else "Unknown","role":s.role,"level":s.level,
                           "status":s.status,"decision":s.decision or "—","score":round(s.live_score,1),
                           "date":s.created_at.strftime("%d %b %Y") if s.created_at else "—"})
    except: pass

    return jsonify({
        "totals":{"total":total,"completed":completed,"active":active,
                  "hired":hired,"rejected":rejected,"maybe":maybe},
        "avg_score":avg_score,"hire_rate":round(hired/max(completed,1)*100,1),
        "completion_rate":round(completed/max(total,1)*100,1),
        "role_counts":role_counts,"level_counts":level_counts,
        "personality_counts":personality_counts,"labels":labels,"daily":daily,"recent":recent,
    })


# ── RECRUITER ANALYTICS ────────────────────────────────────
@admin_routes.route("/api/admin/recruiter-stats")
@login_required
def admin_recruiter_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403

    total_jobs  = _safe(lambda: RecruiterJob.query.count())
    active_jobs = _safe(lambda: RecruiterJob.query.filter_by(is_active=True).count())
    total_apps  = _safe(lambda: JobApplication.query.count())
    selected    = _safe(lambda: JobApplication.query.filter_by(status="selected").count())
    rejected    = _safe(lambda: JobApplication.query.filter_by(status="rejected").count())
    shortlisted = _safe(lambda: JobApplication.query.filter_by(status="shortlisted").count())
    total_msgs  = _safe(lambda: RecruiterMessage.query.count())
    read_msgs   = _safe(lambda: RecruiterMessage.query.filter_by(is_read=True).count())

    top_companies=[]
    try:
        rows=db.session.query(RecruiterJob.company_name,func.count(RecruiterJob.id))\
             .group_by(RecruiterJob.company_name).order_by(func.count(RecruiterJob.id).desc()).limit(8).all()
        for company,cnt in rows:
            top_companies.append({"company":company,"jobs":cnt})
    except: pass

    status_counts={}
    try:
        for s in ["applied","under_review","shortlisted","selected","rejected"]:
            status_counts[s]=JobApplication.query.filter_by(status=s).count()
    except: pass

    top_colleges=[]
    try:
        rows=db.session.query(JobApplication.college,func.count(JobApplication.id))\
             .filter(JobApplication.college.isnot(None),JobApplication.college!="")\
             .group_by(JobApplication.college).order_by(func.count(JobApplication.id).desc()).limit(8).all()
        top_colleges=[{"college":c,"count":n} for c,n in rows if c]
    except: pass

    avg_cgpa=0
    try:
        cgpas=[a.cgpa for a in JobApplication.query.all() if a.cgpa]
        avg_cgpa=round(sum(cgpas)/len(cgpas),2) if cgpas else 0
    except: pass

    top_jobs=[]
    try:
        rows=db.session.query(JobApplication.job_id,func.count(JobApplication.id).label("cnt"))\
             .group_by(JobApplication.job_id).order_by(func.count(JobApplication.id).desc()).limit(6).all()
        for jid,cnt in rows:
            j=RecruiterJob.query.get(jid)
            if j: top_jobs.append({"title":j.title,"company":j.company_name,"apps":cnt})
    except: pass

    msg_types={}
    try:
        for mt in ["general","selected","rejected","interview","offer"]:
            msg_types[mt]=RecruiterMessage.query.filter_by(message_type=mt).count()
    except: pass

    recent_jobs=[]
    try:
        jobs=RecruiterJob.query.order_by(RecruiterJob.created_at.desc()).limit(8).all()
        for j in jobs:
            recent_jobs.append({"title":j.title,"company":j.company_name,"type":j.job_type,
                                 "active":j.is_active,"apps":len(j.applications),
                                 "posted":j.created_at.strftime("%d %b %Y") if j.created_at else "—"})
    except: pass

    return jsonify({
        "totals":{"jobs":total_jobs,"active_jobs":active_jobs,"applications":total_apps,
                  "selected":selected,"rejected":rejected,"shortlisted":shortlisted,
                  "messages":total_msgs,"read_msgs":read_msgs},
        "selection_rate":round(selected/max(total_apps,1)*100,1),
        "msg_read_rate":round(read_msgs/max(total_msgs,1)*100,1),
        "avg_cgpa":avg_cgpa,"top_companies":top_companies,"status_counts":status_counts,
        "top_colleges":top_colleges,"top_jobs":top_jobs,"msg_types":msg_types,"recent_jobs":recent_jobs,
    })


# ── CODING STATS ───────────────────────────────────────────
@admin_routes.route("/api/admin/coding-stats")
@login_required
def admin_coding_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    try:
        total_subs   = Submission.query.count()
        accepted     = Submission.query.filter_by(status="Accepted").count()
        wrong        = Submission.query.filter_by(status="Wrong Answer").count()
        tle          = Submission.query.filter_by(status="Time Limit Exceeded").count()
        error        = Submission.query.filter_by(status="Runtime Error").count()
        total_solved = SolvedProblem.query.count()
        acc_rate     = round(accepted/max(total_subs,1)*100,1)

        lang_counts={}
        rows=db.session.query(Submission.language,func.count(Submission.id))\
             .group_by(Submission.language).order_by(func.count(Submission.id).desc()).all()
        lang_counts={l:c for l,c in rows}

        top_users=[]
        rows=db.session.query(Submission.user_id,func.count(Submission.id).label("cnt"))\
             .group_by(Submission.user_id).order_by(func.count(Submission.id).desc()).limit(8).all()
        for uid,cnt in rows:
            u=User.query.get(uid)
            slvd=_safe(lambda: SolvedProblem.query.filter_by(user_id=uid).count())
            if u: top_users.append({"name":u.name,"email":u.email,"submissions":cnt,"solved":slvd})

        top_problems=[]
        rows=db.session.query(Submission.problem_id,func.count(Submission.id).label("cnt"))\
             .group_by(Submission.problem_id).order_by(func.count(Submission.id).desc()).limit(6).all()
        for pid,cnt in rows:
            prob=Problem.query.get(pid)
            if prob: top_problems.append({"title":prob.title,"difficulty":prob.difficulty,"attempts":cnt})

        try:
            from backend.services.problem_service import get_difficulty_stats
            problem_stats=get_difficulty_stats()
        except: problem_stats={}

        return jsonify({
            "total_submissions":total_subs,"accepted":accepted,"wrong_answer":wrong,
            "tle":tle,"runtime_error":error,"acceptance_rate":acc_rate,"total_solved":total_solved,
            "lang_counts":lang_counts,"problem_counts":problem_stats,
            "top_submitters":top_users,"top_problems":top_problems,
            "status_labels":["Accepted","Wrong Answer","TLE","Runtime Error"],
            "status_values":[accepted,wrong,tle,error],
            "status_colors":["#22c55e","#ff5757","#ffb547","#a855f7"],
        })
    except Exception as e:
        return jsonify({"error":str(e),"total_submissions":0,"accepted":0,"wrong_answer":0,
                        "tle":0,"runtime_error":0,"acceptance_rate":0,"total_solved":0,
                        "lang_counts":{},"problem_counts":{},"top_submitters":[],"top_problems":[],
                        "status_labels":[],"status_values":[],"status_colors":[]})


# ── RESUME STATS ───────────────────────────────────────────
@admin_routes.route("/api/admin/resume-stats")
@login_required
def admin_resume_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    total=Resume.query.count()
    scores=[r.skill_score for r in Resume.query.all() if r.skill_score]
    avg=round(sum(scores)/len(scores),1) if scores else 0
    buckets={"0-25":0,"26-50":0,"51-75":0,"76-100":0}
    for s in scores:
        if s<=25: buckets["0-25"]+=1
        elif s<=50: buckets["26-50"]+=1
        elif s<=75: buckets["51-75"]+=1
        else: buckets["76-100"]+=1
    labels,daily=[],[]
    for i in range(13,-1,-1):
        ds=datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=i)
        de=ds+timedelta(days=1)
        labels.append(ds.strftime("%d %b"))
        daily.append(Resume.query.filter(Resume.uploaded_at>=ds,Resume.uploaded_at<de).count())
    return jsonify({"total":total,"avg_score":avg,"buckets":buckets,
                    "high_score":max(scores) if scores else 0,"low_score":min(scores) if scores else 0,
                    "labels":labels,"daily":daily})


# ── JOB STATS ──────────────────────────────────────────────
@admin_routes.route("/api/admin/job-stats")
@login_required
def admin_job_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    total_jobs=JobPosting.query.count(); total_apps=Application.query.count()
    status_counts=Counter([a.status or "unknown" for a in Application.query.all()])
    sources=Counter([j.source for j in JobPosting.query.all() if j.source])
    roles=Counter([j.role for j in JobPosting.query.all() if j.role])
    return jsonify({"total_jobs":total_jobs,"total_apps":total_apps,"status_counts":dict(status_counts),
                    "top_sources":[{"source":k,"count":v} for k,v in sources.most_common(6)],
                    "top_roles":[{"role":k,"count":v} for k,v in roles.most_common(8)]})


# ── AI TOOLS (CTM + BLIND SPOT) ────────────────────────────
@admin_routes.route("/api/admin/ai-tools-stats")
@login_required
def admin_ai_tools_stats():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    ctm_total  = _safe(lambda: CareerTimeMachine.query.count())
    ctm_active = _safe(lambda: CareerTimeMachine.query.filter_by(is_active=True).count())
    top_roles=[]; top_companies=[]; timeline_dist={}
    try:
        rows=db.session.query(CareerTimeMachine.target_role,func.count(CareerTimeMachine.id))\
             .group_by(CareerTimeMachine.target_role).order_by(func.count(CareerTimeMachine.id).desc()).limit(8).all()
        top_roles=[{"role":r,"count":c} for r,c in rows]
        rows2=db.session.query(CareerTimeMachine.target_company,func.count(CareerTimeMachine.id))\
              .filter(CareerTimeMachine.target_company.isnot(None),CareerTimeMachine.target_company!="")\
              .group_by(CareerTimeMachine.target_company).order_by(func.count(CareerTimeMachine.id).desc()).limit(6).all()
        top_companies=[{"company":c,"count":n} for c,n in rows2 if c]
        for t in [12,24,36]: timeline_dist[str(t)]=CareerTimeMachine.query.filter_by(timeline_months=t).count()
    except: pass

    bs_total=_safe(lambda: BlindSpotReport.query.count()); avg_bs=0; avg_shock=0
    try:
        scores=[r.overall_score for r in BlindSpotReport.query.all() if r.overall_score]
        avg_bs=round(sum(scores)/len(scores),1) if scores else 0
        shocks=[r.shock_factor for r in BlindSpotReport.query.all() if r.shock_factor]
        avg_shock=round(sum(shocks)/len(shocks),1) if shocks else 0
    except: pass

    return jsonify({
        "ctm":{"total":ctm_total,"active":ctm_active,"top_roles":top_roles,
               "top_companies":top_companies,"timeline_dist":timeline_dist},
        "blind_spot":{"total":bs_total,"avg_score":avg_bs,"avg_shock":avg_shock},
    })


# ── HEALTH CHECK ───────────────────────────────────────────
@admin_routes.route("/api/admin/health")
@login_required
def admin_health():
    if not _is_admin(): return jsonify({"error": "Unauthorized"}), 403
    checks={}
    def chk(key,label,fn):
        try: fn(); checks[key]={"status":"ok","label":label,"detail":"Operational"}
        except Exception as e: checks[key]={"status":"error","label":label,"detail":str(e)[:60]}
    chk("database","Database",lambda: User.query.count())
    chk("coding","Coding Module",lambda: Submission.query.count())
    chk("jobs","Job Engine",lambda: JobPosting.query.count())
    chk("recruiter","Recruiter System",lambda: RecruiterJob.query.count())
    chk("social","Social/Posts",lambda: Post.query.count())
    chk("interviews","AI Interviews",lambda: AIInterviewSession.query.count())
    chk("ctm","Career Time Machine",lambda: CareerTimeMachine.query.count())
    chk("blind_spot","Blind Spot Detector",lambda: BlindSpotReport.query.count())
    try:
        from backend.services.resume_service import ResumeService
        checks["ai_service"]={"status":"ok","label":"AI Resume Service","detail":"Loaded"}
    except: checks["ai_service"]={"status":"warning","label":"AI Resume Service","detail":"Not loaded"}
    try:
        from backend.services.elite_scoring_engine import EliteScoringEngine
        checks["scoring"]={"status":"ok","label":"Elite Scoring Engine","detail":"Operational"}
    except: checks["scoring"]={"status":"warning","label":"Elite Scoring Engine","detail":"Not loaded"}
    all_ok=all(v["status"]=="ok" for v in checks.values())
    return jsonify({"overall":"healthy" if all_ok else "degraded",
                    "checks":checks,"timestamp":datetime.utcnow().isoformat()})