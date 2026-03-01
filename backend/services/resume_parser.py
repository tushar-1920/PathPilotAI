import pdfplumber
import docx
import spacy
import re

from backend.models import Skill, SkillAlias


nlp = spacy.load("en_core_web_sm")


class ResumeParser:

    # ==========================
    # 🔹 COMMON NORMALIZER
    # ==========================
    def normalize_text(self, text):

        text = text.lower()

        # Convert hyphens and underscores to space
        text = text.replace("-", " ")
        text = text.replace("_", " ")

        # Remove unwanted characters
        text = re.sub(r'[^a-zA-Z0-9+#.\s]', ' ', text)

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()


    # ==========================
    # PDF TEXT EXTRACTION
    # ==========================
    def extract_text_from_pdf(self, file_path):

        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return self.normalize_text(text)


    # ==========================
    # DOCX TEXT EXTRACTION
    # ==========================
    def extract_text_from_docx(self, file_path):

        doc = docx.Document(file_path)

        text = ""

        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"

        return self.normalize_text(text)


    # ==========================
    # 🔥 SKILL EXTRACTION ENGINE (FIXED)
    # ==========================
    def extract_skills(self, resume_text):

        resume_text = self.normalize_text(resume_text)

        tokens = set(resume_text.split())

        extracted_skills = set()

        # --------------------------
        # Exact Skill Matching
        # --------------------------
        skills = Skill.query.all()

        for skill in skills:

            normalized_skill = self.normalize_text(skill.name)

            skill_tokens = normalized_skill.split()

            if all(token in tokens for token in skill_tokens):
                extracted_skills.add(skill.name)

        # --------------------------
        # Alias Matching
        # --------------------------
        aliases = SkillAlias.query.all()

        for alias in aliases:

            normalized_alias = self.normalize_text(alias.alias)

            alias_tokens = normalized_alias.split()

            if all(token in tokens for token in alias_tokens):
                extracted_skills.add(alias.skill.name)

        return sorted(list(extracted_skills))


    # ==========================
    # MAIN PARSER FUNCTION
    # ==========================
    def parse_resume(self, file_path):

        text = ""

        if file_path.endswith(".pdf"):
            text = self.extract_text_from_pdf(file_path)

        elif file_path.endswith(".docx"):
            text = self.extract_text_from_docx(file_path)

        else:
            return []

        skills = self.extract_skills(text)

        return skills