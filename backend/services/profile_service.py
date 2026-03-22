"""
PathPilot AI — Profile Service
Provides user stats, activity calendar, streaks, and leaderboard.
"""

from datetime import datetime, timedelta, date
from collections import defaultdict
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def _get_models():
    from backend.models import Submission, SolvedProblem, User
    return Submission, SolvedProblem, User


def _get_db():
    from backend.extensions import db
    return db


# ─────────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────────

def get_user_profile(user_id: int) -> Optional[Dict]:
    """
    Return basic user profile info.
    Falls back gracefully if User model doesn't exist yet.
    """
    try:
        _, _, User = _get_models()
        user = User.query.get(user_id)
        if not user:
            return _default_profile(user_id)
        return {
            "id": user.id,
            "username": getattr(user, "username", f"User{user_id}"),
            "email": getattr(user, "email", ""),
            "name": getattr(user, "name", getattr(user, "username", f"User{user_id}")),
            "avatar": getattr(user, "avatar", None),
            "joined_at": (
                user.created_at.isoformat()
                if hasattr(user, "created_at") and user.created_at
                else None
            ),
            "plan": getattr(user, "plan", "Free"),
        }
    except Exception as e:
        logger.warning(f"get_user_profile fallback for user {user_id}: {e}")
        return _default_profile(user_id)


def _default_profile(user_id: int) -> Dict:
    return {
        "id": user_id,
        "username": f"User{user_id}",
        "email": "",
        "name": f"User {user_id}",
        "avatar": None,
        "joined_at": None,
        "plan": "Free",
    }


# ─────────────────────────────────────────────
#  SOLVED COUNTS  &  DIFFICULTY STATS
# ─────────────────────────────────────────────

def get_user_solved_count(user_id: int) -> int:
    """Total number of distinct problems a user has solved."""
    try:
        _, SolvedProblem, _ = _get_models()
        return SolvedProblem.query.filter_by(user_id=user_id).count()
    except Exception as e:
        logger.error(f"get_user_solved_count failed: {e}")
        return 0


def get_user_difficulty_stats(user_id: int) -> Dict[str, int]:
    """
    Returns per-difficulty solved counts by joining with problem data.
    { "Easy": 45, "Medium": 30, "Hard": 12 }
    """
    try:
        from backend.services.problem_service import get_problem_by_id
        _, SolvedProblem, _ = _get_models()

        solved_records = SolvedProblem.query.filter_by(user_id=user_id).all()
        stats = {"Easy": 0, "Medium": 0, "Hard": 0}

        for record in solved_records:
            problem = get_problem_by_id(record.problem_id)
            if problem:
                diff = problem.get("difficulty", "")
                if diff in stats:
                    stats[diff] += 1

        return stats
    except Exception as e:
        logger.error(f"get_user_difficulty_stats failed: {e}")
        return {"Easy": 0, "Medium": 0, "Hard": 0}


# ─────────────────────────────────────────────
#  ACTIVITY CALENDAR
# ─────────────────────────────────────────────

def get_user_activity_calendar(user_id: int, days: int = 365) -> Dict[str, int]:
    """
    Returns a dict of { "YYYY-MM-DD": submission_count } for the last `days` days.
    Used to render the GitHub-style contribution calendar on the profile page.
    """
    try:
        Submission, _, _ = _get_models()

        since = datetime.utcnow() - timedelta(days=days)
        subs = (
            Submission.query.filter(
                Submission.user_id == user_id,
                Submission.created_at >= since,
            ).all()
        )

        calendar: Dict[str, int] = defaultdict(int)
        for sub in subs:
            day_str = sub.created_at.strftime("%Y-%m-%d")
            calendar[day_str] += 1

        return dict(calendar)
    except Exception as e:
        logger.error(f"get_user_activity_calendar failed: {e}")
        return {}


# ─────────────────────────────────────────────
#  STREAK CALCULATION
# ─────────────────────────────────────────────

def update_user_streak(user_id: int) -> Dict[str, int]:
    """
    Calculate current and longest streaks based on submission activity.
    Returns { "current": int, "longest": int, "today_solved": bool }
    """
    try:
        Submission, _, _ = _get_models()

        # Get all distinct submission dates for this user
        subs = (
            Submission.query.filter_by(user_id=user_id)
            .order_by(Submission.created_at.desc())
            .all()
        )

        if not subs:
            return {"current": 0, "longest": 0, "today_solved": False}

        # Build sorted set of unique dates
        dates = sorted(
            {sub.created_at.date() for sub in subs}, reverse=True
        )

        today = date.today()
        today_solved = today in dates

        # Current streak
        current = 0
        check = today if today_solved else today - timedelta(days=1)
        for d in dates:
            if d == check:
                current += 1
                check -= timedelta(days=1)
            elif d < check:
                break

        # Longest streak
        longest = 0
        run = 1
        for i in range(1, len(dates)):
            if (dates[i - 1] - dates[i]).days == 1:
                run += 1
                longest = max(longest, run)
            else:
                run = 1
        longest = max(longest, run, current)

        return {"current": current, "longest": longest, "today_solved": today_solved}
    except Exception as e:
        logger.error(f"update_user_streak failed: {e}")
        return {"current": 0, "longest": 0, "today_solved": False}


# ─────────────────────────────────────────────
#  RECENT SUBMISSIONS
# ─────────────────────────────────────────────

def get_user_recent_submissions(user_id: int, limit: int = 10) -> List[Dict]:
    """
    Return the most recent `limit` submissions for a user,
    enriched with problem title and difficulty from the problem service.
    """
    try:
        from backend.services.problem_service import get_problem_by_id
        Submission, _, _ = _get_models()

        subs = (
            Submission.query.filter_by(user_id=user_id)
            .order_by(Submission.created_at.desc())
            .limit(limit)
            .all()
        )

        results = []
        for sub in subs:
            problem = get_problem_by_id(sub.problem_id) or {}
            results.append({
                "submission_id": sub.id,
                "problem_id": sub.problem_id,
                "problem_title": problem.get("title", f"Problem #{sub.problem_id}"),
                "difficulty": problem.get("difficulty", ""),
                "language": sub.language,
                "status": sub.status,
                "runtime_ms": getattr(sub, "runtime_ms", 0),
                "memory_kb": getattr(sub, "memory_kb", 0),
                "created_at": sub.created_at.isoformat() if sub.created_at else None,
            })
        return results
    except Exception as e:
        logger.error(f"get_user_recent_submissions failed: {e}")
        return []


# ─────────────────────────────────────────────
#  LEADERBOARD
# ─────────────────────────────────────────────

def get_leaderboard(period: str = "weekly", limit: int = 50) -> List[Dict]:
    """
    Build a leaderboard ranked by problems solved in the given period.
    period: "weekly" | "monthly" | "all_time"
    """
    try:
        from backend.services.problem_service import get_problem_by_id
        Submission, SolvedProblem, User = _get_models()
        db = _get_db()
        from sqlalchemy import func

        # Time window filter
        now = datetime.utcnow()
        if period == "weekly":
            since = now - timedelta(days=7)
        elif period == "monthly":
            since = now - timedelta(days=30)
        else:
            since = datetime(2020, 1, 1)

        # Count distinct solved problems per user in the window
        rows = (
            db.session.query(
                SolvedProblem.user_id,
                func.count(SolvedProblem.problem_id).label("solved_count"),
            )
            .filter(SolvedProblem.solved_at >= since)
            .group_by(SolvedProblem.user_id)
            .order_by(func.count(SolvedProblem.problem_id).desc())
            .limit(limit)
            .all()
        )

        leaders = []
        for rank, row in enumerate(rows, 1):
            try:
                user = User.query.get(row.user_id)
            except Exception:
                user = None

            # Per-difficulty breakdown
            diff_stats = get_user_difficulty_stats(row.user_id)

            leaders.append({
                "rank": rank,
                "user_id": row.user_id,
                "username": getattr(user, "username", f"User{row.user_id}") if user else f"User{row.user_id}",
                "name": getattr(user, "name", "") if user else "",
                "avatar": getattr(user, "avatar", None) if user else None,
                "solved": row.solved_count,
                "easy": diff_stats.get("Easy", 0),
                "medium": diff_stats.get("Medium", 0),
                "hard": diff_stats.get("Hard", 0),
                "score": (
                    diff_stats.get("Easy", 0) * 1
                    + diff_stats.get("Medium", 0) * 3
                    + diff_stats.get("Hard", 0) * 7
                ),
            })

        return leaders
    except Exception as e:
        logger.error(f"get_leaderboard failed: {e}")
        return _mock_leaderboard(limit)


def _mock_leaderboard(limit: int) -> List[Dict]:
    """Fallback demo leaderboard when DB query fails."""
    names = [
        ("Raj Sharma", "🇮🇳"), ("Alex Chen", "🇨🇳"), ("Priya Singh", "🇮🇳"),
        ("John Smith", "🇺🇸"), ("Maria Garcia", "🇪🇸"), ("Tanaka Hiroshi", "🇯🇵"),
        ("Emma Wilson", "🇬🇧"), ("Lucas Oliveira", "🇧🇷"), ("Sophie Martin", "🇫🇷"),
        ("Kim Ji-ho", "🇰🇷"),
    ]
    leaders = []
    for i, (name, flag) in enumerate(names[:min(limit, len(names))], 1):
        solved = max(5, 1800 - i * 90 + (i % 3) * 20)
        easy = int(solved * 0.45)
        medium = int(solved * 0.38)
        hard = solved - easy - medium
        leaders.append({
            "rank": i,
            "user_id": i,
            "username": name.replace(" ", "_").lower(),
            "name": f"{flag} {name}",
            "avatar": name[0],
            "solved": solved,
            "easy": easy,
            "medium": medium,
            "hard": hard,
            "score": easy * 1 + medium * 3 + hard * 7,
        })
    return leaders


# ─────────────────────────────────────────────
#  XP / POINTS SYSTEM
# ─────────────────────────────────────────────

_XP_PER_DIFFICULTY = {"Easy": 10, "Medium": 30, "Hard": 70}


def calculate_user_xp(user_id: int) -> int:
    """Calculate total XP based on solved problems."""
    try:
        from backend.services.problem_service import get_problem_by_id
        _, SolvedProblem, _ = _get_models()

        records = SolvedProblem.query.filter_by(user_id=user_id).all()
        total_xp = 0
        for record in records:
            problem = get_problem_by_id(record.problem_id)
            if problem:
                diff = problem.get("difficulty", "Easy")
                total_xp += _XP_PER_DIFFICULTY.get(diff, 10)
        return total_xp
    except Exception as e:
        logger.error(f"calculate_user_xp failed: {e}")
        return 0


def get_user_badges(user_id: int) -> List[Dict]:
    """
    Return earned badges based on milestones.
    Extend with more badge types as needed.
    """
    diff_stats = get_user_difficulty_stats(user_id)
    streak_data = update_user_streak(user_id)
    solved = sum(diff_stats.values())

    badges = []

    if solved >= 1:
        badges.append({"id": "first_solve", "name": "First Blood", "icon": "🩸", "color": "#ff5757"})
    if solved >= 10:
        badges.append({"id": "ten_solved", "name": "Problem Crusher", "icon": "💪", "color": "#ffb547"})
    if solved >= 50:
        badges.append({"id": "fifty_solved", "name": "Half Century", "icon": "🎯", "color": "#00e5c8"})
    if solved >= 100:
        badges.append({"id": "century", "name": "Century Club", "icon": "💯", "color": "#5b6bff"})
    if diff_stats.get("Hard", 0) >= 10:
        badges.append({"id": "hard_mode", "name": "Hard Mode", "icon": "🔥", "color": "#ff5757"})
    if diff_stats.get("Hard", 0) >= 50:
        badges.append({"id": "legend", "name": "Legend", "icon": "👑", "color": "#ffd700"})
    if streak_data.get("current", 0) >= 7:
        badges.append({"id": "week_streak", "name": "7-Day Streak", "icon": "🔥", "color": "#ffb547"})
    if streak_data.get("current", 0) >= 30:
        badges.append({"id": "month_streak", "name": "30-Day Streak", "icon": "⚡", "color": "#a855f7"})
    if diff_stats.get("Medium", 0) >= 50:
        badges.append({"id": "medium_master", "name": "Medium Master", "icon": "🎓", "color": "#38bdf8"})

    return badges