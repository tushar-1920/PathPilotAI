from backend.app import create_app
from backend.extensions import db
from backend.models import Skill, SkillAlias

app = create_app()

ALIASES = {

    # ==========================
    # Programming Languages
    # ==========================

    "Python": ["py", "python3", "cpython"],

    "JavaScript": ["js", "javascript es6", "node"],

    "TypeScript": ["ts"],

    "C++": ["cpp", "c plus plus"],

    "C#": ["csharp", ".net c#"],

    "Go": ["golang"],

    "Rust": ["rustlang"],

    "Kotlin": ["kt"],

    "Swift": ["swiftlang"],

    "MATLAB": ["mat lab"],

    "R": ["r language", "r stats"],


    # ==========================
    # Frontend Frameworks
    # ==========================

    "React": ["reactjs", "react.js"],

    "Angular": ["angularjs"],

    "Vue.js": ["vue", "vuejs"],

    "Next.js": ["nextjs"],

    "HTML": ["html5"],

    "CSS": ["css3"],

    "Tailwind CSS": ["tailwind"],

    "Bootstrap": ["bootstrap5"],


    # ==========================
    # Backend Frameworks
    # ==========================

    "Node.js": ["node", "nodejs"],

    "Express.js": ["express", "expressjs"],

    "Django": ["django framework"],

    "Flask": ["flask framework"],

    "FastAPI": ["fast api"],

    "Spring Boot": ["springboot"],

    "ASP.NET": ["asp net", ".net"],


    # ==========================
    # AI / Machine Learning
    # ==========================

    "Machine Learning": ["ml", "machinelearning"],

    "Deep Learning": ["dl", "deeplearning"],

    "TensorFlow": ["tf", "tensorflow2"],

    "PyTorch": ["torch"],

    "Scikit-learn": ["sklearn", "scikit learn"],

    "Natural Language Processing": ["nlp"],

    "Computer Vision": ["cv"],

    "OpenCV": ["opencv-python"],

    "Transformers": ["huggingface transformers"],

    "LangChain": ["langchain framework"],

    "LangGraph": ["langgraph framework"],

    "CrewAI": ["crewai framework"],

    "AutoGen": ["autogen framework"],


    # ==========================
    # Data Science
    # ==========================

    "NumPy": ["numpy library"],

    "Pandas": ["pandas library"],

    "Matplotlib": ["matplotlib library"],

    "Seaborn": ["seaborn library"],

    "Plotly": ["plotly library"],

    "SciPy": ["scipy library"],


    # ==========================
    # Databases
    # ==========================

    "MySQL": ["mysql database"],

    "PostgreSQL": ["postgres", "postgresql database"],

    "MongoDB": ["mongo", "mongodb database"],

    "SQLite": ["sqlite3"],

    "Redis": ["redis cache"],

    "Oracle Database": ["oracle", "oracle sql"],

    "MariaDB": ["mariadb database"],

    "Firebase": ["firebase database"],


    # ==========================
    # Cloud Platforms
    # ==========================

    "AWS": ["amazon web services"],

    "Amazon EC2": ["ec2"],

    "Amazon S3": ["s3"],

    "AWS Lambda": ["lambda"],

    "Microsoft Azure": ["azure cloud"],

    "Google Cloud Platform": ["gcp", "google cloud"],


    # ==========================
    # DevOps Tools
    # ==========================

    "Docker": ["docker container"],

    "Kubernetes": ["k8s"],

    "CI/CD": ["cicd"],

    "Jenkins": ["jenkins ci"],

    "GitHub Actions": ["github actions ci"],

    "Terraform": ["terraform infra"],

    "Ansible": ["ansible automation"],


    # ==========================
    # Version Control
    # ==========================

    "Git": ["git vcs"],

    "GitHub": ["github platform"],

    "GitLab": ["gitlab platform"],


    # ==========================
    # Mobile Development
    # ==========================

    "Flutter": ["flutter sdk"],

    "React Native": ["reactnative"],

    "Android Development": ["android dev"],

    "iOS Development": ["ios dev"],


    # ==========================
    # Blockchain
    # ==========================

    "Blockchain": ["block chain"],

    "Ethereum": ["eth"],

    "Solidity": ["solidity language"],

    "Web3": ["web3js"],


    # ==========================
    # Operating Systems
    # ==========================

    "Linux": ["linux os"],

    "Ubuntu": ["ubuntu linux"],

    "Windows": ["windows os"],

    "macOS": ["mac os"],


    # ==========================
    # Networking
    # ==========================

    "TCP/IP": ["tcp ip"],

    "HTTP": ["http protocol"],

    "HTTPS": ["https protocol"],

    "DNS": ["dns protocol"],

    "SSH": ["ssh protocol"],


    # ==========================
    # Tools
    # ==========================

    "VS Code": ["vscode"],

    "PyCharm": ["pycharm ide"],

    "IntelliJ": ["intellij ide"],

    "Postman": ["postman api"],

    "JIRA": ["jira tool"],

    "Notion": ["notion workspace"]

}
with app.app_context():

    for skill_name, aliases in ALIASES.items():

        skill = Skill.query.filter_by(name=skill_name).first()

        if skill:

            for alias in aliases:

                exists = SkillAlias.query.filter_by(alias=alias).first()

                if not exists:

                    db.session.add(
                        SkillAlias(
                            alias=alias,
                            skill_id=skill.id
                        )
                    )

    db.session.commit()

    print("Skill aliases loaded successfully")