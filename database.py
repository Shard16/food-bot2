import sqlite3
import os

DB_PATH = os.path.join("data", "orders.db")

def init_db():
    """Create the orders table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        timestamp TEXT,
        items TEXT
    )
    """)
    
    conn.commit()
    conn.close()


def save_order_to_db(user_id, username, timestamp, items):
    """Insert a new order into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
    INSERT INTO orders (user_id, username, timestamp, items)
    VALUES (?, ?, ?, ?)
    """, (user_id, username, timestamp, items))
    
    conn.commit()
    conn.close()

