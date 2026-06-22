"""
scripts/seed_recruiters.py

ONE-TIME setup: creates the 9 recruiter User records with hashed passwords.

Run from project root:
    python scripts/seed_recruiters.py

After running, recruiters log in via the normal /login form with the SAME
emails and SAME passwords as before. Nothing changes from their perspective.

Safe to re-run: existing recruiters get their password_hash refreshed,
not duplicated. To rotate a recruiter password, edit the value below
and re-run this script.

DO NOT COMMIT THIS FILE — it is gitignored. The plaintext passwords here
are the same ones that were previously hardcoded in auth_routes.py, so
this file does not introduce any new secret leakage — it just localizes
the leak to your dev machine instead of the public repo.
"""

import sys
import os

# Make `from backend...` work when running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from backend.app import create_app
from backend.extensions import db
from backend.models import User


# Same 9 accounts that were previously hardcoded in auth_routes.py
# Format: (email, plaintext_password, company_display_name)
RECRUITERS = [
    ("recruiter@pathpilot.com", "recruit123",  "PathPilot Hiring"),
    ("google@recruiter.com",    "google@123",  "Google"),
    ("microsoft@recruiter.com", "msft@123",    "Microsoft"),
    ("amazon@recruiter.com",    "amzn@123",    "Amazon"),
    ("startup@recruiter.com",   "start@123",   "TechStartup Inc"),
    ("tcs@recruiter.com",       "tcs@123",     "TCS"),
    ("infosys@recruiter.com",   "infy@123",    "Infosys"),
    ("wipro@recruiter.com",     "wipro@123",   "Wipro"),
    ("caelius@recruiter.com",   "caelius@123", "Caelius Consulting"),
]


def seed():
    app = create_app()
    with app.app_context():
        for email, plain_pw, company in RECRUITERS:
            existing = User.query.filter_by(email=email).first()
            if existing:
                existing.password_hash = generate_password_hash(plain_pw)
                existing.role          = "recruiter"
                existing.name          = company
                existing.is_verified   = True
                print(f"  updated: {email}")
            else:
                u = User(
                    email         = email,
                    name          = company,
                    role          = "recruiter",
                    password_hash = generate_password_hash(plain_pw),
                    is_verified   = True,
                )
                db.session.add(u)
                print(f"  created: {email}")
        db.session.commit()
        print(f"\nDone. {len(RECRUITERS)} recruiter accounts seeded.")


if __name__ == "__main__":
    seed()