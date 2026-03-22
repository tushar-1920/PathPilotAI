from backend.models import Follow, User, Profile, Post, PostLike, db
from datetime import datetime


class PostService:

    def create(self, user_id: int, content: str, post_type: str = "text") -> Post:
        post = Post(user_id=user_id, content=content,
                    post_type=post_type, created_at=datetime.utcnow())
        db.session.add(post)
        db.session.commit()
        return post

    def delete(self, post_id: int, user_id: int) -> bool:
        post = Post.query.get(post_id)
        if not post or post.user_id != user_id:
            return False
        db.session.delete(post)
        db.session.commit()
        return True

    def toggle_like(self, post_id: int, user_id: int) -> dict:
        existing = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing:
            db.session.delete(existing)
            liked = False
        else:
            db.session.add(PostLike(post_id=post_id, user_id=user_id))
            liked = True
        db.session.commit()
        count = PostLike.query.filter_by(post_id=post_id).count()
        return {"liked": liked, "likes": count}

    def get_feed(self, user_id: int, page: int = 1, limit: int = 10) -> list:
        following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=user_id).all()]
        following_ids.append(user_id)
        posts = Post.query.filter(Post.user_id.in_(following_ids)) \
                    .order_by(Post.created_at.desc()) \
                    .offset((page - 1) * limit).limit(limit).all()
        return [self._serialize(p, user_id) for p in posts]

    def get_user_posts(self, profile_user_id: int, viewer_id: int, limit: int = 20) -> list:
        posts = Post.query.filter_by(user_id=profile_user_id) \
                    .order_by(Post.created_at.desc()).limit(limit).all()
        return [self._serialize(p, viewer_id) for p in posts]

    def _serialize(self, post: Post, viewer_id: int) -> dict:
        u     = User.query.get(post.user_id)
        pr    = Profile.query.filter_by(user_id=post.user_id).first()
        likes = PostLike.query.filter_by(post_id=post.id).count()
        liked = PostLike.query.filter_by(post_id=post.id, user_id=viewer_id).first() is not None
        return {
            "id":        post.id,
            "content":   post.content,
            "post_type": post.post_type,
            "created_at": post.created_at.strftime("%b %d, %Y") if post.created_at else "",
            "user_id":   post.user_id,
            "user_name": u.name if u else "Unknown",
            "headline":  pr.headline if pr else "",
            "user_image": f"/static/{pr.profile_image}" if pr and pr.profile_image else None,
            "likes": likes,
            "liked": liked,
        }