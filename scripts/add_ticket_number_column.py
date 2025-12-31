
# scripts/add_ticket_number_column.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "app.db"

def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())

def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DB not found: {DB_PATH}. Start the app once or run scripts/init_db.py"
        )
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            if not column_exists(conn, "computers", "ticket_number"):
                conn.execute("ALTER TABLE computers ADD COLUMN ticket_number TEXT")
                print("Added ticket_number column to computers.")
            else:
                print("ticket_number column already exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
