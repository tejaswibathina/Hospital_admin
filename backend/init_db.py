import sqlite3

conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    address TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT NOT NULL,
    room_type TEXT NOT NULL,
    price_per_day REAL,
    status TEXT DEFAULT 'Available'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    phone TEXT,
    availability_status TEXT DEFAULT 'Available',
    consultation_fee REAL DEFAULT 500
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS insurance_providers (
    insurance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name TEXT NOT NULL,
    coverage_percent INTEGER,
    status TEXT DEFAULT 'Active'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS room_bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    room_id INTEGER,
    booking_date TEXT,
    booking_status TEXT DEFAULT 'Booked',
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(room_id) REFERENCES rooms(room_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    appointment_date TEXT,
    appointment_time TEXT,
    status TEXT DEFAULT 'Booked',
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admissions (
    admission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    room_id INTEGER,
    doctor_id INTEGER,
    insurance_id INTEGER,
    admission_date TEXT,
    discharge_date TEXT,
    status TEXT DEFAULT 'Admitted',
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(room_id) REFERENCES rooms(room_id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY(insurance_id) REFERENCES insurance_providers(insurance_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS billing (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_id INTEGER,
    total_amount REAL,
    insurance_coverage REAL,
    payable_amount REAL,
    bill_date TEXT,
    status TEXT DEFAULT 'Generated',
    FOREIGN KEY(admission_id) REFERENCES admissions(admission_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query TEXT,
    system_response TEXT,
    created_at TEXT
)
""")

cursor.execute("DELETE FROM billing")
cursor.execute("DELETE FROM appointments")
cursor.execute("DELETE FROM room_bookings")
cursor.execute("DELETE FROM admissions")
cursor.execute("DELETE FROM rooms")
cursor.execute("DELETE FROM doctors")
cursor.execute("DELETE FROM insurance_providers")
cursor.execute("DELETE FROM patients")
cursor.execute("DELETE FROM chat_history")

rooms = [
    ("G101", "General", 1000, "Available"),
    ("G102", "General", 1000, "Available"),
    ("G103", "General", 1000, "Occupied"),
    ("D201", "Deluxe", 2500, "Available"),
    ("D202", "Deluxe", 2500, "Occupied"),
    ("D203", "Deluxe", 2500, "Available"),
    ("L301", "Luxury", 5000, "Available"),
    ("L302", "Luxury", 5000, "Occupied"),
    ("L303", "Luxury", 5000, "Available"),
]

doctors = [
    ("Dr. Arjun", "Dentist", "9000011111", "Available", 600),
    ("Dr. Priya", "Dentist", "9000011112", "Busy", 600),
    ("Dr. Kiran", "Dentist", "9000011113", "Available", 600),
    ("Dr. Meena", "ENT", "9000022221", "Available", 700),
    ("Dr. Suresh", "ENT", "9000022222", "On Leave", 700),
    ("Dr. Naveen", "ENT", "9000022223", "Available", 700),
    ("Dr. Ramesh", "Cardiologist", "9000033331", "Available", 1200),
    ("Dr. Kavya", "Cardiologist", "9000033332", "Busy", 1200),
    ("Dr. Sanjay", "Cardiologist", "9000033333", "Available", 1200),
    ("Dr. Lakshmi", "Pediatrician", "9000044441", "Available", 800),
    ("Dr. Varun", "Pediatrician", "9000044442", "Busy", 800),
    ("Dr. Deepa", "Pediatrician", "9000044443", "Available", 800),
    ("Dr. Sneha", "Dermatologist", "9000055551", "Available", 900),
    ("Dr. Harish", "Dermatologist", "9000055552", "On Leave", 900),
    ("Dr. Teja", "Dermatologist", "9000055553", "Available", 900),
]

insurance = [
    ("LIC", 60, "Active"),
    ("AIG", 70, "Active"),
    ("Indian", 40, "Active"),
    ("SBI", 50, "Active"),
]

patients = [
    ("Rahul Sharma", 35, "Male", "9876543210", "Hyderabad"),
    ("Anjali Reddy", 28, "Female", "9876501234", "Vijayawada"),
    ("Kiran Kumar", 45, "Male", "9876512345", "Chennai"),
]

cursor.executemany(
    "INSERT INTO rooms (room_number, room_type, price_per_day, status) VALUES (?, ?, ?, ?)",
    rooms
)

cursor.executemany(
    "INSERT INTO doctors (doctor_name, specialization, phone, availability_status, consultation_fee) VALUES (?, ?, ?, ?, ?)",
    doctors
)

cursor.executemany(
    "INSERT INTO insurance_providers (provider_name, coverage_percent, status) VALUES (?, ?, ?)",
    insurance
)

cursor.executemany(
    "INSERT INTO patients (patient_name, age, gender, phone, address) VALUES (?, ?, ?, ?, ?)",
    patients
)

conn.commit()
conn.close()

print("Hospital database created successfully.")