import hashlib
from app.models.database import get_connection


class HumanModel:
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

        HumanModel.add_column_if_missing(cursor, "users", "phone", "TEXT")
        HumanModel.add_column_if_missing(cursor, "users", "email", "TEXT")
        HumanModel.add_column_if_missing(cursor, "users", "status", "TEXT DEFAULT 'active'")
        HumanModel.add_column_if_missing(cursor, "users", "created_at", "TEXT")

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
    def get_all_users():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                u.id,
                IFNULL(u.full_name, ''),
                IFNULL(u.username, ''),
                IFNULL(u.phone, ''),
                IFNULL(u.email, ''),
                IFNULL(u.role, ''),
                IFNULL(u.status, 'active'),
                (
                    SELECT COUNT(*)
                    FROM invoices i
                    WHERE i.user_id = u.id
                      AND i.status = 'paid'
                ) AS order_count,
                IFNULL((
                    SELECT SUM(i.total_price)
                    FROM invoices i
                    WHERE i.user_id = u.id
                      AND i.status = 'paid'
                ), 0) AS revenue,
                IFNULL(u.created_at, '')
            FROM users u
            ORDER BY u.id DESC
        """)

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def add_user(full_name, username, password, phone, email, role, status):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (
                full_name,
                username,
                password,
                phone,
                email,
                role,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            full_name,
            username,
            HumanModel.hash_password(password),
            phone,
            email,
            role,
            status
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def update_user(user_id, full_name, username, phone, email, role, status):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET full_name = ?,
                username = ?,
                phone = ?,
                email = ?,
                role = ?,
                status = ?
            WHERE id = ?
        """, (
            full_name,
            username,
            phone,
            email,
            role,
            status,
            user_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_user(user_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Không tìm thấy nhân sự"

        if str(row[0]).lower() == "admin":
            cursor.execute("SELECT COUNT(*) FROM users WHERE LOWER(role) = 'admin'")
            admin_count = cursor.fetchone()[0]

            if admin_count <= 1:
                conn.close()
                return False, "Không thể xóa admin cuối cùng"

        cursor.execute("SELECT COUNT(*) FROM invoices WHERE user_id = ?", (user_id,))
        invoice_count = cursor.fetchone()[0]

        if invoice_count > 0:
            conn.close()
            return False, "Nhân viên đã có hóa đơn, nên khóa tài khoản thay vì xóa"

        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True, "Đã xóa nhân sự"

    @staticmethod
    def reset_password(user_id, new_password):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET password = ?
            WHERE id = ?
        """, (HumanModel.hash_password(new_password), user_id))

        conn.commit()
        conn.close()

    @staticmethod
    def toggle_status(user_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return

        current_status = row[0] or "active"
        new_status = "inactive" if current_status == "active" else "active"

        cursor.execute("""
            UPDATE users
            SET status = ?
            WHERE id = ?
        """, (new_status, user_id))

        conn.commit()
        conn.close()

    @staticmethod
    def grant_manager(user_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET role = 'quản lý',
                status = 'active'
            WHERE id = ?
        """, (user_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def get_summary(selected_user_id=None):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
        active = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE LOWER(role) IN ('sale', 'nhân viên')
        """)
        sale_users = cursor.fetchone()[0]

        selected_revenue = 0
        if selected_user_id:
            cursor.execute("""
                SELECT IFNULL(SUM(total_price), 0)
                FROM invoices
                WHERE user_id = ?
                  AND status = 'paid'
            """, (selected_user_id,))
            selected_revenue = cursor.fetchone()[0]

        conn.close()
        return total, active, sale_users, selected_revenue

    @staticmethod
    def get_performance(limit=10):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                IFNULL(u.full_name, ''),
                COUNT(i.id) AS order_count,
                IFNULL(SUM(i.total_price), 0) AS revenue,
                IFNULL(AVG(i.total_price), 0) AS aov
            FROM users u
            LEFT JOIN invoices i ON i.user_id = u.id AND i.status = 'paid'
            GROUP BY u.id
            ORDER BY revenue DESC, order_count DESC
            LIMIT ?
        """, (limit,))

        data = cursor.fetchall()
        conn.close()
        return data