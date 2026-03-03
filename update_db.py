import sqlite3

conn = sqlite3.connect("procurement.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE rfq_vendors ADD COLUMN thread_id TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE rfq_vendors ADD COLUMN reply_date TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE rfq_vendors ADD COLUMN extracted_unit_price REAL")
except:
    pass

try:
    cursor.execute("ALTER TABLE rfq_vendors ADD COLUMN extracted_delivery_days TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE rfq_vendors ADD COLUMN extracted_payment_terms TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE rfq_vendors ADD COLUMN raw_reply TEXT")
except:
    pass

conn.commit()
conn.close()

print("Columns added successfully (if not already present).")