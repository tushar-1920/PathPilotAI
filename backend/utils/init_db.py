from backend.app import create_app
from backend.extensions import db
from backend.models import SkillCategory, Skill

app = create_app()

with app.app_context():

    db.create_all()

    print("Database created successfully")