import sqlite3

DB_PATH = "lvshop.db"   # đổi thành đường dẫn file db của bạn
OUTPUT_FILE = "erd.mmd"


def get_tables(conn):
    sql = """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
    """
    return [row[0] for row in conn.execute(sql)]


def get_columns(conn, table):
    return conn.execute(f"PRAGMA table_info('{table}')").fetchall()


def get_foreign_keys(conn, table):
    return conn.execute(f"PRAGMA foreign_key_list('{table}')").fetchall()


def get_unique_columns(conn, table):
    unique_cols = set()

    indexes = conn.execute(f"PRAGMA index_list('{table}')").fetchall()
    for index in indexes:
        index_name = index[1]
        is_unique = index[2]

        if is_unique:
            cols = conn.execute(f"PRAGMA index_info('{index_name}')").fetchall()
            for col in cols:
                unique_cols.add(col[2])

    return unique_cols


def sqlite_type_to_mermaid(sqlite_type):
    if not sqlite_type:
        return "TEXT"

    t = sqlite_type.upper()

    if "INT" in t:
        return "int"
    if "REAL" in t or "FLOA" in t or "DOUB" in t:
        return "float"
    if "TEXT" in t or "CHAR" in t or "CLOB" in t:
        return "string"
    if "BLOB" in t:
        return "blob"

    return t.lower()


def generate_mermaid_erd(db_path):
    conn = sqlite3.connect(db_path)

    tables = get_tables(conn)

    lines = ["erDiagram"]

    # Sinh entity + field
    for table in tables:
        columns = get_columns(conn, table)
        unique_cols = get_unique_columns(conn, table)

        lines.append(f"  {table} {{")

        for col in columns:
            cid, name, col_type, notnull, default_value, pk = col

            data_type = sqlite_type_to_mermaid(col_type)
            constraints = []

            if pk:
                constraints.append("PK")
            if name in unique_cols:
                constraints.append("UK")
            if notnull:
                constraints.append("NOT_NULL")

            constraint_text = " ".join(constraints)

            if constraint_text:
                lines.append(f"    {data_type} {name} \"{constraint_text}\"")
            else:
                lines.append(f"    {data_type} {name}")

        lines.append("  }")

    # Sinh relationship từ FK
    for table in tables:
        foreign_keys = get_foreign_keys(conn, table)

        for fk in foreign_keys:
            # fk format:
            # id, seq, ref_table, from_col, to_col, on_update, on_delete, match
            _, _, ref_table, from_col, to_col, *_ = fk

            lines.append(
                f"  {ref_table} ||--o{{ {table} : \"{to_col} to {from_col}\""
            )

    conn.close()

    return "\n".join(lines)


if __name__ == "__main__":
    erd_code = generate_mermaid_erd(DB_PATH)

    print(erd_code)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(erd_code)

    print(f"\nĐã xuất ERD ra file: {OUTPUT_FILE}")