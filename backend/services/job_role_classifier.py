class JobRoleClassifier:

    def classify(self, title):

        title_lower = title.lower()

        if "backend" in title_lower:
            return "Backend Developer"

        if "ai" in title_lower or "machine learning" in title_lower:
            return "AI Engineer"

        if "full stack" in title_lower:
            return "Full Stack Developer"

        if "data" in title_lower:
            return "Data Scientist"

        if "devops" in title_lower:
            return "DevOps Engineer"

        if "mobile" in title_lower or "android" in title_lower or "ios" in title_lower:
            return "Mobile Developer"

        if "frontend" in title_lower:
            return "Frontend Developer"

        if "cloud" in title_lower:
            return "Cloud Engineer"

        if "qa" in title_lower or "test" in title_lower:
            return "QA Engineer"

        if "security" in title_lower:
            return "Security Engineer"

        return "Other"