import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "lvshop.db"


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return column_name in [row[1] for row in cursor.fetchall()]


def add_column_if_missing(cursor, table_name, column_name, column_type):
    if not column_exists(cursor, table_name, column_name):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"✅ Added {table_name}.{column_name}")
    else:
        print(f"⏭ Exists {table_name}.{column_name}")


def fix_warranties_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warranties (
        id INTEGER PRIMARY KEY AUTOINCREMENT
    )
    """)

    add_column_if_missing(cursor, "warranties", "invoice_item_id", "INTEGER")
    add_column_if_missing(cursor, "warranties", "customer_id", "INTEGER")
    add_column_if_missing(cursor, "warranties", "imei_id", "INTEGER")
    add_column_if_missing(cursor, "warranties", "imei", "TEXT")
    add_column_if_missing(cursor, "warranties", "product_name", "TEXT")
    add_column_if_missing(cursor, "warranties", "start_date", "TEXT")
    add_column_if_missing(cursor, "warranties", "end_date", "TEXT")
    add_column_if_missing(cursor, "warranties", "status", "TEXT DEFAULT 'active'")
    add_column_if_missing(cursor, "warranties", "note", "TEXT")

    conn.commit()
    conn.close()

    print("✅ Đã fix xong bảng warranties")


if __name__ == "__main__":
    fix_warranties_table()