import sqlite3
from datetime import datetime, timedelta
from app.models.database import get_connection


class SalesModel:
    @staticmethod
    def ensure_schema():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT UNIQUE,
            email TEXT,
            address TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            user_id INTEGER,
            subtotal REAL DEFAULT 0,
            discount_code TEXT,
            discount_amount REAL DEFAULT 0,
            total_price REAL DEFAULT 0,
            payment_method TEXT,
            paid_amount REAL DEFAULT 0,
            change_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'paid',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            variant_id INTEGER,
            imei_id INTEGER,
            imei TEXT,
            product_name TEXT,
            storage TEXT,
            color TEXT,
            quantity INTEGER DEFAULT 1,
            price REAL DEFAULT 0,
            warranty_month INTEGER DEFAULT 12,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id),
            FOREIGN KEY(variant_id) REFERENCES product_variants(id),
            FOREIGN KEY(imei_id) REFERENCES product_imeis(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS warranties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_item_id INTEGER,
            customer_id INTEGER,
            imei_id INTEGER,
            imei TEXT,
            product_name TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'active',
            note TEXT,
            FOREIGN KEY(invoice_item_id) REFERENCES invoice_items(id),
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(imei_id) REFERENCES product_imeis(id)
        )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def find_customer_by_phone(phone):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, phone, email, address
            FROM customers
            WHERE phone = ?
            LIMIT 1
        """, (phone,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def upsert_customer(name, phone, email, address):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM customers WHERE phone = ?", (phone,))
        row = cursor.fetchone()

        if row:
            customer_id = row[0]
            cursor.execute("""
                UPDATE customers
                SET name = ?, email = ?, address = ?
                WHERE id = ?
            """, (name, email, address, customer_id))
        else:
            cursor.execute("""
                INSERT INTO customers(name, phone, email, address)
                VALUES (?, ?, ?, ?)
            """, (name, phone, email, address))
            customer_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return customer_id

    @staticmethod
    def find_imei_for_sale(imei):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                pi.id,
                pi.imei,
                pv.id,
                p.name,
                p.brand,
                s.name,
                c.name,
                pv.price,
                pi.import_price,
                pi.status
            FROM product_imeis pi
            JOIN product_variants pv ON pi.variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            JOIN storages s ON pv.storage_id = s.id
            JOIN colors c ON pv.color_id = c.id
            WHERE pi.imei = ?
            LIMIT 1
        """, (imei,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def search_available_imeis(keyword=""):
        conn = get_connection()
        cursor = conn.cursor()

        keyword = f"%{keyword}%"

        cursor.execute("""
            SELECT
                pi.id,
                pi.imei,
                p.name,
                s.name || ' / ' || c.name AS variant_text,
                pv.price
            FROM product_imeis pi
            JOIN product_variants pv ON pi.variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            JOIN storages s ON pv.storage_id = s.id
            JOIN colors c ON pv.color_id = c.id
            WHERE pi.status = 'in_stock'
              AND (
                    pi.imei LIKE ?
                    OR p.name LIKE ?
                    OR s.name LIKE ?
                    OR c.name LIKE ?
              )
            ORDER BY p.name ASC
            LIMIT 50
        """, (keyword, keyword, keyword, keyword))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def sync_variant_stock(variant_id, cursor=None):
        close_conn = False

        if cursor is None:
            conn = get_connection()
            cursor = conn.cursor()
            close_conn = True

        cursor.execute("""
            SELECT COUNT(*)
            FROM product_imeis
            WHERE variant_id = ?
              AND status = 'in_stock'
        """, (variant_id,))
        stock = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE product_variants
            SET stock = ?
            WHERE id = ?
        """, (stock, variant_id))

        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def create_invoice(customer_data, cart_items, payment_data, user_id=None):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            name = customer_data["name"]
            phone = customer_data["phone"]
            email = customer_data["email"]
            address = customer_data["address"]

            customer_id = SalesModel.upsert_customer(name, phone, email, address)

            subtotal = payment_data["subtotal"]
            discount_code = payment_data.get("discount_code", "")
            discount_amount = payment_data.get("discount_amount", 0)
            total_price = payment_data["total_price"]
            payment_method = payment_data["payment_method"]
            paid_amount = payment_data.get("paid_amount", 0)
            change_amount = payment_data.get("change_amount", 0)

            cursor.execute("""
                INSERT INTO invoices(
                    customer_id,
                    user_id,
                    subtotal,
                    discount_code,
                    discount_amount,
                    total_price,
                    payment_method,
                    paid_amount,
                    change_amount,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'paid', ?)
            """, (
                customer_id,
                user_id,
                subtotal,
                discount_code,
                discount_amount,
                total_price,
                payment_method,
                paid_amount,
                change_amount,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            invoice_id = cursor.lastrowid

            for item in cart_items:
                cursor.execute("""
                    SELECT status
                    FROM product_imeis
                    WHERE id = ?
                """, (item["imei_id"],))

                row = cursor.fetchone()

                if not row:
                    raise Exception(f"Không tìm thấy IMEI {item['imei']}")

                if row[0] != "in_stock":
                    raise Exception(f"IMEI {item['imei']} không còn trong kho")

                cursor.execute("""
                    INSERT INTO invoice_items(
                        invoice_id,
                        variant_id,
                        imei_id,
                        imei,
                        product_name,
                        storage,
                        color,
                        quantity,
                        price,
                        warranty_month
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """, (
                    invoice_id,
                    item["variant_id"],
                    item["imei_id"],
                    item["imei"],
                    item["product_name"],
                    item["storage"],
                    item["color"],
                    item["price"],
                    item["warranty_month"]
                ))

                invoice_item_id = cursor.lastrowid

                cursor.execute("""
                    UPDATE product_imeis
                    SET status = 'sold',
                        sold_at = ?,
                        invoice_item_id = ?
                    WHERE id = ?
                """, (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    invoice_item_id,
                    item["imei_id"]
                ))

                SalesModel.sync_variant_stock(item["variant_id"], cursor)

                start_date = datetime.now()
                end_date = start_date + timedelta(days=30 * item["warranty_month"])

                cursor.execute("""
                    INSERT INTO warranties(
                        invoice_item_id,
                        customer_id,
                        imei_id,
                        imei,
                        product_name,
                        start_date,
                        end_date,
                        status,
                        note
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
                """, (
                    invoice_item_id,
                    customer_id,
                    item["imei_id"],
                    item["imei"],
                    item["product_name"],
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    "Tự động tạo khi bán hàng"
                ))

            conn.commit()
            conn.close()
            return True, invoice_id, "Tạo hóa đơn thành công"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, None, str(e)

    @staticmethod
    def get_invoice_detail(invoice_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT i.id,
                              i.created_at,
                              c.name,
                              c.phone,
                              c.email,
                              c.address,
                              i.subtotal,
                              i.discount_code,
                              i.discount_amount,
                              i.total_price,
                              i.payment_method,
                              i.paid_amount,
                              i.change_amount,
                              IFNULL(u.full_name, 'Không rõ') AS staff_name
                       FROM invoices i
                                LEFT JOIN customers c ON i.customer_id = c.id
                                LEFT JOIN users u ON i.user_id = u.id
                       WHERE i.id = ?
                       """, (invoice_id,))

        invoice = cursor.fetchone()

        cursor.execute("""
                       SELECT product_name,
                              storage,
                              color,
                              imei,
                              price,
                              warranty_month
                       FROM invoice_items
                       WHERE invoice_id = ?
                       """, (invoice_id,))

        items = cursor.fetchall()

        conn.close()
        return invoice, items

    @staticmethod
    def get_available_products_for_ai():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                pi.id AS imei_id,
                pi.imei,
                pv.id AS variant_id,
                p.name AS product_name,
                p.brand,
                s.name AS storage,
                c.name AS color,
                pv.price,
                pi.import_price,
                pi.status
            FROM product_imeis pi
            JOIN product_variants pv ON pi.variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            JOIN storages s ON pv.storage_id = s.id
            JOIN colors c ON pv.color_id = c.id
            WHERE pi.status = 'in_stock'
            ORDER BY pv.price ASC
            LIMIT 200
        """)

        data = cursor.fetchall()
        conn.close()
        return data

