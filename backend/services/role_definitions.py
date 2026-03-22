# ============================================================
#  ROLE DEFINITIONS — 50+ Global Career Paths
#  Each role has stages: Foundation → Core → Advanced → Expert
# ============================================================

ROLE_DEFINITIONS = {

    # ── SOFTWARE ENGINEERING ────────────────────────────────
    "Full Stack Developer": {
        "Foundation": ["HTML", "CSS", "JavaScript", "Git", "Linux Basics"],
        "Frontend Core": ["React", "TypeScript", "Redux", "Tailwind CSS", "REST APIs"],
        "Backend Core": ["Node.js", "Express.js", "SQL", "MongoDB", "Authentication"],
        "Advanced": ["Docker", "CI/CD", "AWS", "GraphQL", "Testing"],
        "Expert": ["System Design", "Microservices", "Performance Optimization", "DevOps Integration"],
    },

    "Frontend Developer": {
        "Foundation": ["HTML", "CSS", "JavaScript", "Git", "Responsive Design"],
        "Core": ["React", "TypeScript", "Redux", "Webpack", "REST APIs"],
        "Advanced": ["Next.js", "Testing (Jest)", "Web Performance", "Accessibility", "CSS-in-JS"],
        "Expert": ["Micro Frontends", "WebAssembly", "Advanced Animations", "Design Systems"],
    },

    "Backend Developer": {
        "Foundation": ["Python", "SQL", "Git", "Linux", "HTTP/REST"],
        "Core": ["Node.js", "Express.js", "PostgreSQL", "MongoDB", "Authentication & JWT"],
        "Advanced": ["Docker", "Redis", "Message Queues", "API Design", "Testing"],
        "Expert": ["System Design", "Microservices", "Kubernetes", "Performance Tuning", "Security"],
    },

    "Python Developer": {
        "Foundation": ["Python", "Git", "Linux", "Data Structures", "OOP"],
        "Core": ["Flask", "FastAPI", "SQL", "SQLAlchemy", "REST APIs"],
        "Advanced": ["Docker", "Celery", "Redis", "Testing (pytest)", "Async Python"],
        "Expert": ["System Design", "Microservices", "Cloud Deployment", "Performance Profiling"],
    },

    "Java Developer": {
        "Foundation": ["Java", "OOP", "Data Structures", "Git", "Maven/Gradle"],
        "Core": ["Spring Boot", "Hibernate", "SQL", "REST APIs", "JUnit"],
        "Advanced": ["Spring Security", "Microservices", "Docker", "Kafka", "Redis"],
        "Expert": ["System Design", "JVM Internals", "Distributed Systems", "Cloud (AWS/GCP)"],
    },

    "Go Developer": {
        "Foundation": ["Go", "Git", "Linux", "Data Structures", "HTTP"],
        "Core": ["Go Modules", "Goroutines & Channels", "SQL", "REST APIs", "Testing"],
        "Advanced": ["gRPC", "Docker", "Kubernetes", "Microservices", "Performance"],
        "Expert": ["Distributed Systems", "Cloud Native", "System Design", "eBPF"],
    },

    "Rust Developer": {
        "Foundation": ["Rust", "Systems Programming", "Git", "Memory Management", "Cargo"],
        "Core": ["Ownership & Borrowing", "Async Rust", "Tokio", "CLI Tools", "Testing"],
        "Advanced": ["WebAssembly", "FFI", "Embedded Rust", "Performance", "Unsafe Rust"],
        "Expert": ["Compiler Internals", "OS Development", "Distributed Systems", "Security"],
    },

    "Mobile Developer (iOS)": {
        "Foundation": ["Swift", "Xcode", "Git", "OOP", "UI Basics"],
        "Core": ["SwiftUI", "UIKit", "Core Data", "Networking", "App Store Deployment"],
        "Advanced": ["Combine", "ARKit", "Core ML", "Push Notifications", "Testing"],
        "Expert": ["App Architecture", "Performance Optimization", "Metal", "App Security"],
    },

    "Mobile Developer (Android)": {
        "Foundation": ["Kotlin", "Android Studio", "Git", "OOP", "XML Layouts"],
        "Core": ["Jetpack Compose", "Room Database", "Retrofit", "MVVM", "Coroutines"],
        "Advanced": ["Firebase", "Push Notifications", "Testing", "Hilt/Dagger", "WorkManager"],
        "Expert": ["App Architecture", "Performance", "Play Store Optimization", "Security"],
    },

    "React Native Developer": {
        "Foundation": ["JavaScript", "React", "Git", "Mobile UX Basics", "Node.js"],
        "Core": ["React Native", "Expo", "Navigation", "State Management", "REST APIs"],
        "Advanced": ["Native Modules", "Animations", "Push Notifications", "Testing", "Performance"],
        "Expert": ["CI/CD for Mobile", "App Store Deployment", "Security", "Offline Support"],
    },

    "Flutter Developer": {
        "Foundation": ["Dart", "Flutter Basics", "Git", "OOP", "Mobile UX"],
        "Core": ["Flutter Widgets", "State Management (Provider/Bloc)", "REST APIs", "Local Storage"],
        "Advanced": ["Firebase", "Animations", "Testing", "Platform Channels", "CI/CD"],
        "Expert": ["Custom Rendering", "App Architecture", "Performance", "Publishing"],
    },

    # ── AI / ML / DATA ──────────────────────────────────────
    "AI Engineer": {
        "Foundation": ["Python", "Mathematics", "Statistics", "Git", "Linear Algebra"],
        "ML Core": ["Scikit-learn", "Pandas", "NumPy", "Data Preprocessing", "Feature Engineering"],
        "Deep Learning": ["TensorFlow", "PyTorch", "Neural Networks", "CNNs", "RNNs"],
        "LLM & GenAI": ["LangChain", "OpenAI API", "Prompt Engineering", "RAG", "Vector Databases"],
        "Expert": ["MLOps", "Model Deployment", "Fine-tuning LLMs", "AI System Design", "Production AI"],
    },

    "Data Scientist": {
        "Foundation": ["Python", "Statistics", "Mathematics", "SQL", "Git"],
        "Analysis": ["Pandas", "NumPy", "Matplotlib", "Seaborn", "EDA"],
        "Machine Learning": ["Scikit-learn", "Feature Engineering", "Model Evaluation", "Cross Validation"],
        "Advanced": ["TensorFlow", "PyTorch", "NLP", "Time Series", "A/B Testing"],
        "Expert": ["MLOps", "Causal Inference", "Bayesian Methods", "Big Data (Spark)", "Research"],
    },

    "Machine Learning Engineer": {
        "Foundation": ["Python", "Linear Algebra", "Statistics", "Git", "SQL"],
        "ML Core": ["Scikit-learn", "Pandas", "NumPy", "Feature Engineering", "Model Evaluation"],
        "Deep Learning": ["TensorFlow", "PyTorch", "Computer Vision", "NLP", "Model Optimization"],
        "Production": ["Docker", "FastAPI", "MLflow", "CI/CD", "Cloud (AWS/GCP)"],
        "Expert": ["MLOps", "Distributed Training", "Model Compression", "AutoML", "Research"],
    },

    "Data Analyst": {
        "Foundation": ["SQL", "Excel", "Statistics", "Python Basics", "Data Literacy"],
        "Core Tools": ["Pandas", "NumPy", "Matplotlib", "Seaborn", "Tableau/Power BI"],
        "Advanced Analysis": ["A/B Testing", "Cohort Analysis", "Funnel Analysis", "EDA", "Regression"],
        "Business Intelligence": ["Dashboard Design", "KPI Reporting", "Data Storytelling", "BigQuery"],
        "Expert": ["Predictive Analytics", "Machine Learning Basics", "dbt", "Data Governance"],
    },

    "Data Engineer": {
        "Foundation": ["Python", "SQL", "Linux", "Git", "Database Concepts"],
        "Core": ["Apache Spark", "Airflow", "ETL Pipelines", "PostgreSQL", "Data Modeling"],
        "Cloud & Storage": ["AWS S3", "Snowflake", "BigQuery", "Kafka", "Redshift"],
        "Advanced": ["dbt", "Delta Lake", "Streaming Pipelines", "Data Quality", "Orchestration"],
        "Expert": ["Data Architecture", "Lakehouse Design", "Real-time Analytics", "Cost Optimization"],
    },

    "Business Intelligence Developer": {
        "Foundation": ["SQL", "Excel", "Data Modeling", "Statistics", "Business Acumen"],
        "Core BI Tools": ["Tableau", "Power BI", "Looker", "DAX", "Data Visualization"],
        "Advanced": ["ETL", "Data Warehousing", "BigQuery", "Snowflake", "Dimensional Modeling"],
        "Expert": ["Enterprise BI Architecture", "Self-service Analytics", "Embedded Analytics"],
    },

    "NLP Engineer": {
        "Foundation": ["Python", "Linguistics", "Statistics", "Git", "Regular Expressions"],
        "Core NLP": ["NLTK", "spaCy", "Text Preprocessing", "Tokenization", "Word Embeddings"],
        "Deep NLP": ["Transformers", "BERT", "GPT", "Hugging Face", "Fine-tuning"],
        "Advanced": ["LangChain", "RAG Systems", "Semantic Search", "Summarization", "NER"],
        "Expert": ["LLM Training", "Multilingual NLP", "Production NLP Systems", "Research"],
    },

    "Computer Vision Engineer": {
        "Foundation": ["Python", "Linear Algebra", "Image Processing", "Git", "OpenCV"],
        "Core": ["Convolutional Networks", "Object Detection", "Image Classification", "PyTorch/TF"],
        "Advanced": ["YOLO", "Segmentation", "GANs", "Video Analysis", "3D Vision"],
        "Expert": ["Real-time Inference", "Edge Deployment", "Custom Architectures", "Research"],
    },

    # ── CLOUD / DEVOPS ──────────────────────────────────────
    "DevOps Engineer": {
        "Foundation": ["Linux", "Bash/Shell", "Git", "Networking Basics", "Python Scripting"],
        "CI/CD": ["Docker", "Jenkins", "GitHub Actions", "GitLab CI", "Artifact Management"],
        "Infrastructure": ["Kubernetes", "Terraform", "Ansible", "AWS/GCP/Azure", "Helm"],
        "Observability": ["Prometheus", "Grafana", "ELK Stack", "Distributed Tracing", "Alerting"],
        "Expert": ["Platform Engineering", "FinOps", "Security (DevSecOps)", "Service Mesh", "SRE"],
    },

    "Cloud Engineer (AWS)": {
        "Foundation": ["Linux", "Networking", "Python", "Git", "Cloud Concepts"],
        "Core AWS": ["EC2", "S3", "IAM", "VPC", "RDS"],
        "Advanced AWS": ["Lambda", "EKS", "CloudFormation", "CDK", "API Gateway"],
        "Architecture": ["Well-Architected Framework", "Cost Optimization", "High Availability", "Security"],
        "Expert": ["Multi-Account Strategy", "Enterprise Architecture", "AWS Certifications", "FinOps"],
    },

    "Cloud Engineer (GCP)": {
        "Foundation": ["Linux", "Python", "Networking", "Git", "Cloud Concepts"],
        "Core GCP": ["Compute Engine", "Cloud Storage", "BigQuery", "Cloud Run", "IAM"],
        "Advanced": ["GKE", "Dataflow", "Pub/Sub", "Cloud Functions", "Terraform"],
        "Expert": ["Data Architecture", "MLOps on GCP", "Enterprise Solutions", "Cost Management"],
    },

    "Site Reliability Engineer (SRE)": {
        "Foundation": ["Linux", "Python", "Networking", "Git", "Systems Thinking"],
        "Core": ["Monitoring & Alerting", "On-call Practice", "Incident Management", "SLOs/SLAs"],
        "Reliability": ["Chaos Engineering", "Capacity Planning", "Performance Tuning", "Toil Reduction"],
        "Infrastructure": ["Kubernetes", "Terraform", "Docker", "Service Mesh", "Distributed Tracing"],
        "Expert": ["Large-scale Systems", "Production Excellence", "Reliability Architecture"],
    },

    "Platform Engineer": {
        "Foundation": ["Linux", "Python", "Git", "Networking", "Cloud Concepts"],
        "Core": ["Kubernetes", "Docker", "Terraform", "CI/CD", "Internal Developer Platforms"],
        "Advanced": ["Backstage", "GitOps (ArgoCD)", "Service Mesh (Istio)", "FinOps", "Observability"],
        "Expert": ["Platform Architecture", "Developer Experience", "Golden Paths", "Multi-tenancy"],
    },

    # ── SECURITY ────────────────────────────────────────────
    "Cybersecurity Engineer": {
        "Foundation": ["Networking", "Linux", "Python", "Cryptography Basics", "Security Fundamentals"],
        "Core": ["Penetration Testing", "SIEM", "Vulnerability Assessment", "Firewalls & IDS/IPS"],
        "Offensive": ["Kali Linux", "Metasploit", "Burp Suite", "OSINT", "Social Engineering"],
        "Defensive": ["Threat Intelligence", "Incident Response", "Digital Forensics", "Zero Trust"],
        "Expert": ["Red Team Operations", "Security Architecture", "Malware Analysis", "Certifications (OSCP/CEH)"],
    },

    "Application Security Engineer": {
        "Foundation": ["Secure Coding", "OWASP Top 10", "Git", "Python/Java", "Web Technologies"],
        "Core": ["SAST/DAST Tools", "Code Review", "Penetration Testing", "Threat Modeling"],
        "Advanced": ["DevSecOps", "Supply Chain Security", "API Security", "Container Security"],
        "Expert": ["Security Architecture", "Compliance (SOC2/ISO)", "Bug Bounty", "Research"],
    },

    "Cloud Security Engineer": {
        "Foundation": ["Cloud Fundamentals", "Networking", "IAM", "Cryptography", "Linux"],
        "Core": ["AWS/GCP/Azure Security", "CSPM", "Cloud Pen Testing", "Zero Trust"],
        "Advanced": ["SIEM on Cloud", "Data Security", "Container Security", "Compliance"],
        "Expert": ["Security Architecture", "FedRAMP/SOC2", "Multi-cloud Security", "Research"],
    },

    # ── BLOCKCHAIN / WEB3 ───────────────────────────────────
    "Blockchain Developer": {
        "Foundation": ["JavaScript", "Python", "Cryptography Basics", "Git", "Networking"],
        "Core": ["Solidity", "Ethereum", "Smart Contracts", "Web3.js/Ethers.js", "Hardhat/Foundry"],
        "DeFi & dApps": ["DeFi Protocols", "ERC Standards", "NFTs", "IPFS", "Metamask Integration"],
        "Advanced": ["Layer 2 Solutions", "Cross-chain Bridges", "ZK Proofs", "DAO Governance"],
        "Expert": ["Protocol Design", "Smart Contract Auditing", "Tokenomics", "Consensus Mechanisms"],
    },

    "Web3 Frontend Developer": {
        "Foundation": ["JavaScript", "React", "TypeScript", "Git", "Web Fundamentals"],
        "Core": ["Ethers.js", "Wagmi", "RainbowKit", "Wallet Integration", "IPFS"],
        "Advanced": ["Next.js", "The Graph", "Subgraph Queries", "NFT Marketplaces", "DeFi UI"],
        "Expert": ["dApp Architecture", "Multi-chain Support", "Gas Optimization UX", "Security UX"],
    },

    # ── EMBEDDED / SYSTEMS ──────────────────────────────────
    "Embedded Systems Engineer": {
        "Foundation": ["C", "C++", "Electronics Basics", "Microcontrollers", "Git"],
        "Core": ["RTOS", "Bare Metal Programming", "UART/SPI/I2C", "Memory Management", "Debugging"],
        "Advanced": ["ARM Architecture", "Linux Drivers", "FPGA Basics", "Power Management"],
        "Expert": ["Safety-critical Systems", "AUTOSAR", "Functional Safety (ISO 26262)", "Optimization"],
    },

    "Systems Programmer": {
        "Foundation": ["C", "C++", "Linux", "Computer Architecture", "Git"],
        "Core": ["Memory Management", "Concurrency", "System Calls", "File Systems", "Networking"],
        "Advanced": ["OS Internals", "Compiler Design", "Virtual Memory", "Performance Profiling"],
        "Expert": ["Kernel Development", "Hypervisors", "Distributed Systems", "Security Research"],
    },

    # ── PRODUCT & DESIGN ────────────────────────────────────
    "Product Manager": {
        "Foundation": ["Product Thinking", "User Research", "Wireframing", "Data Analysis", "Communication"],
        "Core": ["Roadmap Planning", "Agile/Scrum", "A/B Testing", "Metrics & KPIs", "Stakeholder Management"],
        "Advanced": ["Go-to-market Strategy", "Competitive Analysis", "Pricing Strategy", "OKRs"],
        "Expert": ["Product Strategy", "Platform Products", "Enterprise Product", "P&L Management"],
    },

    "UX/UI Designer": {
        "Foundation": ["Design Principles", "Typography", "Color Theory", "Figma Basics", "User Research"],
        "Core": ["Wireframing", "Prototyping", "User Testing", "Information Architecture", "Design Systems"],
        "Advanced": ["Motion Design", "Accessibility", "Design Tokens", "Advanced Figma", "Design Ops"],
        "Expert": ["Product Strategy", "DesignOps", "Design Leadership", "Research Methods"],
    },

    # ── GAME DEV ────────────────────────────────────────────
    "Game Developer (Unity)": {
        "Foundation": ["C#", "Unity Basics", "Linear Algebra", "Git", "Game Design Principles"],
        "Core": ["Unity Physics", "Animation", "UI Systems", "Audio", "Scripting Patterns"],
        "Advanced": ["Shaders (HLSL)", "Networking (Multiplayer)", "Optimization", "Addressables"],
        "Expert": ["Custom Render Pipeline", "Game Architecture", "Platform Publishing", "Tool Development"],
    },

    "Game Developer (Unreal)": {
        "Foundation": ["C++", "Blueprints", "Unreal Basics", "Game Design", "Git"],
        "Core": ["Gameplay Framework", "AI (Behavior Trees)", "Animation Blueprint", "Materials"],
        "Advanced": ["Networking", "Lumen/Nanite", "Performance", "Procedural Generation"],
        "Expert": ["Engine Customization", "Real-time Rendering", "Large-scale Games", "Shipping"],
    },

    # ── QA / TESTING ────────────────────────────────────────
    "QA Engineer": {
        "Foundation": ["Testing Fundamentals", "Bug Reporting", "Agile", "Git", "SQL"],
        "Manual Testing": ["Test Case Design", "Regression Testing", "API Testing (Postman)", "Exploratory Testing"],
        "Automation": ["Selenium", "Playwright", "Cypress", "Python/JavaScript", "CI/CD Integration"],
        "Advanced": ["Performance Testing (JMeter)", "Security Testing", "Mobile Testing", "Test Architecture"],
        "Expert": ["Testing Strategy", "Quality Engineering", "Chaos Testing", "Test Infrastructure"],
    },

    "SDET (Software Dev Engineer in Test)": {
        "Foundation": ["Java/Python", "OOP", "Git", "Testing Fundamentals", "Agile"],
        "Core": ["Selenium", "REST Assured", "JUnit/TestNG", "CI/CD", "API Testing"],
        "Advanced": ["Performance Testing", "Contract Testing (Pact)", "BDD (Cucumber)", "Observability"],
        "Expert": ["Test Framework Design", "Shift-left Testing", "Quality Architecture"],
    },

    # ── DATABASE ────────────────────────────────────────────
    "Database Administrator": {
        "Foundation": ["SQL", "Relational Database Concepts", "Linux", "Backup & Recovery", "Indexing"],
        "Core": ["PostgreSQL", "MySQL", "Query Optimization", "Schema Design", "Replication"],
        "Advanced": ["NoSQL (MongoDB/Cassandra)", "Sharding", "High Availability", "Monitoring", "Security"],
        "Expert": ["Distributed Databases", "Database Architecture", "Performance at Scale", "Migration"],
    },

    "Database Engineer": {
        "Foundation": ["SQL", "Data Modeling", "Python", "Git", "Database Internals"],
        "Core": ["PostgreSQL", "Query Optimization", "Indexing Strategies", "Partitioning"],
        "Advanced": ["Distributed SQL", "TimescaleDB", "Analytics DBs (Snowflake)", "Data Pipelines"],
        "Expert": ["Database Architecture", "Custom Storage Engines", "Large-scale Design"],
    },

    # ── NETWORKING ──────────────────────────────────────────
    "Network Engineer": {
        "Foundation": ["TCP/IP", "OSI Model", "Routing & Switching", "Linux", "Cisco IOS"],
        "Core": ["BGP/OSPF", "VLANs", "Firewalls", "VPN", "Network Troubleshooting"],
        "Advanced": ["SD-WAN", "Network Automation (Ansible/Python)", "Cloud Networking", "MPLS"],
        "Expert": ["Network Architecture", "Zero Trust Networking", "5G/Edge", "Network Design"],
    },

    # ── FINANCE TECH ────────────────────────────────────────
    "Quantitative Analyst": {
        "Foundation": ["Python", "Statistics", "Linear Algebra", "Financial Mathematics", "R"],
        "Core": ["Time Series Analysis", "Statistical Modeling", "Risk Management", "Derivatives Pricing"],
        "Advanced": ["Machine Learning for Finance", "Algorithmic Trading", "Monte Carlo Simulation"],
        "Expert": ["High-frequency Trading", "Stochastic Calculus", "Portfolio Optimization", "Research"],
    },

    "FinTech Developer": {
        "Foundation": ["Python/Java", "SQL", "Git", "Financial Concepts", "REST APIs"],
        "Core": ["Payment APIs", "Banking APIs (Plaid)", "Compliance (PCI DSS)", "Security", "Blockchain Basics"],
        "Advanced": ["Real-time Payments", "Fraud Detection", "RegTech", "Open Banking"],
        "Expert": ["Payment Architecture", "Core Banking Systems", "Central Bank Digital Currency"],
    },

    # ── CLOUD NATIVE ────────────────────────────────────────
    "Kubernetes Engineer": {
        "Foundation": ["Linux", "Docker", "Networking", "YAML", "Git"],
        "Core": ["Kubernetes Core (Pods/Services/Deployments)", "Helm", "RBAC", "Storage", "Networking"],
        "Advanced": ["Operators", "Custom Controllers", "Service Mesh (Istio)", "GitOps (ArgoCD)", "Multi-cluster"],
        "Expert": ["Kubernetes Internals", "Platform Engineering", "Security Hardening", "Performance"],
    },

    # ── ACADEMIC / RESEARCH ─────────────────────────────────
    "Research Scientist (AI)": {
        "Foundation": ["Python", "Mathematics", "Statistics", "Linear Algebra", "Calculus"],
        "Core": ["PyTorch", "Research Paper Reading", "Experiment Tracking (MLflow/W&B)", "Literature Review"],
        "Advanced": ["Novel Architecture Design", "Large-scale Experiments", "Writing Papers", "Benchmarking"],
        "Expert": ["Publishing at Top Venues (NeurIPS/ICML)", "Reproducibility", "Open Source Contributions"],
    },

    # ── AUTOMATION / RPA ────────────────────────────────────
    "Automation Engineer": {
        "Foundation": ["Python", "Linux", "Shell Scripting", "Git", "APIs"],
        "Core": ["Selenium", "Robot Framework", "Process Automation", "CI/CD", "Scripting"],
        "Advanced": ["RPA Tools (UiPath/Automation Anywhere)", "AI-powered Automation", "API Automation"],
        "Expert": ["Enterprise Automation Architecture", "Cognitive Automation", "CoE Leadership"],
    },

    # ── ADDITIONAL HIGH-DEMAND ──────────────────────────────
    "API Developer": {
        "Foundation": ["HTTP/REST", "Python/Node.js", "JSON", "Git", "SQL"],
        "Core": ["FastAPI/Express", "Authentication (JWT/OAuth)", "API Design", "Documentation (Swagger)"],
        "Advanced": ["GraphQL", "gRPC", "Rate Limiting", "Caching", "Versioning"],
        "Expert": ["API Gateway", "Developer Experience", "Monetization", "Large-scale APIs"],
    },

    "Prompt Engineer": {
        "Foundation": ["Language Models Basics", "Python", "Technical Writing", "API Basics"],
        "Core": ["Prompt Design Patterns", "Chain-of-Thought", "Few-shot Learning", "OpenAI/Anthropic APIs"],
        "Advanced": ["LangChain", "RAG Systems", "Evaluation Frameworks", "Red Teaming"],
        "Expert": ["LLM Fine-tuning", "AI Product Development", "Agentic Systems", "LLMOps"],
    },

    "MLOps Engineer": {
        "Foundation": ["Python", "Docker", "Git", "Linux", "Cloud Basics"],
        "Core": ["MLflow", "Model Deployment (FastAPI)", "CI/CD for ML", "Feature Stores", "Data Versioning"],
        "Advanced": ["Kubernetes for ML", "Kubeflow", "Model Monitoring", "A/B Testing Models", "Distributed Training"],
        "Expert": ["ML Platform Architecture", "LLMOps", "Cost Optimization", "Enterprise MLOps"],
    },

    "Technical Writer": {
        "Foundation": ["Writing Skills", "Git/Markdown", "API Basics", "Documentation Tools", "Research"],
        "Core": ["API Documentation", "User Guides", "Docs-as-Code", "Static Site Generators", "Diagrams"],
        "Advanced": ["Developer Portals", "SDK Documentation", "Content Strategy", "Localization"],
        "Expert": ["Documentation Architecture", "Content Systems", "Developer Experience", "Standards"],
    },

    "Solutions Architect": {
        "Foundation": ["Cloud Fundamentals", "Networking", "Security", "Databases", "Systems Design"],
        "Core": ["AWS/GCP/Azure Architecture", "Microservices", "Event-Driven Architecture", "Cost Estimation"],
        "Advanced": ["Enterprise Architecture", "Migration Strategy", "Well-Architected Review", "Compliance"],
        "Expert": ["Global Architecture", "Digital Transformation", "Architecture Governance", "Certifications"],
    },

    "Engineering Manager": {
        "Foundation": ["Software Development Experience", "Communication", "Agile/Scrum", "People Management"],
        "Core": ["1:1 Management", "Hiring & Interviews", "Performance Reviews", "Roadmap Planning", "OKRs"],
        "Advanced": ["Technical Strategy", "Cross-team Collaboration", "Budget Management", "Conflict Resolution"],
        "Expert": ["Organizational Design", "Engineering Culture", "VP-level Leadership", "M&A Integration"],
    },

    "Startup CTO": {
        "Foundation": ["Full Stack Development", "System Design", "Cloud", "Git", "Product Thinking"],
        "Core": ["Architecture Decisions", "Tech Stack Selection", "Team Building", "MVP Development"],
        "Advanced": ["Scalability", "Security", "DevOps Culture", "Fundraising Support", "Compliance"],
        "Expert": ["Technical Vision", "Board Communication", "IPO Readiness", "Global Engineering"],
    },
}