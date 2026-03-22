"""
VidCode — Live Collaborative Coding + Video Call Platform
All routes + Socket.IO events in ONE file. No socket folder needed.

Add to app.py:
    from flask_socketio import SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    from backend.routes.vidcode_routes import vidcode_routes, register_socketio_events
    app.register_blueprint(vidcode_routes)
    register_socketio_events(socketio)

Install:
    pip install flask-socketio
"""

from flask import Blueprint, jsonify, render_template, session, request, redirect, url_for
from backend.utils.auth_decorator import login_required
from backend.services.meeting_service import MeetingService, LANGUAGES, STARTER_CODE
from backend.models import User, Profile
import subprocess, sys, tempfile, os, time, threading

vidcode_routes = Blueprint("vidcode_routes", __name__)
svc            = MeetingService()

# ── Helper ──────────────────────────────────────────────────────
def _get_user():
    uid  = session.get("user_id")
    if not uid: return None, None, None
    user = User.query.get(uid)
    pr   = Profile.query.filter_by(user_id=uid).first() if user else None
    img  = f"/static/{pr.profile_image}" if pr and pr.profile_image else ""
    return uid, user.name if user else "Guest", img


# ══════════════════════════════════════════════════════════════
#  HTTP PAGES
# ══════════════════════════════════════════════════════════════

@vidcode_routes.route("/vidcode")
@login_required
def vidcode_home():
    uid, name, img = _get_user()
    return render_template("vidcode_home.html", user_name=name, user_image=img,
                           languages=LANGUAGES)


@vidcode_routes.route("/vidcode/room/<room_code>")
@login_required
def room_page(room_code):
    uid, name, img = _get_user()
    room = svc.get_room(room_code)
    if not room:
        return redirect(url_for("vidcode_routes.vidcode_home"))
    # Auto-join if not already in room
    if str(uid) not in room["participants"]:
        svc.join_room(room_code, uid, name, img)
    # Render as standalone page (no base.html navbar)
    from flask import make_response
    resp = make_response(render_template("vidcode_room.html",
        room=svc.room_state(room_code),
        user_id=uid, user_name=name, user_image=img,
        languages=LANGUAGES, is_host=room["host_id"]==uid))
    return resp


# ══════════════════════════════════════════════════════════════
#  HTTP APIs
# ══════════════════════════════════════════════════════════════

@vidcode_routes.route("/api/vidcode/create", methods=["POST"])
@login_required
def create_room():
    uid, name, img = _get_user()
    data  = request.get_json() or {}
    title = data.get("title", "").strip()
    room  = svc.create_room(uid, name, img, title)
    return jsonify({"success": True, "room_code": room["room_code"],
                    "redirect": f"/vidcode/room/{room['room_code']}"})


@vidcode_routes.route("/api/vidcode/join", methods=["POST"])
@login_required
def join_room():
    uid, name, img = _get_user()
    data = request.get_json() or {}
    code = (data.get("room_code") or "").strip().upper()
    room = svc.join_room(code, uid, name, img)
    if not room:
        return jsonify({"error": "Room not found or has ended"}), 404
    return jsonify({"success": True, "redirect": f"/vidcode/room/{code}"})


@vidcode_routes.route("/api/vidcode/room/<room_code>")
@login_required
def get_room(room_code):
    state = svc.room_state(room_code)
    if not state: return jsonify({"error": "Room not found"}), 404
    return jsonify(state)


@vidcode_routes.route("/api/vidcode/languages")
@login_required
def get_languages():
    return jsonify(LANGUAGES)


@vidcode_routes.route("/api/vidcode/run", methods=["POST"])
@login_required
def run_code():
    """Execute code server-side for Python/JS. Others show simulated output."""
    data     = request.get_json() or {}
    code     = data.get("code", "")
    language = data.get("language", "python")
    room_code= data.get("room_code", "")

    output, status = _execute_code(code, language)

    # Persist output so all participants see it
    if room_code:
        svc.set_output(room_code, output, status)

    return jsonify({"output": output, "status": status})


def _execute_code(code: str, language: str) -> tuple:
    """Safe sandboxed execution for Python. Simulate for others."""
    if language == "python":
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                             delete=False, encoding="utf-8") as f:
                f.write(code)
                path = f.name
            result = subprocess.run(
                [sys.executable, path],
                capture_output=True, text=True, timeout=10,
            )
            os.unlink(path)
            output = result.stdout + result.stderr
            status = "error" if result.returncode != 0 else "success"
            return (output or "(no output)"), status
        except subprocess.TimeoutExpired:
            return "⏱️ Time limit exceeded (10s)", "error"
        except Exception as e:
            return f"Execution error: {str(e)}", "error"

    elif language == "javascript":
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".js",
                                             delete=False, encoding="utf-8") as f:
                f.write(code)
                path = f.name
            result = subprocess.run(
                ["node", path], capture_output=True, text=True, timeout=10,
            )
            os.unlink(path)
            output = result.stdout + result.stderr
            status = "error" if result.returncode != 0 else "success"
            return (output or "(no output)"), status
        except FileNotFoundError:
            return "Node.js not installed on server", "error"
        except subprocess.TimeoutExpired:
            return "⏱️ Time limit exceeded (10s)", "error"
        except Exception as e:
            return f"Execution error: {str(e)}", "error"

    else:
        return f"✅ Code received ({language.upper()})\n💡 Server-side execution available for Python & JavaScript.\nOther languages: install runtime on server.", "info"


# ══════════════════════════════════════════════════════════════
#  SOCKET.IO EVENTS — registered via register_socketio_events()
# ══════════════════════════════════════════════════════════════

def register_socketio_events(socketio):
    """Call this from app.py after creating socketio instance."""
    from flask_socketio import join_room as sio_join, leave_room as sio_leave, emit

    # ── JOIN ROOM ──
    @socketio.on("vc_join")
    def on_join(data):
        room_code = data.get("room_code", "").upper()
        user_id   = data.get("user_id")
        user_name = data.get("user_name", "Guest")
        sid       = request.sid

        sio_join(room_code)
        svc.set_sid(room_code, user_id, sid)

        state = svc.room_state(room_code)
        if not state: return

        # Send full state to the joining user
        emit("vc_room_state", state)

        # Notify everyone else
        emit("vc_user_joined", {
            "user_id": user_id, "user_name": user_name, "sid": sid,
            "participants": state["participants"],
        }, room=room_code, include_self=False)

        # Announce in chat
        entry = svc.add_chat(room_code, 0, "System",
                             f"👋 {user_name} joined the room")
        emit("vc_chat_msg", entry, room=room_code)

    # ── LEAVE ROOM ──
    @socketio.on("vc_leave")
    def on_leave(data):
        room_code = data.get("room_code", "").upper()
        user_id   = data.get("user_id")
        user_name = data.get("user_name", "Someone")

        svc.leave_room(room_code, user_id)
        sio_leave(room_code)

        state = svc.room_state(room_code)
        emit("vc_user_left", {
            "user_id": user_id,
            "participants": state["participants"] if state else [],
        }, room=room_code)

        entry = svc.add_chat(room_code, 0, "System",
                             f"👋 {user_name} left the room")
        emit("vc_chat_msg", entry, room=room_code)

    # ── DISCONNECT ──
    @socketio.on("disconnect")
    def on_disconnect():
        pass  # handled by vc_leave

    # ── CODE CHANGE — real-time sync ──
    @socketio.on("vc_code_change")
    def on_code_change(data):
        room_code = data.get("room_code", "").upper()
        code      = data.get("code", "")
        language  = data.get("language", "python")
        user_id   = data.get("user_id")
        cursor    = data.get("cursor")

        # Check permission
        room = svc.get_room(room_code)
        if not room: return
        p = room["participants"].get(str(user_id), {})
        if not p.get("can_code") and room["host_id"] != user_id: return
        if room["locked"] and room["host_id"] != user_id: return

        svc.update_code(room_code, code, language)
        emit("vc_code_update", {
            "code": code, "language": language,
            "changed_by": user_id, "cursor": cursor,
        }, room=room_code, include_self=False)

    # ── LANGUAGE CHANGE ──
    @socketio.on("vc_change_language")
    def on_change_language(data):
        room_code = data.get("room_code", "").upper()
        lang      = data.get("language", "python")
        user_id   = data.get("user_id")

        room = svc.get_room(room_code)
        if not room or room["host_id"] != user_id: return

        svc.change_language(room_code, lang)
        emit("vc_language_changed", {
            "language": lang,
            "code": STARTER_CODE.get(lang, ""),
        }, room=room_code)

    # ── CHAT ──
    @socketio.on("vc_chat")
    def on_chat(data):
        room_code = data.get("room_code", "").upper()
        user_id   = data.get("user_id")
        user_name = data.get("user_name", "User")
        message   = (data.get("message") or "").strip()

        if not message: return
        entry = svc.add_chat(room_code, user_id, user_name, message)
        emit("vc_chat_msg", entry, room=room_code)

    # ── RUN CODE (broadcast output to all) ──
    @socketio.on("vc_run_code")
    def on_run_code(data):
        room_code = data.get("room_code", "").upper()
        code      = data.get("code", "")
        language  = data.get("language", "python")
        user_id   = data.get("user_id")

        room = svc.get_room(room_code)
        if not room: return
        if room["host_id"] != user_id:
            p = room["participants"].get(str(user_id), {})
            if not p.get("can_code"): return

        # Notify running
        emit("vc_output_update", {"output": "⏳ Running...", "status": "running"},
             room=room_code)

        # Run in background thread
        def run():
            output, status = _execute_code(code, language)
            svc.set_output(room_code, output, status)
            socketio.emit("vc_output_update",
                          {"output": output, "status": status},
                          room=room_code)

        t = threading.Thread(target=run)
        t.daemon = True
        t.start()

    # ── HOST CONTROLS ──
    @socketio.on("vc_grant_coding")
    def on_grant_coding(data):
        room_code = data.get("room_code", "").upper()
        host_id   = data.get("host_id")
        target_id = data.get("target_id")
        allow     = data.get("allow", True)

        ok = svc.grant_coding(room_code, host_id, target_id, allow)
        if ok:
            state = svc.room_state(room_code)
            emit("vc_participants_update", {"participants": state["participants"]},
                 room=room_code)
            msg = "can now edit code" if allow else "can no longer edit code"
            name = next((p["name"] for p in state["participants"]
                         if p["user_id"] == target_id), "User")
            entry = svc.add_chat(room_code, 0, "Host",
                                 f"🔑 {name} {msg}")
            emit("vc_chat_msg", entry, room=room_code)

    @socketio.on("vc_kick")
    def on_kick(data):
        room_code = data.get("room_code", "").upper()
        host_id   = data.get("host_id")
        target_id = data.get("target_id")
        target_name = data.get("target_name", "User")

        sid = svc.kick(room_code, host_id, target_id)
        if sid:
            socketio.emit("vc_kicked", {"message": "You were removed by the host"},
                          room=sid)
            state = svc.room_state(room_code)
            emit("vc_participants_update",
                 {"participants": state["participants"] if state else []},
                 room=room_code)
            entry = svc.add_chat(room_code, 0, "Host",
                                 f"🚫 {target_name} was removed")
            emit("vc_chat_msg", entry, room=room_code)

    @socketio.on("vc_mute")
    def on_mute(data):
        room_code = data.get("room_code", "").upper()
        host_id   = data.get("host_id")
        target_id = data.get("target_id")

        muted = svc.mute(room_code, host_id, target_id)
        state = svc.room_state(room_code)
        if state:
            emit("vc_participants_update",
                 {"participants": state["participants"]}, room=room_code)
            target_sid = next(
                (p["sid"] for p in state["participants"] if p["user_id"] == target_id), None)
            if target_sid:
                socketio.emit("vc_force_mute", {"muted": muted}, room=target_sid)

    @socketio.on("vc_toggle_lock")
    def on_toggle_lock(data):
        room_code = data.get("room_code", "").upper()
        host_id   = data.get("host_id")

        locked = svc.toggle_lock(room_code, host_id)
        emit("vc_lock_changed", {"locked": locked}, room=room_code)
        entry = svc.add_chat(room_code, 0, "Host",
                             f"{'🔒 Editor locked' if locked else '🔓 Editor unlocked'} by host")
        emit("vc_chat_msg", entry, room=room_code)

    # ── WebRTC SIGNALING ──
    @socketio.on("vc_webrtc_offer")
    def on_offer(data):
        target_sid = data.get("target_sid")
        if target_sid:
            emit("vc_webrtc_offer", data, room=target_sid)

    @socketio.on("vc_webrtc_answer")
    def on_answer(data):
        target_sid = data.get("target_sid")
        if target_sid:
            emit("vc_webrtc_answer", data, room=target_sid)

    @socketio.on("vc_ice_candidate")
    def on_ice(data):
        target_sid = data.get("target_sid")
        if target_sid:
            emit("vc_ice_candidate", data, room=target_sid)

    # ── CURSOR POSITION (show other users' cursors) ──
    @socketio.on("vc_cursor")
    def on_cursor(data):
        room_code = data.get("room_code", "").upper()
        emit("vc_cursor_update", data, room=room_code, include_self=False)

    # ── TYPING INDICATOR ──
    @socketio.on("vc_typing")
    def on_typing(data):
        room_code = data.get("room_code", "").upper()
        emit("vc_typing_update", data, room=room_code, include_self=False)