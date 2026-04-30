import sqlite3

db_path = "./database/pathpilot.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("Starting fix...")

cur.executescript("""
    PRAGMA foreign_keys = OFF;

    CREATE TABLE users_new (
        id INTEGER NOT NULL,
        name VARCHAR(200) NOT NULL,
        email VARCHAR(200) NOT NULL,
        password_hash VARCHAR(255),
        role VARCHAR(50),
        is_verified BOOLEAN,
        normalized_skills TEXT,
        created_at DATETIME,
        subscription_plan VARCHAR(50),
        subscription_status VARCHAR(50),
        subscription_expiry DATETIME,
        stripe_customer_id VARCHAR(255),
        stripe_subscription_id VARCHAR(255),
        billing_cycle VARCHAR(20),
        otp_code TEXT,
        otp_expires_at DATETIME,
        otp_attempts INTEGER DEFAULT 0,
        google_id VARCHAR(200),
        auth_provider VARCHAR(50) DEFAULT 'email',
        PRIMARY KEY (id),
        UNIQUE (email),
        UNIQUE (google_id)
    );

    INSERT INTO users_new SELECT
        id, name, email, password_hash, role, is_verified,
        normalized_skills, created_at, subscription_plan,
        subscription_status, subscription_expiry, stripe_customer_id,
        stripe_subscription_id, billing_cycle, otp_code, otp_expires_at,
        otp_attempts, google_id, auth_provider
    FROM users;

    DROP TABLE users;
    ALTER TABLE users_new RENAME TO users;

    PRAGMA foreign_keys = ON;
""")

conn.commit()
conn.close()
print("✅ Fixed! password_hash is now nullable. Restart Flask now.")