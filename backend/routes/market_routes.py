from flask import Blueprint, jsonify, render_template
from backend.services.market_intelligence_service import MarketIntelligenceService
from backend.utils.auth_decorator import login_required

market_routes = Blueprint("market_routes", __name__)
service = MarketIntelligenceService()

@market_routes.route("/market")
@login_required
def market_page():
    return render_template("market.html")

@market_routes.route("/api/market-ai")
@login_required
def market_ai():
    data = service.generate_market_intelligence()
    return jsonify(data)

@market_routes.route("/api/market-role-analysis")
@login_required
def market_role_analysis():
    return jsonify(service.role_analysis())

@market_routes.route("/api/market-sectors")
@login_required
def market_sectors():
    from backend.models import JobPosting
    from collections import Counter
    jobs = JobPosting.query.all()
    skill_counts = Counter()
    for job in jobs:
        if job.normalized_skills:
            for s in job.normalized_skills.split(","):
                sk = s.strip().lower()
                if sk: skill_counts[sk] += 1
    return jsonify(service._sector_breakdown(dict(skill_counts)))

@market_routes.route("/api/market-roles")
@login_required
def market_roles():
    from backend.models import JobPosting
    from collections import Counter
    jobs = JobPosting.query.all()
    role_counts = Counter()
    for job in jobs:
        if job.role:
            r = job.role.strip()
            if r.lower() not in ["other","unknown","misc",""]:
                role_counts[r] += 1
    return jsonify(service._role_demand(dict(role_counts)))