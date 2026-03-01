from backend.app import create_app
from backend.extensions import db
from backend.models import User

app = create_app()

with app.app_context():

    existing = User.query.filter_by(email="test@pathpilot.ai").first()

    if not existing:

        user = User(
            name="Test User",
            email="test@pathpilot.ai"
        )

        db.session.add(user)

        db.session.commit()

        print("Test user created")

    else:

        print("User already exists")