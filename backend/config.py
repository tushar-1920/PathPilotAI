import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =========================
    # Security
    # =========================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # =========================
    # Database
    # =========================
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "..", "database", "pathpilot.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # Session Security
    # =========================
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Set to True only in production (HTTPS required)
    SESSION_COOKIE_SECURE = False

    # =========================
    # Upload Settings
    # =========================
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB upload limit