from app.models.database import get_connection


class WarrantyModel:
    @staticmethod
    def ensure_schema():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS warranties (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
        """)

        WarrantyModel.add_column_if_missing(cursor, "warranties", "invoice_item_id", "INTEGER")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "customer_id", "INTEGER")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "imei_id", "INTEGER")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "imei", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "product_name", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "start_date", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "end_date", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "status", "TEXT DEFAULT 'active'")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "note", "TEXT")

        WarrantyModel.add_column_if_missing(cursor, "warranties", "receive_date", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "return_date", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "issue", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "device_condition", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "tech_note", "TEXT")
        WarrantyModel.add_column_if_missing(cursor, "warranties", "created_at", "TEXT")

        cursor.execute("""
            UPDATE warranties
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL OR created_at = ''
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def add_column_if_missing(cursor, table, column, column_type):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")

    @staticmethod
    def search_device_by_imei(imei):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                pi.id AS imei_id,
                pi.imei,
                pi.status AS imei_status,
                ii.id AS invoice_item_id,
                ii.product_name,
                ii.storage,
                ii.color,
                ii.warranty_month,
                i.id AS invoice_id,
                i.created_at AS sold_date,
                c.id AS customer_id,
                IFNULL(c.name, ''),
                IFNULL(c.phone, ''),
                IFNULL(w.end_date, '')
            FROM product_imeis pi
            LEFT JOIN invoice_items ii ON pi.invoice_item_id = ii.id
            LEFT JOIN invoices i ON ii.invoice_id = i.id
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN warranties w ON w.invoice_item_id = ii.id
            WHERE pi.imei = ?
            ORDER BY w.id ASC
            LIMIT 1
        """, (imei,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def get_history(status_filter="Tất cả trạng thái", imei=None):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                w.id,
                IFNULL(w.imei, ''),
                IFNULL(w.product_name, ''),
                IFNULL(c.name, ''),
                IFNULL(w.receive_date, ''),
                IFNULL(w.return_date, ''),
                IFNULL(w.status, ''),
                IFNULL(w.issue, ''),
                IFNULL(w.tech_note, '')
            FROM warranties w
            LEFT JOIN customers c ON w.customer_id = c.id
            WHERE 1 = 1
        """

        params = []

        if status_filter and status_filter != "Tất cả trạng thái":
            query += " AND w.status = ?"
            params.append(status_filter)

        if imei:
            query += " AND w.imei = ?"
            params.append(imei)

        query += " ORDER BY w.id DESC"

        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_warranty_by_id(warranty_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                invoice_item_id,
                customer_id,
                imei_id,
                imei,
                product_name,
                start_date,
                end_date,
                status,
                note,
                receive_date,
                return_date,
                issue,
                device_condition,
                tech_note
            FROM warranties
            WHERE id = ?
        """, (warranty_id,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def create_warranty_claim(data):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO warranties (
                invoice_item_id,
                customer_id,
                imei_id,
                imei,
                product_name,
                start_date,
                end_date,
                status,
                note,
                receive_date,
                return_date,
                issue,
                device_condition,
                tech_note,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data["invoice_item_id"],
            data["customer_id"],
            data["imei_id"],
            data["imei"],
            data["product_name"],
            data["start_date"],
            data["end_date"],
            data["status"],
            data["note"],
            data["receive_date"],
            data["return_date"],
            data["issue"],
            data["device_condition"],
            data["tech_note"],
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def update_warranty_claim(warranty_id, status, receive_date, return_date, issue, device_condition, tech_note):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE warranties
            SET status = ?,
                receive_date = ?,
                return_date = ?,
                issue = ?,
                device_condition = ?,
                tech_note = ?,
                note = ?
            WHERE id = ?
        """, (
            status,
            receive_date,
            return_date,
            issue,
            device_condition,
            tech_note,
            tech_note,
            warranty_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def cancel_warranty(warranty_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE warranties
            SET status = 'cancelled'
            WHERE id = ?
        """, (warranty_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def return_device(warranty_id, return_date):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE warranties
            SET status = 'returned',
                return_date = ?
            WHERE id = ?
        """, (return_date, warranty_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_summary():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM warranties")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM warranties
            WHERE status IN ('pending', 'checking', 'repairing')
        """)
        pending = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM warranties
            WHERE status IN ('done', 'returned')
        """)
        done = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM warranties
            WHERE end_date IS NOT NULL
              AND end_date != ''
              AND DATE(end_date) < DATE('now', 'localtime')
        """)
        expired = cursor.fetchone()[0]

        conn.close()
        return total, pending, done, expired