<div align="center">

<!-- BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=PathPilot%20AI&fontSize=70&fontColor=fff&animation=twinkling&fontAlignY=32&desc=Your%20AI-Powered%20Career%20Intelligence%20Operating%20System&descAlignY=55&descSize=18" width="100%"/>

<br/>

<!-- BADGES ROW 1 -->
<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Stripe-Payments-008CDD?style=for-the-badge&logo=stripe&logoColor=white"/>
</p>

<!-- BADGES ROW 2 -->
<p>
  <img src="https://img.shields.io/badge/SocketIO-Real--Time-010101?style=for-the-badge&logo=socket.io&logoColor=white"/>
  <img src="https://img.shields.io/badge/Gunicorn-Production-499848?style=for-the-badge&logo=gunicorn&logoColor=white"/>
  <img src="https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white"/>
  <img src="https://img.shields.io/badge/Bootstrap-Frontend-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white"/>
  <img src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
</p>

<!-- BADGES ROW 3 -->
<p>
  <img src="https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Phase-2%20SaaS%20Expansion-blueviolet?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-ff69b4?style=for-the-badge"/>
</p>

<br/>

> ### 🚀 *"Not just a career tool. A career operating system."*
> **PathPilot AI** combines the intelligence of **LinkedIn + Glassdoor + AI Career Coach** into one unified SaaS platform — powered by GPT-4 and built for the next generation of professionals.

<br/>

</div>

---

## 📌 Table of Contents

- [🌟 What is PathPilot AI?](#-what-is-pathpilot-ai)
- [🎯 Core Vision](#-core-vision)
- [⚙️ How It Works — Full System Flow](#%EF%B8%8F-how-it-works--full-system-flow)
- [🧠 AI Feature Modules (Detailed)](#-ai-feature-modules-detailed)
- [🗃️ Database Architecture](#%EF%B8%8F-database-architecture)
- [🔌 API Reference](#-api-reference)
- [🏗️ Project Structure](#%EF%B8%8F-project-structure)
- [💻 Tech Stack](#-tech-stack)
- [🚀 Getting Started](#-getting-started)
- [💰 SaaS Subscription Model](#-saas-subscription-model)
- [🔐 Authentication & Security](#-authentication--security)
- [🗺️ Roadmap](#%EF%B8%8F-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

<div align="center">

## 🌟 What is PathPilot AI?

</div>

PathPilot AI is a **full-stack AI-powered Career Intelligence SaaS Platform** built with Flask, powered by OpenAI GPT-4, and deployed on Render. It is designed to help students, developers, and professionals navigate their careers with superhuman clarity — by analyzing resumes, predicting salaries, detecting skill gaps, simulating interviews, running coding duels, and forecasting market trends.

Think of it as your **personal AI career co-pilot**, always in your corner.

<br/>

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   "The platform that replaces 5 career tools with one AI brain."        │
│                                                                         │
│   ✅ Resume Intelligence     ✅ Salary Prediction                       │
│   ✅ Job Match Engine        ✅ AI Interview Simulator                  │
│   ✅ Career Roadmap          ✅ Real-Time Coding Battles                 │
│   ✅ Skill Gap Analysis      ✅ Career Time Machine                     │
│   ✅ Offer Probability       ✅ Blind Spot Detector                     │
│   ✅ Market Intelligence     ✅ AI Cover Letter Generator                │
│   ✅ Career DNA Profiling    ✅ VidCode Collaboration Rooms             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

<div align="center">

## 🎯 Core Vision

</div>

<table align="center">
<tr>
<td align="center" width="33%">

### 🎓 For Students
Understand your career readiness before graduation. Know exactly what skills you're missing for your dream role. Get a personalized AI roadmap.

</td>
<td align="center" width="33%">

### 👨‍💻 For Developers
Benchmark your skills against market demand. Predict your salary at any company. Battle other devs in live coding duels.

</td>
<td align="center" width="33%">

### 🔄 For Career Switchers
Simulate interviews for roles you've never held. Analyze skill transfer gaps. Get a 6-month migration plan powered by AI.

</td>
</tr>
</table>

---

<div align="center">

## ⚙️ How It Works — Full System Flow

</div>

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        PATHPILOT AI — SYSTEM FLOW                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   STEP 1: USER ONBOARDING                                                   ║
║   ┌─────────────────────────────────────────────────────┐                  ║
║   │  Register / Login → Email OTP Verification          │                  ║
║   │  Set Role (Student / Developer / Career Switcher)   │                  ║
║   │  Upload Resume (PDF / DOCX)                         │                  ║
║   └─────────────────┬───────────────────────────────────┘                  ║
║                     │                                                        ║
║   STEP 2: RESUME INTELLIGENCE ENGINE                                        ║
║   ┌─────────────────▼───────────────────────────────────┐                  ║
║   │  pdfplumber / python-docx → Raw Text Extraction     │                  ║
║   │  Skill Extraction → 500+ Skill Global Library       │                  ║
║   │  Skill Normalization → Alias Resolution Engine      │                  ║
║   │  Skill Scoring → Category Breakdown (Frontend,      │                  ║
║   │    Backend, DevOps, ML, Data, Cloud, etc.)          │                  ║
║   │  ATS Score Generation → Career Readiness Report     │                  ║
║   └─────────────────┬───────────────────────────────────┘                  ║
║                     │                                                        ║
║   STEP 3: AI MODULES ACTIVATED (Parallel)                                   ║
║   ┌─────────────────▼───────────────────────────────────┐                  ║
║   │  ┌────────────────┐  ┌──────────────────────────┐  │                  ║
║   │  │ JOB MATCH      │  │ SALARY INTELLIGENCE      │  │                  ║
║   │  │ ENGINE         │  │ ENGINE                   │  │                  ║
║   │  │                │  │                          │  │                  ║
║   │  │ JD Parsing →   │  │ Role + Experience +      │  │                  ║
║   │  │ Skill Extract  │  │ Location + Company →     │  │                  ║
║   │  │ Resume vs JD   │  │ GPT-4 Prompt →           │  │                  ║
║   │  │ Comparison →   │  │ Salary Estimate +        │  │                  ║
║   │  │ Match Score    │  │ Growth Projection        │  │                  ║
║   │  └────────────────┘  └──────────────────────────┘  │                  ║
║   │  ┌────────────────┐  ┌──────────────────────────┐  │                  ║
║   │  │ SKILL GAP      │  │ CAREER ROADMAP           │  │                  ║
║   │  │ ANALYZER       │  │ ENGINE                   │  │                  ║
║   │  │                │  │                          │  │                  ║
║   │  │ User Skills vs │  │ Target Role Detection    │  │                  ║
║   │  │ Target Role    │  │ Gap Identification →     │  │                  ║
║   │  │ Missing Skills │  │ Personalized Learning    │  │                  ║
║   │  │ Priority Queue │  │ Path + Resources         │  │                  ║
║   │  └────────────────┘  └──────────────────────────┘  │                  ║
║   └─────────────────┬───────────────────────────────────┘                  ║
║                     │                                                        ║
║   STEP 4: ADVANCED AI FEATURES                                              ║
║   ┌─────────────────▼───────────────────────────────────┐                  ║
║   │  AI Recruiter → Real Interview Simulation w/ Voice  │                  ║
║   │  Career Time Machine → Future Career Projection     │                  ║
║   │  Offer Predictor → Offer Probability Scoring        │                  ║
║   │  Blind Spot Detector → Hidden Weakness Analysis     │                  ║
║   │  Career Forecast → Market Trend Predictions         │                  ║
║   └─────────────────┬───────────────────────────────────┘                  ║
║                     │                                                        ║
║   STEP 5: SOCIAL + COMPETITIVE LAYER                                        ║
║   ┌─────────────────▼───────────────────────────────────┐                  ║
║   │  Battle Mode → 1v1 Live Coding Duels (Socket.IO)   │                  ║
║   │  VidCode → Collaborative Coding + Video Rooms       │                  ║
║   │  Social Feed → Posts, Achievements, Connections     │                  ║
║   │  Recruiter Portal → Post Jobs, Search Candidates    │                  ║
║   └─────────────────┬───────────────────────────────────┘                  ║
║                     │                                                        ║
║   STEP 6: SAAS INFRASTRUCTURE                                               ║
║   ┌─────────────────▼───────────────────────────────────┐                  ║
║   │  Stripe Subscriptions → Free / Pro / Enterprise     │                  ║
║   │  Admin Dashboard → Platform Analytics               │                  ║
║   │  Notifications Hub → Universal Alert System         │                  ║
║   │  Render Deployment → Gunicorn + gthread Workers     │                  ║
║   └─────────────────────────────────────────────────────┘                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

<div align="center">

## 🧠 AI Feature Modules (Detailed)

</div>

### 📄 1. Resume Intelligence Engine

> *"Your resume speaks. PathPilot translates."*

The Resume Intelligence module is the heart of PathPilot AI. Every feature downstream depends on the data extracted here.

```
Resume Upload (PDF / DOCX)
         │
         ▼
   Text Extraction
   ┌──────────────────────────────────┐
   │  pdfplumber  →  PDF text         │
   │  python-docx →  DOCX text        │
   └──────────────────┬───────────────┘
                      │
         ▼
   Skill Extraction & Normalization
   ┌──────────────────────────────────┐
   │  Global Skill Library (500+)     │
   │  Skill Alias Resolution Engine   │
   │  "JS" → "JavaScript"             │
   │  "Py" → "Python"                 │
   │  "TF" → "TensorFlow"             │
   └──────────────────┬───────────────┘
                      │
         ▼
   Skill Categorization
   ┌──────────────────────────────────┐
   │  Frontend     → React, Vue, CSS  │
   │  Backend      → Node, Django     │
   │  DevOps       → Docker, K8s      │
   │  ML/AI        → PyTorch, TF      │
   │  Data         → SQL, Pandas      │
   │  Cloud        → AWS, GCP, Azure  │
   └──────────────────┬───────────────┘
                      │
         ▼
   Scoring & Output
   ┌──────────────────────────────────┐
   │  Skill Score (0–100)             │
   │  ATS Compatibility Score         │
   │  Career Readiness Tier           │
   │  Missing Skills List             │
   │  Category Breakdown Chart        │
   └──────────────────────────────────┘
```

**Key Technologies:** `pdfplumber`, `python-docx`, `scikit-learn`, Custom Skill Normalizer

---

### 💼 2. Job Intelligence & Match Engine

> *"Know if a job is right for you before you click Apply."*

```
Paste Job Description / URL
         │
         ▼
   JD Parsing Engine
   ┌──────────────────────────────────┐
   │  Role Detection                  │
   │  Required Skills Extraction      │
   │  Experience Level Classification │
   │  Tech Stack Identification       │
   └──────────────────┬───────────────┘
                      │
         ▼
   Resume vs Job Comparison
   ┌──────────────────────────────────┐
   │  Matched Skills List             │
   │  Missing Skills List             │
   │  Match Score (0–100%)            │
   │  Eligibility: Strong/Medium/Weak │
   └──────────────────────────────────┘
```

**Endpoints:** `POST /api/analyze-job`, `POST /api/compare-resume-job`, `GET /api/job-matches`

---

### 💰 3. Salary Intelligence Engine

> *"Know your worth. Then ask for more."*

The AI Salary Engine uses GPT-4 to generate hyper-personalized salary intelligence based on role, location, experience, and target company.

```
Inputs:
  Role + Experience + Country + State + Company
         │
         ▼
   GPT-4 Prompt Engine
   ┌──────────────────────────────────────────┐
   │  "Analyze salary for [Role] with         │
   │   [X] years in [Country] at [Company].   │
   │   Include market demand, growth,         │
   │   negotiation tips, and skill boosters." │
   └──────────────────┬───────────────────────┘
                      │
         ▼
   Outputs:
   ┌──────────────────────────────────────────┐
   │  Salary Estimate (Min / Mid / Max)       │
   │  3-Year Salary Growth Projection         │
   │  Company-Specific Salary Comparison      │
   │  Top Skill Salary Boosters               │
   │  Negotiation Strategy                    │
   │  Market Demand Rating                    │
   └──────────────────────────────────────────┘
```

**Supplementary Services:** `ai_salary_engine.py`, `company_salary_engine.py`, `experience_salary_model.py`, `global_salary_dataset.py`

---

### 🗺️ 4. AI Career Roadmap Generator

> *"Your personalized GPS to your dream role."*

```
User's Current Skills + Target Role
         │
         ▼
   Gap Analysis → Missing Skills Priority Queue
         │
         ▼
   Roadmap Engine (AI)
   ┌──────────────────────────────────────────┐
   │  Month 1–3   → Foundation Skills         │
   │  Month 4–6   → Core Technical Skills     │
   │  Month 7–9   → Advanced + Specialization │
   │  Month 10–12 → Projects + Portfolio      │
   └──────────────────┬───────────────────────┘
                      │
         ▼
   Per-Step Resources:
   ┌──────────────────────────────────────────┐
   │  Free Courses (YouTube, Coursera, freeCC)│
   │  Estimated Time to Complete              │
   │  Practice Projects Suggestions           │
   │  Milestone Checkpoints                   │
   └──────────────────────────────────────────┘
```

---

### 🎭 5. AI Recruiter — Interview Simulator

> *"Face a real AI interviewer. Get brutally honest feedback."*

```
User selects:
  Role + Difficulty Level + Interviewer Personality
         │
         ▼
   AI Recruiter Room
   ┌──────────────────────────────────────────┐
   │  Face Detection (Camera)                 │
   │  Voice Input + Text Fallback             │
   │  GPT-4 Dynamic Follow-up Questions       │
   │  Real-time Response Evaluation           │
   └──────────────────┬───────────────────────┘
                      │
         ▼
   Interview Report:
   ┌──────────────────────────────────────────┐
   │  Communication Score                     │
   │  Technical Accuracy Score                │
   │  Confidence Meter                        │
   │  Strengths & Improvement Areas           │
   │  Tailored Feedback per Answer            │
   │  Session History Tracking                │
   └──────────────────────────────────────────┘
```

**Session History:** Stored per user. Review past interview performance over time.

---

### ⏳ 6. Career Time Machine

> *"See yourself 5 years into the future — and work backwards."*

One of PathPilot's most innovative modules. Users set a target role and company, and the AI constructs a month-by-month career migration plan.

```
Inputs: Target Role + Company + Timeline (months) + Current Level
         │
         ▼
   AI Career Plan Generator (GPT-4)
   ┌──────────────────────────────────────────┐
   │  Analyzes your current resume skills     │
   │  Reverse-engineers path from goal        │
   │  Creates month-by-month milestone plan   │
   │  Identifies transition risks             │
   └──────────────────┬───────────────────────┘
                      │
         ▼
   Milestone Tracker:
   ┌──────────────────────────────────────────┐
   │  CareerTimeMachine DB Model              │
   │  CareerMilestoneProgress Tracking        │
   │  Completion % per Milestone              │
   │  Mark milestones complete in real-time  │
   └──────────────────────────────────────────┘
```

---

### 🔮 7. Offer Predictor Engine

> *"Should you even apply? Get an AI probability score first."*

```
Input: Job Title + Company + Job Description / URL
         │
         ▼
   Deep Analysis (GPT-4)
   ┌──────────────────────────────────────────┐
   │  Offer Probability Score (0–100%)        │
   │  Readiness Tier: Strong / Possible /     │
   │    Long Shot / Not Ready                 │
   │  Top 3 Blockers                          │
   │  Top 3 Strengths                         │
   │  30-Day Close-the-Gap Plan               │
   │  Resume Audit (specific issues)          │
   │  Company Culture Intel                   │
   │  Predicted Interview Questions           │
   │  Salary Intelligence for the Role        │
   │  Brutally Honest Coach Message           │
   └──────────────────────────────────────────┘

Sub-Scores:
  ├── Skills Match Score
  ├── Resume Quality Score
  ├── Project Depth Score
  └── Experience Relevance Score
```

**DB Model:** `OfferPrediction` — full history with JSON blobs per prediction.

---

### 👁️ 8. Blind Spot Detector

> *"See what you can't see about yourself."*

```
Analysis of user's full profile →
  GPT-4 detects hidden weaknesses in:
  ┌──────────────────────────────────┐
  │  Skills that seem present but    │
  │  are superficially listed        │
  │  Resume formatting blind spots   │
  │  Career progression gaps         │
  │  Industry perception issues      │
  │  Keyword absence in resume       │
  └──────────────────────────────────┘

  Deep Dive Report:
  ┌──────────────────────────────────┐
  │  Blind Spot Category             │
  │  Severity Level                  │
  │  Impact on Job Search            │
  │  Actionable Fix                  │
  └──────────────────────────────────┘
```

---

### 📊 9. Market Intelligence Dashboard

> *"Know the job market better than any recruiter."*

```
Market Intelligence Engine:
  ┌────────────────────────────────────────┐
  │  Trending Skills by Domain             │
  │  Skill Demand Ranking (Live Data)      │
  │  Industry Hiring Velocity              │
  │  Role Demand Analysis                  │
  │  Top Paying Skills Right Now           │
  │  Emerging Technology Signals           │
  └────────────────────────────────────────┘

Services:
  market_intelligence.py
  market_intelligence_service.py
  market_analytics.py
```

---

### 📈 10. Career Forecast Engine

> *"Predict the future of your career before the market does."*

```
Forecasting Engine:
  ┌────────────────────────────────────────┐
  │  AI Skill Growth Projections           │
  │  Role Demand Forecast (1–3 years)      │
  │  Emerging Tech Adoption Curve          │
  │  "AI Engineer demand growth → +42%"   │
  │  Risk Assessment per Skill/Role        │
  └────────────────────────────────────────┘
```

---

### ⚔️ 11. Battle Mode — 1v1 Coding Duels

> *"Code faster than your opponent. Win XP. Earn trophies."*

A fully real-time competitive coding system built on **Socket.IO** and **in-memory duel rooms**.

```
Battle Flow:
  Player 1 creates duel → gets DUEL_CODE
         │
         ▼
  Player 2 joins with DUEL_CODE
         │
         ▼
  AI generates problem (Easy/Medium/Hard)
         │
         ▼
  Live Coding Interface
  ┌──────────────────────────────────────────┐
  │  Both players code simultaneously        │
  │  Real-time submission checking           │
  │  Test cases run live                     │
  │  First to pass all test cases wins       │
  └──────────────────┬───────────────────────┘
                     │
         ▼
  XP & Trophy System:
  ┌──────────────────────────────────────────┐
  │  Win Easy    → +50 XP, +15 Trophies      │
  │  Win Medium  → +100 XP, +20 Trophies     │
  │  Win Hard    → +200 XP, +30 Trophies     │
  │  Loss Easy   → +10 XP, -3 Trophies       │
  │  Draw        → +25 XP, ±0 Trophies       │
  │  Streak Bonuses                          │
  │  League Ranking (Bronze → Legend)        │
  └──────────────────────────────────────────┘

BattleProfile: total_xp, trophies, wins, losses,
               current_streak, best_streak,
               easy/medium/hard_wins
```

---

### 🎥 12. VidCode — Collaborative Coding Rooms

> *"Pair program with anyone, anywhere, in real-time."*

```
VidCode Room Features:
  ┌──────────────────────────────────────────┐
  │  Live Collaborative Code Editor          │
  │  Video Call Integration (WebRTC)         │
  │  Multi-language Support (Python, JS,     │
  │    Java, C++, Go, Rust, and more)        │
  │  Code Execution in Browser               │
  │  Room creation with share code           │
  │  Real-time sync via Socket.IO            │
  └──────────────────────────────────────────┘
```

---

### 📝 13. AI Cover Letter Generator

> *"One click. A perfect cover letter tailored to the job."*

```
Inputs: Job Title + Company + Job Description + User Resume
         │
         ▼
   GPT-4 Cover Letter Engine
         │
         ▼
   Output: Personalized, ATS-friendly cover letter
           matching the JD + highlighting relevant skills
```

---

### 📋 14. AI Resume Builder

> *"Build an ATS-ready resume from scratch with AI guidance."*

```
Resume Builder Features:
  ┌──────────────────────────────────────────┐
  │  Section-by-section AI suggestions      │
  │  ATS optimization hints                 │
  │  Keyword insertion recommendations      │
  │  PDF generation via ReportLab           │
  │  Resume history & versioning            │
  │  Side-by-side resume comparison         │
  └──────────────────────────────────────────┘
```

---

### 🔔 15. Notification & Hiring Alert System

```
Notification Types:
  ┌──────────────────────────────────────────┐
  │  recruiter_message  → Recruiter contact  │
  │  job_match          → New matching job   │
  │  battle_invite      → Duel challenge     │
  │  application_update → Status change      │
  │  hiring_alert       → Followed company   │
  └──────────────────────────────────────────┘

CompanyFollow Model:
  Users follow companies → get instant alerts
  when that company posts a new job.
```

---

### 🏢 16. Recruiter Portal

> *"A full employer-side platform built right in."*

```
Recruiter Features:
  ┌──────────────────────────────────────────┐
  │  Post Jobs with Deadline + Requirements  │
  │  Search & Filter Student Profiles        │
  │  View Detailed Student Profiles          │
  │  Manage Applications + Pipeline          │
  │  Send Direct Messages to Candidates      │
  │  Application Status: Applied →           │
  │    Under Review → Shortlisted →          │
  │    Selected / Rejected                   │
  └──────────────────────────────────────────┘

RecruiterJob Model, RecruiterMessage Model,
JobApplication Model (with academic details,
CGPA, batch, college, stream)
```

---

### 🧬 17. Career DNA Profiling

> *"A fingerprint of your professional identity."*

```
Career DNA Analysis:
  ┌──────────────────────────────────────────┐
  │  Identifies your core career archetype  │
  │  Maps your skill distribution           │
  │  Finds your unique professional value   │
  │  Compares against successful profiles   │
  └──────────────────────────────────────────┘
```

---

### 🌐 18. Social Feed & Professional Network

```
Feed Features:
  ┌──────────────────────────────────────────┐
  │  Post updates, achievements, projects    │
  │  Upload images to posts                  │
  │  Connect with other professionals        │
  │  Search Users                            │
  │  Direct Messaging between users          │
  │  Like / Comment on posts                 │
  └──────────────────────────────────────────┘
```

---

<div align="center">

## 🗃️ Database Architecture

</div>

PathPilot AI uses **SQLite** in development and is migration-ready for **PostgreSQL** in production via SQLAlchemy ORM.

```
DATABASE SCHEMA OVERVIEW
═══════════════════════════════════════════════════════════════

users                    resumes                  skills
────────────────         ────────────────         ────────────────
id                       id                       id
name                     user_id (FK)             name
email                    filename                 category_id (FK)
password_hash            uploaded_at              demand_score
role                     skill_score              future_score
subscription_plan        normalized_skills        description
stripe_customer_id
stripe_subscription_id
normalized_skills

job_postings             recruiter_jobs           job_applications
────────────────         ────────────────         ────────────────
id                       id                       id
title                    recruiter_email          job_id (FK)
company                  company_name             user_id (FK)
location                 title                    cgpa / batch
description              description              college / stream
                         deadline                 status
                         salary_range             resume_filename

battle_profiles          battle_history           offer_predictions
────────────────         ────────────────         ────────────────
user_id (FK)             user_id (FK)             user_id (FK)
total_xp                 duel_code                offer_probability
trophies                 difficulty               readiness_tier
wins / losses / draws    result                   blockers_json
current_streak           xp_earned                gap_plan_json
best_streak              trophies_change          skill_match_json
                                                  coach_message

notifications            company_follows          career_time_machine
────────────────         ────────────────         ────────────────
user_id (FK)             user_id (FK)             user_id (FK)
notif_type               company_name             target_role
title / body                                      target_company
link / is_read                                    timeline_months
                                                  milestone_data_json
```

---

<div align="center">

## 🔌 API Reference

</div>

### 📄 Resume APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload-resume` | Upload and analyze resume (PDF/DOCX) |
| `GET` | `/api/resume-history` | Get all user resumes with scores |
| `POST` | `/api/resume-compare` | Compare two resumes side-by-side |
| `POST` | `/api/resume-ai` | AI-powered resume enhancement suggestions |
| `POST` | `/api/build-resume` | Build resume section by section |

### 💼 Job APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze-job` | Analyze a job description |
| `POST` | `/api/compare-resume-job` | Resume vs Job fit scoring |
| `GET` | `/api/job-matches` | Get AI-matched jobs for user |
| `POST` | `/api/save-job` | Save a job for tracking |
| `GET` | `/api/saved-jobs` | Get all saved jobs |
| `DELETE`| `/api/delete-saved-job/<id>` | Remove saved job |

### 💰 Salary APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ai-salary` | GPT-4 salary analysis |
| `GET` | `/api/salary-data` | Role-based market salary data |

### 🎯 Career Intelligence APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/roadmap` | Generate personalized career roadmap |
| `POST` | `/api/skill-gap` | Detect skill gaps for a role |
| `POST` | `/api/offer-predictor` | Calculate offer probability |
| `POST` | `/api/blind-spot` | Run blind spot analysis |
| `GET` | `/api/forecast` | Career market forecast data |
| `GET` | `/api/market` | Market intelligence dashboard |
| `POST` | `/api/career-dna` | Generate career DNA profile |
| `POST` | `/api/career-time-machine` | Build career time machine plan |

### 🎭 AI Recruiter APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ai-recruiter/start` | Start interview session |
| `POST` | `/api/ai-recruiter/answer` | Submit answer, get next question |
| `GET` | `/api/ai-recruiter/result/<id>` | Get interview evaluation |

### ⚔️ Battle & VidCode APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/battle/create` | Create a duel room |
| `POST` | `/api/battle/join` | Join with duel code |
| `POST` | `/api/battle/submit` | Submit solution |
| `POST` | `/api/vidcode/create` | Create collab coding room |
| `POST` | `/api/vidcode/run` | Execute code in room |

### 🏢 Recruiter Portal APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/recruiter/post-job` | Post a new job listing |
| `GET` | `/recruiter/applications` | View all applications |
| `POST` | `/recruiter/update-status` | Update application status |
| `GET` | `/recruiter/search-students` | Search candidate profiles |

---

<div align="center">

## 🏗️ Project Structure

</div>

```
PathPilotAI/
│
├── 📁 backend/
│   ├── app.py                        # Flask app factory + SocketIO init
│   ├── config.py                     # Environment configuration
│   ├── extensions.py                 # SQLAlchemy, JWT, CORS setup
│   ├── models.py                     # All SQLAlchemy ORM models (20+ models)
│   │
│   ├── 📁 routes/                    # Blueprint route handlers
│   │   ├── auth_routes.py            # Login, Register, OTP, Logout
│   │   ├── resume_routes.py          # Resume upload & history
│   │   ├── resume_ai_routes.py       # AI resume suggestions
│   │   ├── resume_builder_routes.py  # Step-by-step resume builder
│   │   ├── resume_compare_routes.py  # Resume comparison tool
│   │   ├── job_routes.py             # Job listings & saved jobs
│   │   ├── job_analyzer_routes.py    # JD analysis & matching
│   │   ├── salary_routes.py          # AI salary intelligence
│   │   ├── skill_gap_routes.py       # Skill gap analyzer
│   │   ├── roadmap_routes.py         # Career roadmap generator
│   │   ├── interview_routes.py       # Interview prep questions
│   │   ├── ai_recruiter_routes.py    # AI interview simulator
│   │   ├── career_time_machine_routes.py  # Time machine feature
│   │   ├── offer_predictor_routes.py # Offer probability engine
│   │   ├── blind_spot_routes.py      # Blind spot detector
│   │   ├── forecast_routes.py        # Career forecasting
│   │   ├── market_routes.py          # Market intelligence
│   │   ├── battle_routes.py          # 1v1 coding duels
│   │   ├── vidcode_routes.py         # Collaborative coding rooms
│   │   ├── cover_letter_routes.py    # AI cover letter gen
│   │   ├── recruiter_routes.py       # Recruiter portal
│   │   ├── application_routes.py     # Job application tracking
│   │   ├── dashboard_routes.py       # User dashboard
│   │   ├── profile_routes.py         # User profile management
│   │   ├── admin_routes.py           # Admin dashboard
│   │   └── navbar_routes.py          # Notification + nav data
│   │
│   ├── 📁 services/                  # Core business logic
│   │   ├── resume_parser.py          # PDF/DOCX text extraction
│   │   ├── skill_gap_service.py      # Gap analysis engine
│   │   ├── job_match_engine.py       # JD vs resume matching
│   │   ├── ai_salary_engine.py       # GPT-4 salary analysis
│   │   ├── company_salary_engine.py  # Company-specific data
│   │   ├── global_salary_dataset.py  # Salary benchmarks
│   │   ├── roadmap_engine.py         # Roadmap generation
│   │   ├── interview_service.py      # Interview Q generation
│   │   ├── ai_recruiter_service.py   # AI interview simulator
│   │   ├── career_time_machine_service.py  # Time machine AI
│   │   ├── offer_predictor_service.py      # Offer scoring AI
│   │   ├── blind_spot_service.py     # Blind spot AI engine
│   │   ├── forecasting_service.py    # Career forecast AI
│   │   ├── market_intelligence.py    # Market data engine
│   │   ├── market_intelligence_service.py
│   │   ├── battle_service.py         # Duel logic + XP engine
│   │   ├── meeting_service.py        # VidCode room management
│   │   ├── cover_letter_service.py   # Cover letter AI
│   │   ├── resume_builder_service.py # Resume build logic
│   │   ├── resume_comparison_service.py
│   │   ├── resume_ai_service.py
│   │   ├── recruiter_service.py      # Recruiter portal logic
│   │   ├── scraper_service.py        # Job URL scraping
│   │   ├── skill_score_engine.py     # Skill scoring algorithm
│   │   ├── elite_scoring_engine.py   # Advanced scoring
│   │   ├── global_skill_library.py   # Master skill library (500+)
│   │   ├── job_skill_normalizer.py   # Skill alias resolution
│   │   ├── job_skill_extracter.py    # JD skill extraction
│   │   ├── job_role_classifier.py    # Role classification ML
│   │   ├── career_identity_service.py
│   │   ├── vector_service.py         # Vector similarity search
│   │   ├── subscription_service.py   # SaaS plan management
│   │   ├── stripe_service.py         # Stripe payment processing
│   │   └── social_service.py         # Feed & social features
│   │
│   └── 📁 utils/
│       ├── auth_decorator.py         # @login_required decorator
│       ├── auth_utils.py             # JWT + session helpers
│       ├── subscription_required.py  # Plan-gating decorator
│       ├── init_db.py                # Database initialization
│       ├── load_global_skills.py     # Skill library loader
│       └── load_skill_aliases.py     # Alias table loader
│
├── 📁 frontend/
│   ├── 📁 templates/                 # Jinja2 HTML templates (50+ pages)
│   │   ├── base.html                 # Master layout with nav
│   │   ├── landing.html              # Landing/marketing page
│   │   ├── dashboard.html            # User dashboard
│   │   ├── resume_ai.html            # AI resume analysis
│   │   ├── resume_builder.html       # Resume builder UI
│   │   ├── job_analyzer.html         # Job analysis tool
│   │   ├── salary.html               # Salary intelligence
│   │   ├── skill_gap.html            # Skill gap display
│   │   ├── roadmap.html              # Career roadmap viewer
│   │   ├── interview.html            # Interview prep
│   │   ├── ai_recruiter.html         # AI interview room
│   │   ├── career_time_machine.html  # Time machine tool
│   │   ├── offer_predictor.html      # Offer probability
│   │   ├── blind_spot_detector.html  # Blind spot analysis
│   │   ├── forecast.html             # Career forecasting
│   │   ├── market_dashboard.html     # Market intelligence
│   │   ├── battle_home.html          # Battle mode lobby
│   │   ├── battle_room.html          # Live duel interface
│   │   ├── vidcode_home.html         # VidCode lobby
│   │   ├── vidcode_room.html         # Live coding + video
│   │   ├── cover_letter.html         # Cover letter generator
│   │   ├── feed.html                 # Social feed
│   │   ├── profile.html              # User profile
│   │   ├── admin_dashboard.html      # Admin panel
│   │   ├── billing.html              # Subscription & billing
│   │   ├── pricing.html              # Pricing page
│   │   └── recruiter/                # Recruiter portal pages
│   │       ├── dashboard.html
│   │       ├── post_job.html
│   │       ├── applications.html
│   │       └── search_students.html
│   │
│   └── 📁 static/
│       ├── css/style.css             # Global stylesheet
│       └── css/js/main.js            # Frontend JavaScript
│
├── 📁 database/
│   └── pathpilot.db                  # SQLite database
│
├── run.py                            # Application entry point
├── Procfile                          # Gunicorn process config
├── render.yaml                       # Render deployment config
├── runtime.txt                       # Python version pin
├── migrate_db.py                     # DB migration scripts
└── PROJECT_CONTEXT.md                # Startup context document
```

---

<div align="center">

## 💻 Tech Stack

</div>

<table>
<tr>
<th>Layer</th>
<th>Technology</th>
<th>Purpose</th>
</tr>
<tr>
<td><strong>Backend Framework</strong></td>
<td>Flask 3.0.3</td>
<td>Core web framework with Blueprints</td>
</tr>
<tr>
<td><strong>AI Engine</strong></td>
<td>OpenAI GPT-4</td>
<td>Salary, roadmap, interview, offer, blind spot, time machine analysis</td>
</tr>
<tr>
<td><strong>Database ORM</strong></td>
<td>Flask-SQLAlchemy 3.1.1</td>
<td>20+ database models with relationships</td>
</tr>
<tr>
<td><strong>Authentication</strong></td>
<td>Flask-Login + Flask-JWT-Extended</td>
<td>Session auth + JWT tokens</td>
</tr>
<tr>
<td><strong>Real-Time</strong></td>
<td>Flask-SocketIO 5.3.6</td>
<td>Live battle duels + VidCode collaboration</td>
</tr>
<tr>
<td><strong>Payments</strong></td>
<td>Stripe 10.12.0</td>
<td>Subscription billing (Free/Pro/Enterprise)</td>
</tr>
<tr>
<td><strong>Resume Parsing</strong></td>
<td>pdfplumber + python-docx</td>
<td>PDF & DOCX text extraction</td>
</tr>
<tr>
<td><strong>PDF Generation</strong></td>
<td>ReportLab 4.2.2</td>
<td>Resume PDF export</td>
</tr>
<tr>
<td><strong>ML & Data</strong></td>
<td>scikit-learn + pandas + numpy</td>
<td>Skill scoring, role classification, data modeling</td>
</tr>
<tr>
<td><strong>Task Scheduling</strong></td>
<td>APScheduler 3.10.4</td>
<td>Background jobs, data refresh</td>
</tr>
<tr>
<td><strong>Frontend</strong></td>
<td>Bootstrap + Chart.js + Jinja2</td>
<td>Responsive UI with glassmorphism design</td>
</tr>
<tr>
<td><strong>CORS</strong></td>
<td>Flask-CORS 6.0.2</td>
<td>Cross-origin resource sharing</td>
</tr>
<tr>
<td><strong>Production Server</strong></td>
<td>Gunicorn (gthread workers)</td>
<td>Multi-threaded production WSGI server</td>
</tr>
<tr>
<td><strong>Deployment</strong></td>
<td>Render.com</td>
<td>Cloud hosting with auto-deploy</td>
</tr>
<tr>
<td><strong>Python Version</strong></td>
<td>Python 3.11+</td>
<td>Latest stable runtime</td>
</tr>
</table>

---

<div align="center">

## 🚀 Getting Started

</div>

### Prerequisites

- Python 3.11+
- pip
- OpenAI API Key
- Stripe API Key (for billing features)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/PathPilotAI.git
cd PathPilotAI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Required
SECRET_KEY=your-super-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key

# Database
DATABASE_URL=sqlite:///database/pathpilot.db

# Stripe (for billing features)
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Initialize Database

```bash
python backend/utils/init_db.py
python backend/utils/load_global_skills.py
python backend/utils/load_skill_aliases.py
```

### 6. Run the Application

```bash
python run.py
```

Application will be available at: **http://localhost:5000**

### 7. Deploy to Render

The project is pre-configured for Render deployment via `render.yaml`.

```bash
# Render auto-deploys on git push
# Set environment variables in Render dashboard:
# OPENAI_API_KEY, SECRET_KEY, STRIPE_SECRET_KEY
```

Build Command: `pip install -r backend/requirements.txt`

Start Command: `gunicorn --worker-class gthread --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT run:app`

---

<div align="center">

## 💰 SaaS Subscription Model

</div>

PathPilot AI is built as a **Freemium SaaS** with Stripe-powered billing:

<table>
<tr>
<th>Feature</th>
<th>🆓 Free</th>
<th>⭐ Pro</th>
<th>🏢 Enterprise</th>
</tr>
<tr>
<td>Resume Upload & Analysis</td>
<td>✅</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Basic Job Matching</td>
<td>✅</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Social Feed</td>
<td>✅</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Salary Intelligence (GPT-4)</td>
<td>❌</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>AI Career Roadmap</td>
<td>❌</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Offer Predictor</td>
<td>❌</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Blind Spot Detector</td>
<td>❌</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Career Time Machine</td>
<td>❌</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>AI Recruiter Interview</td>
<td>❌</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Battle Mode (Duels)</td>
<td>Limited</td>
<td>Unlimited</td>
<td>Unlimited</td>
</tr>
<tr>
<td>Market Intelligence</td>
<td>❌</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Recruiter Portal Access</td>
<td>❌</td>
<td>❌</td>
<td>✅</td>
</tr>
<tr>
<td>Admin Analytics</td>
<td>❌</td>
<td>❌</td>
<td>✅</td>
</tr>
</table>

**Billing Infrastructure:** `stripe_service.py`, `subscription_service.py`
**Plan Models:** `User.subscription_plan` → `free | pro | enterprise`
**Gate Decorator:** `@subscription_required` on Pro/Enterprise routes

---

<div align="center">

## 🔐 Authentication & Security

</div>

```
Auth Flow:
  Register → Email OTP Verification → Login
       │
       ▼
  Session-based Auth (Flask-Login)
  JWT Tokens (Flask-JWT-Extended)
       │
       ▼
  Role-Based Access Control:
  ├── user   → Standard platform access
  ├── admin  → Full admin dashboard
  └── recruiter → Recruiter portal access

Security Features:
  ✅ Werkzeug password hashing (bcrypt-compatible)
  ✅ @login_required decorator on all protected routes
  ✅ @subscription_required for premium features
  ✅ Session management with SECRET_KEY
  ✅ CORS protection via Flask-CORS
  ✅ OTP email verification on registration
  ✅ Stripe webhook signature verification
```

---

<div align="center">

## 🗺️ Roadmap

</div>

### ✅ Phase 1 — Foundation (Complete)
- [x] Resume Intelligence Engine
- [x] Job Match Engine
- [x] Salary Intelligence (GPT-4)
- [x] Career Roadmap Generator
- [x] Skill Gap Analyzer
- [x] Authentication System
- [x] Admin Dashboard

### ✅ Phase 2 — SaaS Expansion (Current)
- [x] AI Recruiter Interview Simulator
- [x] Career Time Machine
- [x] Offer Predictor
- [x] Blind Spot Detector
- [x] Battle Mode (1v1 Coding Duels)
- [x] VidCode Collaborative Rooms
- [x] Stripe Subscription Billing
- [x] Social Feed & Profiles
- [x] Recruiter Portal
- [x] Notification System
- [x] Company Follow & Hiring Alerts
- [x] Market Intelligence Dashboard
- [x] Career Forecasting Engine

### 🔜 Phase 3 — Scale (Upcoming)
- [ ] Mobile App (React Native)
- [ ] Resume Vector Search (semantic matching)
- [ ] Company Salary Intelligence Dataset Expansion
- [ ] AI Career Coach (chat interface)
- [ ] Interview Recording & Playback Analysis
- [ ] LinkedIn Profile Analyzer
- [ ] GitHub Portfolio Analyzer
- [ ] Team Plan for universities and bootcamps
- [ ] Multi-language support (Hindi, Spanish)
- [ ] Public API for third-party integrations

---

<div align="center">

## 📊 Platform Stats (Development)

</div>

```
┌─────────────────────────────────────────────────────┐
│  📁 Backend Routes:          28 blueprint files      │
│  ⚙️  Service Modules:         40+ service files       │
│  🗃️  Database Models:         20+ ORM models          │
│  📄 Frontend Templates:      50+ HTML pages           │
│  🧩 AI Features:             15+ unique AI modules    │
│  🔌 API Endpoints:           60+ REST endpoints       │
│  📚 Skills Library:          500+ normalized skills   │
│  🌍 Salary Datasets:         Global + India coverage  │
└─────────────────────────────────────────────────────┘
```

---

<div align="center">

## 🤝 Contributing

</div>

Contributions are very welcome! PathPilot AI is actively growing and there are many ways to help:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/AmazingFeature`
3. **Commit** your changes: `git commit -m 'Add AmazingFeature'`
4. **Push** to your branch: `git push origin feature/AmazingFeature`
5. **Open** a Pull Request

### Areas to Contribute
- New AI feature modules
- Frontend design improvements
- Additional salary datasets
- New coding battle problem sets
- Mobile app development
- Testing & documentation

---

<div align="center">

## 📄 License

</div>

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## 👨‍💻 Built By

</div>

<div align="center">

**PathPilot AI** was built with passion, caffeine, and a firm belief that every professional deserves AI-powered career intelligence — not just those at elite companies.

<br/>

> *"The future belongs to those who understand their skills, know their market, and move with intelligence."*

<br/>

⭐ **If PathPilot AI helped you, please star this repo!**

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer" width="100%"/>

</div>
