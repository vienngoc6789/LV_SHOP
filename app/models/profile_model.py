import hashlib
from app.models.database import get_connection


class ProfileModel:
    @staticmethod
    def ensure_schema():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'nhân viên',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        ProfileModel.add_column_if_missing(cursor, "users", "phone", "TEXT")
        ProfileModel.add_column_if_missing(cursor, "users", "email", "TEXT")
        ProfileModel.add_column_if_missing(cursor, "users", "address", "TEXT")
        ProfileModel.add_column_if_missing(cursor, "users", "status", "TEXT DEFAULT 'active'")
        ProfileModel.add_column_if_missing(cursor, "users", "created_at", "TEXT")

        cursor.execute("""
            UPDATE users
            SET status = 'active'
            WHERE status IS NULL OR status = ''
        """)

        cursor.execute("""
            UPDATE users
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL OR created_at = ''
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def add_column_if_missing(cursor, table, column, definition):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def get_first_user_id():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()

        conn.close()
        return row[0] if row else None

    @staticmethod
    def get_user_by_id(user_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                IFNULL(full_name, ''),
                IFNULL(username, ''),
                IFNULL(phone, ''),
                IFNULL(email, ''),
                IFNULL(address, ''),
                IFNULL(role, ''),
                IFNULL(status, 'active'),
                IFNULL(created_at, '')
            FROM users
            WHERE id = ?
        """, (user_id,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def update_profile(user_id, full_name, phone, email, address=""):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT IFNULL(phone, ''), IFNULL(email, ''), IFNULL(role, '')
            FROM users
            WHERE id = ?
        """, (user_id,))
        old_user = cursor.fetchone()
        old_phone = old_user[0] if old_user else ""
        old_email = old_user[1] if old_user else ""
        role = (old_user[2] if old_user else "").lower()

        cursor.execute("""
            UPDATE users
            SET full_name = ?,
                phone = ?,
                email = ?,
                address = ?
            WHERE id = ?
        """, (full_name, phone, email, address, user_id))

        if role in ["customer", "khách hàng", "khach hang"]:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT UNIQUE,
                    email TEXT,
                    address TEXT,
                    customer_group TEXT DEFAULT 'Thuong',
                    note TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("PRAGMA table_info(customers)")
            customer_columns = [row[1] for row in cursor.fetchall()]
            if "customer_group" not in customer_columns:
                cursor.execute("ALTER TABLE customers ADD COLUMN customer_group TEXT DEFAULT 'Thuong'")
            if "note" not in customer_columns:
                cursor.execute("ALTER TABLE customers ADD COLUMN note TEXT")
            if "created_at" not in customer_columns:
                cursor.execute("ALTER TABLE customers ADD COLUMN created_at TEXT")

            cursor.execute("""
                SELECT id
                FROM customers
                WHERE (phone != '' AND phone IN (?, ?))
                   OR (email != '' AND email IN (?, ?))
                LIMIT 1
            """, (old_phone, phone, old_email, email))
            row = cursor.fetchone()

            if row:
                cursor.execute("""
                    UPDATE customers
                    SET name = ?,
                        phone = ?,
                        email = ?,
                        address = ?
                    WHERE id = ?
                """, (full_name, phone, email, address, row[0]))
            else:
                cursor.execute("""
                    INSERT INTO customers(name, phone, email, address, customer_group, note, created_at)
                    VALUES (?, ?, ?, ?, 'Thuong', 'Tai khoan customer tu dang ky', CURRENT_TIMESTAMP)
                """, (full_name, phone, email, address))

        conn.commit()
        conn.close()

    @staticmethod
    def check_password(user_id, old_password):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password
            FROM users
            WHERE id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return False

        saved_password = row[0] or ""
        hashed_old = ProfileModel.hash_password(old_password)

        return saved_password == hashed_old or saved_password == old_password

    @staticmethod
    def change_password(user_id, new_password):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET password = ?
            WHERE id = ?
        """, (ProfileModel.hash_password(new_password), user_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_my_summary(user_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*),
                IFNULL(SUM(total_price), 0),
                IFNULL(AVG(total_price), 0)
            FROM invoices
            WHERE user_id = ?
              AND status = 'paid'
        """, (user_id,))

        total_invoice, total_revenue, aov = cursor.fetchone()

        cursor.execute("""
            SELECT
                COUNT(*),
                IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE user_id = ?
              AND status = 'paid'
              AND DATE(created_at) = DATE('now', 'localtime')
        """, (user_id,))

        today_order, today_revenue = cursor.fetchone()

        cursor.execute("""
            SELECT
                COUNT(*),
                IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE user_id = ?
              AND status = 'paid'
              AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')
        """, (user_id,))

        month_order, month_revenue = cursor.fetchone()

        conn.close()

        return {
            "total_invoice": total_invoice,
            "total_revenue": total_revenue,
            "aov": aov,
            "today_order": today_order,
            "today_revenue": today_revenue,
            "month_order": month_order,
            "month_revenue": month_revenue,
        }

    @staticmethod
    def get_my_recent_invoices(user_id, limit=20):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                i.id,
                i.created_at,
                IFNULL(c.name, ''),
                (
                    SELECT COUNT(*)
                    FROM invoice_items ii
                    WHERE ii.invoice_id = i.id
                ) AS item_count,
                IFNULL(i.total_price, 0),
                IFNULL(i.payment_method, '')
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.user_id = ?
            ORDER BY i.id DESC
            LIMIT ?
        """, (user_id, limit))

        data = cursor.fetchall()
        conn.close()
        return data
