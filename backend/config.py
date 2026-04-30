import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    # =========================
    # Environment
    # =========================
    ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # =========================
    # Security
    # =========================
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    # =========================
    # Database
    # =========================
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "..", "database", "pathpilot.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    

    # =========================
    # Upload Settings
    # =========================
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    # =========================
    # Stripe Configuration
    # =========================
    STRIPE_SECRET_KEY = None
    STRIPE_MONTHLY_PRICE_ID = None
    STRIPE_ANNUAL_PRICE_ID = None
    STRIPE_WEBHOOK_SECRET = None

    

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    