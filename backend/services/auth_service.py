from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User
from backend.extensions import db


class AuthService:

    def register_user(self, name, email, password):

        existing = User.query.filter_by(email=email).first()

        if existing:
            return None, "Email already registered"

        hashed = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password_hash=hashed,
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        return user, None


    def login_user(self, email, password):

        user = User.query.filter_by(email=email).first()

        if not user:
            return None, "Invalid email"

        if not check_password_hash(user.password_hash, password):
            return None, "Invalid password"

        return user, None