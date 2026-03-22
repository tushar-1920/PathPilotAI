# 🚀 PathPilot AI — Startup Context Document

## 🎯 Vision

PathPilot AI is an **AI-powered Career Intelligence SaaS platform** designed to help students, developers, and professionals understand their career readiness, job market fit, salary potential, and skill gaps.

The platform combines **Resume Intelligence, Job Intelligence, Salary Intelligence, and Career Forecasting** into one unified AI system.

Goal:
Build a **Glassdoor + LinkedIn Career Intelligence + AI Career Coach platform**.

---

# 🧠 Core System Modules

## 1️⃣ Resume Intelligence

AI analyzes resumes to extract insights.

Features:

* Resume parsing (PDF / DOCX)
* Skill extraction
* Skill normalization
* Skill categorization
* Resume skill score
* ATS-style scoring

Outputs:

* Extracted skills
* Skill score
* Missing skills
* Career readiness indicators

---

## 2️⃣ Career Analytics

Measures overall readiness for specific roles.

Metrics:

* Skill Score Engine
* Career Readiness Score
* Skill Category Breakdown
* Skill distribution visualization

Example:
Frontend Skills → 70%
Backend Skills → 55%
DevOps → 30%

---

## 3️⃣ AI Career Roadmap

Automatically generates learning paths.

Capabilities:

* Role detection
* Skill gap detection
* Personalized learning roadmap
* Resource recommendations

Example Output:
Year 1 → Python + Data Structures
Year 2 → ML + Statistics
Year 3 → Deep Learning + MLOps

---

## 4️⃣ Job Intelligence

Analyzes job descriptions and compares them with resumes.

Features:

* Job description parsing
* Skill extraction
* Resume vs Job skill comparison
* Fit scoring (Strong / Medium / Weak)

Outputs:

* Match Score
* Matched Skills
* Missing Skills
* Eligibility Score

---

## 5️⃣ Salary Intelligence

AI predicts salary insights based on role, location, experience, and company.

Inputs:

* Role
* Experience
* Country
* State
* Company

Outputs:

* Salary estimate
* Salary growth projection
* Company salary comparison
* Skill salary boosters

Uses:

* AI prompt-based analysis via OpenAI API.

---

## 6️⃣ Market Intelligence

Analyzes job market demand.

Insights:

* Trending skills
* Skill demand ranking
* Industry hiring patterns
* Job role demand analysis

---

## 7️⃣ Career Forecasting

Predicts future career trends.

Capabilities:

* Skill growth projection
* Future role demand
* Emerging technologies

Example:
AI Engineer demand growth → +42%

---

## 8️⃣  Panel

 dashboard for monitoring the platform.

Metrics:

* Total users
* Total resumes
* Total jobs analyzed
* Total applications
* Platform activity metrics
* Mock SaaS revenue analytics

---

# 🔐 Authentication System

Authentication Method:

* Session-based authentication

Security Features:

* Password hashing
* Login required decorator
* Role-based access

Roles:

* Admin
* User

---

# 🗃 Database Models

## User

Stores user profile.

Fields:

* id
* name
* email
* password_hash
* normalized_skills

---

## Resume

Stores uploaded resumes.

Fields:

* id
* user_id
* filename
* normalized_skills
* skill_score
* uploaded_at

---

## SavedJob

Stores analyzed job descriptions.

Fields:

* id
* user_id
* title
* job_level
* description
* job_skills
* score
* eligibility
* created_at

---

## JobPosting

Stores job market data.

Fields:

* id
* title
* role
* description
* company
* location

---

## Application

Tracks saved jobs or applications.

Fields:

* id
* user_id
* job_id
* status

---

# 📂 Project Folder Structure

backend/
app.py
extensions.py
models.py

```
routes/
    job_routes.py
    resume_routes.py
    salary_routes.py
    auth_routes.py

services/
    ai_salary_engine.py
    job_match_engine.py
    job_ingest_service.py
    resume_parser_service.py

utils/
    auth_decorator.py
```

templates/
base.html
dashboard.html
jobs.html
job_analyzer.html
saved_jobs.html
resume_history.html
salary.html

static/
css/
js/

run.py

---

# 🔌 API Endpoints

## Resume APIs

Upload Resume
POST /api/upload-resume

Resume History
GET /api/resume-history

Resume Comparison
POST /api/resume-compare

---

## Job APIs

Get Job Matches
GET /api/job-matches

Analyze Job Description
POST /api/analyze-job

Save Job
POST /api/save-job

Get Saved Jobs
GET /api/saved-jobs

Delete Saved Job
DELETE /api/delete-saved-job/<id>

---

## Resume vs Job Comparison

POST /api/compare-resume-job

Returns:

* match score
* matched skills
* missing skills

---

## Salary Intelligence API

POST /api/ai-salary

Inputs:

* role
* experience
* country
* state
* company

Returns:

* AI-generated salary insights
* career advice
* salary predictions

---

# 🤖 AI Systems

## Salary AI

Uses OpenAI API.

Prompt Example:

"Analyze salary intelligence for a {role} with {experience} years experience in {country}, working at {company}. Provide salary estimate, market demand insights, and career advice."

---

## Resume Intelligence AI

Tasks:

* skill extraction
* skill normalization
* ATS scoring

---

## Job Match AI

Tasks:

* job skill extraction
* resume vs job comparison
* eligibility scoring

---

# 🎨 Frontend Pages

Main Pages:

Dashboard
Resume Upload
Resume History
Job Analyzer
Saved Jobs
Salary Intelligence

Features:

* Chart.js analytics
* glassmorphism UI
* responsive Bootstrap layout

---

# 🧠 Core Algorithms

Resume Skill Extraction
Skill Matching Engine
Job Fit Scoring
Salary Prediction Logic

---

# 🧩 Current Phase

Phase 2 — SaaS Expansion

The core platform is functional with:

* Resume intelligence
* Job intelligence
* Salary intelligence

---

# 🔥 Future Roadmap

## Short Term

Skill Gap Analyzer Pro
AI Career Coach
Salary Market Dataset Expansion
Resume ATS Optimization AI

---

## Mid Term

Subscription Model (SaaS)
Freemium + Premium Plans

Example:

Free

* Resume Analysis
* Basic Job Match

Pro

* Salary Intelligence
* AI Career Roadmap
* Market Intelligence

---

## Long Term

Full Career Operating System

Features:

AI Recruiter Insights
Company Salary Intelligence
Career Path Simulator
AI Interview Trainer
Job Market Forecast Engine

---

# 🌍 Product Positioning

PathPilot AI aims to become:

"An AI-powered career intelligence platform combining the functionality of LinkedIn, Glassdoor, and an AI career coach."

---

# 📈 Startup Goal

Launch as SaaS product with:

Student market
Developer market
Career switchers

Revenue Model:

Freemium → Premium AI features
