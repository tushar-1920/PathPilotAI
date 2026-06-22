"""
backend/extensions.py

Flask extensions instantiated at import time (no app bound yet).
Each extension's .init_app(app) is called from create_app() in app.py.
"""

import os
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ── DB ──
db = SQLAlchemy()


# ── Rate limiter ──
def _rate_limit_key() -> str:
    """
    Per-user limits when logged in, per-IP otherwise.
    This way one user's heavy usage doesn't lock out other users on
    the same shared NAT (college wifi, mobile carrier IPs, etc).
    """
    uid = session.get("user_id")
    return f"user:{uid}" if uid else get_remote_address()


limiter = Limiter(
    key_func=_rate_limit_key,
    default_limits=["300 per hour", "3000 per day"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
    strategy="fixed-window",
)