from datetime import datetime, timedelta
from backend.models import User
from backend.extensions import db


class SubscriptionService:

    PRO_FEATURES = {
        "skill_gap_pro",
        "advanced_forecasting",
        "market_intelligence_pro"
    }

    def is_pro_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        if user.subscription_plan in ["pro", "enterprise"] \
           and user.subscription_status == "active":
            return True

        return False

    def upgrade_to_pro(self, user_id, months=1):
        user = User.query.get(user_id)

        if not user:
            return False

        user.subscription_plan = "pro"
        user.subscription_status = "active"
        user.subscription_expiry = datetime.utcnow() + timedelta(days=30*months)

        db.session.commit()
        return True

    def downgrade_to_free(self, user_id):
        user = User.query.get(user_id)

        if not user:
            return False

        user.subscription_plan = "free"
        user.subscription_status = "active"
        user.subscription_expiry = None

        db.session.commit()
        return True

    def can_use_skill_gap(self, user):

        if user.subscription_plan == "pro":
            return True

    # Free users limited to 3 checks per day
        from datetime import datetime
        today = datetime.utcnow().date()

        if not hasattr(user, "daily_usage"):
            
            return True