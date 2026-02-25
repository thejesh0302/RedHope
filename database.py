import sqlite3

def create_connection():
    conn = sqlite3.connect("redhope.db")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        phone TEXT,
        city TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # DONOR DETAILS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donor_details (
        donor_id INTEGER PRIMARY KEY,
        blood_group TEXT NOT NULL,
        age INTEGER,
        weight REAL,
        last_donation_date TEXT,
        availability_status TEXT DEFAULT 'Available',
        medical_conditions TEXT,
        hemoglobin_level REAL,
        FOREIGN KEY (donor_id) REFERENCES users(id)
    )
    """)

    # PATIENT REQUESTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        blood_group_needed TEXT NOT NULL,
        units_required INTEGER,
        hospital_name TEXT,
        city TEXT,
        urgency_level TEXT,
        request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    # BLOOD MATCH TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blood_requests (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER,
        donor_id INTEGER,
        match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        match_status TEXT DEFAULT 'Pending',
        FOREIGN KEY (request_id) REFERENCES patient_requests(request_id),
        FOREIGN KEY (donor_id) REFERENCES users(id)
    )
    """)

    # DONATION HISTORY TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donation_history (
        donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER,
        patient_id INTEGER,
        donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hospital_name TEXT,
        units_donated INTEGER,
        FOREIGN KEY (donor_id) REFERENCES users(id),
        FOREIGN KEY (patient_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")