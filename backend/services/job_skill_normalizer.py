import re

from backend.services.global_skill_library import (
    GLOBAL_SKILLS, GLOBAL_SKILLS_LOWER, SKILL_ALIASES
)
from backend.services.skill_metadata import SKILL_METADATA


# ── CANONICAL FORM MAP ───────────────────────────────────────
# Handles: casing variations, punctuation, common mislabelings
CANONICAL_MAP = {
    # Languages
    "python3":              "Python",
    "python 3":             "Python",
    "python2":              "Python",
    "py":                   "Python",
    "javascript":           "JavaScript",
    "js":                   "JavaScript",
    "typescript":           "TypeScript",
    "ts":                   "TypeScript",
    "golang":               "Go",
    "c plus plus":          "C++",
    "cplusplus":            "C++",
    "c sharp":              "C#",
    "csharp":               "C#",
    "dotnet":               ".NET",
    "dot net":              ".NET",

    # Frameworks
    "reactjs":              "React",
    "react js":             "React",
    "react.js":             "React",
    "vuejs":                "Vue.js",
    "vue js":               "Vue.js",
    "nextjs":               "Next.js",
    "next js":              "Next.js",
    "nodejs":               "Node.js",
    "node js":              "Node.js",
    "expressjs":            "Express.js",
    "express js":           "Express.js",
    "nestjs":               "NestJS",
    "nest js":              "NestJS",
    "angularjs":            "Angular",
    "angular js":           "Angular",
    "springboot":           "Spring Boot",
    "spring-boot":          "Spring Boot",

    # AI/ML
    "ml":                   "Machine Learning",
    "dl":                   "Deep Learning",
    "ai":                   "Artificial Intelligence",
    "nlp":                  "Natural Language Processing",
    "natural lang proc":    "Natural Language Processing",
    "cv":                   "Computer Vision",
    "rl":                   "Reinforcement Learning",
    "llm":                  "Large Language Models",
    "llms":                 "Large Language Models",
    "genai":                "Generative AI",
    "gen ai":               "Generative AI",
    "sklearn":              "Scikit-learn",
    "scikit learn":         "Scikit-learn",
    "scikit-learn":         "Scikit-learn",
    "xgb":                  "XGBoost",
    "lgbm":                 "LightGBM",
    "tf":                   "TensorFlow",
    "pytorch":              "PyTorch",
    "huggingface":          "Hugging Face",
    "hugging face":         "Hugging Face",
    "openai api":           "OpenAI API",
    "openai":               "OpenAI API",
    "wandb":                "Weights & Biases",
    "w&b":                  "Weights & Biases",

    # Cloud / DevOps
    "aws":                  "AWS",
    "amazon web services":  "AWS",
    "amazon aws":           "AWS",
    "gcp":                  "Google Cloud",
    "google cloud platform":"Google Cloud",
    "azure":                "Azure",
    "microsoft azure":      "Azure",
    "k8s":                  "Kubernetes",
    "docker compose":       "Docker",
    "helm charts":          "Helm",
    "argo cd":              "ArgoCD",
    "github actions":       "GitHub Actions",
    "gitlab ci/cd":         "GitLab CI",
    "gitlab ci":            "GitLab CI",
    "terraform iac":        "Terraform",
    "ci/cd":                "CI/CD",
    "ci cd":                "CI/CD",
    "cicd":                 "CI/CD",
    "devops practices":     "DevOps",

    # Databases
    "postgresql":           "PostgreSQL",
    "postgres":             "PostgreSQL",
    "mysql database":       "MySQL",
    "mongodb":              "MongoDB",
    "mongo db":             "MongoDB",
    "redis cache":          "Redis",
    "elasticsearch":        "Elasticsearch",
    "elastic search":       "Elasticsearch",
    "dynamodb":             "DynamoDB",
    "dynamo db":            "DynamoDB",
    "sql server":           "Microsoft SQL Server",
    "mssql":                "Microsoft SQL Server",
    "ms sql":               "Microsoft SQL Server",
    "bigquery":             "BigQuery",
    "big query":            "BigQuery",
    "snowflake dw":         "Snowflake",

    # Data
    "apache spark":         "Apache Spark",
    "spark":                "Apache Spark",
    "apache kafka":         "Apache Kafka",
    "kafka":                "Apache Kafka",
    "airflow":              "Apache Airflow",
    "apache airflow":       "Apache Airflow",
    "dbt":                  "dbt",
    "data build tool":      "dbt",
    "etl pipeline":         "ETL",
    "data pipelines":       "Data Pipelines",
    "data warehouse":       "Data Warehousing",
    "data lake":            "Data Lake",

    # Security
    "cybersecurity":        "Cybersecurity",
    "cyber security":       "Cybersecurity",
    "infosec":              "Cybersecurity",
    "information security": "Cybersecurity",
    "pen testing":          "Penetration Testing",
    "pentest":              "Penetration Testing",
    "ethical hacking":      "Ethical Hacking",
    "network sec":          "Network Security",
    "app sec":              "Application Security",
    "appsec":               "Application Security",
    "cloud sec":            "Cloud Security",

    # Blockchain
    "smart contract":       "Smart Contracts",
    "smart contracts":      "Smart Contracts",
    "web3 dev":             "Web3",
    "ethereum blockchain":  "Ethereum",
    "solidity dev":         "Solidity",

    # Testing
    "unit test":            "Unit Testing",
    "unit tests":           "Unit Testing",
    "integration test":     "Integration Testing",
    "e2e testing":          "End-to-End Testing",
    "end to end testing":   "End-to-End Testing",
    "load testing":         "Load Testing",
    "performance testing":  "Performance Testing",

    # Tools
    "git version control":  "Git",
    "github":               "Git",
    "vscode":               "VS Code",
    "vs code":              "VS Code",
    "jupyter":              "Jupyter Notebook",
    "jupyter lab":          "JupyterLab",
    "google colab":         "Google Colab",
    "postman api":          "Postman",
    "figma design":         "Figma",

    # Analytics / BI
    "powerbi":              "Power BI",
    "power bi":             "Power BI",
    "pbi":                  "Power BI",
    "tableau desktop":      "Tableau",
    "looker studio":        "Looker",
    "data visualization":   "Data Visualization",

    # Methodologies
    "agile methodology":    "Agile",
    "scrum framework":      "Scrum",
    "oop":                  "Object-Oriented Programming",
    "object oriented":      "Object-Oriented Programming",
    "object-oriented":      "Object-Oriented Programming",
    "fp":                   "Functional Programming",
    "functional prog":      "Functional Programming",
    "tdd":                  "TDD",
    "bdd":                  "BDD",
    "rest api":             "REST API",
    "restful api":          "RESTful API",
    "restful":              "RESTful API",
    "graphql api":          "GraphQL",
    "microservices arch":   "Microservices",
    "micro services":       "Microservices",
    "system design":        "System Design",
    "distributed systems":  "Distributed Systems",
    "clean code":           "Clean Code",
    "design patterns":      "Design Patterns",
    "solid principles":     "SOLID Principles",
}


class JobSkillNormalizer:
    """
    Normalizes raw skill strings to their canonical form.
    Uses: CANONICAL_MAP → SKILL_ALIASES → SKILL_METADATA → GLOBAL_SKILLS_LOWER → passthrough
    """

    def normalize_one(self, raw_skill: str) -> str:
        """Normalize a single skill string to its canonical form."""
        if not raw_skill:
            return raw_skill

        s = raw_skill.strip()
        s_lower = s.lower()

        # 1. Direct canonical map hit
        if s_lower in CANONICAL_MAP:
            return CANONICAL_MAP[s_lower]

        # 2. Global skill alias map
        if s_lower in SKILL_ALIASES:
            return SKILL_ALIASES[s_lower]

        # 3. Global skill library exact match (case-insensitive)
        if s_lower in GLOBAL_SKILLS_LOWER:
            return GLOBAL_SKILLS_LOWER[s_lower]

        # 4. SKILL_METADATA canonical match
        for canonical in SKILL_METADATA.keys():
            if s_lower == canonical.lower():
                return canonical

        # 5. Partial match in SKILL_METADATA (s is contained in canonical)
        for canonical in SKILL_METADATA.keys():
            if s_lower in canonical.lower() and len(s_lower) >= 3:
                return canonical

        # 6. Return cleaned original (capitalize properly)
        return self._smart_capitalize(s)

    def normalize(self, skills_list: list) -> list:
        """Normalize a list of skills, removing duplicates."""
        seen = {}  # canonical_lower -> canonical

        for raw in skills_list:
            canonical = self.normalize_one(raw)
            if canonical:
                seen[canonical.lower()] = canonical

        return sorted(list(seen.values()))

    def normalize_and_categorize(self, skills_list: list) -> dict:
        """
        Normalize skills AND group them by category.
        Returns: { 'Languages': [...], 'Frameworks': [...], ... }
        """
        normalized = self.normalize(skills_list)
        categories = {
            "Languages":         [],
            "AI / ML":           [],
            "Data Engineering":  [],
            "Frontend":          [],
            "Backend":           [],
            "Mobile":            [],
            "Databases":         [],
            "Cloud / DevOps":    [],
            "Security":          [],
            "Testing":           [],
            "Tools":             [],
            "Other":             [],
        }

        lang_keywords  = {'python','java','javascript','typescript','go','rust','kotlin',
                          'swift','c','c++','c#','scala','r','ruby','php','dart','haskell'}
        ai_keywords    = {'machine learning','deep learning','nlp','computer vision',
                          'tensorflow','pytorch','keras','scikit','xgboost','llm',
                          'transformers','langchain','generative ai','prompt','rag',
                          'hugging face','openai','reinforcement','neural','bert','gpt'}
        data_keywords  = {'spark','kafka','airflow','flink','dbt','etl','data pipeline',
                          'snowflake','bigquery','databricks','hadoop','redshift','data lake',
                          'data warehouse','data engineering'}
        front_keywords = {'react','angular','vue','next','svelte','html','css','tailwind',
                          'bootstrap','webpack','vite','redux','jquery','graphql','nuxt'}
        back_keywords  = {'flask','django','fastapi','node.js','express','nestjs','spring',
                          'laravel','rails','asp.net','grpc','rest api','microservice',
                          'graphql api','api development'}
        mobile_words   = {'android','ios','flutter','react native','swift','kotlin',
                          'swiftui','jetpack','expo','xamarin'}
        db_keywords    = {'mysql','postgresql','mongodb','redis','cassandra','sqlite',
                          'oracle','dynamodb','elasticsearch','neo4j','supabase','firebase',
                          'influxdb','pinecone','weaviate','qdrant'}
        cloud_kw       = {'aws','azure','gcp','google cloud','docker','kubernetes','terraform',
                          'ansible','jenkins','github actions','ci/cd','devops','sre','helm',
                          'argocd','prometheus','grafana','datadog','serverless','cloud'}
        sec_kw         = {'cybersecurity','penetration','ethical hack','siem','zero trust',
                          'owasp','vulnerability','cryptography','security','infosec'}
        test_kw        = {'testing','selenium','playwright','cypress','jest','pytest',
                          'jmeter','junit','tdd','bdd','unit test','integration test'}
        tool_kw        = {'git','github','jira','confluence','figma','postman','vs code',
                          'jupyter','tableau','power bi','looker','linux','bash','docker',
                          'agile','scrum','notion','slack'}

        for skill in normalized:
            s_lower = skill.lower()
            if   any(kw in s_lower for kw in lang_keywords):  categories["Languages"].append(skill)
            elif any(kw in s_lower for kw in ai_keywords):    categories["AI / ML"].append(skill)
            elif any(kw in s_lower for kw in data_keywords):  categories["Data Engineering"].append(skill)
            elif any(kw in s_lower for kw in front_keywords): categories["Frontend"].append(skill)
            elif any(kw in s_lower for kw in back_keywords):  categories["Backend"].append(skill)
            elif any(kw in s_lower for kw in mobile_words):   categories["Mobile"].append(skill)
            elif any(kw in s_lower for kw in db_keywords):    categories["Databases"].append(skill)
            elif any(kw in s_lower for kw in cloud_kw):       categories["Cloud / DevOps"].append(skill)
            elif any(kw in s_lower for kw in sec_kw):         categories["Security"].append(skill)
            elif any(kw in s_lower for kw in test_kw):        categories["Testing"].append(skill)
            elif any(kw in s_lower for kw in tool_kw):        categories["Tools"].append(skill)
            else:                                              categories["Other"].append(skill)

        return {k: v for k, v in categories.items() if v}

    @staticmethod
    def _smart_capitalize(text: str) -> str:
        """Capitalize skill names properly (not just title case — preserves C++, AWS etc.)"""
        preserve_upper = {'aws','gcp','sql','html','css','api','ai','ml','ux','ui',
                          'ci','cd','nlp','llm','rag','oop','fp','tdd','bdd','vba',
                          'php','ios','sdk','ide','rtos','iot','grpc','rest','jwt',
                          'sre','iam','vpc','dns','http','tcp','udp','orm','dsl',
                          'etl','elt','elk','cdk','jvm','jpa','mvp','dbt','bdd',
                          'cli','gui','pos','kpi','okr','cto','coo','ceo','sla','slo'}
        words = text.split()
        result = []
        for word in words:
            if word.lower() in preserve_upper:
                result.append(word.upper())
            elif '+' in word or '#' in word:
                result.append(word)  # C++, C# etc.
            else:
                result.append(word.capitalize())
        return ' '.join(result)