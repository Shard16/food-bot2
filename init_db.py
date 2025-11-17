import sqlite3, os

db_path = os.path.join("data", "orders.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS orders")

cursor.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    price REAL NOT NULL,
    total REAL NOT NULL,
    timestamp TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("✅ Recreated 'orders' table with item_name, quantity, price, total")
