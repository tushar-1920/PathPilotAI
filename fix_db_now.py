"""
Run from D:\PathPilotAI\:
    python fix_db_now.py
"""
import sqlite3, os, glob

# Auto-find ALL .db files in project
db_files = glob.glob("**/*.db", recursive=True) + glob.glob("*.db")
print("Found DB files:", db_files)

if not db_files:
    print("No .db files found! Check your DATABASE_URL or SQLALCHEMY_DATABASE_URI in config.")
    exit(1)

# Use the first one (usually the right one)
db_path = db_files[0]
print(f"Using: {db_path}")

conn = sqlite3.connect(db_path)
cur  = conn.cursor()

# Show existing tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

def col_exists(table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def tbl_exists(t):
    return t in tables

done = []

# ── profiles ──
if tbl_exists("profiles"):
    if not col_exists("profiles", "username"):
        cur.execute("ALTER TABLE profiles ADD COLUMN username VARCHAR(30)")
        done.append("profiles.username")
    if not col_exists("profiles", "username_set"):
        cur.execute("ALTER TABLE profiles ADD COLUMN username_set BOOLEAN DEFAULT 0")
        done.append("profiles.username_set")

# ── posts ──
if tbl_exists("posts"):
    if not col_exists("posts", "image_url"):
        cur.execute("ALTER TABLE posts ADD COLUMN image_url VARCHAR(500)")
        done.append("posts.image_url")

# ── certificates ──
if tbl_exists("certificates"):
    if not col_exists("certificates", "image_url"):
        cur.execute("ALTER TABLE certificates ADD COLUMN image_url VARCHAR(500)")
        done.append("certificates.image_url")

# ── post_comments (new table) ──
if not tbl_exists("post_comments"):
    cur.execute("""CREATE TABLE post_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    done.append("post_comments table")

# ── messages (new table) ──
if not tbl_exists("messages"):
    cur.execute("""CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    done.append("messages table")

conn.commit()
conn.close()

if done:
    print("\n✅ Fixed:", ", ".join(done))
else:
    print("\n✅ Already up to date")

print("Now restart: python run.py")