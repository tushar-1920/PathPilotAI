from functools import wraps
from flask import session, jsonify
from backend.services.subscription_service import SubscriptionService

service = SubscriptionService()

def pro_required(feature_name=None):

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            user_id = session.get("user_id")

            if not user_id:
                return jsonify({"error": "Unauthorized"}), 401

            if not service.is_pro_user(user_id):
                return jsonify({
                    "error": "Pro subscription required",
                    "upgrade_required": True
                }), 403

            return f(*args, **kwargs)

        return wrapper
    return decorator