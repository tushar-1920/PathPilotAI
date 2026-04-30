"""
Run this file ONCE to add new columns to your existing database.
Usage: python migrate_db.py

This adds:
- profiles.username
- profiles.username_set
- posts.image_url
- certificates.image_url
- New tables: post_comments, messages
"""

import sqlite3
import os

# ── Find your database file ──
# Common locations — adjust if yours is different
DB_PATHS = [
    "instance/pathpilot.db",
    "instance/app.db",
    "instance/database.db",
    "backend/database.db",
    "database.db",
    "app.db",
]

db_path = None
for path in DB_PATHS:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    # Search for any .db file
    for root, dirs, files in os.walk("."):
        for f in files:
            if f.endswith(".db"):
                db_path = os.path.join(root, f)
                break
        if db_path:
            break

if not db_path:
    print("❌ Could not find database file.")
    print("Please set db_path manually, e.g.: db_path = 'instance/myapp.db'")
    exit(1)

print(f"✅ Found database: {db_path}")

conn = sqlite3.connect(db_path)
cur  = conn.cursor()


def column_exists(table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())

def table_exists(table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


migrations = []
# ── users table — Google auth columns ──
if table_exists("users"):
    if not column_exists("users", "google_id"):
        cur.execute("ALTER TABLE users ADD COLUMN google_id VARCHAR(200)")
        migrations.append("users.google_id")

    if not column_exists("users", "auth_provider"):
        cur.execute("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(50) DEFAULT 'email'")
        migrations.append("users.auth_provider")
else:
    print("⚠️  users table does not exist")

# ── profiles table ──
if table_exists("profiles"):
    if not column_exists("profiles", "username"):
        cur.execute("ALTER TABLE profiles ADD COLUMN username VARCHAR(30) UNIQUE")
        migrations.append("profiles.username")

    if not column_exists("profiles", "username_set"):
        cur.execute("ALTER TABLE profiles ADD COLUMN username_set BOOLEAN DEFAULT 0")
        migrations.append("profiles.username_set")
else:
    print("⚠️  profiles table does not exist — run db.create_all() first")

# ── posts table ──
if table_exists("posts"):
    if not column_exists("posts", "image_url"):
        cur.execute("ALTER TABLE posts ADD COLUMN image_url VARCHAR(500)")
        migrations.append("posts.image_url")
else:
    print("⚠️  posts table does not exist — run db.create_all() first")

# ── certificates table ──
if table_exists("certificates"):
    if not column_exists("certificates", "image_url"):
        cur.execute("ALTER TABLE certificates ADD COLUMN image_url VARCHAR(500)")
        migrations.append("certificates.image_url")
else:
    print("⚠️  certificates table does not exist — run db.create_all() first")

# ── post_comments table (new) ──
if not table_exists("post_comments"):
    cur.execute("""
        CREATE TABLE post_comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id    INTEGER NOT NULL REFERENCES posts(id),
            user_id    INTEGER NOT NULL REFERENCES users(id),
            content    TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    migrations.append("post_comments (new table)")

# ── messages table (new) ──
if not table_exists("messages"):
    cur.execute("""
        CREATE TABLE messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id   INTEGER NOT NULL REFERENCES users(id),
            receiver_id INTEGER NOT NULL REFERENCES users(id),
            content     TEXT NOT NULL,
            is_read     BOOLEAN DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    migrations.append("messages (new table)")

conn.commit()
conn.close()

if migrations:
    print("\n✅ Migration complete! Changes made:")
    for m in migrations:
        print(f"   + {m}")
else:
    print("\n✅ All columns already exist — nothing to migrate.")

print("\nRestart your Flask app now: python run.py")