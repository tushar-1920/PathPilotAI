from backend.app import create_app, db
from backend.models import SkillCategory, Skill

app = create_app()

# Global skill categories
SKILL_CATEGORIES = {

    # ==========================
    # Programming Languages
    # ==========================
    "Programming Languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript",
        "Go", "Rust", "Kotlin", "Swift", "Ruby", "PHP", "R", "MATLAB",
        "Dart", "Scala", "Perl", "Haskell", "Objective-C", "Assembly",
        "Bash", "PowerShell", "Groovy", "Julia", "COBOL", "Fortran"
    ],

    # ==========================
    # Web Development Frontend
    # ==========================
    "Frontend Development": [
        "HTML", "CSS", "SASS", "LESS",
        "Bootstrap", "Tailwind CSS",
        "JavaScript", "TypeScript",
        "React", "Next.js", "Angular", "Vue.js",
        "Redux", "jQuery", "Webpack", "Vite",
        "Responsive Design", "Web Accessibility"
    ],

    # ==========================
    # Backend Development
    # ==========================
    "Backend Development": [
        "Node.js", "Express.js", "Flask", "Django",
        "FastAPI", "Spring Boot", "Laravel",
        "ASP.NET", "Ruby on Rails",
        "REST API", "GraphQL", "Microservices",
        "Authentication", "JWT", "OAuth"
    ],

    # ==========================
    # Database Technologies
    # ==========================
    "Database": [
        "SQL", "MySQL", "PostgreSQL", "SQLite",
        "MongoDB", "Redis", "Oracle Database",
        "MariaDB", "Cassandra", "DynamoDB",
        "Neo4j", "Firebase", "Supabase",
        "NoSQL", "Database Design", "Query Optimization"
    ],

    # ==========================
    # AI and Machine Learning
    # ==========================
    "AI and Machine Learning": [
        "Machine Learning", "Deep Learning",
        "Supervised Learning", "Unsupervised Learning",
        "Reinforcement Learning",
        "TensorFlow", "PyTorch", "Keras",
        "Scikit-learn", "XGBoost", "LightGBM",
        "Natural Language Processing", "NLP",
        "Computer Vision", "OpenCV",
        "Transformers", "Hugging Face",
        "LLM", "LangChain", "LangGraph",
        "AutoGen", "CrewAI",
        "Model Training", "Model Deployment",
        "Feature Engineering", "Model Evaluation"
    ],

    # ==========================
    # Data Science
    # ==========================
    "Data Science": [
        "Pandas", "NumPy", "SciPy",
        "Data Analysis", "Data Cleaning",
        "Data Visualization",
        "Matplotlib", "Seaborn", "Plotly",
        "Statistics", "Probability",
        "Exploratory Data Analysis",
        "Jupyter Notebook"
    ],

    # ==========================
    # Data Engineering
    # ==========================
    "Data Engineering": [
        "Apache Spark", "PySpark",
        "Apache Kafka", "Apache Airflow",
        "ETL", "Data Pipeline",
        "Data Warehousing",
        "Snowflake", "BigQuery", "Redshift"
    ],

    # ==========================
    # Cloud Computing
    # ==========================
    "Cloud Computing": [
        "AWS", "Amazon EC2", "Amazon S3",
        "AWS Lambda", "AWS RDS",
        "Microsoft Azure",
        "Google Cloud Platform",
        "Cloud Architecture",
        "Serverless Computing"
    ],

    # ==========================
    # DevOps
    # ==========================
    "DevOps": [
        "Docker", "Kubernetes",
        "CI/CD", "Jenkins", "GitHub Actions",
        "GitLab CI/CD",
        "Terraform", "Ansible",
        "Containerization", "Orchestration"
    ],

    # ==========================
    # Mobile Development
    # ==========================
    "Mobile Development": [
        "Android Development",
        "Kotlin", "Java Android",
        "Flutter", "Dart",
        "React Native",
        "iOS Development", "Swift"
    ],

    # ==========================
    # Cybersecurity
    # ==========================
    "Cybersecurity": [
        "Network Security",
        "Application Security",
        "Web Security",
        "Cryptography",
        "Ethical Hacking",
        "Penetration Testing",
        "Vulnerability Assessment",
        "OWASP",
        "Encryption", "Authentication"
    ],

    # ==========================
    # Operating Systems
    # ==========================
    "Operating Systems": [
        "Linux", "Ubuntu", "CentOS",
        "Windows", "macOS",
        "Shell Scripting",
        "Process Management",
        "Memory Management"
    ],

    # ==========================
    # Networking
    # ==========================
    "Networking": [
        "TCP/IP", "HTTP", "HTTPS",
        "DNS", "FTP", "SSH",
        "Network Protocols",
        "Socket Programming"
    ],

    # ==========================
    # Version Control
    # ==========================
    "Version Control": [
        "Git", "GitHub", "GitLab",
        "Bitbucket", "Version Control"
    ],

    # ==========================
    # Testing
    # ==========================
    "Testing": [
        "Unit Testing",
        "Integration Testing",
        "Test Automation",
        "Selenium",
        "PyTest",
        "JUnit",
        "Software Testing"
    ],

    # ==========================
    # UI/UX Design
    # ==========================
    "UI UX Design": [
        "UI Design",
        "UX Design",
        "Figma",
        "Adobe XD",
        "Wireframing",
        "Prototyping"
    ],

    # ==========================
    # Blockchain
    # ==========================
    "Blockchain": [
        "Blockchain",
        "Ethereum",
        "Solidity",
        "Smart Contracts",
        "Web3"
    ],

    # ==========================
    # Tools
    # ==========================
    "Tools": [
        "VS Code",
        "PyCharm",
        "IntelliJ",
        "Eclipse",
        "Postman",
        "Swagger",
        "JIRA",
        "Notion"
    ]

}


with app.app_context():

    for category_name, skills in SKILL_CATEGORIES.items():

        category = SkillCategory.query.filter_by(name=category_name).first()

        if not category:
            category = SkillCategory(name=category_name)
            db.session.add(category)
            db.session.commit()

        for skill_name in skills:

            exists = Skill.query.filter_by(name=skill_name).first()

            if not exists:
                skill = Skill(
                    name=skill_name,
                    category_id=category.id,
                    demand_score=0.5,
                    future_score=0.5
                )

                db.session.add(skill)

    db.session.commit()

    print("Global skills loaded successfully")