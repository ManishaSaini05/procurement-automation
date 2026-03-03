import sqlite3

conn = sqlite3.connect("procurement.db")
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:")
print(cursor.fetchall())

# Show rfq_master data
cursor.execute("SELECT * FROM rfq_master;")
print("\nrfq_master:")
print(cursor.fetchall())

# Show rfq_vendors data
cursor.execute("SELECT * FROM rfq_vendors;")
print("\nrfq_vendors:")
print(cursor.fetchall())

conn.close()