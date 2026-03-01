from flask import Flask
from backend.config import Config
from backend.extensions import db
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


def create_app():

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    app.config.from_object(Config)

    db.init_app(app)

    # ==========================================
    # 🔥 CREATE TABLES + SEED DEFAULT DATA
    # ==========================================
    with app.app_context():

        from backend import models
        db.create_all()

        from backend.models import User, Skill

        # ------------------------------
        # Seed Default Test User
        # ------------------------------
        

        # ------------------------------
        # Seed Global Skills
        # ------------------------------
        if Skill.query.count() == 0:

            
            global_skills = [

    # =========================================
    # 🌍 Programming Languages
    # =========================================
    "Python", "Java", "C", "C++", "C#", "JavaScript",
    "TypeScript", "Go", "Rust", "Swift", "Kotlin",
    "PHP", "Ruby", "Scala", "R", "MATLAB",
    "Dart", "Groovy", "Objective-C",
    "Assembly", "Bash", "PowerShell", "VBA",

    # =========================================
    # 🌍 Frontend Development
    # =========================================
    "HTML", "CSS", "SASS", "LESS",
    "Bootstrap", "Tailwind CSS", "Material UI",
    "React", "Next.js", "Redux",
    "Angular", "Vue.js", "Nuxt.js",
    "Svelte", "jQuery",

    # =========================================
    # 🌍 Backend Development
    # =========================================
    "Node.js", "Express.js",
    "Django", "Flask", "FastAPI",
    "Spring Boot", "ASP.NET",
    "Laravel", "Ruby on Rails",
    "GraphQL", "REST API",

    # =========================================
    # 🌍 Mobile Development
    # =========================================
    "Android", "iOS",
    "React Native", "Flutter",
    "SwiftUI", "Kotlin Multiplatform",
    "Xamarin",

    # =========================================
    # 🌍 Databases
    # =========================================
    "MySQL", "PostgreSQL", "MongoDB",
    "Redis", "SQLite", "Oracle",
    "Microsoft SQL Server",
    "Firebase", "Supabase",
    "Cassandra", "DynamoDB",
    "Elasticsearch",

    # =========================================
    # 🌍 Cloud Platforms
    # =========================================
    "AWS", "Azure", "Google Cloud",
    "DigitalOcean", "Heroku",
    "Vercel", "Netlify",

    # =========================================
    # 🌍 DevOps & Infrastructure
    # =========================================
    "Docker", "Kubernetes",
    "CI/CD", "Jenkins",
    "GitHub Actions", "GitLab CI",
    "Terraform", "Ansible",
    "Nginx", "Apache",
    "Linux", "Unix",

    # =========================================
    # 🌍 AI / ML / Data Science
    # =========================================
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

    # =========================================
    # 🌍 Data Engineering
    # =========================================
    "Big Data", "Data Mining",
    "Data Visualization", "Data Analysis",
    "Hadoop", "Spark", "Kafka",
    "Airflow", "ETL",
    "Data Warehousing",
    "Snowflake", "BigQuery",
    "Databricks",

    # =========================================
    # 🌍 Web Scraping
    # =========================================
    "BeautifulSoup", "Scrapy",
    "Selenium", "Web Scraping",

    # =========================================
    # 🌍 Cybersecurity
    # =========================================
    "Cybersecurity", "Ethical Hacking",
    "Penetration Testing", "Network Security",
    "Cryptography", "SOC", "SIEM",

    # =========================================
    # 🌍 Blockchain / Web3
    # =========================================
    "Blockchain", "Solidity",
    "Web3", "Smart Contracts",
    "Ethereum", "Hyperledger",

    # =========================================
    # 🌍 Testing / QA
    # =========================================
    "Unit Testing", "Automation Testing",
    "Cypress", "Jest", "PyTest",
    "Postman",

    # =========================================
    # 🌍 BI / Analytics
    # =========================================
    "Power BI", "Tableau",
    "Excel", "Looker",
    "Google Analytics",

    # =========================================
    # 🌍 Design
    # =========================================
    "Figma", "Adobe XD",
    "Photoshop", "UI/UX Design",
    "Wireframing",

    # =========================================
    # 🌍 Agile / Product
    # =========================================
    "Agile", "Scrum", "Kanban",
    "Product Management",
    "Project Management",
    "Jira", "Notion",

    # =========================================
    # 🌍 Soft Skills
    # =========================================
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
    # ==============================
    # Start Background Scheduler
    # ==============================
    start_scheduler(app)

    return app


# ==========================================
# Background Job Scheduler
# ==========================================
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