from app.models.database import get_connection


class ProductModel:
    @staticmethod
    def get_all_products():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT pv.id,
                              p.name,
                              p.brand,
                              s.name,
                              c.name,
                              pv.price,
                              IFNULL((SELECT AVG(pi.import_price)
                                      FROM product_imeis pi
                                      WHERE pi.variant_id = pv.id), 0)  AS avg_import_price,
                              (SELECT COUNT(*)
                               FROM product_imeis pi
                               WHERE pi.variant_id = pv.id
                                 AND pi.status = 'in_stock')            AS imei_stock,
                              IFNULL(p.description, ''),
                              IFNULL((SELECT GROUP_CONCAT(pi.imei, ' ')
                                      FROM product_imeis pi
                                      WHERE pi.variant_id = pv.id), '') AS imei_search_text
                       FROM product_variants pv
                                JOIN products p ON pv.product_id = p.id
                                JOIN storages s ON pv.storage_id = s.id
                                JOIN colors c ON pv.color_id = c.id
                       ORDER BY p.name ASC, s.name ASC, c.name ASC
                       """)

        data = cursor.fetchall()
        conn.close()
        return data
    @staticmethod
    def get_product_names():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT name
            FROM products
            ORDER BY name ASC
        """)

        data = [row[0] for row in cursor.fetchall()]
        conn.close()
        return data

    @staticmethod
    def get_product_info_by_name(name):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT brand, description, base_price
            FROM products
            WHERE LOWER(name) = LOWER(?)
            LIMIT 1
        """, (name,))

        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def get_low_stock(limit=3):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                pv.id,
                p.name,
                s.name,
                c.name,
                (
                    SELECT COUNT(*)
                    FROM product_imeis pi
                    WHERE pi.variant_id = pv.id
                      AND pi.status = 'in_stock'
                ) AS imei_stock
            FROM product_variants pv
            JOIN products p ON pv.product_id = p.id
            JOIN storages s ON pv.storage_id = s.id
            JOIN colors c ON pv.color_id = c.id
            WHERE imei_stock <= ?
            ORDER BY imei_stock ASC
        """, (limit,))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_or_create_product(name, brand, description, base_price):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM products
            WHERE LOWER(name) = LOWER(?) AND LOWER(brand) = LOWER(?)
        """, (name, brand))

        row = cursor.fetchone()

        if row:
            product_id = row[0]
            cursor.execute("""
                UPDATE products
                SET description = ?, base_price = ?
                WHERE id = ?
            """, (description, base_price, product_id))
        else:
            cursor.execute("""
                INSERT INTO products(name, brand, description, base_price)
                VALUES (?, ?, ?, ?)
            """, (name, brand, description, base_price))
            product_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def get_or_create_storage(name):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM storages
            WHERE LOWER(name) = LOWER(?)
        """, (name,))

        row = cursor.fetchone()

        if row:
            storage_id = row[0]
        else:
            cursor.execute("INSERT INTO storages(name) VALUES (?)", (name,))
            storage_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return storage_id

    @staticmethod
    def get_or_create_color(name):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM colors
            WHERE LOWER(name) = LOWER(?)
        """, (name,))

        row = cursor.fetchone()

        if row:
            color_id = row[0]
        else:
            cursor.execute("INSERT INTO colors(name) VALUES (?)", (name,))
            color_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return color_id

    @staticmethod
    def upsert_variant(name, brand, storage, color, price, description):
        product_id = ProductModel.get_or_create_product(name, brand, description, price)
        storage_id = ProductModel.get_or_create_storage(storage)
        color_id = ProductModel.get_or_create_color(color)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM product_variants
            WHERE product_id = ? AND storage_id = ? AND color_id = ?
        """, (product_id, storage_id, color_id))

        row = cursor.fetchone()

        if row:
            variant_id = row[0]
            cursor.execute("""
                UPDATE product_variants
                SET price = ?
                WHERE id = ?
            """, (price, variant_id))
            action = "updated"
        else:
            cursor.execute("""
                INSERT INTO product_variants(product_id, storage_id, color_id, price, stock)
                VALUES (?, ?, ?, ?, 0)
            """, (product_id, storage_id, color_id, price))
            variant_id = cursor.lastrowid
            action = "created"

        conn.commit()
        conn.close()

        return action, variant_id

    @staticmethod
    def update_full_variant(variant_id, name, brand, storage, color, price, description):
        product_id = ProductModel.get_or_create_product(name, brand, description, price)
        storage_id = ProductModel.get_or_create_storage(storage)
        color_id = ProductModel.get_or_create_color(color)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE product_variants
            SET product_id = ?, storage_id = ?, color_id = ?, price = ?
            WHERE id = ?
        """, (product_id, storage_id, color_id, price, variant_id))

        conn.commit()
        conn.close()

    @staticmethod
    def sync_variant_stock(variant_id):
        conn = get_connection()
        cursor = conn.cursor()

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

        conn.commit()
        conn.close()

    @staticmethod
    def delete_variant(variant_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM invoice_items
            WHERE variant_id = ?
        """, (variant_id,))
        used_invoice = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM product_imeis
            WHERE variant_id = ?
        """, (variant_id,))
        imei_count = cursor.fetchone()[0]

        if used_invoice > 0 or imei_count > 0:
            conn.close()
            return False

        cursor.execute("DELETE FROM product_variants WHERE id = ?", (variant_id,))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_imeis_by_variant(variant_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, imei, status, import_price, created_at
            FROM product_imeis
            WHERE variant_id = ?
            ORDER BY id DESC
        """, (variant_id,))

        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def add_imei(variant_id, imei, import_price=0, note=""):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO product_imeis(variant_id, imei, status, import_price, note)
                VALUES (?, ?, 'in_stock', ?, ?)
            """, (variant_id, imei, import_price, note))

            conn.commit()
            conn.close()

            ProductModel.sync_variant_stock(variant_id)
            return True, "Đã thêm IMEI"

        except Exception as e:
            conn.close()
            return False, str(e)

    @staticmethod
    def add_imeis_bulk(variant_id, imeis, import_price=0):
        success = 0
        errors = []

        for imei in imeis:
            ok, msg = ProductModel.add_imei(variant_id, imei, import_price)
            if ok:
                success += 1
            else:
                errors.append(f"{imei}: {msg}")

        ProductModel.sync_variant_stock(variant_id)
        return success, errors

    @staticmethod
    def update_imei_status(imei_id, status):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT variant_id FROM product_imeis WHERE id = ?", (imei_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False

        variant_id = row[0]

        cursor.execute("""
            UPDATE product_imeis
            SET status = ?
            WHERE id = ?
        """, (status, imei_id))

        conn.commit()
        conn.close()

        ProductModel.sync_variant_stock(variant_id)
        return True

    @staticmethod
    def delete_imei(imei_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT variant_id, status
            FROM product_imeis
            WHERE id = ?
        """, (imei_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Không tìm thấy IMEI"

        variant_id, status = row

        if status == "sold":
            conn.close()
            return False, "IMEI đã bán không thể xóa"

        cursor.execute("DELETE FROM product_imeis WHERE id = ?", (imei_id,))

        conn.commit()
        conn.close()

        ProductModel.sync_variant_stock(variant_id)
        return True, "Đã xóa IMEI"