"""
Run this ONCE from your project root to add OTP columns to the existing database.
Usage:  python migrate_otp.py
"""

import sqlite3
import os

# Path to your database — adjust if different
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "pathpilot.db")

def migrate():
    print(f"Connecting to: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    existing = {row[1] for row in cursor.fetchall()}
    print(f"Existing columns: {existing}")

    migrations = [
        ("otp_code",       "ALTER TABLE users ADD COLUMN otp_code TEXT"),
        ("otp_expires_at", "ALTER TABLE users ADD COLUMN otp_expires_at DATETIME"),
        ("otp_attempts",   "ALTER TABLE users ADD COLUMN otp_attempts INTEGER DEFAULT 0"),
    ]

    for col_name, sql in migrations:
        if col_name not in existing:
            print(f"  Adding column: {col_name}")
            cursor.execute(sql)
        else:
            print(f"  Already exists, skipping: {col_name}")

    conn.commit()
    conn.close()
    print("\nMigration complete! You can now run python run.py")

if __name__ == "__main__":
    migrate()