import sqlite3

conn = sqlite3.connect("lvshop.db")
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

plantuml_lines = ["@startuml", "!theme plain"]

# Process each table
for (table,) in tables:
    plantuml_lines.append(f'entity "{table}" {{')
    cols = cursor.execute(f"PRAGMA table_info({table})").fetchall()
    for cid, name, ctype, notnull, dflt, pk in cols:
        pk_flag = " <<PK>>" if pk else ""
        plantuml_lines.append(f"  {name} : {ctype}{pk_flag}")
    plantuml_lines.append("}")

# Process relationships (foreign keys)
for (table,) in tables:
    fks = cursor.execute(f"PRAGMA foreign_key_list({table})").fetchall()
    for fk in fks:
        id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
        plantuml_lines.append(
            f'"{table}"::"{from_col}" --> "{ref_table}"::"{to_col}"'
        )

plantuml_lines.append("@enduml")

conn.close()

# Save to file
with open("lvshop_erd.txt", "w") as f:
    f.write("\n".join(plantuml_lines))

print("PlantUML ERD code generated: lvshop_erd.txt")