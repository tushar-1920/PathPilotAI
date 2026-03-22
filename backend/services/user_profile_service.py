from backend.models import User, Profile, Certificate, Follow, Post, db


class ProfileService:

    def get_or_create(self, user_id: int) -> Profile:
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = Profile(user_id=user_id)
            db.session.add(profile)
            db.session.commit()
        return profile

    def update(self, user_id: int, data: dict) -> Profile:
        profile = self.get_or_create(user_id)
        fields  = ["headline","bio","location","skills_summary",
                   "github","linkedin","portfolio","twitter"]
        for f in fields:
            if f in data:
                setattr(profile, f, data[f])
        user = User.query.get(user_id)
        if data.get("name"):
            user.name = data["name"]
        db.session.commit()
        return profile

    def set_photo(self, user_id: int, image_path: str) -> Profile:
        profile = self.get_or_create(user_id)
        profile.profile_image = image_path
        db.session.commit()
        return profile

    def get_stats(self, user_id: int) -> dict:
        followers = Follow.query.filter_by(following_id=user_id).count()
        following = Follow.query.filter_by(follower_id=user_id).count()
        posts     = Post.query.filter_by(user_id=user_id).count()
        certs     = Certificate.query.filter_by(user_id=user_id).count()
        return {"followers": followers, "following": following,
                "posts": posts, "certificates": certs}