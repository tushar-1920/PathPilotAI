# backend/services/stripe_service.py

try:
    import stripe
except ImportError:
    stripe = None

from flask import current_app, url_for
from backend.models import User
from backend.extensions import db


class StripeService:

    # =========================================
    # Internal Stripe Initialization
    # =========================================
    def _init_stripe(self):

        stripe_key = current_app.config.get("STRIPE_SECRET_KEY")

        if stripe and stripe_key:
            stripe.api_key = stripe_key
            return True

        return False

    # =========================================
    # Create Checkout Session
    # =========================================
    def create_checkout_session(self, user_id, billing_cycle):

        stripe_ready = self._init_stripe()

        # 🔥 If Stripe NOT configured → Simulate Upgrade
        if not stripe_ready:
            user = User.query.get(user_id)

            if user:
                user.subscription_plan = "pro"
                user.subscription_status = "active"
                user.billing_cycle = billing_cycle
                db.session.commit()

            # Redirect directly to dashboard
            return url_for("dashboard_routes.dashboard_page")

        # ===============================
        # REAL STRIPE FLOW (Future Use)
        # ===============================

        if billing_cycle == "annual":
            price_id = current_app.config.get("STRIPE_ANNUAL_PRICE_ID")
        else:
            price_id = current_app.config.get("STRIPE_MONTHLY_PRICE_ID")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            success_url=url_for(
                "dashboard_routes.dashboard_page",
                _external=True
            ),
            cancel_url=url_for(
                "dashboard_routes.pricing_page",
                _external=True
            ),
            metadata={
                "user_id": user_id,
                "billing_cycle": billing_cycle
            }
        )

        return session.url

    # =========================================
    # Handle Webhook Events (Optional)
    # =========================================
    def handle_webhook(self, payload, sig_header):

        stripe_ready = self._init_stripe()

        if not stripe_ready:
            return True  # Do nothing if Stripe not configured

        webhook_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret
        )

        if event["type"] == "checkout.session.completed":

            session_data = event["data"]["object"]
            user_id = session_data["metadata"]["user_id"]
            billing_cycle = session_data["metadata"]["billing_cycle"]

            subscription_id = session_data.get("subscription")
            customer_id = session_data.get("customer")

            user = User.query.get(user_id)

            if user:
                user.subscription_plan = "pro"
                user.subscription_status = "active"
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                user.billing_cycle = billing_cycle

                db.session.commit()

        if event["type"] == "customer.subscription.deleted":

            subscription = event["data"]["object"]
            subscription_id = subscription["id"]

            user = User.query.filter_by(
                stripe_subscription_id=subscription_id
            ).first()

            if user:
                user.subscription_plan = "free"
                user.subscription_status = "cancelled"
                user.stripe_subscription_id = None
                db.session.commit()

        return True