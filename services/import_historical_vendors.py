import sqlite3
from pathlib import Path
from datetime import datetime

# ---- Path to your database ----
BASE_DIR = Path(__file__).resolve().parent.parent  # parent of 'services'
DB_PATH = BASE_DIR / "procurement.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---- Historical vendor data ----
# Fill in all your past procurement data here
historical_data = [
    {
        "vendor_name": "QWE",
        "email": "QWE@gmail.com",
        "phone": "1234567890",
        "project": "Project X",
        "material": "Module",
        "unit_price": 100,
        "quantity": 1000,
        "delivery_days": 15,
        "payment_terms": "30% advance",
        "received_date": "2025-12-01 10:00:00"
    },
    {
        "vendor_name": "RTY",
        "email": "RTY@gmail.com.com",
        "phone": "9876543210",
        "project": "Project Y",
        "material": "Inverter",
        "unit_price": 200,
        "quantity": 5,
        "delivery_days": 20,
        "payment_terms": "50% advance",
        "received_date": "2025-12-05 11:00:00"
    }
    # Add more historical vendors here
]

# ---- Insert data into database ----
conn = get_connection()
cursor = conn.cursor()

for row in historical_data:
    # Insert vendor
    cursor.execute("""
        INSERT OR IGNORE INTO vendors (vendor_name, email, phone)
        VALUES (?, ?, ?)
    """, (row['vendor_name'], row['email'], row['phone']))
    
    cursor.execute("SELECT id FROM vendors WHERE vendor_name=?", (row['vendor_name'],))
    vendor_id = cursor.fetchone()['id']

    # Insert project
    cursor.execute("INSERT OR IGNORE INTO projects (project_name) VALUES (?)", (row['project'],))
    cursor.execute("SELECT id FROM projects WHERE project_name=?", (row['project'],))
    project_id = cursor.fetchone()['id']

    # Insert material
    cursor.execute("""
        INSERT OR IGNORE INTO materials (project_id, material_name)
        VALUES (?, ?)
    """, (project_id, row['material']))
    cursor.execute("SELECT id FROM materials WHERE project_id=? AND material_name=?", (project_id, row['material']))
    material_id = cursor.fetchone()['id']

    # Insert vendor quote
    cursor.execute("""
        INSERT INTO vendor_quotes
        (material_id, vendor_id, unit_price, quantity, delivery_days, payment_terms, received_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        material_id,
        vendor_id,
        row['unit_price'],
        row['quantity'],
        row['delivery_days'],
        row['payment_terms'],
        row['received_date']
    ))

conn.commit()
conn.close()
print("Historical vendor data imported successfully!")
