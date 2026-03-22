from backend.models import Follow, User, Profile, db


class SocialService:

    def follow(self, follower_id: int, following_id: int) -> dict:
        if follower_id == following_id:
            return {"error": "Cannot follow yourself"}
        exists = Follow.query.filter_by(
            follower_id=follower_id, following_id=following_id).first()
        if exists:
            return {"error": "Already following"}
        db.session.add(Follow(follower_id=follower_id, following_id=following_id))
        db.session.commit()
        return {"success": True, "following": True,
                "count": Follow.query.filter_by(following_id=following_id).count()}

    def unfollow(self, follower_id: int, following_id: int) -> dict:
        f = Follow.query.filter_by(
            follower_id=follower_id, following_id=following_id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
        return {"success": True, "following": False,
                "count": Follow.query.filter_by(following_id=following_id).count()}

    def is_following(self, follower_id: int, following_id: int) -> bool:
        return Follow.query.filter_by(
            follower_id=follower_id, following_id=following_id).first() is not None

    def get_followers(self, user_id: int) -> list:
        follows = Follow.query.filter_by(following_id=user_id).all()
        result  = []
        for f in follows:
            u  = User.query.get(f.follower_id)
            pr = Profile.query.filter_by(user_id=f.follower_id).first()
            if u:
                result.append({
                    "id": u.id, "name": u.name,
                    "headline": pr.headline if pr else "",
                    "image": f"/static/{pr.profile_image}" if pr and pr.profile_image else None,
                })
        return result

    def get_following(self, user_id: int) -> list:
        follows = Follow.query.filter_by(follower_id=user_id).all()
        result  = []
        for f in follows:
            u  = User.query.get(f.following_id)
            pr = Profile.query.filter_by(user_id=f.following_id).first()
            if u:
                result.append({
                    "id": u.id, "name": u.name,
                    "headline": pr.headline if pr else "",
                    "image": f"/static/{pr.profile_image}" if pr and pr.profile_image else None,
                })
        return result