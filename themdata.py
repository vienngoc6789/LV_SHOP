import sqlite3
from datetime import datetime

DB_PATH = "lvshop.db"


PHONES = [
    ("iPhone 11", "Apple", "128GB", "Đen", 6900000, 5200000, "35388810"),
    ("iPhone 11", "Apple", "128GB", "Trắng", 7100000, 5400000, "35388811"),
    ("iPhone 12", "Apple", "128GB", "Tím", 8900000, 6900000, "35678910"),
    ("iPhone 12 Pro", "Apple", "128GB", "Xanh", 10900000, 8500000, "35678911"),
    ("iPhone 13", "Apple", "128GB", "Hồng", 11900000, 9300000, "35712310"),
    ("iPhone 13", "Apple", "256GB", "Xanh", 13500000, 10800000, "35712311"),
    ("iPhone 13 Pro", "Apple", "256GB", "Xám", 16900000, 13800000, "35712312"),
    ("iPhone 13 Pro Max", "Apple", "256GB", "Vàng", 18900000, 15600000, "35712313"),
    ("iPhone 14", "Apple", "128GB", "Tím", 15900000, 12800000, "35845610"),
    ("iPhone 14 Pro", "Apple", "256GB", "Đen", 22500000, 18800000, "35845611"),
    ("iPhone 14 Pro Max", "Apple", "256GB", "Tím", 24900000, 20900000, "35845612"),
    ("iPhone 15", "Apple", "128GB", "Xanh", 18900000, 15600000, "35978910"),
    ("iPhone 15 Plus", "Apple", "128GB", "Hồng", 20900000, 17300000, "35978911"),
    ("iPhone 15 Pro", "Apple", "256GB", "Titan Tự Nhiên", 28500000, 24000000, "35978912"),
    ("iPhone 15 Pro Max", "Apple", "256GB", "Titan Xanh", 31900000, 27000000, "35978913"),
    ("iPhone 16", "Apple", "128GB", "Đen", 22900000, 19000000, "35123410"),
    ("iPhone 16 Pro", "Apple", "256GB", "Titan Trắng", 32900000, 28000000, "35123411"),
    ("iPhone 16 Pro Max", "Apple", "256GB", "Titan Sa Mạc", 38900000, 33500000, "35123412"),

    ("Samsung Galaxy A55 5G", "Samsung", "128GB", "Xanh", 7990000, 6200000, "35245610"),
    ("Samsung Galaxy S22", "Samsung", "128GB", "Đen", 9500000, 7300000, "35245611"),
    ("Samsung Galaxy S23", "Samsung", "256GB", "Kem", 14500000, 11200000, "35245612"),
    ("Samsung Galaxy S23 Ultra", "Samsung", "256GB", "Xanh", 19900000, 16000000, "35245613"),
    ("Samsung Galaxy S24", "Samsung", "256GB", "Tím", 18900000, 15000000, "35245614"),
    ("Samsung Galaxy S24 Ultra", "Samsung", "256GB", "Titan Xám", 28500000, 23800000, "35245615"),
    ("Samsung Galaxy Z Flip5", "Samsung", "256GB", "Tím", 15900000, 12600000, "35245616"),
    ("Samsung Galaxy Z Fold5", "Samsung", "256GB", "Đen", 27900000, 23000000, "35245617"),

    ("Xiaomi Redmi Note 13 Pro", "Xiaomi", "256GB", "Đen", 5900000, 4300000, "35432110"),
    ("Xiaomi 13T Pro", "Xiaomi", "256GB", "Xanh", 10900000, 8200000, "35432111"),
    ("OPPO Reno10 5G", "OPPO", "256GB", "Bạc", 7500000, 5600000, "35565410"),
    ("Vivo V29 5G", "Vivo", "256GB", "Đỏ", 8500000, 6400000, "35698710"),
]


def imei_check_digit(first_14_digits: str) -> str:
    total = 0

    for index, char in enumerate(first_14_digits):
        digit = int(char)

        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit = digit // 10 + digit % 10

        total += digit

    return str((10 - total % 10) % 10)


def make_imei(tac8: str, serial_number: int) -> str:
    serial6 = str(serial_number).zfill(6)
    first14 = f"{tac8}{serial6}"
    return first14 + imei_check_digit(first14)


def get_or_create(cursor, table, name):
    cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(f"INSERT INTO {table}(name) VALUES (?)", (name,))
    return cursor.lastrowid


def get_or_create_product(cursor, name, brand, price):
    cursor.execute(
        """
        SELECT id
        FROM products
        WHERE name = ? AND brand = ?
        LIMIT 1
        """,
        (name, brand)
    )
    row = cursor.fetchone()

    if row:
        product_id = row[0]
        cursor.execute(
            """
            UPDATE products
            SET base_price = ?
            WHERE id = ?
            """,
            (price, product_id)
        )
        return product_id

    cursor.execute(
        """
        INSERT INTO products(name, brand, description, base_price)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            brand,
            f"{name} {brand} - hàng mẫu thêm tự động",
            price
        )
    )
    return cursor.lastrowid


def get_or_create_variant(cursor, product_id, storage_id, color_id, price):
    cursor.execute(
        """
        SELECT id
        FROM product_variants
        WHERE product_id = ?
          AND storage_id = ?
          AND color_id = ?
        LIMIT 1
        """,
        (product_id, storage_id, color_id)
    )
    row = cursor.fetchone()

    if row:
        variant_id = row[0]
        cursor.execute(
            """
            UPDATE product_variants
            SET price = ?
            WHERE id = ?
            """,
            (price, variant_id)
        )
        return variant_id

    cursor.execute(
        """
        INSERT INTO product_variants(product_id, storage_id, color_id, price, stock)
        VALUES (?, ?, ?, ?, 0)
        """,
        (product_id, storage_id, color_id, price)
    )
    return cursor.lastrowid


def sync_variant_stock(cursor, variant_id):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM product_imeis
        WHERE variant_id = ?
          AND status = 'in_stock'
        """,
        (variant_id,)
    )
    stock = cursor.fetchone()[0]

    cursor.execute(
        """
        UPDATE product_variants
        SET stock = ?
        WHERE id = ?
        """,
        (stock, variant_id)
    )


def seed_phones():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inserted = 0
        skipped = 0
        touched_variants = set()

        for index, item in enumerate(PHONES, start=1):
            product_name, brand, storage, color, sale_price, import_price, tac8 = item

            product_id = get_or_create_product(cursor, product_name, brand, sale_price)
            storage_id = get_or_create(cursor, "storages", storage)
            color_id = get_or_create(cursor, "colors", color)
            variant_id = get_or_create_variant(cursor, product_id, storage_id, color_id, sale_price)

            imei = make_imei(tac8, index)

            cursor.execute(
                """
                SELECT id
                FROM product_imeis
                WHERE imei = ?
                LIMIT 1
                """,
                (imei,)
            )

            if cursor.fetchone():
                skipped += 1
                touched_variants.add(variant_id)
                continue

            cursor.execute(
                """
                INSERT INTO product_imeis(
                    variant_id,
                    imei,
                    status,
                    import_price,
                    note,
                    created_at
                )
                VALUES (?, ?, 'in_stock', ?, ?, ?)
                """,
                (
                    variant_id,
                    imei,
                    import_price,
                    "Dữ liệu mẫu điện thoại thật tế - thêm bằng script",
                    now
                )
            )

            inserted += 1
            touched_variants.add(variant_id)

        for variant_id in touched_variants:
            sync_variant_stock(cursor, variant_id)

        conn.commit()

        print("Thêm dữ liệu mẫu hoàn tất.")
        print(f"Đã thêm mới: {inserted} IMEI")
        print(f"Bỏ qua do trùng IMEI: {skipped}")

    except Exception as e:
        conn.rollback()
        print("Lỗi khi thêm dữ liệu:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    seed_phones()