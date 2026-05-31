import hashlib

from app.models.database import get_connection


class UserModel:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_employee_code():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0] + 1

        conn.close()

        return f"NV{count:03d}"

    @staticmethod
    def generate_customer_code():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users WHERE LOWER(role) IN ('customer', 'khách hàng', 'khach hang')")
        count = cursor.fetchone()[0] + 1

        conn.close()

        return f"KH{count:03d}"

    @staticmethod
    def create_user(data):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users (
            full_name, birth_date, gender, role, phone, email,
            address, username, employee_code, password
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["full_name"],
            data["birth_date"],
            data["gender"],
            data["role"],
            data["phone"],
            data["email"],
            data["address"],
            data["username"],
            data["employee_code"],
            UserModel.hash_password(data["password"])
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def check_login(username_or_email, password):
        conn = get_connection()
        cursor = conn.cursor()

        hashed_password = UserModel.hash_password(password)

        cursor.execute("""
                       SELECT *
                       FROM users
                       WHERE (username = ? OR email = ?)
                         AND (password = ? OR password = ?)
                       """, (username_or_email, username_or_email, password, hashed_password))

        user = cursor.fetchone()
        conn.close()

        return user

    @staticmethod
    def ensure_customer_profile(user):
        if not user or len(user) < 8:
            return None

        user_id = user[0]
        full_name = user[1] or user[8] or f"Khach hang {user_id}"
        phone = user[5] or ""
        email = user[6] or ""
        address = user[7] or ""

        conn = get_connection()
        cursor = conn.cursor()

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

        customer = None

        if phone:
            cursor.execute("SELECT id FROM customers WHERE phone = ? LIMIT 1", (phone,))
            customer = cursor.fetchone()

        if not customer and email:
            cursor.execute("SELECT id FROM customers WHERE email = ? LIMIT 1", (email,))
            customer = cursor.fetchone()

        if customer:
            customer_id = customer[0]
            cursor.execute("""
                UPDATE customers
                SET name = ?,
                    phone = COALESCE(NULLIF(?, ''), phone),
                    email = COALESCE(NULLIF(?, ''), email),
                    address = COALESCE(NULLIF(?, ''), address)
                WHERE id = ?
            """, (full_name, phone, email, address, customer_id))
        else:
            cursor.execute("""
                INSERT INTO customers(name, phone, email, address, customer_group, note, created_at)
                VALUES (?, ?, ?, ?, 'Thuong', 'Tai khoan customer tu dang ky', CURRENT_TIMESTAMP)
            """, (full_name, phone, email, address))
            customer_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return customer_id
