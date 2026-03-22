from flask import Flask
from backend.config import Config
from backend.extensions import db
from apscheduler.schedulers.background import BackgroundScheduler
from flask_socketio import SocketIO
import atexit

# ── Create SocketIO instance at module level so run.py can import it ──
socketio = SocketIO()

def create_app():

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    app.config.from_object(Config)

    db.init_app(app)

    # ── Init SocketIO with app ──
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")

    import json
    app.jinja_env.filters["fromjson"] = json.loads

    # ==========================================
    # CREATE TABLES + SEED DEFAULT DATA
    # ==========================================
    with app.app_context():

        from backend import models
        db.create_all()

        from backend.models import User, Skill

        if Skill.query.count() == 0:
            global_skills = [
    "Python", "Java", "C", "C++", "C#", "JavaScript",
    "TypeScript", "Go", "Rust", "Swift", "Kotlin",
    "PHP", "Ruby", "Scala", "R", "MATLAB",
    "Dart", "Groovy", "Objective-C",
    "Assembly", "Bash", "PowerShell", "VBA",
    "HTML", "CSS", "SASS", "LESS",
    "Bootstrap", "Tailwind CSS", "Material UI",
    "React", "Next.js", "Redux",
    "Angular", "Vue.js", "Nuxt.js",
    "Svelte", "jQuery",
    "Node.js", "Express.js",
    "Django", "Flask", "FastAPI",
    "Spring Boot", "ASP.NET",
    "Laravel", "Ruby on Rails",
    "GraphQL", "REST API",
    "Android", "iOS",
    "React Native", "Flutter",
    "SwiftUI", "Kotlin Multiplatform",
    "Xamarin",
    "MySQL", "PostgreSQL", "MongoDB",
    "Redis", "SQLite", "Oracle",
    "Microsoft SQL Server",
    "Firebase", "Supabase",
    "Cassandra", "DynamoDB",
    "Elasticsearch",
    "AWS", "Azure", "Google Cloud",
    "DigitalOcean", "Heroku",
    "Vercel", "Netlify",
    "Docker", "Kubernetes",
    "CI/CD", "Jenkins",
    "GitHub Actions", "GitLab CI",
    "Terraform", "Ansible",
    "Nginx", "Apache",
    "Linux", "Unix",
    "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "Data Science",
    "NLP", "Computer Vision",
    "Reinforcement Learning",
    "TensorFlow", "PyTorch", "Keras",
    "Scikit-learn", "XGBoost", "LightGBM",
    "Pandas", "NumPy", "SciPy",
    "Matplotlib", "Seaborn", "Plotly",
    "OpenCV",
    "Hugging Face", "Transformers",
    "LangChain", "LLMs",
    "Big Data", "Data Mining",
    "Data Visualization", "Data Analysis",
    "Hadoop", "Spark", "Kafka",
    "Airflow", "ETL",
    "Data Warehousing",
    "Snowflake", "BigQuery",
    "Databricks",
    "BeautifulSoup", "Scrapy",
    "Selenium", "Web Scraping",
    "Cybersecurity", "Ethical Hacking",
    "Penetration Testing", "Network Security",
    "Cryptography", "SOC", "SIEM",
    "Blockchain", "Solidity",
    "Web3", "Smart Contracts",
    "Ethereum", "Hyperledger",
    "Unit Testing", "Automation Testing",
    "Cypress", "Jest", "PyTest",
    "Postman",
    "Power BI", "Tableau",
    "Excel", "Looker",
    "Google Analytics",
    "Figma", "Adobe XD",
    "Photoshop", "UI/UX Design",
    "Wireframing",
    "Agile", "Scrum", "Kanban",
    "Product Management",
    "Project Management",
    "Jira", "Notion",
    "Communication", "Leadership",
    "Problem Solving", "Critical Thinking",
    "Teamwork", "Time Management"
]
            for skill_name in global_skills:
                db.session.add(Skill(name=skill_name))
            db.session.commit()

    # ==============================
    # Register Blueprints
    # ==============================
    from backend.routes.main_routes import main_routes
    from backend.routes.resume_routes import resume_routes
    from backend.routes.dashboard_routes import dashboard_routes
    from backend.routes.roadmap_routes import roadmap_routes
    from backend.routes.salary_routes import salary_routes
    from backend.routes.job_routes import job_routes
    from backend.routes.auth_routes import auth_routes
    from backend.routes.market_routes import market_routes
    from backend.routes.skill_gap_routes import skill_gap_routes
    from backend.routes.forecast_routes import forecast_routes
    from backend.routes.admin_routes import admin_routes
    from backend.routes.application_routes import application_routes
    from backend.routes.resume_compare_routes import resume_compare_routes
    from backend.routes.resume_ai_routes import resume_ai_routes
    from backend.routes.resume_builder_routes import resume_builder
    from backend.routes.coding_routes import coding_bp
    from backend.routes.profile_routes import profile_routes
    from backend.routes.interview_routes import interview_routes
    from backend.routes.ai_recruiter_routes import ai_recruiter_routes
    from backend.routes.vidcode_routes import vidcode_routes, register_socketio_events

    app.register_blueprint(main_routes)
    app.register_blueprint(resume_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(roadmap_routes)
    app.register_blueprint(salary_routes)
    app.register_blueprint(job_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(market_routes)
    app.register_blueprint(skill_gap_routes)
    app.register_blueprint(forecast_routes)
    app.register_blueprint(admin_routes)
    app.register_blueprint(application_routes)
    app.register_blueprint(resume_compare_routes)
    app.register_blueprint(resume_ai_routes)
    app.register_blueprint(resume_builder)
    app.register_blueprint(coding_bp)
    app.register_blueprint(profile_routes)
    app.register_blueprint(interview_routes)
    app.register_blueprint(ai_recruiter_routes)
    app.register_blueprint(vidcode_routes)
    register_socketio_events(socketio)

    # ==============================
    # Start Background Scheduler
    # ==============================
    start_scheduler(app)

    return app


def start_scheduler(app):
    from backend.services.job_ingest_service import JobIngestService
    scheduler = BackgroundScheduler()
    ingest_service = JobIngestService()

    def ingest_wrapper():
        with app.app_context():
            result = ingest_service.fetch_remoteok_jobs()
            print("Job ingestion result:", result)

    scheduler.add_job(
        ingest_wrapper,
        trigger="interval",
        hours=6,
        id="job_ingestion_task",
        replace_existing=True
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())