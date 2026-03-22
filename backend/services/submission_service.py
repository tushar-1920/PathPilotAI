"""
PathPilot AI — Submission Service
Handles saving submissions, querying history, and marking problems as solved.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# Lazy import — avoids circular import at module load time
def _get_db():
    from backend.extensions import db
    return db

def _get_models():
    from backend.models import Submission, SolvedProblem
    return Submission, SolvedProblem


# ─────────────────────────────────────────────
#  WRITE OPERATIONS
# ─────────────────────────────────────────────

def save_submission(
    user_id: int,
    problem_id: int,
    code: str,
    language: str,
    status: str,
    runtime_ms: float = 0.0,
    memory_kb: int = 0,
    passed_cases: int = 0,
    total_cases: int = 0,
) -> Optional[Any]:
    """
    Persist a new Submission row and return the model instance.
    Returns None on failure (logs the error).
    """
    try:
        db = _get_db()
        Submission, _ = _get_models()

        sub = Submission(
            user_id=user_id,
            problem_id=problem_id,
            code=code,
            language=language,
            status=status,
            runtime_ms=runtime_ms,
            memory_kb=memory_kb,
            passed_cases=passed_cases,
            total_cases=total_cases,
            created_at=datetime.utcnow(),
        )
        db.session.add(sub)
        db.session.commit()
        logger.info(
            f"Saved submission id={sub.id} user={user_id} "
            f"problem={problem_id} status={status}"
        )
        return sub
    except Exception as e:
        logger.error(f"save_submission failed: {e}")
        try:
            _get_db().session.rollback()
        except Exception:
            pass
        return None


def mark_problem_solved(user_id: int, problem_id: int) -> bool:
    """
    Insert a SolvedProblem record if one doesn't already exist.
    Returns True if newly marked solved, False if already solved or error.
    """
    try:
        db = _get_db()
        _, SolvedProblem = _get_models()

        existing = SolvedProblem.query.filter_by(
            user_id=user_id, problem_id=problem_id
        ).first()

        if existing:
            return False  # Already marked

        solved = SolvedProblem(
            user_id=user_id,
            problem_id=problem_id,
            solved_at=datetime.utcnow(),
        )
        db.session.add(solved)
        db.session.commit()
        logger.info(f"Marked problem {problem_id} solved for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"mark_problem_solved failed: {e}")
        try:
            _get_db().session.rollback()
        except Exception:
            pass
        return False


def update_submission_status(submission_id: int, status: str) -> bool:
    """Update the status of an existing submission (e.g. after re-evaluation)."""
    try:
        db = _get_db()
        Submission, _ = _get_models()
        sub = Submission.query.get(submission_id)
        if sub:
            sub.status = status
            db.session.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"update_submission_status failed: {e}")
        try:
            _get_db().session.rollback()
        except Exception:
            pass
        return False


# ─────────────────────────────────────────────
#  READ OPERATIONS
# ─────────────────────────────────────────────

def get_user_submissions(
    user_id: int,
    page: int = 1,
    per_page: int = 20,
    problem_id: Optional[int] = None,
) -> Tuple[List[Dict], int]:
    """
    Return (list_of_submission_dicts, total_count) for a user.
    Optionally filter by problem_id.
    """
    try:
        Submission, _ = _get_models()

        query = Submission.query.filter_by(user_id=user_id)
        if problem_id:
            query = query.filter_by(problem_id=problem_id)

        query = query.order_by(Submission.created_at.desc())
        total = query.count()
        subs = query.offset((page - 1) * per_page).limit(per_page).all()

        return [_submission_to_dict(s) for s in subs], total
    except Exception as e:
        logger.error(f"get_user_submissions failed: {e}")
        return [], 0


def get_submission_by_id(submission_id: int) -> Optional[Dict]:
    """Return a single submission as a dict, including full code."""
    try:
        Submission, _ = _get_models()
        sub = Submission.query.get(submission_id)
        return _submission_to_dict(sub, include_code=True) if sub else None
    except Exception as e:
        logger.error(f"get_submission_by_id failed: {e}")
        return None


def get_problem_submission_stats(problem_id: int) -> Dict:
    """
    Return submission statistics for a given problem.
    { "total_submissions": int, "accepted": int, "acceptance_rate": float }
    """
    try:
        Submission, _ = _get_models()
        total = Submission.query.filter_by(problem_id=problem_id).count()
        accepted = Submission.query.filter_by(
            problem_id=problem_id, status="Accepted"
        ).count()
        rate = round((accepted / total * 100), 1) if total > 0 else 0.0
        return {
            "total_submissions": total,
            "accepted": accepted,
            "acceptance_rate": rate,
        }
    except Exception as e:
        logger.error(f"get_problem_submission_stats failed: {e}")
        return {"total_submissions": 0, "accepted": 0, "acceptance_rate": 0.0}


def get_user_solved_ids(user_id: int) -> List[int]:
    """Return all problem IDs a user has solved."""
    try:
        _, SolvedProblem = _get_models()
        records = SolvedProblem.query.filter_by(user_id=user_id).all()
        return [r.problem_id for r in records]
    except Exception as e:
        logger.error(f"get_user_solved_ids failed: {e}")
        return []


def is_problem_solved(user_id: int, problem_id: int) -> bool:
    """Check if a specific user has solved a specific problem."""
    try:
        _, SolvedProblem = _get_models()
        return (
            SolvedProblem.query.filter_by(
                user_id=user_id, problem_id=problem_id
            ).first()
            is not None
        )
    except Exception as e:
        logger.error(f"is_problem_solved failed: {e}")
        return False


def get_latest_submission_for_problem(
    user_id: int, problem_id: int, language: Optional[str] = None
) -> Optional[Dict]:
    """
    Return the most recent submission for a (user, problem) pair.
    Useful for pre-filling the code editor.
    """
    try:
        Submission, _ = _get_models()
        query = Submission.query.filter_by(
            user_id=user_id, problem_id=problem_id
        )
        if language:
            query = query.filter_by(language=language)
        sub = query.order_by(Submission.created_at.desc()).first()
        return _submission_to_dict(sub, include_code=True) if sub else None
    except Exception as e:
        logger.error(f"get_latest_submission_for_problem failed: {e}")
        return None


# ─────────────────────────────────────────────
#  STATISTICS
# ─────────────────────────────────────────────

def get_user_language_stats(user_id: int) -> List[Dict]:
    """
    Returns submission breakdown by language.
    [{ "language": "python", "count": 42 }, ...]
    """
    try:
        Submission, _ = _get_models()
        from sqlalchemy import func
        db = _get_db()

        rows = (
            db.session.query(
                Submission.language,
                func.count(Submission.id).label("count"),
            )
            .filter(Submission.user_id == user_id)
            .group_by(Submission.language)
            .all()
        )
        return [{"language": r.language, "count": r.count} for r in rows]
    except Exception as e:
        logger.error(f"get_user_language_stats failed: {e}")
        return []


def get_user_status_stats(user_id: int) -> Dict[str, int]:
    """
    Returns count of each submission status for a user.
    { "Accepted": 120, "Wrong Answer": 45, "TLE": 5, ... }
    """
    try:
        Submission, _ = _get_models()
        from sqlalchemy import func
        db = _get_db()

        rows = (
            db.session.query(
                Submission.status,
                func.count(Submission.id).label("count"),
            )
            .filter(Submission.user_id == user_id)
            .group_by(Submission.status)
            .all()
        )
        return {r.status: r.count for r in rows}
    except Exception as e:
        logger.error(f"get_user_status_stats failed: {e}")
        return {}


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _submission_to_dict(sub, include_code: bool = False) -> Dict:
    d = {
        "id": sub.id,
        "user_id": sub.user_id,
        "problem_id": sub.problem_id,
        "language": sub.language,
        "status": sub.status,
        "runtime_ms": getattr(sub, "runtime_ms", 0),
        "memory_kb": getattr(sub, "memory_kb", 0),
        "passed_cases": getattr(sub, "passed_cases", 0),
        "total_cases": getattr(sub, "total_cases", 0),
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
    }
    if include_code:
        d["code"] = sub.code
    return d