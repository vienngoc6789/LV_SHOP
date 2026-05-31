from app.models.database import get_connection


class InvoiceModel:
    @staticmethod
    def get_all_invoices():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                i.id,
                i.created_at,
                IFNULL(c.name, ''),
                IFNULL(c.phone, ''),
                (
                    SELECT COUNT(*)
                    FROM invoice_items ii
                    WHERE ii.invoice_id = i.id
                ) AS item_count,
                IFNULL(i.subtotal, 0),
                IFNULL(i.discount_amount, 0),
                IFNULL(i.total_price, 0),
                IFNULL(i.payment_method, ''),
                IFNULL(i.status, '')
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.id DESC
        """)

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_invoice_items(invoice_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                imei,
                product_name,
                storage,
                color,
                price
            FROM invoice_items
            WHERE invoice_id = ?
        """, (invoice_id,))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_invoice_detail(invoice_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                i.id,
                i.created_at,
                IFNULL(c.name, ''),
                IFNULL(c.phone, ''),
                IFNULL(u.full_name, 'Không rõ'),
                IFNULL(i.payment_method, ''),
                IFNULL(i.subtotal, 0),
                IFNULL(i.discount_amount, 0),
                IFNULL(i.total_price, 0),
                IFNULL(i.status, '')
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN users u ON i.user_id = u.id
            WHERE i.id = ?
        """, (invoice_id,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def get_summary():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM invoices")
        total_invoices = cursor.fetchone()[0]

        cursor.execute("""
            SELECT IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE DATE(created_at) = DATE('now', 'localtime')
              AND status = 'paid'
        """)
        today_revenue = cursor.fetchone()[0]

        cursor.execute("""
            SELECT IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')
              AND status = 'paid'
        """)
        month_revenue = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM invoices
            WHERE status IN ('cancelled', 'returned')
        """)
        cancelled = cursor.fetchone()[0]

        conn.close()
        return total_invoices, today_revenue, month_revenue, cancelled

    @staticmethod
    def cancel_invoice(invoice_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE invoices
            SET status = 'cancelled'
            WHERE id = ?
        """, (invoice_id,))

        cursor.execute("""
            UPDATE product_imeis
            SET status = 'in_stock',
                sold_at = NULL,
                invoice_item_id = NULL
            WHERE invoice_item_id IN (
                SELECT id FROM invoice_items WHERE invoice_id = ?
            )
        """, (invoice_id,))

        cursor.execute("""
            SELECT DISTINCT variant_id
            FROM invoice_items
            WHERE invoice_id = ?
        """, (invoice_id,))

        variant_ids = [row[0] for row in cursor.fetchall()]

        for variant_id in variant_ids:
            cursor.execute("""
                UPDATE product_variants
                SET stock = (
                    SELECT COUNT(*)
                    FROM product_imeis
                    WHERE variant_id = ?
                      AND status = 'in_stock'
                )
                WHERE id = ?
            """, (variant_id, variant_id))

        conn.commit()
        conn.close()