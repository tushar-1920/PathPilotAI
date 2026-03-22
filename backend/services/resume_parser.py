import re
import pdfplumber
import docx

from backend.models import Skill, SkillAlias
from backend.services.global_skill_library import (
    GLOBAL_SKILLS, GLOBAL_SKILLS_LOWER, SKILL_ALIASES
)


class ResumeParser:
    """
    Multi-strategy resume parser.

    Extraction pipeline:
      1. Database skill matching  (Skill + SkillAlias models)
      2. Global library matching  (1000+ skills, n-gram aware)
      3. Alias resolution         (handles abbreviations + typos)
      4. Pattern-based extraction (versions, compound skills)
    """

    # ── NORMALIZATION ────────────────────────────────────────
    def normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[\-_/\\]', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9#+.\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def normalize_for_matching(self, text: str) -> str:
        """Normalizes specifically for skill matching — keeps + and # intact."""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    # ── FILE EXTRACTION ──────────────────────────────────────
    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"[ResumeParser] PDF error: {e}")
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
            # Also extract from tables (skills often listed in tables)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text:
                            text += cell.text + "\n"
        except Exception as e:
            print(f"[ResumeParser] DOCX error: {e}")
        return text

    # ── CORE EXTRACTION ENGINE ───────────────────────────────
    def extract_skills(self, resume_text: str) -> list:
        """
        Multi-strategy extraction:
        1. Database exact match
        2. Global library n-gram match
        3. Alias / abbreviation resolution
        4. Regex pattern match (frameworks with versions etc.)
        """
        raw_text     = resume_text
        norm_text    = self.normalize_text(resume_text)
        lower_text   = resume_text.lower()

        extracted = set()

        # ── Strategy 1: Database Skill Matching ──────────────
        try:
            db_skills = Skill.query.all()
            tokens = set(norm_text.split())

            for skill in db_skills:
                skill_norm = self.normalize_text(skill.name)
                skill_tokens = skill_norm.split()
                if all(t in tokens for t in skill_tokens):
                    extracted.add(skill.name)

            # Alias matching from DB
            aliases = SkillAlias.query.all()
            for alias in aliases:
                alias_norm   = self.normalize_text(alias.alias)
                alias_tokens = alias_norm.split()
                if all(t in tokens for t in alias_tokens):
                    extracted.add(alias.skill.name)
        except Exception as e:
            # DB may not be set up in testing — continue gracefully
            print(f"[ResumeParser] DB strategy skipped: {e}")

        # ── Strategy 2: Global Library N-gram Matching ───────
        # Build n-grams from resume text (unigrams, bigrams, trigrams, 4-grams)
        words       = lower_text.split()
        ngrams_set  = set()
        for n in range(1, 5):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngrams_set.add(ngram)

        for skill in GLOBAL_SKILLS:
            skill_lower = skill.lower()
            # Direct ngram match
            if skill_lower in ngrams_set:
                extracted.add(skill)
                continue
            # Normalized match (handles c++, c#, .net etc.)
            skill_norm = self.normalize_for_matching(skill)
            if skill_norm in ngrams_set:
                extracted.add(skill)
                continue
            # Regex word-boundary match for compound/special skills
            try:
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, lower_text):
                    extracted.add(skill)
            except re.error:
                pass

        # ── Strategy 3: Alias Resolution ─────────────────────
        for alias, canonical in SKILL_ALIASES.items():
            try:
                pattern = r'\b' + re.escape(alias.lower()) + r'\b'
                if re.search(pattern, lower_text):
                    extracted.add(canonical)
            except re.error:
                pass

        # ── Strategy 4: Regex Pattern Matching ───────────────
        # Catches: Python 3.x, React 18, Node 20, TF 2.x, etc.
        version_patterns = [
            (r'\bpython\s*[23][\.\d]*\b',                    'Python'),
            (r'\bjava\s*(se\s*)?\d+\b',                      'Java'),
            (r'\bnode\.?js\s*\d+[\.\d]*\b',                  'Node.js'),
            (r'\breact\.?js?\s*\d+[\.\d]*\b',                'React'),
            (r'\btensorflow\s*[12][\.\d]*\b',                 'TensorFlow'),
            (r'\bpytorch\s*\d[\.\d]*\b',                     'PyTorch'),
            (r'\bangular\s*\d+\b',                            'Angular'),
            (r'\bvue\.?js?\s*[23]\b',                        'Vue.js'),
            (r'\bdocker\s*(compose)?\b',                      'Docker'),
            (r'\bkubernetes\b',                               'Kubernetes'),
            (r'\bsql\s*server\b',                             'Microsoft SQL Server'),
            (r'\bpostgres(ql)?\b',                            'PostgreSQL'),
            (r'\bmachine\s+learning\b',                       'Machine Learning'),
            (r'\bdeep\s+learning\b',                          'Deep Learning'),
            (r'\bnatural\s+language\s+processing\b',          'Natural Language Processing'),
            (r'\bcomputer\s+vision\b',                        'Computer Vision'),
            (r'\breinforcement\s+learning\b',                 'Reinforcement Learning'),
            (r'\blarge\s+language\s+model[s]?\b',             'Large Language Models'),
            (r'\bgenerative\s+ai\b',                          'Generative AI'),
            (r'\bprompt\s+engineering\b',                     'Prompt Engineering'),
            (r'\brest\s*(ful)?\s*(api[s]?)?\b',               'REST API'),
            (r'\bci\s*/\s*cd\b',                              'CI/CD'),
            (r'\bgit\s*(hub|lab)?\b',                         'Git'),
            (r'\bmicro\s*service[s]?\b',                      'Microservices'),
            (r'\bdata\s+science\b',                           'Data Science'),
            (r'\bdata\s+engineer(ing)?\b',                    'Data Engineering'),
            (r'\bdata\s+anal[iy]s[it][sc]\b',                 'Data Analysis'),
            (r'\bdata\s+visual[iz]{1,2}ation\b',              'Data Visualization'),
            (r'\bfeature\s+engineer(ing)?\b',                 'Feature Engineering'),
            (r'\bmodel\s+deploy(ment)?\b',                    'Model Deployment'),
            (r'\bsystem\s+design\b',                          'System Design'),
            (r'\bdistributed\s+systems?\b',                   'Distributed Systems'),
            (r'\bcloud\s+computing\b',                        'Cloud Computing'),
            (r'\bdevops\b',                                   'DevOps'),
            (r'\bmlops\b',                                    'MLOps'),
            (r'\bllm\s*ops\b',                                'LLMOps'),
            (r'\bsmart\s+contract[s]?\b',                     'Smart Contracts'),
            (r'\bembedded\s+(c|systems?|linux)\b',            'Embedded Systems'),
            (r'\breal\s*-?\s*time\s+system[s]?\b',            'Real-time Systems'),
            (r'\binternet\s+of\s+things\b',                   'IoT'),
            (r'\bapache\s+spark\b',                           'Apache Spark'),
            (r'\bapache\s+kafka\b',                           'Apache Kafka'),
            (r'\bapache\s+airflow\b',                         'Apache Airflow'),
            (r'\bapache\s+flink\b',                           'Apache Flink'),
            (r'\bspring\s+boot\b',                            'Spring Boot'),
            (r'\bspring\s+cloud\b',                           'Spring Cloud'),
            (r'\bspring\s+security\b',                        'Spring Security'),
            (r'\bunit\s+test(ing)?\b',                        'Unit Testing'),
            (r'\bend\s*[-\s]to\s*[-\s]end\s+test(ing)?\b',   'End-to-End Testing'),
            (r'\bintegration\s+test(ing)?\b',                 'Integration Testing'),
            (r'\bload\s+test(ing)?\b',                        'Load Testing'),
            (r'\bobject\s*[-\s]oriented\b',                   'Object-Oriented Programming'),
            (r'\bfunctional\s+programming\b',                 'Functional Programming'),
            (r'\bdesign\s+pattern[s]?\b',                     'Design Patterns'),
            (r'\bsolid\s+principle[s]?\b',                    'SOLID Principles'),
            (r'\bclean\s+code\b',                             'Clean Code'),
            (r'\bpenetration\s+test(ing)?\b',                 'Penetration Testing'),
            (r'\bvulnerability\s+assess(ment)?\b',            'Vulnerability Assessment'),
            (r'\bnetwork\s+security\b',                       'Network Security'),
            (r'\bapplication\s+security\b',                   'Application Security'),
            (r'\bcloud\s+security\b',                         'Cloud Security'),
            (r'\ba/?b\s+test(ing)?\b',                        'A/B Testing'),
            (r'\bstatistical\s+anal[iy]s[it][sc]\b',          'Statistical Analysis'),
            (r'\bpredictive\s+model(ing|ling)?\b',            'Predictive Modeling'),
            (r'\btime\s+series\b',                            'Time Series Analysis'),
            (r'\banomaly\s+detect(ion)?\b',                   'Anomaly Detection'),
            (r'\brecommendation\s+system[s]?\b',              'Recommendation Systems'),
            (r'\bgraph\s+(neural\s+network|network[s]?|db)\b','Graph Neural Networks'),
            (r'\bweb\s+scrap(ing|per)\b',                     'Web Scraping'),
            (r'\bdata\s+warehouse(ing)?\b',                   'Data Warehousing'),
            (r'\betl\s*(pipeline[s]?)?\b',                    'ETL'),
            (r'\bpublic\s+speak(ing)?\b',                     'Public Speaking'),
            (r'\bproject\s+manag(er|ement)\b',                'Project Management'),
            (r'\bteam\s+(lead|leader|leadership)\b',          'Leadership'),
            (r'\bopen\s+source\b',                            'Open Source Contribution'),
        ]

        for pattern, skill_name in version_patterns:
            try:
                if re.search(pattern, lower_text):
                    extracted.add(skill_name)
            except re.error:
                pass

        # ── Strategy 5: Section-Aware Extraction ─────────────
        # Skills explicitly listed under "Technical Skills" section
        skills_section = self._extract_skills_section(raw_text)
        if skills_section:
            for chunk in re.split(r'[,|\n•·\-\|]', skills_section):
                chunk_clean = chunk.strip()
                if 2 <= len(chunk_clean) <= 40:
                    # Lookup in global library
                    chunk_lower = chunk_clean.lower()
                    if chunk_lower in GLOBAL_SKILLS_LOWER:
                        extracted.add(GLOBAL_SKILLS_LOWER[chunk_lower])
                    elif chunk_lower in SKILL_ALIASES:
                        extracted.add(SKILL_ALIASES[chunk_lower])
                    elif len(chunk_clean) >= 2 and chunk_clean.replace(' ', '').isalpha():
                        # Add as-is if looks like a real word (not a number/symbol)
                        extracted.add(chunk_clean)

        # ── Deduplicate & filter garbage ────────────────────
        cleaned = set()
        for skill in extracted:
            s = skill.strip()
            if s and len(s) >= 2 and not s.isnumeric():
                cleaned.add(s)

        print(f"[ResumeParser] Extracted {len(cleaned)} skills total.")
        return sorted(list(cleaned))

    # ── SECTION EXTRACTOR ────────────────────────────────────
    def _extract_skills_section(self, text: str) -> str:
        """Extracts text under 'Technical Skills' or 'Skills' section."""
        patterns = [
            r'(?i)technical\s+skills?\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)skills?\s+&?\s*expertise\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)core\s+competenc(y|ies)\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)languages\s+&\s+tools?\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)technologies?\s*[:\-]?\s*\n([\s\S]{20,600}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
            r'(?i)tools?\s+&\s+technologies?\s*[:\-]?\s*\n([\s\S]{20,400}?)(?=\n[A-Z][A-Z\s]{3,}|\Z)',
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                return m.group(1) or m.group(2) or ''
        return ''

    # ── MAIN PARSE ENTRY POINT ───────────────────────────────
    def parse_resume(self, file_path: str) -> list:
        text = ""
        if file_path.lower().endswith(".pdf"):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(".docx"):
            text = self.extract_text_from_docx(file_path)
        elif file_path.lower().endswith(".txt"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            except Exception as e:
                print(f"[ResumeParser] TXT error: {e}")
        else:
            print(f"[ResumeParser] Unsupported file type: {file_path}")
            return []

        if not text.strip():
            print("[ResumeParser] Warning: No text extracted from file.")
            return []

        return self.extract_skills(text)