
# scripts/add_is_manager_column.py
"""
Add a boolean-like column `is_manager` (0/1) to `computers` in app.db.
- Creates the column if it doesn't exist.
- Initializes all rows to 0.
- Optionally backfills: set is_manager=1 where manager_staff_id IS NOT NULL.

Run:
  python scripts/add_is_manager_column.py
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "app.db"

def column_exists(conn, table: str, column: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]  # row[1] = name
    return column in cols

def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"SQLite file not found: {DB_PATH}\n"
                                "Make sure you've run scripts/init_db.py or started the app once.")

    print(f"Opening DB: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:  # transaction
            # 1) Create column if missing
            if not column_exists(conn, "computers", "is_manager"):
                print("Adding column `is_manager` to `computers` ...")
                conn.execute("ALTER TABLE computers ADD COLUMN is_manager INTEGER NOT NULL DEFAULT 0")
            else:
                print("Column `is_manager` already exists; skipping ADD.")

            # 2) Normalize NULLs (defensive): set any NULL to 0
            print("Ensuring all rows have a 0/1 value in `is_manager` ...")
            conn.execute("UPDATE computers SET is_manager = COALESCE(is_manager, 0)")

            # 3) Optional backfill from legacy manager_staff_id
            print("Backfilling: set is_manager = 1 where manager_staff_id IS NOT NULL ...")
            conn.execute("UPDATE computers SET is_manager = 1 WHERE manager_staff_id IS NOT NULL")

        print("Done. `is_manager` column is present and initialized.")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
