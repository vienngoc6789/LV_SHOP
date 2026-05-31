from app.models.database import get_connection


class ReportModel:
    @staticmethod
    def get_kpi(date_from, date_to):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*),
                IFNULL(SUM(total_price), 0),
                IFNULL(AVG(total_price), 0)
            FROM invoices
            WHERE status = 'paid'
              AND DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        """, (date_from, date_to))
        order_count, revenue, aov = cursor.fetchone()

        cursor.execute("""
            SELECT IFNULL(SUM(ii.price - IFNULL(pi.import_price, 0)), 0)
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            LEFT JOIN product_imeis pi ON pi.imei = ii.imei
            WHERE i.status = 'paid'
              AND DATE(i.created_at) BETWEEN DATE(?) AND DATE(?)
        """, (date_from, date_to))
        profit = cursor.fetchone()[0]

        conn.close()
        return order_count, revenue, profit, aov

    @staticmethod
    def get_revenue_grouped(date_from, date_to, group_type):
        conn = get_connection()
        cursor = conn.cursor()

        group_type = (group_type or "Theo ngày").strip()

        if group_type == "Theo tháng":
            group_sql = "strftime('%Y-%m', created_at)"
        elif group_type == "Theo năm":
            group_sql = "strftime('%Y', created_at)"
        else:
            group_sql = "DATE(created_at)"

        cursor.execute(f"""
            SELECT
                {group_sql} AS label,
                IFNULL(SUM(total_price), 0)
            FROM invoices
            WHERE status = 'paid'
              AND DATE(created_at) BETWEEN DATE(?) AND DATE(?)
            GROUP BY label
            ORDER BY label
        """, (date_from, date_to))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_top_brands(date_from, date_to, limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT CASE
                                  WHEN LOWER(ii.product_name) LIKE '%iphone%' OR LOWER(ii.product_name) LIKE '%apple%'
                                      THEN 'Apple'
                                  WHEN LOWER(ii.product_name) LIKE '%samsung%' THEN 'Samsung'
                                  WHEN LOWER(ii.product_name) LIKE '%xiaomi%' THEN 'Xiaomi'
                                  WHEN LOWER(ii.product_name) LIKE '%redmi%' THEN 'Xiaomi'
                                  WHEN LOWER(ii.product_name) LIKE '%oppo%' THEN 'OPPO'
                                  WHEN LOWER(ii.product_name) LIKE '%vivo%' THEN 'Vivo'
                                  WHEN LOWER(ii.product_name) LIKE '%realme%' THEN 'Realme'
                                  WHEN LOWER(ii.product_name) LIKE '%honor%' THEN 'Honor'
                                  WHEN LOWER(ii.product_name) LIKE '%huawei%' THEN 'Huawei'
                                  WHEN LOWER(ii.product_name) LIKE '%nokia%' THEN 'Nokia'
                                  ELSE 'Khác'
                                  END                  AS brand,
                              COUNT(*)                 AS qty,
                              IFNULL(SUM(ii.price), 0) AS revenue
                       FROM invoice_items ii
                                JOIN invoices i ON ii.invoice_id = i.id
                       WHERE i.status = 'paid'
                         AND DATE (i.created_at) BETWEEN DATE (?)
                         AND DATE (?)
                       GROUP BY brand
                       ORDER BY qty DESC, revenue DESC
                           LIMIT ?
                       """, (date_from, date_to, limit))

        data = cursor.fetchall()
        conn.close()
        return data
    @staticmethod
    def get_top_products(date_from, date_to, limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                ii.product_name,
                COUNT(*) AS qty,
                IFNULL(SUM(ii.price), 0) AS revenue
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.status = 'paid'
              AND DATE(i.created_at) BETWEEN DATE(?) AND DATE(?)
            GROUP BY ii.product_name
            ORDER BY qty DESC, revenue DESC
            LIMIT ?
        """, (date_from, date_to, limit))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_top_customers(date_from, date_to, limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                IFNULL(c.name, 'Khách lẻ') AS customer_name,
                COUNT(i.id) AS order_count,
                IFNULL(SUM(i.total_price), 0) AS total_spent
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.status = 'paid'
              AND DATE(i.created_at) BETWEEN DATE(?) AND DATE(?)
            GROUP BY i.customer_id
            ORDER BY total_spent DESC
            LIMIT ?
        """, (date_from, date_to, limit))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_top_discounts(limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                code,
                IFNULL(used_count, 0),
                IFNULL(total_discount_amount, 0)
            FROM discounts
            ORDER BY used_count DESC, total_discount_amount DESC
            LIMIT ?
        """, (limit,))

        data = cursor.fetchall()
        conn.close()
        return data