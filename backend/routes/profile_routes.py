from flask import Blueprint, jsonify, render_template, session, request, redirect, url_for
from backend.utils.auth_decorator import login_required
from backend.services.user_profile_service import ProfileService
from backend.services.social_service import SocialService
from backend.services.post_service import PostService
from backend.models import User, Profile, Certificate, Follow, Post, PostLike, PostComment, Message, db
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import or_, and_
import os, re

profile_routes = Blueprint("profile_routes", __name__)
profile_svc    = ProfileService()
social_svc     = SocialService()
post_svc       = PostService()

UPLOAD_FOLDER        = os.path.join("frontend", "static", "uploads", "profile_images")
POST_UPLOAD_FOLDER   = os.path.join("frontend", "static", "uploads", "post_images")
CERT_UPLOAD_FOLDER   = os.path.join("frontend", "static", "uploads", "cert_images")
ALLOWED_EXT          = {"png", "jpg", "jpeg", "webp", "gif"}

def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def _safe_skills(user):
    try:
        return [s.strip() for s in (user.normalized_skills or "").split(",") if s.strip()]
    except Exception:
        return []

def _profile_image_url(profile):
    if profile and profile.profile_image:
        return f"/static/{profile.profile_image}"
    return None


# ══════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════

@profile_routes.route("/profile")
@login_required
def my_profile():
    return redirect(url_for("profile_routes.view_profile", user_id=session["user_id"]))


@profile_routes.route("/profile/<int:user_id>")
@login_required
def view_profile(user_id):
    user    = User.query.get_or_404(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    me      = session.get("user_id")

    # Auto-create profile for own page
    if not profile and user_id == me:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()

    certs   = Certificate.query.filter_by(user_id=user_id).order_by(Certificate.id.desc()).all()
    posts   = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).limit(10).all()
    followers_count = Follow.query.filter_by(following_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=user_id).count()
    is_following    = Follow.query.filter_by(follower_id=me, following_id=user_id).first() is not None if me and me != user_id else False

    # Unread message count from this user
    unread_from = Message.query.filter_by(sender_id=user_id, receiver_id=me, is_read=False).count() if me else 0

    return render_template("profile.html",
        user=user, profile=profile, certs=certs or [], posts=posts or [],
        followers_count=followers_count or 0, following_count=following_count or 0,
        is_following=is_following, is_own=me == user_id,
        resume_skills=_safe_skills(user), unread_from=unread_from)


@profile_routes.route("/edit-profile")
@login_required
def edit_profile_page():
    user_id = session["user_id"]
    user    = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile); db.session.commit()
    certs = Certificate.query.filter_by(user_id=user_id).all()
    return render_template("edit_profile.html",
        user=user, profile=profile, certs=certs or [],
        resume_skills=_safe_skills(user))


@profile_routes.route("/feed")
@login_required
def feed_page():
    return render_template("feed.html", me=session["user_id"])


@profile_routes.route("/certificates")
@login_required
def certificates_page():
    user_id = session["user_id"]
    certs   = Certificate.query.filter_by(user_id=user_id).order_by(Certificate.id.desc()).all()
    return render_template("certificates.html", certs=certs or [])


@profile_routes.route("/messages")
@login_required
def messages_page():
    me = session["user_id"]
    # Get all conversations (unique users I've messaged or been messaged by)
    sent     = db.session.query(Message.receiver_id).filter_by(sender_id=me).distinct()
    received = db.session.query(Message.sender_id).filter_by(receiver_id=me).distinct()
    conv_ids = {r[0] for r in sent} | {r[0] for r in received}
    conversations = []
    for uid in conv_ids:
        u  = User.query.get(uid)
        pr = Profile.query.filter_by(user_id=uid).first()
        if not u: continue
        last_msg = Message.query.filter(
            or_(and_(Message.sender_id==me, Message.receiver_id==uid),
                and_(Message.sender_id==uid, Message.receiver_id==me))
        ).order_by(Message.created_at.desc()).first()
        unread = Message.query.filter_by(sender_id=uid, receiver_id=me, is_read=False).count()
        conversations.append({
            "user_id":   uid,
            "name":      u.name,
            "username":  pr.username if pr else None,
            "image":     _profile_image_url(pr),
            "last_msg":  last_msg.content[:60] if last_msg else "",
            "last_time": last_msg.created_at.strftime("%b %d") if last_msg else "",
            "unread":    unread,
        })
    conversations.sort(key=lambda x: x["last_time"], reverse=True)
    return render_template("messages.html", me=me, conversations=conversations)


@profile_routes.route("/messages/<int:user_id>")
@login_required
def chat_page(user_id):
    me       = session["user_id"]
    other    = User.query.get_or_404(user_id)
    other_pr = Profile.query.filter_by(user_id=user_id).first()
    # Mark messages as read
    Message.query.filter_by(sender_id=user_id, receiver_id=me, is_read=False).update({"is_read": True})
    db.session.commit()
    msgs = Message.query.filter(
        or_(and_(Message.sender_id==me, Message.receiver_id==user_id),
            and_(Message.sender_id==user_id, Message.receiver_id==me))
    ).order_by(Message.created_at.asc()).all()
    return render_template("chat.html", me=me, other=other,
                           other_profile=other_pr, messages=msgs)


@profile_routes.route("/search")
@login_required
def search_page():
    q = request.args.get("q", "").strip()
    return render_template("search_users.html", q=q)


# ══════════════════════════════════════════════════════════════
#  PROFILE API
# ══════════════════════════════════════════════════════════════

@profile_routes.route("/api/profile/update", methods=["POST"])
@login_required
def update_profile():
    user_id = session["user_id"]
    data    = request.get_json() or {}
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)

    for field in ["headline","bio","location","skills_summary","github","linkedin","portfolio","twitter"]:
        if field in data:
            setattr(profile, field, data[field])
    user = User.query.get(user_id)
    if data.get("name"):
        user.name = data["name"]
    db.session.commit()
    return jsonify({"success": True})


@profile_routes.route("/api/profile/set-username", methods=["POST"])
@login_required
def set_username():
    user_id  = session["user_id"]
    data     = request.get_json() or {}
    username = (data.get("username") or "").strip().lower()

    if not username:
        return jsonify({"error": "Username required"}), 400
    if not re.match(r'^[a-z0-9_]{3,20}$', username):
        return jsonify({"error": "Username must be 3-20 chars, letters/numbers/underscores only"}), 400

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)

    if profile.username_set:
        return jsonify({"error": "Username can only be set once"}), 400

    # Check uniqueness
    existing = Profile.query.filter_by(username=username).first()
    if existing and existing.user_id != user_id:
        return jsonify({"error": "Username already taken"}), 400

    profile.username     = username
    profile.username_set = True
    db.session.commit()
    return jsonify({"success": True, "username": username})


@profile_routes.route("/api/profile/check-username")
@login_required
def check_username():
    username = request.args.get("username","").strip().lower()
    if not username:
        return jsonify({"available": False})
    if not re.match(r'^[a-z0-9_]{3,20}$', username):
        return jsonify({"available": False, "error": "Invalid format"})
    exists = Profile.query.filter_by(username=username).first()
    return jsonify({"available": exists is None})


@profile_routes.route("/api/profile/upload-photo", methods=["POST"])
@login_required
def upload_photo():
    user_id = session["user_id"]
    if "photo" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["photo"]
    if not file or not _allowed(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = f"user_{user_id}_{secure_filename(file.filename)}"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id); db.session.add(profile)
    profile.profile_image = f"uploads/profile_images/{filename}"
    db.session.commit()
    return jsonify({"success": True, "image_url": f"/static/{profile.profile_image}"})


@profile_routes.route("/api/profile/<int:user_id>")
@login_required
def get_profile_api(user_id):
    user    = User.query.get_or_404(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    certs   = Certificate.query.filter_by(user_id=user_id).all()
    return jsonify({
        "id": user.id, "name": user.name,
        "username":    profile.username    if profile else None,
        "headline":    profile.headline    if profile else "",
        "bio":         profile.bio         if profile else "",
        "github":      profile.github      if profile else "",
        "linkedin":    profile.linkedin    if profile else "",
        "portfolio":   profile.portfolio   if profile else "",
        "location":    profile.location    if profile else "",
        "skills_summary": profile.skills_summary if profile else "",
        "profile_image": _profile_image_url(profile),
        "followers":   Follow.query.filter_by(following_id=user_id).count(),
        "following":   Follow.query.filter_by(follower_id=user_id).count(),
        "certificates": [{"id":c.id,"title":c.title,"issuer":c.issuer,
                           "date":c.issued_date,"link":c.link,"image":c.image_url} for c in certs],
    })


# ══════════════════════════════════════════════════════════════
#  SEARCH API
# ══════════════════════════════════════════════════════════════

@profile_routes.route("/api/users/search")
@login_required
def search_users():
    q   = request.args.get("q", "").strip()
    me  = session["user_id"]
    if not q:
        # Return suggested users (not self, not already following)
        following_ids = {f.following_id for f in Follow.query.filter_by(follower_id=me).all()}
        following_ids.add(me)
        users = User.query.filter(~User.id.in_(following_ids)).limit(8).all()
    else:
        # Search by name OR username
        users = User.query.join(Profile, User.id == Profile.user_id, isouter=True).filter(
            or_(User.name.ilike(f"%{q}%"), Profile.username.ilike(f"%{q}%"))
        ).limit(12).all()

    result = []
    for u in users:
        pr = Profile.query.filter_by(user_id=u.id).first()
        is_following = Follow.query.filter_by(follower_id=me, following_id=u.id).first() is not None
        result.append({
            "id": u.id, "name": u.name,
            "username":  pr.username  if pr else None,
            "headline":  pr.headline  if pr else "",
            "image":     _profile_image_url(pr),
            "is_following": is_following,
        })
    return jsonify(result)


# ══════════════════════════════════════════════════════════════
#  CERTIFICATES API
# ══════════════════════════════════════════════════════════════

@profile_routes.route("/api/certificates/add", methods=["POST"])
@login_required
def add_certificate():
    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"error": "Title required"}), 400
    cert = Certificate(
        user_id=session["user_id"], title=data["title"],
        issuer=data.get("issuer",""), issued_date=data.get("issued_date",""),
        credential_id=data.get("credential_id",""), link=data.get("link",""),
        image_url=data.get("image_url",""),
    )
    db.session.add(cert); db.session.commit()
    # Notify followers in feed (create a post)
    _notify_cert(cert, session["user_id"])
    return jsonify({"success": True, "id": cert.id})


def _notify_cert(cert, user_id):
    """Auto-create a feed post when user adds a certificate."""
    try:
        content = f"🏆 Just earned: {cert.title}"
        if cert.issuer:
            content += f" from {cert.issuer}"
        post = Post(user_id=user_id, content=content,
                    post_type="achievement", created_at=datetime.utcnow())
        db.session.add(post); db.session.commit()
    except Exception:
        pass


@profile_routes.route("/api/certificates/upload-image/<int:cert_id>", methods=["POST"])
@login_required
def upload_cert_image(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    if cert.user_id != session["user_id"]:
        return jsonify({"error": "Unauthorized"}), 403
    if "image" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["image"]
    if not file or not _allowed(file.filename):
        return jsonify({"error": "Invalid file"}), 400
    os.makedirs(CERT_UPLOAD_FOLDER, exist_ok=True)
    filename = f"cert_{cert_id}_{secure_filename(file.filename)}"
    file.save(os.path.join(CERT_UPLOAD_FOLDER, filename))
    cert.image_url = f"/static/uploads/cert_images/{filename}"
    db.session.commit()
    return jsonify({"success": True, "image_url": cert.image_url})


@profile_routes.route("/api/certificates/delete/<int:cert_id>", methods=["DELETE"])
@login_required
def delete_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    if cert.user_id != session["user_id"]:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(cert); db.session.commit()
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════
#  FOLLOW API
# ══════════════════════════════════════════════════════════════

@profile_routes.route("/api/follow/<int:user_id>", methods=["POST"])
@login_required
def follow_user(user_id):
    me = session["user_id"]
    if me == user_id: return jsonify({"error": "Cannot follow yourself"}), 400
    if Follow.query.filter_by(follower_id=me, following_id=user_id).first():
        return jsonify({"error": "Already following"}), 400
    db.session.add(Follow(follower_id=me, following_id=user_id))
    db.session.commit()
    return jsonify({"success": True, "following": True,
                    "followers_count": Follow.query.filter_by(following_id=user_id).count()})


@profile_routes.route("/api/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow_user(user_id):
    me = session["user_id"]
    f  = Follow.query.filter_by(follower_id=me, following_id=user_id).first()
    if f: db.session.delete(f); db.session.commit()
    return jsonify({"success": True, "following": False,
                    "followers_count": Follow.query.filter_by(following_id=user_id).count()})


# ══════════════════════════════════════════════════════════════
#  POSTS API
# ══════════════════════════════════════════════════════════════

@profile_routes.route("/api/posts/create", methods=["POST"])
@login_required
def create_post():
    data    = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content: return jsonify({"error": "Content required"}), 400
    post = Post(user_id=session["user_id"], content=content,
                post_type=data.get("post_type","text"),
                image_url=data.get("image_url",""),
                created_at=datetime.utcnow())
    db.session.add(post); db.session.commit()
    return jsonify({"success": True, "post_id": post.id})


@profile_routes.route("/api/posts/upload-image", methods=["POST"])
@login_required
def upload_post_image():
    if "image" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["image"]
    if not file or not _allowed(file.filename):
        return jsonify({"error": "Invalid file"}), 400
    os.makedirs(POST_UPLOAD_FOLDER, exist_ok=True)
    filename = f"post_{session['user_id']}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
    file.save(os.path.join(POST_UPLOAD_FOLDER, filename))
    return jsonify({"success": True, "image_url": f"/static/uploads/post_images/{filename}"})


@profile_routes.route("/api/posts/feed")
@login_required
def get_feed():
    me   = session["user_id"]
    page = int(request.args.get("page", 1))
    following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=me).all()]
    following_ids.append(me)
    posts = Post.query.filter(Post.user_id.in_(following_ids)) \
                .order_by(Post.created_at.desc()) \
                .offset((page-1)*10).limit(10).all()
    return jsonify([_serialize_post(p, me) for p in posts])


@profile_routes.route("/api/posts/user/<int:user_id>")
@login_required
def get_user_posts(user_id):
    me    = session["user_id"]
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).limit(20).all()
    return jsonify([_serialize_post(p, me) for p in posts])


@profile_routes.route("/api/posts/like/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    me       = session["user_id"]
    existing = PostLike.query.filter_by(post_id=post_id, user_id=me).first()
    if existing:
        db.session.delete(existing); liked = False
    else:
        db.session.add(PostLike(post_id=post_id, user_id=me)); liked = True
    db.session.commit()
    return jsonify({"success": True, "liked": liked,
                    "likes": PostLike.query.filter_by(post_id=post_id).count()})


@profile_routes.route("/api/posts/comment/<int:post_id>", methods=["POST"])
@login_required
def comment_post(post_id):
    data    = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content: return jsonify({"error": "Comment required"}), 400
    c = PostComment(post_id=post_id, user_id=session["user_id"],
                    content=content, created_at=datetime.utcnow())
    db.session.add(c); db.session.commit()
    u  = User.query.get(session["user_id"])
    pr = Profile.query.filter_by(user_id=session["user_id"]).first()
    return jsonify({"success": True, "id": c.id, "content": c.content,
                    "user_name": u.name, "created_at": c.created_at.strftime("%b %d"),
                    "user_image": _profile_image_url(pr)})


@profile_routes.route("/api/posts/delete/<int:post_id>", methods=["DELETE"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != session["user_id"]: return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(post); db.session.commit()
    return jsonify({"success": True})


def _serialize_post(post, viewer_id):
    u      = User.query.get(post.user_id)
    pr     = Profile.query.filter_by(user_id=post.user_id).first()
    likes  = PostLike.query.filter_by(post_id=post.id).count()
    liked  = PostLike.query.filter_by(post_id=post.id, user_id=viewer_id).first() is not None
    cmts   = PostComment.query.filter_by(post_id=post.id).count()
    return {
        "id": post.id, "content": post.content,
        "post_type": post.post_type, "image_url": post.image_url or "",
        "created_at": post.created_at.strftime("%b %d, %Y") if post.created_at else "",
        "user_id": post.user_id, "user_name": u.name if u else "Unknown",
        "username": pr.username if pr else None,
        "headline": pr.headline if pr else "",
        "user_image": _profile_image_url(pr),
        "likes": likes, "liked": liked, "comments": cmts,
    }


# ══════════════════════════════════════════════════════════════
#  MESSAGES API
# ══════════════════════════════════════════════════════════════

@profile_routes.route("/api/messages/send", methods=["POST"])
@login_required
def send_message():
    data    = request.get_json() or {}
    to_id   = data.get("to_id")
    content = (data.get("content") or "").strip()
    if not to_id or not content:
        return jsonify({"error": "Recipient and message required"}), 400
    msg = Message(sender_id=session["user_id"], receiver_id=to_id,
                  content=content, created_at=datetime.utcnow())
    db.session.add(msg); db.session.commit()
    return jsonify({"success": True, "id": msg.id,
                    "created_at": msg.created_at.strftime("%H:%M")})


@profile_routes.route("/api/messages/conversation/<int:user_id>")
@login_required
def get_conversation(user_id):
    me   = session["user_id"]
    msgs = Message.query.filter(
        or_(and_(Message.sender_id==me, Message.receiver_id==user_id),
            and_(Message.sender_id==user_id, Message.receiver_id==me))
    ).order_by(Message.created_at.asc()).all()
    # Mark as read
    Message.query.filter_by(sender_id=user_id, receiver_id=me, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify([{"id": m.id, "sender_id": m.sender_id, "content": m.content,
                     "created_at": m.created_at.strftime("%H:%M"),
                     "is_mine": m.sender_id == me} for m in msgs])


@profile_routes.route("/api/messages/unread-count")
@login_required
def unread_count():
    count = Message.query.filter_by(receiver_id=session["user_id"], is_read=False).count()
    return jsonify({"count": count})