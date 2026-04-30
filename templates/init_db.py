import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS data(
id INTEGER PRIMARY KEY AUTOINCREMENT,
age INTEGER,
salaire REAL,
ecole TEXT,
android TEXT
)
""")

conn.commit()
conn.close()