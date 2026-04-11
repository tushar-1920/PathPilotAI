from flask import Blueprint, jsonify, render_template, session, request, redirect, url_for
from backend.utils.auth_decorator import login_required
from backend.services.user_profile_service import ProfileService
from backend.services.social_service import SocialService
from backend.services.post_service import PostService
from backend.models import (User, Profile, Certificate, Follow, Post,
                             PostLike, PostComment, Message, db)
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import or_
import os

profile_routes = Blueprint("profile_routes", __name__)
profile_svc    = ProfileService()
social_svc     = SocialService()
post_svc       = PostService()

UPLOAD_FOLDER      = os.path.join("frontend", "static", "uploads", "profile_images")
COVER_FOLDER       = os.path.join("frontend", "static", "uploads", "cover_images")
POST_UPLOAD_FOLDER = os.path.join("frontend", "static", "uploads", "post_images")
CERT_UPLOAD_FOLDER = os.path.join("frontend", "static", "uploads", "cert_images")
ALLOWED_EXT        = {"png", "jpg", "jpeg", "webp", "gif"}


# ════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════

def _allowed(f):
    return "." in f and f.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def _profile_image_url(p):
    return f"/static/{p.profile_image}" if p and p.profile_image else None


def _safe_skills(user):
    try:
        raw = getattr(user, "normalized_skills", None) or getattr(user, "skills", None) or ""
        return [s.strip() for s in raw.split(",") if s.strip()]
    except Exception:
        return []


def _get_all_scores(user_id):
    """
    Compute all dashboard scores using the real EliteScoringEngine —
    exactly the same way dashboard_routes.py does it.
    Returns: (ats_score, competitive_score, readiness_score, percentile, role_fit_pct, dominant_role)
    """
    try:
        from backend.services.elite_scoring_engine import EliteScoringEngine
        user = User.query.get(user_id)
        if not user or not user.normalized_skills:
            return 0, 0, 0, 0, 0, ""

        skills   = [s.strip() for s in user.normalized_skills.split(",") if s.strip()]
        n_skills = len(skills)
        if n_skills == 0:
            return 0, 0, 0, 0, 0, ""

        engine     = EliteScoringEngine()
        elite      = engine.compute_score(skills)
        comp_score = elite["competitive_score"]

        # ── ATS Score (same formula as dashboard_routes) ──
        if   n_skills <= 5:  kw = n_skills * 3.5
        elif n_skills <= 12: kw = 17.5 + (n_skills - 5) * 2.2
        elif n_skills <= 22: kw = 33.0 + (n_skills - 12) * 0.7
        elif n_skills <= 35: kw = 40.0
        else:                kw = max(34.0, 40.0 - (n_skills - 35) * 0.3)
        kw  = min(40.0, round(kw, 1))
        mkt = min(30.0, round((elite["market_score"] / 25.0) * min(1.0, n_skills / 15.0) * 30.0, 1))
        stk = min(20.0, round((elite["stack_completeness"] / 20.0) * 20.0, 1))
        div = min(10.0, round((elite["diversity_score"] / 15.0) * 10.0, 1))
        ats_score = min(100, int(kw + mkt + stk + div))

        # ── Role fit ──────────────────────────────────────
        role_fit_pct  = min(97, int(comp_score * 0.65 + min(n_skills * 2, 30) + 5))
        dominant_role = elite.get("dominant_role", "")

        # ── Readiness ─────────────────────────────────────
        readiness = min(100, int(comp_score * 0.5 + ats_score * 0.3 + role_fit_pct * 0.2))

        # ── Percentile ────────────────────────────────────
        if   comp_score >= 90: percentile = 95
        elif comp_score >= 80: percentile = 85
        elif comp_score >= 70: percentile = 72
        elif comp_score >= 60: percentile = 58
        elif comp_score >= 50: percentile = 44
        elif comp_score >= 35: percentile = 28
        else:                  percentile = max(5, int(comp_score * 0.4))

        return ats_score, int(comp_score), readiness, percentile, role_fit_pct, dominant_role

    except Exception as e:
        print(f"[ProfileScores] {e}")
        return 0, 0, 0, 0, 0, ""


def _get_coding_stats(user_id):
    """Count problems solved — tries SolvedProblem then CodingSubmission then Submission."""
    # Strategy 1 — dedicated SolvedProblem model
    try:
        from backend.models import SolvedProblem
        return SolvedProblem.query.filter_by(user_id=user_id).count()
    except Exception:
        pass
    # Strategy 2 — CodingSubmission model
    try:
        from backend.models import CodingSubmission
        return CodingSubmission.query.filter_by(
            user_id=user_id, status="accepted"
        ).distinct(CodingSubmission.problem_id).count()
    except Exception:
        pass
    # Strategy 3 — generic Submission model
    try:
        from backend.models import Submission
        return Submission.query.filter_by(
            user_id=user_id, status="Accepted"
        ).distinct(Submission.problem_id).count()
    except Exception:
        return 0


# ════════════════════════════════════════════════════════════
#  PAGES
# ════════════════════════════════════════════════════════════

@profile_routes.route("/profile")
@login_required
def my_profile():
    return redirect(url_for("profile_routes.view_profile", user_id=session["user_id"]))


@profile_routes.route("/profile/<int:user_id>")
@login_required
def view_profile(user_id):
    user    = User.query.get_or_404(user_id)
    me      = session.get("user_id")
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile and user_id == me:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()

    certs           = Certificate.query.filter_by(user_id=user_id).order_by(Certificate.id.desc()).all()
    posts           = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).limit(20).all()
    followers_count = Follow.query.filter_by(following_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=user_id).count()
    is_following    = (
        Follow.query.filter_by(follower_id=me, following_id=user_id).first() is not None
        if me and me != user_id else False
    )
    unread_from = (
        Message.query.filter_by(sender_id=user_id, receiver_id=me, is_read=False).count()
        if me else 0
    )

    # ── All scores via EliteScoringEngine (same as dashboard) ──
    skills_list   = _safe_skills(user)
    coding_solved = _get_coding_stats(user_id)
    (ats_score, competitive_score,
     readiness_score, percentile,
     role_fit_pct, dominant_role) = _get_all_scores(user_id)

    # ── Post likes by current user ──
    liked_post_ids = set()
    if me:
        liked_post_ids = {l.post_id for l in PostLike.query.filter_by(user_id=me).all()}

    # ── Comments per post (top 3) with replies ──
    post_comments = {}
    for p in posts:
        cmts = PostComment.query.filter_by(post_id=p.id).order_by(PostComment.created_at.asc()).limit(3).all()
        for c in cmts:
            try:
                from backend.models import PostCommentReply
                c.replies = PostCommentReply.query.filter_by(
                    comment_id=c.id
                ).order_by(PostCommentReply.created_at.asc()).all()
            except Exception:
                c.replies = []
        post_comments[p.id] = cmts

    return render_template("profile.html",
        user=user, profile=profile, certs=certs or [], posts=posts or [],
        followers_count=followers_count or 0, following_count=following_count or 0,
        is_following=is_following, is_own=(me == user_id),
        resume_skills=skills_list, unread_from=unread_from,
        # ── score cards ──
        ats_score=ats_score,
        competitive_score=competitive_score,
        readiness_score=readiness_score,
        percentile=percentile,
        role_fit_pct=role_fit_pct,
        dominant_role=dominant_role,
        coding_solved=coding_solved,
        # ── social ──
        liked_post_ids=liked_post_ids,
        post_comments=post_comments,
        profile_image_url=_profile_image_url(profile),
        me=me,
    )


@profile_routes.route("/edit-profile")
@login_required
def edit_profile_page():
    uid  = session["user_id"]
    user = User.query.get(uid)
    prof = Profile.query.filter_by(user_id=uid).first()
    if not prof:
        prof = Profile(user_id=uid)
        db.session.add(prof)
        db.session.commit()
    certs = Certificate.query.filter_by(user_id=uid).order_by(Certificate.id.desc()).all()
    return render_template("edit_profile.html",
        user=user, profile=prof, certs=certs or [],
        resume_skills=_safe_skills(user))


@profile_routes.route("/feed")
@login_required
def feed_page():
    me = session["user_id"]
    return render_template("feed.html", user=User.query.get(me))


@profile_routes.route("/search")
@login_required
def search_page():
    return render_template("search_users.html", user=User.query.get(session["user_id"]))


@profile_routes.route("/messages")
@login_required
def messages_page():
    me = session["user_id"]

    sent_ids     = db.session.query(Message.receiver_id).filter_by(sender_id=me).distinct()
    received_ids = db.session.query(Message.sender_id).filter_by(receiver_id=me).distinct()
    partner_ids  = {r[0] for r in sent_ids} | {r[0] for r in received_ids}

    conversations = []
    for uid in partner_ids:
        u    = User.query.get(uid)
        prof = Profile.query.filter_by(user_id=uid).first()
        if not u:
            continue
        last_msg = Message.query.filter(
            or_(
                db.and_(Message.sender_id == me,  Message.receiver_id == uid),
                db.and_(Message.sender_id == uid, Message.receiver_id == me),
            )
        ).order_by(Message.created_at.desc()).first()
        unread = Message.query.filter_by(
            sender_id=uid, receiver_id=me, is_read=False
        ).count()
        conversations.append({
            "user_id":   uid,
            "name":      u.name,
            "username":  prof.username if prof else None,
            "image":     _profile_image_url(prof),
            "last_msg":  last_msg.content[:60] if last_msg else "",
            "last_time": last_msg.created_at.strftime("%b %d") if last_msg and last_msg.created_at else "",
            "unread":    unread,
        })
    conversations.sort(key=lambda x: x["last_time"], reverse=True)

    return render_template("messages.html",
        user=User.query.get(me),
        conversations=conversations)


@profile_routes.route("/messages/<int:uid>")
@login_required
def chat_page(uid):
    me            = session["user_id"]
    other         = User.query.get_or_404(uid)
    other_profile = Profile.query.filter_by(user_id=uid).first()

    msgs = Message.query.filter(
        or_(
            db.and_(Message.sender_id == me,  Message.receiver_id == uid),
            db.and_(Message.sender_id == uid, Message.receiver_id == me),
        )
    ).order_by(Message.created_at.asc()).all()

    Message.query.filter_by(
        sender_id=uid, receiver_id=me, is_read=False
    ).update({"is_read": True})
    db.session.commit()

    return render_template("chat.html",
        other=other,
        other_profile=other_profile,
        messages=msgs,
        user=User.query.get(me),
        me=me)


# ════════════════════════════════════════════════════════════
#  CURRENT USER API  (used by feed.html avatar)
# ════════════════════════════════════════════════════════════

@profile_routes.route("/api/profile/me")
@login_required
def my_profile_api():
    uid  = session["user_id"]
    u    = User.query.get(uid)
    prof = Profile.query.filter_by(user_id=uid).first()
    return jsonify({
        "id":    uid,
        "name":  u.name if u else "",
        "image": _profile_image_url(prof),
    })


# ════════════════════════════════════════════════════════════
#  FOLLOWERS / FOLLOWING API
# ════════════════════════════════════════════════════════════

@profile_routes.route("/api/profile/<int:user_id>/followers")
@login_required
def get_followers(user_id):
    rows = Follow.query.filter_by(following_id=user_id).all()
    me   = session["user_id"]
    result = []
    for r in rows:
        u    = User.query.get(r.follower_id)
        prof = Profile.query.filter_by(user_id=r.follower_id).first()
        if u:
            result.append({
                "id":       u.id,
                "name":     u.name,
                "username": prof.username if prof else None,
                "headline": prof.headline if prof else None,
                "image":    _profile_image_url(prof),
                "i_follow": Follow.query.filter_by(follower_id=me, following_id=u.id).first() is not None,
            })
    return jsonify({"success": True, "users": result, "count": len(result)})


@profile_routes.route("/api/profile/<int:user_id>/following")
@login_required
def get_following(user_id):
    rows = Follow.query.filter_by(follower_id=user_id).all()
    me   = session["user_id"]
    result = []
    for r in rows:
        u    = User.query.get(r.following_id)
        prof = Profile.query.filter_by(user_id=r.following_id).first()
        if u:
            result.append({
                "id":       u.id,
                "name":     u.name,
                "username": prof.username if prof else None,
                "headline": prof.headline if prof else None,
                "image":    _profile_image_url(prof),
                "i_follow": Follow.query.filter_by(follower_id=me, following_id=u.id).first() is not None,
            })
    return jsonify({"success": True, "users": result, "count": len(result)})


# ════════════════════════════════════════════════════════════
#  PROFILE UPDATE APIs
# ════════════════════════════════════════════════════════════

@profile_routes.route("/api/profile/update", methods=["POST"])
@login_required
def update_profile():
    uid  = session["user_id"]
    data = request.get_json() or {}
    user = User.query.get(uid)
    prof = Profile.query.filter_by(user_id=uid).first()
    if not prof:
        prof = Profile(user_id=uid)
        db.session.add(prof)
    if "name"           in data: user.name          = data["name"][:100]
    if "headline"       in data: prof.headline       = data["headline"][:220]
    if "bio"            in data: prof.bio            = data["bio"][:1000]
    if "location"       in data: prof.location       = data["location"][:120]
    if "github"         in data: prof.github         = data["github"][:300]
    if "linkedin"       in data: prof.linkedin       = data["linkedin"][:300]
    if "portfolio"      in data: prof.portfolio      = data["portfolio"][:300]
    if "twitter"        in data: prof.twitter        = data["twitter"][:300]
    if "skills_summary" in data: prof.skills_summary = data["skills_summary"][:500]
    db.session.commit()
    return jsonify({"success": True})


@profile_routes.route("/api/profile/upload-photo", methods=["POST"])
@login_required
def upload_photo():
    uid        = session["user_id"]
    photo_type = request.form.get("type", "profile")
    f          = request.files.get("photo")
    if not f or not _allowed(f.filename):
        return jsonify({"error": "Invalid file"}), 400

    ext    = f.filename.rsplit(".", 1)[1].lower() if "." in f.filename else "jpg"
    folder = UPLOAD_FOLDER if photo_type == "profile" else COVER_FOLDER
    os.makedirs(folder, exist_ok=True)

    fname = secure_filename(f"{uid}_{photo_type}_{int(datetime.utcnow().timestamp())}.{ext}")
    path  = os.path.join(folder, fname)
    f.save(path)

    rel = path.replace(os.path.join("frontend", "static", ""), "").replace("\\", "/")

    prof = Profile.query.filter_by(user_id=uid).first()
    if not prof:
        prof = Profile(user_id=uid)
        db.session.add(prof)
    if photo_type == "profile":
        prof.profile_image = rel
    else:
        prof.cover_image = rel
    db.session.commit()

    # ── Sync navbar avatar immediately (no re-login needed) ──
    if photo_type == "profile":
        session["profile_photo"] = f"/static/{rel}"

    return jsonify({"success": True, "url": f"/static/{rel}"})


@profile_routes.route("/api/profile/set-username", methods=["POST"])
@login_required
def set_username():
    uid   = session["user_id"]
    data  = request.get_json() or {}
    uname = (data.get("username") or "").strip().lower()
    import re
    if not re.match(r"^[a-z0-9_]{3,30}$", uname):
        return jsonify({"error": "3-30 chars, a-z 0-9 _ only"}), 400
    existing = Profile.query.filter_by(username=uname).first()
    if existing and existing.user_id != uid:
        return jsonify({"error": "Username taken"}), 400
    prof = Profile.query.filter_by(user_id=uid).first()
    if not prof:
        prof = Profile(user_id=uid)
        db.session.add(prof)
    if prof.username_set:
        return jsonify({"error": "Username can only be set once"}), 400
    prof.username     = uname
    prof.username_set = True
    db.session.commit()
    return jsonify({"success": True, "username": uname})


@profile_routes.route("/api/profile/check-username")
@login_required
def check_username():
    uname = request.args.get("u", "").strip().lower()
    import re
    if not re.match(r"^[a-z0-9_]{3,30}$", uname):
        return jsonify({"available": False, "reason": "Invalid format"})
    exists = Profile.query.filter_by(username=uname).first()
    return jsonify({"available": not exists or exists.user_id == session["user_id"]})


# ════════════════════════════════════════════════════════════
#  FOLLOW / UNFOLLOW
# ════════════════════════════════════════════════════════════

@profile_routes.route("/api/profile/follow", methods=["POST"])
@login_required
def follow_user():
    me  = session["user_id"]
    uid = (request.get_json() or {}).get("user_id")
    if not uid or uid == me:
        return jsonify({"error": "Invalid"}), 400
    existing = Follow.query.filter_by(follower_id=me, following_id=uid).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        count = Follow.query.filter_by(following_id=uid).count()
        return jsonify({"success": True, "following": False, "followers": count})
    db.session.add(Follow(follower_id=me, following_id=uid))
    db.session.commit()
    count = Follow.query.filter_by(following_id=uid).count()
    return jsonify({"success": True, "following": True, "followers": count})


# ════════════════════════════════════════════════════════════
#  POSTS
# ════════════════════════════════════════════════════════════

@profile_routes.route("/api/posts/create", methods=["POST"])
@login_required
def create_post():
    uid = session["user_id"]

    # Support both JSON (feed.html) and multipart form (profile.html)
    if request.is_json:
        data      = request.get_json() or {}
        content   = (data.get("content") or "").strip()
        post_type = data.get("post_type", "text")
        image_url = None
    else:
        data      = request.form
        content   = (data.get("content") or "").strip()
        post_type = data.get("post_type", "text")
        image_url = None
        f = request.files.get("image")
        if f and _allowed(f.filename):
            os.makedirs(POST_UPLOAD_FOLDER, exist_ok=True)
            fname = secure_filename(f"{uid}_{int(datetime.utcnow().timestamp())}.jpg")
            fpath = os.path.join(POST_UPLOAD_FOLDER, fname)
            f.save(fpath)
            image_url = f"/static/uploads/post_images/{fname}"

    if not content:
        return jsonify({"error": "Content required"}), 400

    post = Post(user_id=uid, content=content, post_type=post_type, image_url=image_url)
    db.session.add(post)
    db.session.commit()
    return jsonify({"success": True, "post_id": post.id})


@profile_routes.route("/api/posts/feed")
@login_required
def api_feed():
    me   = session["user_id"]
    page = int(request.args.get("page", 1))
    per  = 10

    following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=me).all()]
    following_ids.append(me)

    posts = Post.query.filter(Post.user_id.in_(following_ids)) \
                .order_by(Post.created_at.desc()) \
                .offset((page - 1) * per).limit(per).all()

    liked = {l.post_id for l in PostLike.query.filter_by(user_id=me).all()}
    result = []
    for p in posts:
        u    = User.query.get(p.user_id)
        prof = Profile.query.filter_by(user_id=p.user_id).first()
        result.append({
            "id":         p.id,
            "content":    p.content,
            "post_type":  p.post_type,
            "image_url":  p.image_url,
            "user_id":    p.user_id,
            "user_name":  u.name if u else "User",
            "user_image": _profile_image_url(prof),
            "headline":   prof.headline if prof else "",
            "liked":      p.id in liked,
            "likes":      len(p.likes),
            "created_at": p.created_at.strftime("%b %d, %Y") if p.created_at else "",
        })
    return jsonify(result)


# Alias: feed.html calls /api/posts/like/<id>
@profile_routes.route("/api/posts/like/<int:post_id>", methods=["POST"])
@login_required
def like_post_alias(post_id):
    return like_post(post_id)


@profile_routes.route("/api/posts/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    uid      = session["user_id"]
    post     = Post.query.get_or_404(post_id)
    existing = PostLike.query.filter_by(post_id=post_id, user_id=uid).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"success": True, "liked": False, "count": len(post.likes)})
    db.session.add(PostLike(post_id=post_id, user_id=uid))
    db.session.commit()
    return jsonify({"success": True, "liked": True, "count": len(post.likes)})


@profile_routes.route("/api/posts/<int:post_id>/comments", methods=["GET"])
@login_required
def get_comments(post_id):
    cmts = PostComment.query.filter_by(post_id=post_id) \
               .order_by(PostComment.created_at.asc()).all()
    result = []
    for c in cmts:
        u    = User.query.get(c.user_id)
        prof = Profile.query.filter_by(user_id=c.user_id).first()
        replies = []
        try:
            from backend.models import PostCommentReply
            reps = PostCommentReply.query.filter_by(comment_id=c.id) \
                       .order_by(PostCommentReply.created_at.asc()).all()
            for r in reps:
                ru = User.query.get(r.user_id)
                replies.append({
                    "id":         r.id,
                    "content":    r.content,
                    "user_id":    r.user_id,
                    "user_name":  ru.name if ru else "User",
                    "created_at": r.created_at.strftime("%b %d") if r.created_at else "",
                })
        except Exception:
            pass
        result.append({
            "id":         c.id,
            "content":    c.content,
            "user_id":    c.user_id,
            "user_name":  u.name if u else "User",
            "user_image": _profile_image_url(prof),
            "created_at": c.created_at.strftime("%b %d") if c.created_at else "",
            "replies":    replies,
        })
    return jsonify({"success": True, "comments": result, "count": len(result)})


@profile_routes.route("/api/posts/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    uid     = session["user_id"]
    data    = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Empty comment"}), 400
    c = PostComment(post_id=post_id, user_id=uid, content=content)
    db.session.add(c)
    db.session.commit()
    u    = User.query.get(uid)
    prof = Profile.query.filter_by(user_id=uid).first()
    return jsonify({"success": True, "comment": {
        "id":         c.id,
        "content":    c.content,
        "user_id":    uid,
        "user_name":  u.name if u else "User",
        "user_image": _profile_image_url(prof),
        "created_at": "Just now",
        "replies":    [],
    }})


@profile_routes.route("/api/comments/<int:comment_id>/reply", methods=["POST"])
@login_required
def add_reply(comment_id):
    uid     = session["user_id"]
    data    = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Empty reply"}), 400
    try:
        from backend.models import PostCommentReply
        r = PostCommentReply(comment_id=comment_id, user_id=uid, content=content)
        db.session.add(r)
        db.session.commit()
        u = User.query.get(uid)
        return jsonify({"success": True, "reply": {
            "id":         r.id,
            "content":    r.content,
            "user_id":    uid,
            "user_name":  u.name if u else "User",
            "created_at": "Just now",
        }})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profile_routes.route("/api/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    uid  = session["user_id"]
    post = Post.query.filter_by(id=post_id, user_id=uid).first()
    if not post:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify({"success": True})


# ════════════════════════════════════════════════════════════
#  CERTIFICATES
# ════════════════════════════════════════════════════════════

@profile_routes.route("/api/certificates/add", methods=["POST"])
@login_required
def add_certificate():
    uid = session["user_id"]
    # Support both JSON and multipart form
    data = request.get_json() if request.is_json else request.form
    c = Certificate(
        user_id=uid,
        title=(data.get("title") or "")[:250],
        issuer=(data.get("issuer") or "")[:200],
        issued_date=(data.get("issued_date") or "")[:50],
        credential_id=(data.get("credential_id") or "")[:200],
        link=(data.get("link") or "")[:500],
        image_url=(data.get("image_url") or ""),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({"success": True, "id": c.id, "cert_id": c.id})


# Primary delete route (profile.html)
@profile_routes.route("/api/certificates/<int:cert_id>/delete", methods=["POST"])
@login_required
def delete_certificate(cert_id):
    c = Certificate.query.filter_by(id=cert_id, user_id=session["user_id"]).first()
    if not c:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"success": True})


# Alias delete route (certificates.html / edit_profile.html — DELETE method)
@profile_routes.route("/api/certificates/delete/<int:cert_id>", methods=["DELETE", "POST"])
@login_required
def delete_certificate_alt(cert_id):
    c = Certificate.query.filter_by(id=cert_id, user_id=session["user_id"]).first()
    if not c:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"success": True})


# ════════════════════════════════════════════════════════════
#  USER SEARCH
# ════════════════════════════════════════════════════════════

def _search_users_logic(q):
    me = session["user_id"]
    if len(q) < 2:
        return []
    users = User.query.filter(
        or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
    ).limit(10).all()

    prof_by_uname = Profile.query.filter(Profile.username.ilike(f"%{q}%")).all()
    extra_ids = {p.user_id for p in prof_by_uname}
    seen = {u.id for u in users}
    for uid in extra_ids:
        if uid not in seen:
            u = User.query.get(uid)
            if u:
                users.append(u)

    result = []
    for u in users:
        prof = Profile.query.filter_by(user_id=u.id).first()
        result.append({
            "id":       u.id,
            "name":     u.name,
            "username": prof.username if prof else None,
            "headline": prof.headline if prof else None,
            "image":    _profile_image_url(prof),
            "i_follow": Follow.query.filter_by(follower_id=me, following_id=u.id).first() is not None,
        })
    return result


@profile_routes.route("/api/profile/search")
@login_required
def search_users():
    q = request.args.get("q", "").strip()
    return jsonify({"users": _search_users_logic(q)})


# messages.html calls /api/users/search — alias, returns plain list
@profile_routes.route("/api/users/search")
@login_required
def search_users_alias():
    q = request.args.get("q", "").strip()
    return jsonify(_search_users_logic(q))


# ════════════════════════════════════════════════════════════
#  MESSAGES
# ════════════════════════════════════════════════════════════

@profile_routes.route("/api/messages/send", methods=["POST"])
@login_required
def send_message():
    me   = session["user_id"]
    data = request.get_json() or {}
    # support both "to_id" (chat.html) and "receiver_id" (other pages)
    to   = data.get("to_id") or data.get("receiver_id")
    text = (data.get("content") or "").strip()
    if not to or not text:
        return jsonify({"error": "Missing fields"}), 400
    m = Message(sender_id=me, receiver_id=int(to), content=text)
    db.session.add(m)
    db.session.commit()
    return jsonify({
        "success":    True,
        "message_id": m.id,
        "created_at": m.created_at.strftime("%H:%M") if m.created_at else "",
    })


@profile_routes.route("/api/messages/<int:uid>/history")
@login_required
def message_history(uid):
    me = session["user_id"]
    msgs = Message.query.filter(
        or_(
            db.and_(Message.sender_id == me,  Message.receiver_id == uid),
            db.and_(Message.sender_id == uid, Message.receiver_id == me),
        )
    ).order_by(Message.created_at.asc()).all()
    return jsonify({"messages": [{
        "id":         m.id,
        "content":    m.content,
        "sender_id":  m.sender_id,
        "created_at": m.created_at.strftime("%H:%M") if m.created_at else "",
    } for m in msgs]})


# chat.html polls /api/messages/conversation/<uid>
@profile_routes.route("/api/messages/conversation/<int:uid>")
@login_required
def conversation_poll(uid):
    me = session["user_id"]
    msgs = Message.query.filter(
        or_(
            db.and_(Message.sender_id == me,  Message.receiver_id == uid),
            db.and_(Message.sender_id == uid, Message.receiver_id == me),
        )
    ).order_by(Message.created_at.asc()).all()
    Message.query.filter_by(
        sender_id=uid, receiver_id=me, is_read=False
    ).update({"is_read": True})
    db.session.commit()
    return jsonify([{
        "id":         m.id,
        "content":    m.content,
        "sender_id":  m.sender_id,
        "is_mine":    m.sender_id == me,
        "created_at": m.created_at.strftime("%H:%M") if m.created_at else "",
    } for m in msgs])


@profile_routes.route("/api/messages/unread-count")
@login_required
def unread_count():
    me    = session["user_id"]
    count = Message.query.filter_by(receiver_id=me, is_read=False).count()
    return jsonify({"count": count})