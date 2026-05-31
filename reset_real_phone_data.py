import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "lvshop.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def create_missing_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brand TEXT NOT NULL,
        description TEXT,
        base_price REAL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS colors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        storage_id INTEGER NOT NULL,
        color_id INTEGER NOT NULL,
        price REAL DEFAULT 0,
        stock INTEGER DEFAULT 0,
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(storage_id) REFERENCES storages(id),
        FOREIGN KEY(color_id) REFERENCES colors(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_imeis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        variant_id INTEGER NOT NULL,
        imei TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'in_stock',
        import_price REAL DEFAULT 0,
        note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        sold_at TEXT,
        invoice_item_id INTEGER,
        FOREIGN KEY(variant_id) REFERENCES product_variants(id)
    )
    """)


def reset_products(cursor):
    cursor.execute("PRAGMA foreign_keys = OFF")

    for table in [
        "product_imeis",
        "product_variants",
        "products",
        "storages",
        "colors",
    ]:
        cursor.execute(f"DELETE FROM {table}")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))

    cursor.execute("PRAGMA foreign_keys = ON")


def insert_lookup(cursor, table, values):
    mapping = {}
    for value in values:
        cursor.execute(f"INSERT INTO {table}(name) VALUES (?)", (value,))
        mapping[value] = cursor.lastrowid
    return mapping


def make_imei(prefix_9_digits, number):
    return f"{prefix_9_digits}{number:06d}"


def sync_stock(cursor, variant_id):
    cursor.execute("""
        SELECT COUNT(*)
        FROM product_imeis
        WHERE variant_id = ? AND status = 'in_stock'
    """, (variant_id,))
    stock = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE product_variants
        SET stock = ?
        WHERE id = ?
    """, (stock, variant_id))


def seed_real_phone_data():
    conn = connect_db()
    cursor = conn.cursor()

    create_missing_tables(cursor)
    reset_products(cursor)

    storages = ["64GB", "128GB", "256GB", "512GB", "1TB"]

    colors = [
        "Đen", "Trắng", "Xanh", "Vàng", "Hồng", "Tím",
        "Titan Tự Nhiên", "Titan Xanh", "Titan Đen", "Titan Trắng",
        "Graphite", "Cream", "Mint", "Lavender"
    ]

    storage_map = insert_lookup(cursor, "storages", storages)
    color_map = insert_lookup(cursor, "colors", colors)

    products = [
        ("iPhone 15 Pro Max", "Apple", "Flagship Apple chip A17 Pro, khung titan, camera cao cấp", 29990000),
        ("iPhone 15 Pro", "Apple", "iPhone Pro nhỏ gọn, hiệu năng mạnh, khung titan", 25990000),
        ("iPhone 15", "Apple", "iPhone thế hệ 15, Dynamic Island, camera 48MP", 19990000),
        ("iPhone 14", "Apple", "iPhone thế hệ 14, hiệu năng ổn định", 16990000),

        ("Samsung Galaxy S24 Ultra", "Samsung", "Flagship Samsung có S Pen, camera zoom xa", 27990000),
        ("Samsung Galaxy S24 Plus", "Samsung", "Galaxy S24 Plus màn lớn, pin tốt", 22990000),
        ("Samsung Galaxy Z Flip5", "Samsung", "Điện thoại gập thời trang, màn hình phụ lớn", 18990000),
        ("Samsung Galaxy A55", "Samsung", "Điện thoại tầm trung Samsung, thiết kế đẹp", 9990000),

        ("Xiaomi 14", "Xiaomi", "Flagship Xiaomi dùng Snapdragon cao cấp", 17990000),
        ("Xiaomi Redmi Note 13 Pro", "Xiaomi", "Máy tầm trung Xiaomi, camera độ phân giải cao", 7990000),

        ("OPPO Reno11 F", "OPPO", "OPPO Reno mỏng nhẹ, camera chân dung đẹp", 8990000),
        ("OPPO Find N3 Flip", "OPPO", "Điện thoại gập cao cấp của OPPO", 19990000),

        ("vivo V30", "vivo", "vivo V30 thiết kế mỏng, camera selfie đẹp", 11990000),
        ("realme 12 Pro Plus", "realme", "realme 12 Pro Plus camera zoom, hiệu năng tốt", 10990000),
    ]

    product_map = {}

    for name, brand, description, base_price in products:
        cursor.execute("""
            INSERT INTO products(name, brand, description, base_price)
            VALUES (?, ?, ?, ?)
        """, (name, brand, description, base_price))
        product_map[name] = cursor.lastrowid

    variants = [
        # product, storage, color, sell_price, import_price, imei_count, 9-digit IMEI prefix
        ("iPhone 15 Pro Max", "256GB", "Titan Tự Nhiên", 29990000, 25490000, 5, "356789150"),
        ("iPhone 15 Pro Max", "256GB", "Titan Xanh", 29990000, 25490000, 4, "356789151"),
        ("iPhone 15 Pro Max", "512GB", "Titan Đen", 34990000, 29990000, 3, "356789152"),

        ("iPhone 15 Pro", "128GB", "Titan Tự Nhiên", 25990000, 21990000, 5, "356789153"),
        ("iPhone 15 Pro", "256GB", "Titan Xanh", 28990000, 24990000, 4, "356789154"),

        ("iPhone 15", "128GB", "Đen", 19990000, 16990000, 6, "356789155"),
        ("iPhone 15", "128GB", "Xanh", 19990000, 16990000, 4, "356789156"),
        ("iPhone 15", "256GB", "Hồng", 22990000, 19490000, 3, "356789157"),

        ("iPhone 14", "128GB", "Trắng", 16990000, 13990000, 5, "356789158"),
        ("iPhone 14", "256GB", "Đen", 19990000, 16490000, 3, "356789159"),

        ("Samsung Galaxy S24 Ultra", "256GB", "Titan Đen", 27990000, 23490000, 5, "357890240"),
        ("Samsung Galaxy S24 Ultra", "512GB", "Titan Xanh", 31990000, 26990000, 3, "357890241"),
        ("Samsung Galaxy S24 Plus", "256GB", "Xanh", 22990000, 18990000, 4, "357890242"),
        ("Samsung Galaxy Z Flip5", "256GB", "Tím", 18990000, 15490000, 3, "357890243"),
        ("Samsung Galaxy A55", "128GB", "Đen", 9990000, 7990000, 7, "357890244"),

        ("Xiaomi 14", "256GB", "Đen", 17990000, 14490000, 5, "358901140"),
        ("Xiaomi 14", "512GB", "Trắng", 20990000, 16990000, 3, "358901141"),
        ("Xiaomi Redmi Note 13 Pro", "128GB", "Đen", 7990000, 6190000, 8, "358901142"),
        ("Xiaomi Redmi Note 13 Pro", "256GB", "Xanh", 8990000, 6990000, 6, "358901143"),

        ("OPPO Reno11 F", "256GB", "Xanh", 8990000, 6990000, 6, "359012110"),
        ("OPPO Reno11 F", "256GB", "Hồng", 8990000, 6990000, 4, "359012111"),
        ("OPPO Find N3 Flip", "256GB", "Vàng", 19990000, 15990000, 3, "359012112"),

        ("vivo V30", "256GB", "Xanh", 11990000, 9490000, 5, "359123300"),
        ("vivo V30", "512GB", "Trắng", 13990000, 10990000, 3, "359123301"),

        ("realme 12 Pro Plus", "256GB", "Xanh", 10990000, 8490000, 5, "359234120"),
    ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for product_name, storage, color, sell_price, import_price, imei_count, imei_prefix in variants:
        product_id = product_map[product_name]
        storage_id = storage_map[storage]
        color_id = color_map[color]

        cursor.execute("""
            INSERT INTO product_variants(product_id, storage_id, color_id, price, stock)
            VALUES (?, ?, ?, ?, 0)
        """, (product_id, storage_id, color_id, sell_price))

        variant_id = cursor.lastrowid

        for i in range(1, imei_count + 1):
            imei = make_imei(imei_prefix, i)

            cursor.execute("""
                INSERT INTO product_imeis(
                    variant_id,
                    imei,
                    status,
                    import_price,
                    note,
                    created_at
                )
                VALUES (?, ?, 'in_stock', ?, ?, ?)
            """, (
                variant_id,
                imei,
                import_price,
                "Dữ liệu điện thoại thật theo hãng, nhập kho mẫu",
                now
            ))

        sync_stock(cursor, variant_id)

    conn.commit()
    conn.close()

    print("✅ Đã reset dữ liệu sản phẩm.")
    print("✅ Mỗi stock tương ứng đúng 1 IMEI.")
    print("✅ Nếu biến thể có stock 5 thì chắc chắn có 5 IMEI.")


if __name__ == "__main__":
    seed_real_phone_data()