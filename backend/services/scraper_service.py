import requests
from backend.models import JobPosting
from backend.extensions import db


class LiveScraperService:

    def fetch_remote_jobs(self):

        url = "https://remoteok.com/api"

        try:
            response = requests.get(url)
            data = response.json()

            for job in data[1:20]:

                if not job.get("position"):
                    continue

                new_job = JobPosting(
                    external_id=str(job.get("id")),
                    title=job.get("position"),
                    company=job.get("company"),
                    location="Remote",
                    role=job.get("position"),
                    skills_required=",".join(job.get("tags", [])),
                    normalized_skills=",".join(job.get("tags", [])),
                    source="RemoteOK"
                )

                db.session.add(new_job)

            db.session.commit()

        except Exception as e:
            print("Scraper error:", e)