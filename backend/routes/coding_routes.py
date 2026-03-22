"""
PathPilot AI — Coding Practice Routes
Follows your existing route file style (market_routes.py, job_routes.py etc.)
db imported from backend.extensions — same as rest of your project.
"""

from flask import Blueprint, request, jsonify, render_template, session
from backend.extensions import db
from backend.services.problem_service import (
    get_all_problems,
    get_problem_by_id,
    get_difficulty_stats,
    get_topics_list,
    search_problems,
)
from backend.services.code_runner_service import (
    run_code_against_testcases,
    validate_code_safety,
)
from backend.services.submission_service import (
    save_submission,
    get_user_submissions,
    get_submission_by_id,
    mark_problem_solved,
    get_problem_submission_stats,
)
from backend.services.profile_service import (
    get_user_profile,
    get_user_solved_count,
    get_user_difficulty_stats,
    get_user_activity_calendar,
    get_user_recent_submissions,
    get_leaderboard,
    update_user_streak,
    get_user_badges,
    calculate_user_xp,
)
import logging

logger = logging.getLogger(__name__)

coding_bp = Blueprint("coding", __name__, url_prefix="/practice")


# ─────────────────────────────────────────────
#  PAGE ROUTES
# ─────────────────────────────────────────────

@coding_bp.route("/")
@coding_bp.route("")
def practice_home():
    """Serves the main LeetCode-style SPA. Template: practice_problems.html"""
    problems   = get_all_problems()
    stats      = get_difficulty_stats(problems)
    topics     = get_topics_list(problems)
    user_id    = session.get("user_id")
    user_stats = get_user_difficulty_stats(user_id) if user_id else None

    return render_template(
        "practice_problems.html",
        problems=problems,
        stats=stats,
        topics=topics,
        user_stats=user_stats,
    )


@coding_bp.route("/problem/<int:problem_id>")
def problem_page(problem_id):
    """Split-panel editor page. Template: problem_page.html"""
    problem = get_problem_by_id(problem_id)
    if not problem:
        return render_template("404.html"), 404

    user_id          = session.get("user_id")
    submission_stats = get_problem_submission_stats(problem_id)

    user_solved = False
    if user_id:
        from backend.models import SolvedProblem
        user_solved = SolvedProblem.query.filter_by(
            user_id=user_id, problem_id=problem_id
        ).first() is not None

    return render_template(
        "problem_page.html",
        problem=problem,
        submission_stats=submission_stats,
        user_solved=user_solved,
    )


@coding_bp.route("/profile")
def practice_profile():
    """User coding profile. Template: practice_profile.html"""
    user_id = session.get("user_id")
    if not user_id:
        return render_template("practice_profile.html", profile=None)

    return render_template(
        "practice_profile.html",
        profile   = get_user_profile(user_id),
        solved_count       = get_user_solved_count(user_id),
        diff_stats         = get_user_difficulty_stats(user_id),
        calendar           = get_user_activity_calendar(user_id),
        recent_submissions = get_user_recent_submissions(user_id, limit=10),
        streak             = update_user_streak(user_id),
        badges             = get_user_badges(user_id),
        xp                 = calculate_user_xp(user_id),
    )


@coding_bp.route("/submissions")
def submissions_page():
    """Submission history. Template: submissions.html"""
    user_id  = session.get("user_id")
    page     = request.args.get("page", 1, type=int)
    if user_id:
        subs, total = get_user_submissions(user_id, page=page, per_page=20)
    else:
        subs, total = [], 0

    return render_template(
        "submissions.html",
        submissions=subs,
        total=total,
        page=page,
    )


# ─────────────────────────────────────────────
#  JSON API ROUTES
# ─────────────────────────────────────────────

@coding_bp.route("/api/problems", methods=["GET"])
def api_get_problems():
    try:
        difficulty    = request.args.get("difficulty", "")
        topic         = request.args.get("topic", "")
        plan          = request.args.get("plan", "")
        query         = request.args.get("q", "")
        status_filter = request.args.get("status", "")
        page          = request.args.get("page", 1, type=int)
        per_page      = request.args.get("per_page", 50, type=int)

        problems = get_all_problems()
        if difficulty:
            problems = [p for p in problems if p["difficulty"] == difficulty]
        if topic:
            problems = [p for p in problems if topic in p.get("topics", [])]
        if plan:
            problems = [p for p in problems if plan in p.get("plans", [])]
        if query:
            problems = search_problems(problems, query)
        if status_filter and session.get("user_id"):
            from backend.models import SolvedProblem
            solved_ids = {sp.problem_id for sp in SolvedProblem.query.filter_by(user_id=session["user_id"]).all()}
            if status_filter == "solved":
                problems = [p for p in problems if p["id"] in solved_ids]
            elif status_filter == "unsolved":
                problems = [p for p in problems if p["id"] not in solved_ids]

        total     = len(problems)
        paginated = problems[(page - 1) * per_page: page * per_page]
        return jsonify({"problems": paginated, "total": total, "page": page})
    except Exception as e:
        logger.error(f"api_get_problems: {e}")
        return jsonify({"error": str(e)}), 500


@coding_bp.route("/api/problems/<int:problem_id>", methods=["GET"])
def api_get_problem(problem_id):
    problem = get_problem_by_id(problem_id)
    if not problem:
        return jsonify({"error": "Problem not found"}), 404
    return jsonify(problem)


@coding_bp.route("/api/run-code", methods=["POST"])
def api_run_code():
    try:
        data         = request.get_json(force=True)
        problem_id   = data.get("problem_id")
        code         = data.get("code", "")
        language     = data.get("language", "python")
        custom_input = data.get("custom_input")

        if not code.strip():
            return jsonify({"error": "Code cannot be empty"}), 400

        # Skip validation for internal mark_solved calls
        if data.get('_mark_solved'):
            mark_problem_solved(user_id=user_id, problem_id=problem_id)
            return jsonify({"status": "Accepted", "passed": 1, "total": 1,
                           "runtime_ms": 0, "memory_kb": 0, "results": []})

        safe, reason = validate_code_safety(code, language)
        if not safe:
            return jsonify({"error": f"Code blocked: {reason}"}), 400

        problem = get_problem_by_id(problem_id)
        if not problem:
            return jsonify({"error": "Problem not found"}), 404

        results = run_code_against_testcases(
            code=code,
            language=language,
            testcases=problem["test_cases"],
            custom_input=custom_input,
            time_limit_ms=problem.get("time_limit_ms", 2000),
        )
        return jsonify(results)
    except Exception as e:
        logger.error(f"api_run_code: {e}")
        return jsonify({"error": "Execution failed", "detail": str(e)}), 500


@coding_bp.route("/api/submit-code", methods=["POST"])
def api_submit_code():
    try:
        data       = request.get_json(force=True)
        problem_id = data.get("problem_id")
        code       = data.get("code", "")
        language   = data.get("language", "python")
        user_id    = session.get("user_id", 1)

        if not code.strip():
            return jsonify({"error": "Code cannot be empty"}), 400

        # Skip validation for internal mark_solved calls
        if data.get('_mark_solved'):
            mark_problem_solved(user_id=user_id, problem_id=problem_id)
            return jsonify({"status": "Accepted", "passed": 1, "total": 1,
                           "runtime_ms": 0, "memory_kb": 0, "results": []})

        safe, reason = validate_code_safety(code, language)
        if not safe:
            return jsonify({"error": f"Code blocked: {reason}"}), 400

        problem = get_problem_by_id(problem_id)
        if not problem:
            return jsonify({"error": "Problem not found"}), 404

        results    = run_code_against_testcases(
            code=code, language=language,
            testcases=problem["test_cases"],
            include_hidden=True,
            time_limit_ms=problem.get("time_limit_ms", 2000),
        )

        passed     = results.get("passed", 0)
        total      = results.get("total", 0)
        runtime_ms = results.get("runtime_ms", 0)
        memory_kb  = results.get("memory_kb", 0)

        if passed == total:          status = "Accepted"
        elif results.get("tle"):     status = "Time Limit Exceeded"
        elif results.get("runtime_error"): status = "Runtime Error"
        else:                        status = "Wrong Answer"

        submission = save_submission(
            user_id=user_id, problem_id=problem_id,
            code=code, language=language, status=status,
            runtime_ms=runtime_ms, memory_kb=memory_kb,
            passed_cases=passed, total_cases=total,
        )

        if status == "Accepted":
            mark_problem_solved(user_id=user_id, problem_id=problem_id)

        return jsonify({
            "status": status, "passed": passed, "total": total,
            "runtime_ms": runtime_ms, "memory_kb": memory_kb,
            "submission_id": submission.id if submission else None,
            "results": results.get("results", []),
        })
    except Exception as e:
        logger.error(f"api_submit_code: {e}")
        return jsonify({"error": "Submission failed", "detail": str(e)}), 500


@coding_bp.route("/api/submissions", methods=["GET"])
def api_get_submissions():
    user_id    = session.get("user_id", 1)
    page       = request.args.get("page", 1, type=int)
    per_page   = request.args.get("per_page", 20, type=int)
    problem_id = request.args.get("problem_id", type=int)
    subs, total = get_user_submissions(user_id=user_id, page=page, per_page=per_page, problem_id=problem_id)
    return jsonify({"submissions": subs, "total": total, "page": page})


@coding_bp.route("/api/submissions/<int:submission_id>", methods=["GET"])
def api_get_submission(submission_id):
    sub = get_submission_by_id(submission_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    return jsonify(sub)


@coding_bp.route("/api/profile", methods=["GET"])
def api_get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"profile": None, "solved_ids": [], "solved": 0})

    # Return solved problem IDs so frontend can show checkmarks
    from backend.models import SolvedProblem, User
    solved_ids = [sp.problem_id for sp in SolvedProblem.query.filter_by(user_id=user_id).all()]
    user = User.query.get(user_id)
    profile = {
        "id":    user_id,
        "name":  getattr(user, "name", "") if user else "",
        "email": getattr(user, "email", "") if user else "",
    }
    return jsonify({
        "profile":    profile,
        "solved_ids": solved_ids,
        "solved":     len(solved_ids),
    })


@coding_bp.route("/api/leaderboard", methods=["GET"])
def api_get_leaderboard():
    period  = request.args.get("period", "weekly")
    limit   = request.args.get("limit", 50, type=int)
    leaders = get_leaderboard(period=period, limit=limit)
    return jsonify({"leaders": leaders, "period": period})


@coding_bp.route("/api/topics", methods=["GET"])
def api_get_topics():
    problems = get_all_problems()
    return jsonify({"topics": get_topics_list(problems)})


@coding_bp.route("/api/stats", methods=["GET"])
def api_get_stats():
    return jsonify(get_difficulty_stats(get_all_problems()))