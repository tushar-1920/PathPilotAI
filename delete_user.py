import sqlite3

db_path = "./database/pathpilot.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("DELETE FROM users WHERE id = 10")
conn.commit()
print("Deleted rows:", cur.rowcount)
conn.close()