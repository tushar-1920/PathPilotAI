import sys, os
sys.path.insert(0, '/opt/render/project/src')
os.chdir('/opt/render/project/src')
from backend.app import create_app, socketio
app = create_app()
