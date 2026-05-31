from app.models.database import get_connection


class DiscountModel:
    @staticmethod
    def ensure_schema():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            type TEXT DEFAULT 'percent',
            value REAL DEFAULT 0,
            max_discount REAL DEFAULT 0,
            min_order REAL DEFAULT 0,
            used_count INTEGER DEFAULT 0,
            usage_limit INTEGER DEFAULT 0,
            per_customer_limit INTEGER DEFAULT 1,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'active',
            revenue_applied REAL DEFAULT 0,
            total_discount_amount REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        DiscountModel.add_column_if_missing(cursor, "type", "TEXT DEFAULT 'percent'")
        DiscountModel.add_column_if_missing(cursor, "value", "REAL DEFAULT 0")
        DiscountModel.add_column_if_missing(cursor, "max_discount", "REAL DEFAULT 0")
        DiscountModel.add_column_if_missing(cursor, "min_order", "REAL DEFAULT 0")
        DiscountModel.add_column_if_missing(cursor, "used_count", "INTEGER DEFAULT 0")
        DiscountModel.add_column_if_missing(cursor, "usage_limit", "INTEGER DEFAULT 0")
        DiscountModel.add_column_if_missing(cursor, "per_customer_limit", "INTEGER DEFAULT 1")
        DiscountModel.add_column_if_missing(cursor, "start_date", "TEXT")
        DiscountModel.add_column_if_missing(cursor, "end_date", "TEXT")
        DiscountModel.add_column_if_missing(cursor, "status", "TEXT DEFAULT 'active'")
        DiscountModel.add_column_if_missing(cursor, "revenue_applied", "REAL DEFAULT 0")
        DiscountModel.add_column_if_missing(cursor, "total_discount_amount", "REAL DEFAULT 0")
        DiscountModel.add_column_if_missing(cursor, "created_at", "TEXT")

        cursor.execute("""
            UPDATE discounts
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL OR created_at = ''
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def add_column_if_missing(cursor, column, definition):
        cursor.execute("PRAGMA table_info(discounts)")
        columns = [row[1] for row in cursor.fetchall()]
        if column not in columns:
            cursor.execute(f"ALTER TABLE discounts ADD COLUMN {column} {definition}")

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                code,
                type,
                value,
                max_discount,
                min_order,
                used_count,
                usage_limit,
                per_customer_limit,
                start_date,
                end_date,
                status,
                revenue_applied
            FROM discounts
            ORDER BY id DESC
        """)

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def add(data):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO discounts (
                code,
                type,
                value,
                max_discount,
                min_order,
                usage_limit,
                per_customer_limit,
                start_date,
                end_date,
                status,
                used_count,
                revenue_applied,
                total_discount_amount,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, CURRENT_TIMESTAMP)
        """, data)

        conn.commit()
        conn.close()

    @staticmethod
    def update(discount_id, data):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE discounts
            SET code = ?,
                type = ?,
                value = ?,
                max_discount = ?,
                min_order = ?,
                usage_limit = ?,
                per_customer_limit = ?,
                start_date = ?,
                end_date = ?,
                status = ?
            WHERE id = ?
        """, (*data, discount_id))

        conn.commit()
        conn.close()

    @staticmethod
    def delete(discount_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM discounts WHERE id = ?", (discount_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def toggle_status(discount_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM discounts WHERE id = ?", (discount_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return

        new_status = "inactive" if row[0] == "active" else "active"

        cursor.execute("""
            UPDATE discounts
            SET status = ?
            WHERE id = ?
        """, (new_status, discount_id))

        conn.commit()
        conn.close()

    @staticmethod
    def duplicate(discount_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                code,
                type,
                value,
                max_discount,
                min_order,
                usage_limit,
                per_customer_limit,
                start_date,
                end_date,
                status
            FROM discounts
            WHERE id = ?
        """, (discount_id,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return

        code, dtype, value, max_discount, min_order, usage_limit, per_customer_limit, start_date, end_date, status = row
        new_code = f"{code}_COPY"

        cursor.execute("""
            INSERT INTO discounts (
                code,
                type,
                value,
                max_discount,
                min_order,
                usage_limit,
                per_customer_limit,
                start_date,
                end_date,
                status,
                used_count,
                revenue_applied,
                total_discount_amount,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, CURRENT_TIMESTAMP)
        """, (
            new_code,
            dtype,
            value,
            max_discount,
            min_order,
            usage_limit,
            per_customer_limit,
            start_date,
            end_date,
            status
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def validate_code(code, order_total):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                code,
                type,
                value,
                max_discount,
                min_order,
                used_count,
                usage_limit,
                per_customer_limit,
                start_date,
                end_date,
                status
            FROM discounts
            WHERE UPPER(code) = UPPER(?)
            LIMIT 1
        """, (code,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, "Mã không tồn tại", 0

        (
            discount_id,
            code,
            dtype,
            value,
            max_discount,
            min_order,
            used_count,
            usage_limit,
            per_customer_limit,
            start_date,
            end_date,
            status
        ) = row

        if status != "active":
            return False, "Mã đang tắt hoặc không hoạt động", 0

        if order_total < float(min_order or 0):
            return False, f"Đơn tối thiểu phải từ {float(min_order):,.0f} đ", 0

        if usage_limit and used_count >= usage_limit:
            return False, "Mã đã hết lượt sử dụng", 0

        if dtype == "percent":
            discount_amount = order_total * float(value or 0) / 100
            if max_discount and max_discount > 0:
                discount_amount = min(discount_amount, float(max_discount))
        else:
            discount_amount = float(value or 0)

        discount_amount = min(discount_amount, order_total)

        return True, "Mã hợp lệ", discount_amount

    @staticmethod
    def record_usage(code, order_total, discount_amount):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE discounts
            SET used_count = IFNULL(used_count, 0) + 1,
                revenue_applied = IFNULL(revenue_applied, 0) + ?,
                total_discount_amount = IFNULL(total_discount_amount, 0) + ?
            WHERE UPPER(code) = UPPER(?)
        """, (order_total, discount_amount, code))

        conn.commit()
        conn.close()

    @staticmethod
    def get_summary():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM discounts")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM discounts WHERE status = 'active'")
        active = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM discounts
            WHERE end_date IS NOT NULL
              AND end_date != ''
              AND DATE(end_date) < DATE('now', 'localtime')
        """)
        expired = cursor.fetchone()[0]

        cursor.execute("SELECT IFNULL(SUM(used_count), 0) FROM discounts")
        used = cursor.fetchone()[0]

        conn.close()
        return total, active, expired, used

    @staticmethod
    def get_usage_stats(limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                code,
                IFNULL(used_count, 0),
                IFNULL(total_discount_amount, 0),
                IFNULL(revenue_applied, 0)
            FROM discounts
            ORDER BY used_count DESC, revenue_applied DESC
            LIMIT ?
        """, (limit,))

        data = cursor.fetchall()
        conn.close()
        return data