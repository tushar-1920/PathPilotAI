import requests
from backend.models import db, JobPosting
from backend.services.job_skill_normalizer import JobSkillNormalizer
from backend.services.job_role_classifier import JobRoleClassifier


class JobIngestService:

    def __init__(self):
        self.normalizer = JobSkillNormalizer()
        self.classifier = JobRoleClassifier()

    def fetch_remoteok_jobs(self):

        url = "https://remoteok.com/api"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
        except Exception:
            return {"inserted": 0, "error": "Request failed"}

        if response.status_code != 200:
            return {"inserted": 0, "error": "API Failed"}

        data = response.json()

        if not isinstance(data, list):
            return {"inserted": 0, "error": "Invalid API format"}

        jobs_data = data[1:]

        inserted = 0
        skipped = 0

        for job in jobs_data[:50]:

            external_id = str(job.get("id"))
            title = job.get("position")
            company = job.get("company")
            location = job.get("location")
            tags = job.get("tags", [])

            if not external_id or not title:
                continue

            exists = JobPosting.query.filter_by(
                external_id=external_id,
                source="remoteok"
            ).first()

            if exists:
                skipped += 1
                continue

            normalized_skills = self.normalizer.normalize(tags)
            role = self.classifier.classify(title)

            new_job = JobPosting(
                external_id=external_id,
                title=title,
                company=company,
                location=location,
                role=role,
                skills_required=", ".join(tags),
                normalized_skills=", ".join(normalized_skills),
                salary="Not Specified",
                source="remoteok"
            )

            db.session.add(new_job)
            inserted += 1

        db.session.commit()

        return {
            "inserted": inserted,
            "skipped_duplicates": skipped
        }