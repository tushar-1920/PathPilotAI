import random, string
from datetime import datetime

_rooms = {}

def _gen_code():
    for _ in range(20):
        code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
        if code not in _rooms:
            return code
    return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))

LANGUAGES = {
    "python":     {"label": "Python 3",   "icon": "🐍"},
    "javascript": {"label": "JavaScript", "icon": "🟨"},
    "java":       {"label": "Java",       "icon": "☕"},
    "cpp":        {"label": "C++",        "icon": "⚡"},
    "typescript": {"label": "TypeScript", "icon": "🔷"},
    "go":         {"label": "Go",         "icon": "🐹"},
    "rust":       {"label": "Rust",       "icon": "🦀"},
    "sql":        {"label": "SQL",        "icon": "🗄️"},
}

STARTER_CODE = {
    "python":     "# Welcome to VidCode\n\ndef solution():\n    pass\n\nprint(solution())\n",
    "javascript": "// Welcome to VidCode\n\nfunction solution() {\n    \n}\n\nconsole.log(solution());\n",
    "java":       "// Welcome to VidCode\npublic class Solution {\n    public static void main(String[] args) {\n        \n    }\n}\n",
    "cpp":        "// Welcome to VidCode\n#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}\n",
    "typescript": "// Welcome to VidCode\nfunction solution(): void {\n    \n}\nsolution();\n",
    "go":         "// Welcome to VidCode\npackage main\nimport \"fmt\"\nfunc main() {\n    fmt.Println(\"Hello VidCode\")\n}\n",
    "rust":       "// Welcome to VidCode\nfn main() {\n    println!(\"Hello VidCode\");\n}\n",
    "sql":        "-- Welcome to VidCode\nSELECT * FROM users WHERE id = 1;\n",
}


class MeetingService:

    def create_room(self, host_id, host_name, host_image, title=""):
        code = _gen_code()
        room = {
            "room_code": code, "host_id": host_id,
            "title": title or f"{host_name}'s VidCode Room",
            "created_at": datetime.utcnow().isoformat(),
            "participants": {
                str(host_id): {"user_id": host_id, "name": host_name, "image": host_image,
                               "role": "host", "can_code": True, "muted": False,
                               "video_off": False, "sid": None,
                               "joined_at": datetime.utcnow().isoformat()}
            },
            "code": STARTER_CODE["python"], "language": "python",
            "chat": [], "output": "", "output_status": "",
            "locked": False, "active": True,
        }
        _rooms[code] = room
        return room

    def get_room(self, code):
        return _rooms.get((code or "").upper().strip())

    def join_room(self, code, user_id, user_name, user_image):
        room = self.get_room(code)
        if not room or not room["active"]: return None
        uid = str(user_id)
        if uid not in room["participants"]:
            room["participants"][uid] = {
                "user_id": user_id, "name": user_name, "image": user_image,
                "role": "participant", "can_code": False, "muted": False,
                "video_off": False, "sid": None,
                "joined_at": datetime.utcnow().isoformat()
            }
        return room

    def leave_room(self, code, user_id):
        room = _rooms.get(code)
        if not room: return
        room["participants"].pop(str(user_id), None)
        if not room["participants"]:
            _rooms.pop(code, None)

    def set_sid(self, code, user_id, sid):
        room = _rooms.get(code)
        if room and str(user_id) in room["participants"]:
            room["participants"][str(user_id)]["sid"] = sid

    def grant_coding(self, code, host_id, target_id, allow):
        room = _rooms.get(code)
        if not room or room["host_id"] != host_id: return False
        uid = str(target_id)
        if uid in room["participants"]:
            room["participants"][uid]["can_code"] = allow
            return True
        return False

    def kick(self, code, host_id, target_id):
        room = _rooms.get(code)
        if not room or room["host_id"] != host_id: return None
        p = room["participants"].pop(str(target_id), None)
        return p["sid"] if p else None

    def mute(self, code, host_id, target_id):
        room = _rooms.get(code)
        if not room or room["host_id"] != host_id: return False
        uid = str(target_id)
        if uid in room["participants"]:
            room["participants"][uid]["muted"] = not room["participants"][uid]["muted"]
            return room["participants"][uid]["muted"]
        return False

    def toggle_lock(self, code, host_id):
        room = _rooms.get(code)
        if not room or room["host_id"] != host_id: return False
        room["locked"] = not room["locked"]
        return room["locked"]

    def update_code(self, code, new_code, lang):
        room = _rooms.get(code)
        if room:
            room["code"] = new_code
            room["language"] = lang

    def change_language(self, code, lang):
        room = _rooms.get(code)
        if room and lang in STARTER_CODE:
            room["language"] = lang
            room["code"] = STARTER_CODE[lang]

    def add_chat(self, code, user_id, name, msg):
        room = _rooms.get(code)
        entry = {"user_id": user_id, "name": name, "message": msg,
                 "time": datetime.utcnow().strftime("%H:%M")}
        if room: room["chat"].append(entry)
        return entry

    def set_output(self, code, output, status):
        room = _rooms.get(code)
        if room:
            room["output"] = output
            room["output_status"] = status

    def room_state(self, code):
        room = _rooms.get(code)
        if not room: return None
        return {
            "room_code": room["room_code"], "title": room["title"],
            "host_id": room["host_id"], "code": room["code"],
            "language": room["language"], "locked": room["locked"],
            "output": room["output"], "output_status": room["output_status"],
            "chat": room["chat"][-50:],
            "participants": list(room["participants"].values()),
        }

    def get_languages(self): return LANGUAGES
    def get_starter(self, lang): return STARTER_CODE.get(lang, "")