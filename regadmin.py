import sqlite3

conn = sqlite3.connect("lvshop.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO users (
    full_name,
    birth_date,
    gender,
    role,
    phone,
    email,
    address,
    username,
    employee_code,
    password
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "Admin LV SHOP",
    "2000-01-01",
    "Nam",
    "Admin",
    "0123456789",
    "admin@gmail.com",
    "Hà Nội",
    "admin",
    "EMP000",
    "Admin123"
))

conn.commit()
conn.close()