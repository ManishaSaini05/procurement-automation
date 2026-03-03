import sqlite3
from pathlib import Path

# ---- Path to your database ----
DB_PATH = Path(r"C:\Users\Manisha\Desktop\ProcurementSystem\procurement.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ---- Check if 'quantity' column exists ----
cursor.execute("PRAGMA table_info(vendor_quotes)")
columns = [col[1] for col in cursor.fetchall()]  # col[1] is column name

if "quantity" not in columns:
    cursor.execute("""
        ALTER TABLE vendor_quotes
        ADD COLUMN quantity REAL DEFAULT 0
    """)
    conn.commit()
    print("✅ 'quantity' column added successfully to vendor_quotes!")
else:
    print("ℹ️ 'quantity' column already exists, no changes made.")

conn.close()
