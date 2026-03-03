from db import get_connection

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES ('procurement', 'procure123', 'procurement')
    """)

    # PROJECTS
    # PROJECTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_code TEXT UNIQUE,
        project_name TEXT,
        client TEXT,
        location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # MATERIALS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        material_name TEXT,
        specification TEXT,
        boq_quantity REAL,
        status TEXT DEFAULT 'Pending'
    )
    """)

    # VENDORS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT,
        email TEXT,
        phone TEXT
    )
    """)

    # VENDOR QUOTES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendor_quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id INTEGER,
        vendor_id INTEGER,
        unit_price REAL,
        total_price REAL,
        delivery_days INTEGER,
        payment_terms TEXT,
        received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # MATERIAL APPROVALS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS material_approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id INTEGER,
        vendor_id INTEGER,
        approval_token TEXT,
        status TEXT DEFAULT 'Pending',
        approved_at TIMESTAMP,
        remarks TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rfq_master (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        material_name TEXT,
        rfq_date TEXT,
        status TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rfq_vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfq_id INTEGER,
        vendor_name TEXT,
        vendor_email TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
