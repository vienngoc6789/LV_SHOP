from app.models.database import get_connection


class CustomerModel:
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
            customer_group TEXT DEFAULT 'Thường',
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        CustomerModel.add_column_if_missing(cursor, "customers", "customer_group", "TEXT DEFAULT 'Thường'")
        CustomerModel.add_column_if_missing(cursor, "customers", "note", "TEXT")

        # SQLite không cho ADD COLUMN với DEFAULT CURRENT_TIMESTAMP
        CustomerModel.add_column_if_missing(cursor, "customers", "created_at", "TEXT")

        cursor.execute("""
            UPDATE customers
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
    def get_all_customers():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.id,
                IFNULL(c.name, ''),
                IFNULL(c.phone, ''),
                IFNULL(c.email, ''),
                IFNULL(c.address, ''),
                IFNULL(c.customer_group, 'Thường'),
                (
                    SELECT COUNT(*)
                    FROM invoices i
                    WHERE i.customer_id = c.id
                ) AS invoice_count,
                IFNULL((
                    SELECT SUM(i.total_price)
                    FROM invoices i
                    WHERE i.customer_id = c.id
                ), 0) AS total_spent,
                IFNULL(c.created_at, '')
            FROM customers c
            ORDER BY c.id DESC
        """)

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_customer_by_phone(phone):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                IFNULL(name, ''),
                IFNULL(phone, ''),
                IFNULL(email, ''),
                IFNULL(address, ''),
                IFNULL(customer_group, 'Thường'),
                IFNULL(note, ''),
                IFNULL(created_at, '')
            FROM customers
            WHERE phone = ?
            LIMIT 1
        """, (phone,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def add_customer(name, phone, email, address, customer_group, note):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO customers(
                name,
                phone,
                email,
                address,
                customer_group,
                note,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, phone, email, address, customer_group, note))

        conn.commit()
        conn.close()

    @staticmethod
    def update_customer(customer_id, name, phone, email, address, customer_group, note):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE customers
            SET name = ?,
                phone = ?,
                email = ?,
                address = ?,
                customer_group = ?,
                note = ?
            WHERE id = ?
        """, (name, phone, email, address, customer_group, note, customer_id))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_customer(customer_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM invoices WHERE customer_id = ?", (customer_id,))
        invoice_count = cursor.fetchone()[0]

        if invoice_count > 0:
            conn.close()
            return False

        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def mark_vip(customer_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE customers
            SET customer_group = 'VIP'
            WHERE id = ?
        """, (customer_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def get_customer_summary(customer_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_group = 'VIP'")
        vip_customers = cursor.fetchone()[0]

        cursor.execute("""
            SELECT IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE customer_id = ?
        """, (customer_id,))
        selected_spent = cursor.fetchone()[0]

        conn.close()
        return total_customers, vip_customers, selected_spent

    @staticmethod
    def get_customer_invoices(customer_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                created_at,
                total_price,
                payment_method,
                status
            FROM invoices
            WHERE customer_id = ?
            ORDER BY id DESC
        """, (customer_id,))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_customer_bought_imeis(customer_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                ii.imei,
                ii.product_name,
                i.created_at,
                ii.warranty_month || ' tháng',
                IFNULL(w.status, 'active')
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            LEFT JOIN warranties w ON w.invoice_item_id = ii.id
            WHERE i.customer_id = ?
            ORDER BY i.id DESC
        """, (customer_id,))

        data = cursor.fetchall()
        conn.close()
        return data