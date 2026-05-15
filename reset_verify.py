from run import app
from backend.extensions import db
from backend.models import User

with app.app_context():
    user = User.query.filter_by(email="tusharchdmks@gmail.com").first()
    user.is_verified = False
    db.session.commit()
    print("Done! is_verified =", user.is_verified)