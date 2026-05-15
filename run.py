import os
from backend.app import create_app, socketio
from dotenv import load_dotenv
load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=debug,
    )