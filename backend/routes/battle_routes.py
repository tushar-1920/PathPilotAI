"""
PathPilot AI — Battle Mode Routes
1v1 Live Coding Duels with real-time Socket.IO events.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import join_room as sio_join, leave_room as sio_leave, emit
from backend.utils.auth_decorator import login_required
from backend.models import User, Profile
from backend.services.battle_service import (
    create_duel, get_duel, join_duel, set_player_sid, set_player_ready,
    start_duel, update_player_code, record_test_pass, submit_solution,
    add_chat, duel_state, get_battle_problem, get_league, get_xp_rank,
    get_trophy_rewards, get_battle_profile, get_battle_history,
    next_question_for_all,
    BATTLE_PROBLEMS, LEAGUES, XP_RANKS
)
import subprocess, sys, tempfile, os, time, threading, json

battle_routes = Blueprint("battle_routes", __name__)

SUPPORTED_LANGS = {
    "python":     {"label": "Python 3",   "icon": "🐍", "ext": "py"},
    "javascript": {"label": "JavaScript", "icon": "🟨", "ext": "js"},
}


def _get_user():
    uid = session.get("user_id")
    if not uid: return None, None, None
    user = User.query.get(uid)
    pr   = Profile.query.filter_by(user_id=uid).first() if user else None
    img  = f"/static/{pr.profile_image}" if pr and pr.profile_image else ""
    return uid, user.name if user else "Guest", img


# ══════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════════════

@battle_routes.route("/battle")
@login_required
def battle_home():
    uid, name, img = _get_user()
    return render_template("battle_home.html",
        user_name=name, user_image=img,
        languages=SUPPORTED_LANGS,
        easy_count=len(BATTLE_PROBLEMS["easy"]),
        medium_count=len(BATTLE_PROBLEMS["medium"]),
        hard_count=len(BATTLE_PROBLEMS["hard"]),
    )


@battle_routes.route("/battle/room/<duel_code>")
@login_required
def battle_room(duel_code):
    uid, name, img = _get_user()
    duel = get_duel(duel_code)
    if not duel:
        return redirect(url_for("battle_routes.battle_home"))
    # Auto-join if not in duel
    if str(uid) not in duel["players"]:
        result = join_duel(duel_code, uid, name, img)
        if not result:
            return redirect(url_for("battle_routes.battle_home"))
    state = duel_state(duel_code)
    return render_template("battle_room.html",
        duel=state,
        user_id=uid, user_name=name, user_image=img,
        is_host=(duel["host_id"] == uid),
        languages=SUPPORTED_LANGS,
    )


@battle_routes.route("/battle/result/<duel_code>")
@login_required
def battle_result(duel_code):
    uid, name, img = _get_user()
    duel = get_duel(duel_code)
    if not duel:
        return redirect(url_for("battle_routes.battle_home"))
    state = duel_state(duel_code)
    return render_template("battle_result.html",
        duel=state, user_id=uid, user_name=name,
    )


# ══════════════════════════════════════════════════════════════
#  HTTP API
# ══════════════════════════════════════════════════════════════

@battle_routes.route("/api/battle/create", methods=["POST"])
@login_required
def create_battle():
    uid, name, img = _get_user()
    data       = request.get_json() or {}
    difficulty = data.get("difficulty", "easy")
    language   = data.get("language", "python")
    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "easy"
    if language not in SUPPORTED_LANGS:
        language = "python"
    duel = create_duel(uid, name, img, difficulty, language)
    return jsonify({"success": True, "duel_code": duel["duel_code"],
                    "redirect": f"/battle/room/{duel['duel_code']}"})


@battle_routes.route("/api/battle/join", methods=["POST"])
@login_required
def join_battle():
    uid, name, img = _get_user()
    data = request.get_json() or {}
    code = (data.get("duel_code") or "").strip().upper()
    duel = join_duel(code, uid, name, img)
    if not duel:
        return jsonify({"error": "Room not found, full, or already started"}), 404
    return jsonify({"success": True, "redirect": f"/battle/room/{code}"})


@battle_routes.route("/api/battle/room/<duel_code>")
@login_required
def get_battle_state(duel_code):
    state = duel_state(duel_code)
    if not state:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(state)


@battle_routes.route("/api/battle/run", methods=["POST"])
@login_required
def run_battle_code():
    """Run code against a specific test case index — for Test button."""
    uid = session.get("user_id")
    data = request.get_json() or {}
    code       = data.get("code", "")
    language   = data.get("language", "python")
    duel_code  = (data.get("duel_code") or "").upper()
    test_idx   = int(data.get("test_idx", 0))

    duel = get_duel(duel_code)
    if not duel:
        return jsonify({"error": "Duel not found"}), 404

    test_cases = [tc for tc in duel["problem"].get("test_cases", []) if not tc.get("hidden", False)]
    if not test_cases:
        return jsonify({"error": "No test cases"}), 400
    tc = test_cases[min(test_idx, len(test_cases)-1)]
    test_input = tc.get("input", "")
    expected   = tc.get("expected", "")

    output, status, exec_time = _execute_code(code, language, test_input)
    passed = _check_output(output, expected)

    return jsonify({
        "output": output,
        "status": status,
        "passed": passed,
        "exec_time": round(exec_time, 3),
        "expected": expected,
        "test_idx": test_idx,
        "total_visible": len(test_cases),
    })


@battle_routes.route("/api/battle/next-question", methods=["POST"])
@login_required
def next_question():
    """Host can request a new question for the same duel (practice mode)."""
    uid = session.get("user_id")
    data = request.get_json() or {}
    duel_code = (data.get("duel_code") or "").upper()
    duel = get_duel(duel_code)
    if not duel:
        return jsonify({"error": "Duel not found"}), 404
    if duel["host_id"] != uid:
        return jsonify({"error": "Only host can change question"}), 403
    exclude = [duel["problem"]["id"]]
    new_problem = get_battle_problem(duel["difficulty"], exclude_ids=exclude)
    duel["problem"] = new_problem
    duel["time_limit"] = new_problem.get("time_limit", 15) * 60
    # Reset all players
    for p in duel["players"].values():
        p["submitted"] = False
        p["passed"] = False
        p["passed_count"] = 0
        p["total_tests"] = len(new_problem.get("test_cases", []))
        p["submit_time"] = None
        p["xp_earned"] = 0
        p["result"] = None
        p["code"] = new_problem.get("boilerplate", {}).get(duel["language"], "# Write your solution here\n")
    duel["status"] = "active"
    duel["winner_id"] = None
    duel["events"].append({"text": "🔄 New question loaded! Battle continues!", "uid": 0, "t": __import__("time").time()})
    state = duel_state(duel_code)
    return jsonify({"success": True, "state": state})


@battle_routes.route("/api/battle/submit", methods=["POST"])
@login_required
def submit_battle():
    """Submit solution — run ALL test cases and determine result."""
    uid = session.get("user_id")
    data      = request.get_json() or {}
    code      = data.get("code", "")
    language  = data.get("language", "python")
    duel_code = (data.get("duel_code") or "").upper()

    duel = get_duel(duel_code)
    if not duel:
        return jsonify({"error": "Duel not found"}), 404

    player = duel["players"].get(str(uid))
    if not player:
        return jsonify({"error": "Not in this duel"}), 403
    if player.get("submitted"):
        return jsonify({"error": "Already submitted"}), 400

    test_cases = duel["problem"].get("test_cases", [])
    passed_count = 0
    results = []
    total_start = time.time()

    for i, tc in enumerate(test_cases):
        output, status, exec_time = _execute_code(code, language, tc.get("input", ""))
        passed = _check_output(output, tc.get("expected", ""))
        if passed:
            passed_count += 1
        results.append({
            "test_num": i + 1,
            "passed": passed,
            "output": output,
            "expected": tc.get("expected", ""),
            "exec_time": round(exec_time, 3),
            "hidden": tc.get("hidden", False),
        })

    total_time = time.time() - total_start
    all_passed = passed_count == len(test_cases)

    # Record in duel state
    finish_data = submit_solution(duel_code, uid, all_passed, passed_count,
                                  len(test_cases), total_time)

    return jsonify({
        "passed": all_passed,
        "passed_count": passed_count,
        "total": len(test_cases),
        "results": results,
        "exec_time": round(total_time, 3),
        "finished": finish_data.get("finished", False),
        "winner_id": finish_data.get("winner_id"),
    })


@battle_routes.route("/api/battle/profile")
@login_required
def get_my_battle_profile():
    uid = session.get("user_id")
    profile = get_battle_profile(uid)
    history = get_battle_history(uid, limit=15)
    return jsonify({"profile": profile, "history": history})


@battle_routes.route("/api/battle/profile/<int:user_id>")
@login_required
def get_user_battle_profile(user_id):
    profile = get_battle_profile(user_id)
    history = get_battle_history(user_id, limit=10)
    return jsonify({"profile": profile, "history": history})


@battle_routes.route("/api/battle/leaderboard")
@login_required
def get_leaderboard():
    try:
        from backend.models import BattleProfile, User
        rows = BattleProfile.query.order_by(BattleProfile.trophies.desc()).limit(50).all()
        result = []
        for r in rows:
            user = User.query.get(r.user_id)
            if not user: continue
            league = get_league(r.trophies)
            result.append({
                "user_id": r.user_id,
                "name": user.name,
                "trophies": r.trophies,
                "total_xp": r.total_xp,
                "wins": r.wins,
                "total_battles": r.total_battles,
                "win_rate": round((r.wins/max(1,r.total_battles))*100,1),
                "league": league["full_name"],
                "league_icon": league["icon"],
            })
        return jsonify({"leaderboard": result})
    except Exception as e:
        return jsonify({"leaderboard": [], "error": str(e)})


# ══════════════════════════════════════════════════════════════
#  CODE EXECUTION ENGINE
# ══════════════════════════════════════════════════════════════

def _execute_code(code: str, language: str, stdin_data: str = "") -> tuple:
    start = time.time()
    try:
        if language == "python":
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
                f.write(code); path = f.name
            result = subprocess.run(
                [sys.executable, path],
                input=stdin_data, capture_output=True, text=True, timeout=10
            )
            os.unlink(path)
            output = (result.stdout + result.stderr).strip()
            status = "error" if result.returncode != 0 else "success"
        elif language == "javascript":
            with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(code); path = f.name
            result = subprocess.run(
                ["node", path],
                input=stdin_data, capture_output=True, text=True, timeout=10
            )
            os.unlink(path)
            output = (result.stdout + result.stderr).strip()
            status = "error" if result.returncode != 0 else "success"
        else:
            output = f"Language {language} not supported"
            status = "error"
    except subprocess.TimeoutExpired:
        output = "⏱️ Time Limit Exceeded (10s)"
        status = "tle"
    except FileNotFoundError:
        output = f"{language} runtime not found on server"
        status = "error"
    except Exception as e:
        output = f"Execution error: {str(e)}"
        status = "error"
    return output, status, time.time() - start


def _check_output(actual: str, expected: str) -> bool:
    """Flexible output comparison."""
    a = actual.strip().lower().replace(" ", "").replace("\n", "")
    e = expected.strip().lower().replace(" ", "").replace("\n", "")
    return a == e


# ══════════════════════════════════════════════════════════════
#  SOCKET.IO EVENTS
# ══════════════════════════════════════════════════════════════

def register_battle_socket_events(socketio):
    """Call from app.py after socketio is created."""

    @socketio.on("battle_join")
    def on_battle_join(data):
        duel_code = (data.get("duel_code") or "").upper()
        user_id   = data.get("user_id")
        user_name = data.get("user_name", "Player")
        sid       = request.sid

        sio_join(duel_code)
        set_player_sid(duel_code, user_id, sid)

        state = duel_state(duel_code)
        if not state: return

        # Send full state to joiner
        emit("battle_state", state)

        # Tell everyone someone joined
        emit("battle_player_joined", {
            "user_id": user_id,
            "user_name": user_name,
            "players": state["players"],
        }, room=duel_code, include_self=False)

        # System chat message
        entry = add_chat(duel_code, 0, "System", f"⚔️ {user_name} entered the arena!")
        emit("battle_chat", entry, room=duel_code)

        # If 2 players and status waiting, auto start countdown
        if len(state["players"]) == 2 and state["status"] == "waiting":
            _broadcast_countdown(socketio, duel_code)

    @socketio.on("battle_ready")
    def on_ready(data):
        duel_code = (data.get("duel_code") or "").upper()
        user_id   = data.get("user_id")
        all_ready = set_player_ready(duel_code, user_id)
        state = duel_state(duel_code)
        emit("battle_ready_update", {"players": state["players"]}, room=duel_code)
        if all_ready:
            _broadcast_countdown(socketio, duel_code)

    @socketio.on("battle_code_change")
    def on_code_change(data):
        duel_code = (data.get("duel_code") or "").upper()
        user_id   = data.get("user_id")
        code      = data.get("code", "")
        update_player_code(duel_code, user_id, code)
        # Don't broadcast code to opponent (no copy-paste cheating!)

    @socketio.on("battle_test_pass")
    def on_test_pass(data):
        """Client reports passing a visible test case."""
        duel_code = (data.get("duel_code") or "").upper()
        user_id   = data.get("user_id")
        test_num  = data.get("test_num", 1)
        result    = record_test_pass(duel_code, user_id, test_num)
        if result.get("event"):
            emit("battle_live_event", {
                "text": result["event"],
                "uid": user_id,
                "type": "test_pass",
                "state": duel_state(duel_code),
            }, room=duel_code)

    @socketio.on("battle_submitted")
    def on_submitted(data):
        """Broadcast to everyone that someone submitted."""
        duel_code  = (data.get("duel_code") or "").upper()
        user_id    = data.get("user_id")
        user_name  = data.get("user_name", "Player")
        passed     = data.get("passed", False)
        passed_count = data.get("passed_count", 0)
        total      = data.get("total", 3)
        finished   = data.get("finished", False)
        winner_id  = data.get("winner_id")

        result_text = "✅ ACCEPTED" if passed else f"❌ {passed_count}/{total} passed"
        event_text  = f"🏁 {user_name} submitted — {result_text}"

        emit("battle_live_event", {
            "text": event_text,
            "uid": user_id,
            "type": "submit",
            "state": duel_state(duel_code),
        }, room=duel_code)

        if finished:
            state = duel_state(duel_code)
            emit("battle_finished", {
                "winner_id": winner_id,
                "state": state,
            }, room=duel_code)

    @socketio.on("battle_chat")
    def on_chat(data):
        duel_code = (data.get("duel_code") or "").upper()
        user_id   = data.get("user_id")
        user_name = data.get("user_name", "Player")
        message   = (data.get("message") or "").strip()
        if not message: return
        entry = add_chat(duel_code, user_id, user_name, message)
        emit("battle_chat", entry, room=duel_code)

    @socketio.on("battle_leave")
    def on_leave(data):
        duel_code = (data.get("duel_code") or "").upper()
        user_id   = data.get("user_id")
        user_name = data.get("user_name", "Player")
        sio_leave(duel_code)
        entry = add_chat(duel_code, 0, "System", f"💨 {user_name} left the arena")
        emit("battle_chat", entry, room=duel_code)
        state = duel_state(duel_code)
        if state:
            emit("battle_player_left", {"user_id": user_id, "state": state}, room=duel_code)

    @socketio.on("battle_typing")
    def on_typing(data):
        duel_code = (data.get("duel_code") or "").upper()
        emit("battle_typing_update", {
            "user_id": data.get("user_id"),
            "user_name": data.get("user_name"),
        }, room=duel_code, include_self=False)

    @socketio.on("battle_new_question")
    def on_new_question(data):
        """Either player can trigger a new question — resets both sides equally."""
        duel_code = (data.get("duel_code") or "").upper()
        user_id   = data.get("user_id")
        result = next_question_for_all(duel_code, user_id)
        if result.get("success"):
            state = result["state"]
            emit("battle_question_changed", {"state": state}, room=duel_code)
            player_name = data.get("user_name", "A player")
            entry = add_chat(duel_code, 0, "System", f"\U0001f504 {player_name} loaded a new question! Code reset for everyone.")
            emit("battle_chat", entry, room=duel_code)


def _broadcast_countdown(socketio, duel_code: str):
    """Run 5-second countdown then start duel in background thread."""
    def _run():
        for i in range(5, 0, -1):
            socketio.emit("battle_countdown", {"count": i}, room=duel_code)
            time.sleep(1)
        start_duel(duel_code)
        state = duel_state(duel_code)
        socketio.emit("battle_started", {"state": state}, room=duel_code)
    t = threading.Thread(target=_run, daemon=True)
    t.start()