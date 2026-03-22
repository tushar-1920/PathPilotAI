import re

from backend.services.global_skill_library import (
    GLOBAL_SKILLS, GLOBAL_SKILLS_LOWER, SKILL_ALIASES
)


class JobSkillExtractor:
    """
    Extracts skills from job descriptions using:
    1. N-gram global library matching
    2. Alias/abbreviation resolution
    3. Regex patterns for compound & versioned skills
    4. Inline list parsing (comma/bullet/pipe separated)
    """

    # ── TECH-SPECIFIC REGEX PATTERNS ─────────────────────────
    JD_PATTERNS = [
        (r'\bpython\b',                                   'Python'),
        (r'\bjava\b(?!script)',                           'Java'),
        (r'\bjavascript\b|\bjs\b',                       'JavaScript'),
        (r'\btypescript\b|\bts\b',                       'TypeScript'),
        (r'\bc\+\+\b',                                   'C++'),
        (r'\bc#\b|c\s+sharp',                            'C#'),
        (r'\bgolang\b|\bgo\s+lang\b|\bgo\b(?=\s+(?:developer|engineer|programm))', 'Go'),
        (r'\bruntime?\b|\brust\s+lang\b',                'Rust'),
        (r'\bkotlin\b',                                  'Kotlin'),
        (r'\bswift\b',                                   'Swift'),
        (r'\b\.net\b|\bdotnet\b',                        '.NET'),
        (r'\bnode\.?js?\b',                              'Node.js'),
        (r'\breact\.?js?\b',                             'React'),
        (r'\bvue\.?js?\b',                               'Vue.js'),
        (r'\bangular\.?js?\b',                           'Angular'),
        (r'\bnext\.?js?\b',                              'Next.js'),
        (r'\bsvelte(kit)?\b',                            'Svelte'),
        (r'\bflutter\b',                                 'Flutter'),
        (r'\bspring\s+boot\b',                           'Spring Boot'),
        (r'\bspring\s+cloud\b',                          'Spring Cloud'),
        (r'\bspring\s+security\b',                       'Spring Security'),
        (r'\bdjango\b',                                  'Django'),
        (r'\bfastapi\b',                                 'FastAPI'),
        (r'\bflask\b',                                   'Flask'),
        (r'\bexpress\.?js?\b',                          'Express.js'),
        (r'\bnestjs\b',                                  'NestJS'),
        (r'\blaravel\b',                                 'Laravel'),
        (r'\bruby\s+on\s+rails\b',                      'Ruby on Rails'),
        (r'\basp\.net\b',                                'ASP.NET'),
        (r'\bpostgres(ql)?\b',                           'PostgreSQL'),
        (r'\bmysql\b',                                   'MySQL'),
        (r'\bmongodb\b',                                 'MongoDB'),
        (r'\bredis\b',                                   'Redis'),
        (r'\belastic\s*search\b',                        'Elasticsearch'),
        (r'\bcassandra\b',                               'Cassandra'),
        (r'\bdynamo\s*db\b',                             'DynamoDB'),
        (r'\bsql\s+server\b|\bmssql\b',                 'Microsoft SQL Server'),
        (r'\bsnowflake\b',                               'Snowflake'),
        (r'\bbig\s*query\b',                             'BigQuery'),
        (r'\btensorflow\b|\btf\b',                       'TensorFlow'),
        (r'\bpytorch\b|\btorch\b',                       'PyTorch'),
        (r'\bkeras\b',                                   'Keras'),
        (r'\bscikit[\s\-]?learn\b|\bsklearn\b',         'Scikit-learn'),
        (r'\bxgboost\b',                                 'XGBoost'),
        (r'\blightgbm\b',                                'LightGBM'),
        (r'\bpandas\b',                                  'Pandas'),
        (r'\bnumpy\b',                                   'NumPy'),
        (r'\bmatplotlib\b',                              'Matplotlib'),
        (r'\bhugging\s*face\b',                          'Hugging Face'),
        (r'\blangchain\b',                               'LangChain'),
        (r'\bllama\s*index\b|\bllamaindex\b',            'LlamaIndex'),
        (r'\bopenai\b',                                  'OpenAI API'),
        (r'\bmlflow\b',                                  'MLflow'),
        (r'\bweights\s*&?\s*biases\b|\bw&b\b|\bwandb\b','Weights & Biases'),
        (r'\bdocker\b',                                  'Docker'),
        (r'\bkubernetes\b|\bk8s\b',                     'Kubernetes'),
        (r'\bhelm\b',                                    'Helm'),
        (r'\bterraform\b',                               'Terraform'),
        (r'\bansible\b',                                 'Ansible'),
        (r'\bjenkins\b',                                 'Jenkins'),
        (r'\bgithub\s+actions\b',                        'GitHub Actions'),
        (r'\bgitlab\s+ci\b',                             'GitLab CI'),
        (r'\bcircle\s*ci\b',                             'CircleCI'),
        (r'\bargo\s*cd\b',                               'ArgoCD'),
        (r'\bci\s*/\s*cd\b|\bcicd\b',                   'CI/CD'),
        (r'\bpulumi\b',                                  'Pulumi'),
        (r'\bprometheus\b',                              'Prometheus'),
        (r'\bgrafana\b',                                 'Grafana'),
        (r'\bdatadog\b',                                 'Datadog'),
        (r'\belk\s+stack\b',                             'ELK Stack'),
        (r'\baws\b|\bamazon\s+web\s+services\b',         'AWS'),
        (r'\bazure\b|\bmicrosoft\s+azure\b',             'Azure'),
        (r'\bgcp\b|\bgoogle\s+cloud\b',                  'Google Cloud'),
        (r'\bmachine\s+learning\b',                      'Machine Learning'),
        (r'\bdeep\s+learning\b',                         'Deep Learning'),
        (r'\bnatural\s+language\s+processing\b|\bnlp\b', 'Natural Language Processing'),
        (r'\bcomputer\s+vision\b',                       'Computer Vision'),
        (r'\breinforcement\s+learning\b',                'Reinforcement Learning'),
        (r'\blarge\s+language\s+models?\b|\bllm[s]?\b',  'Large Language Models'),
        (r'\bgenerative\s+ai\b|\bgen\s*ai\b',            'Generative AI'),
        (r'\bprompt\s+engineering\b',                    'Prompt Engineering'),
        (r'\bvector\s+database[s]?\b',                   'Vector Database'),
        (r'\brag\b|\bretrieval[\s\-]augmented\b',        'RAG'),
        (r'\btransformers?\b',                           'Transformers'),
        (r'\bmicro[\s\-]?service[s]?\b',                 'Microservices'),
        (r'\brest[\s\-]?ful?\s*(api[s]?)?\b',            'REST API'),
        (r'\bgraphql\b',                                 'GraphQL'),
        (r'\bgrpc\b',                                    'gRPC'),
        (r'\bsystem\s+design\b',                         'System Design'),
        (r'\bdistributed\s+system[s]?\b',                'Distributed Systems'),
        (r'\bdevops\b',                                  'DevOps'),
        (r'\bmlops\b',                                   'MLOps'),
        (r'\bdata\s+science\b',                          'Data Science'),
        (r'\bdata\s+engineer(ing)?\b',                   'Data Engineering'),
        (r'\bapache\s+spark\b',                          'Apache Spark'),
        (r'\bapache\s+kafka\b',                          'Apache Kafka'),
        (r'\bapache\s+airflow\b',                        'Apache Airflow'),
        (r'\bdbt\b',                                     'dbt'),
        (r'\betl\b',                                     'ETL'),
        (r'\bdata\s+warehouse\b',                        'Data Warehousing'),
        (r'\bdata\s+lake\b',                             'Data Lake'),
        (r'\bsolidity\b',                                'Solidity'),
        (r'\bethereum\b',                                'Ethereum'),
        (r'\bsmart\s+contract[s]?\b',                    'Smart Contracts'),
        (r'\bcybersecurity\b|\binfosec\b',               'Cybersecurity'),
        (r'\bpenetration\s+test(ing)?\b|\bpen\s+test\b', 'Penetration Testing'),
        (r'\bsiem\b',                                    'SIEM'),
        (r'\bzero\s+trust\b',                            'Zero Trust'),
        (r'\bgit\b',                                     'Git'),
        (r'\blinux\b',                                   'Linux'),
        (r'\bbash\b',                                    'Bash'),
        (r'\bsql\b',                                     'SQL'),
        (r'\bunit\s+test(ing)?\b',                       'Unit Testing'),
        (r'\bselenium\b',                                'Selenium'),
        (r'\bplaywright\b',                              'Playwright'),
        (r'\bcypress\b',                                 'Cypress'),
        (r'\bjest\b',                                    'Jest'),
        (r'\bpytest\b',                                  'pytest'),
        (r'\bjmeter\b',                                  'JMeter'),
        (r'\bfigma\b',                                   'Figma'),
        (r'\btableau\b',                                 'Tableau'),
        (r'\bpower\s*bi\b',                              'Power BI'),
        (r'\blooker\b',                                  'Looker'),
        (r'\bagile\b',                                   'Agile'),
        (r'\bscrum\b',                                   'Scrum'),
        (r'\bjira\b',                                    'Jira'),
    ]

    def extract(self, job_description: str) -> list:
        """Main extraction method for job descriptions."""
        text       = job_description
        lower_text = text.lower()
        extracted  = set()

        # ── 1. Regex Pattern Matching ────────────────────────
        for pattern, skill_name in self.JD_PATTERNS:
            try:
                if re.search(pattern, lower_text, re.IGNORECASE):
                    extracted.add(skill_name)
            except re.error:
                pass

        # ── 2. Global Library N-gram Matching ────────────────
        words = lower_text.split()
        ngrams_set = set()
        for n in range(1, 5):
            for i in range(len(words) - n + 1):
                ngrams_set.add(' '.join(words[i:i+n]))

        for skill in GLOBAL_SKILLS:
            skill_lower = skill.lower()
            if skill_lower in ngrams_set:
                extracted.add(skill)

        # ── 3. Alias Resolution ──────────────────────────────
        for alias, canonical in SKILL_ALIASES.items():
            try:
                if re.search(r'\b' + re.escape(alias.lower()) + r'\b', lower_text):
                    extracted.add(canonical)
            except re.error:
                pass

        # ── 4. Requirements Section Parsing ─────────────────
        req_text = self._extract_requirements_section(text)
        if req_text:
            for chunk in re.split(r'[,\n•·\-\|/]', req_text):
                chunk_clean = chunk.strip()
                if 2 <= len(chunk_clean) <= 40:
                    chunk_lower = chunk_clean.lower()
                    if chunk_lower in GLOBAL_SKILLS_LOWER:
                        extracted.add(GLOBAL_SKILLS_LOWER[chunk_lower])
                    elif chunk_lower in SKILL_ALIASES:
                        extracted.add(SKILL_ALIASES[chunk_lower])

        # Cleanup
        cleaned = {s.strip() for s in extracted if s.strip() and len(s.strip()) >= 2}
        return sorted(list(cleaned))

    def _extract_requirements_section(self, text: str) -> str:
        """Extracts text from requirements/qualifications sections."""
        patterns = [
            r'(?i)requirements?\s*[:\-]?\s*\n([\s\S]{20,1000}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)qualifications?\s*[:\-]?\s*\n([\s\S]{20,1000}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)what\s+you.ll\s+(need|bring)\s*[:\-]?\s*\n([\s\S]{20,800}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)must\s+have\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)technical\s+requirements?\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)skills?\s+required\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                return m.group(1) or ''
        return ''