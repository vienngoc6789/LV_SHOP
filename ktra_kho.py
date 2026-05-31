import sqlite3

DB_PATH = "lvshop.db"


def money(v):
    return f"{float(v):,.0f} đ"


def show_all_imei():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            pi.id,
            pi.imei,
            pi.status,
            pi.import_price,
            pi.created_at,

            p.name,
            p.brand,

            s.name AS storage,
            c.name AS color,

            pv.price
        FROM product_imeis pi
        JOIN product_variants pv ON pi.variant_id = pv.id
        JOIN products p ON pv.product_id = p.id
        JOIN storages s ON pv.storage_id = s.id
        JOIN colors c ON pv.color_id = c.id
        ORDER BY pi.id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    print("=" * 170)
    print(
        f"{'ID':<6}"
        f"{'IMEI':<20}"
        f"{'TRẠNG THÁI':<14}"
        f"{'TÊN MÁY':<30}"
        f"{'HÃNG':<12}"
        f"{'BỘ NHỚ':<10}"
        f"{'MÀU':<18}"
        f"{'GIÁ BÁN':<16}"
        f"{'GIÁ NHẬP':<16}"
        f"{'NGÀY NHẬP'}"
    )
    print("=" * 170)

    for row in rows:
        (
            row_id,
            imei,
            status,
            import_price,
            created_at,
            product_name,
            brand,
            storage,
            color,
            sale_price
        ) = row

        print(
            f"{str(row_id):<6}"
            f"{imei:<20}"
            f"{status:<14}"
            f"{product_name[:28]:<30}"
            f"{brand:<12}"
            f"{storage:<10}"
            f"{color[:16]:<18}"
            f"{money(sale_price):<16}"
            f"{money(import_price):<16}"
            f"{created_at}"
        )

    print("=" * 170)
    print(f"Tổng IMEI: {len(rows)}")


if __name__ == "__main__":
    show_all_imei()