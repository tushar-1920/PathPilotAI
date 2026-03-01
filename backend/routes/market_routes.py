from flask import Blueprint, jsonify, render_template
from backend.services.market_intelligence_service import MarketIntelligenceService
from backend.utils.auth_decorator import login_required

market_routes = Blueprint("market_routes", __name__)

service = MarketIntelligenceService()


# ==========================================
# Market Intelligence Page
# ==========================================
@market_routes.route("/market")
@login_required
def market_page():
    return render_template("market.html")


# ==========================================
# Top Skills Demand
# ==========================================
@market_routes.route("/api/market/top-skills")
@login_required
def top_skills():
    return jsonify(service.get_top_skills())


# ==========================================
# Role Demand Distribution
# ==========================================
@market_routes.route("/api/market/role-demand")
@login_required
def role_demand():
    return jsonify(service.get_role_demand())


# ==========================================
# Hiring Trend Over Time
# ==========================================
@market_routes.route("/api/market/hiring-trend")
@login_required
def hiring_trend():
    return jsonify(service.get_hiring_trend())