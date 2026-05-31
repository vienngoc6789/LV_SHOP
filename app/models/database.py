import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "lvshop.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        birth_date TEXT,
        gender TEXT,
        role TEXT,
        phone TEXT,
        email TEXT UNIQUE,
        address TEXT,
        username TEXT UNIQUE,
        employee_code TEXT,
        password TEXT
    )
    """)

    # PRODUCTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        brand TEXT,
        description TEXT,
        base_price REAL
    )
    """)

    # STORAGE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    # COLORS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS colors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    # PRODUCT VARIANT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        storage_id INTEGER,
        color_id INTEGER,
        price REAL,
        stock INTEGER,
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(storage_id) REFERENCES storages(id),
        FOREIGN KEY(color_id) REFERENCES colors(id)
    )
    """)

    # CUSTOMERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        address TEXT
    )
    """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS discounts
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       code
                       TEXT
                       UNIQUE,
                       type
                       TEXT,
                       value
                       REAL,
                       min_order
                       REAL,
                       max_discount
                       REAL,
                       start_date
                       TEXT,
                       end_date
                       TEXT,
                       quantity
                       INTEGER,
                       used_count
                       INTEGER
                       DEFAULT
                       0,
                       status
                       TEXT
                   )
                   """)

    # INVOICES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        user_id INTEGER,
        total_price REAL,
        created_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # INVOICE ITEMS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        variant_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY(invoice_id) REFERENCES invoices(id),
        FOREIGN KEY(variant_id) REFERENCES product_variants(id)
    )
    """)

    # WARRANTY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warranties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_item_id INTEGER,
        status TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY(invoice_item_id) REFERENCES invoice_items(id)
    )
    """)

    conn.commit()
    conn.close()