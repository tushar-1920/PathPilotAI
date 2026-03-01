from backend.app import create_app
from backend.models import User, UserSkill

app = create_app()

with app.app_context():

    user = User.query.filter_by(email="test@pathpilot.ai").first()

    for us in user.user_skills:

        print(us.skill.name)