import sqlite3
import json

DB_PATH = "traces.sqlite3"

def check_traces():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM traces ORDER BY created_at DESC LIMIT 5")
    columns = [description[0] for description in cursor.description]
    for row in cursor.fetchall():
        print(dict(zip(columns, row)))
    conn.close()

if __name__ == "__main__":
    check_traces()
