import sqlite3
from datetime import date, datetime

DB_NAME = "hospital.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


# ---------------- DASHBOARD ----------------

def get_dashboard_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Available'")
    available_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Booked'")
    booked_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Occupied'")
    occupied_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM doctors WHERE availability_status = 'Available'")
    available_doctors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM admissions WHERE status = 'Admitted'")
    active_admissions = cursor.fetchone()[0]

    conn.close()

    return {
        "total_patients": total_patients,
        "available_rooms": available_rooms,
        "booked_rooms": booked_rooms,
        "occupied_rooms": occupied_rooms,
        "available_doctors": available_doctors,
        "active_admissions": active_admissions
    }

# ---------------- PATIENTS ----------------

def add_patient(patient_name, age, gender, phone, address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (patient_name, age, gender, phone, address)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_name, age, gender, phone, address))

    conn.commit()
    conn.close()

    return f"Patient {patient_name} registered successfully."


def view_patients():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_id, patient_name, age, gender, phone, address
        FROM patients
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_patient_id(patient_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT patient_id FROM patients WHERE LOWER(patient_name)=LOWER(?)",
        (patient_name,)
    )

    patient = cursor.fetchone()
    conn.close()

    return patient[0] if patient else None
def get_or_create_patient_id(patient_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT patient_id FROM patients WHERE LOWER(patient_name)=LOWER(?)",
        (patient_name,)
    )

    patient = cursor.fetchone()

    if patient:
        conn.close()
        return patient[0]

    cursor.execute("""
        INSERT INTO patients (patient_name, age, gender, phone, address)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_name, 0, "Not specified", "", ""))

    patient_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return patient_id

# ---------------- ROOMS ----------------

def check_available_rooms(room_type):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT room_id, room_number, room_type, price_per_day, status
        FROM rooms
        WHERE LOWER(room_type)=LOWER(?)
        AND status='Available'
    """, (room_type,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def count_available_rooms(room_type):
    if room_type == "All":
        total = 0
        for category in ["General", "Deluxe", "Luxury"]:
            total += len(check_available_rooms(category))
        return total

    return len(check_available_rooms(room_type))


# ---------------- DOCTORS ----------------

def check_available_doctors(specialization):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT doctor_id, doctor_name, specialization, phone, availability_status, consultation_fee
        FROM doctors
        WHERE LOWER(specialization)=LOWER(?)
        AND availability_status='Available'
    """, (specialization,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def count_available_doctors(specialization):
    if specialization == "All":
        total = 0
        for spec in ["Dentist", "ENT", "Cardiologist", "Pediatrician", "Dermatologist"]:
            total += len(check_available_doctors(spec))
        return total

    return len(check_available_doctors(specialization))


# ---------------- INSURANCE ----------------

def check_insurance(provider_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT insurance_id, provider_name, coverage_percent, status
        FROM insurance_providers
        WHERE LOWER(provider_name)=LOWER(?)
        AND status='Active'
    """, (provider_name,))

    row = cursor.fetchone()
    conn.close()
    return row


def view_insurance_providers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT provider_name, coverage_percent, status
        FROM insurance_providers
        WHERE status='Active'
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- ROOM BOOKING ----------------

def book_room_for_patient(patient_name, room_type):
    conn = get_connection()
    cursor = conn.cursor()

    patient_id = get_patient_id(patient_name)
    if not patient_id:
        return "Patient not found. Please register patient first."

    cursor.execute("""
        SELECT rb.booking_id
        FROM room_bookings rb
        JOIN patients p ON rb.patient_id = p.patient_id
        WHERE LOWER(p.patient_name)=LOWER(?)
        AND rb.booking_status='Booked'
    """, (patient_name,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return f"{patient_name} already has an active room booking."

    cursor.execute("""
        SELECT room_id, room_number
        FROM rooms
        WHERE LOWER(room_type)=LOWER(?)
        AND status='Available'
        LIMIT 1
    """, (room_type,))
    room = cursor.fetchone()

    if not room:
        conn.close()
        return f"No available {room_type} rooms for booking."

    cursor.execute("""
        INSERT INTO room_bookings (patient_id, room_id, booking_date, booking_status)
        VALUES (?, ?, ?, 'Booked')
    """, (patient_id, room[0], str(date.today())))

    cursor.execute("""
        UPDATE rooms SET status='Booked' WHERE room_id=?
    """, (room[0],))

    conn.commit()
    conn.close()

    return f"{room_type} room booked successfully for {patient_name}. Room Number: {room[1]}."


def view_room_bookings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rb.booking_id, p.patient_name, r.room_number, r.room_type,
               rb.booking_date, rb.booking_status
        FROM room_bookings rb
        JOIN patients p ON rb.patient_id = p.patient_id
        JOIN rooms r ON rb.room_id = r.room_id
        WHERE rb.booking_status='Booked'
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def cancel_room_booking(patient_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rb.booking_id, rb.room_id
        FROM room_bookings rb
        JOIN patients p ON rb.patient_id = p.patient_id
        WHERE LOWER(p.patient_name)=LOWER(?)
        AND rb.booking_status='Booked'
        LIMIT 1
    """, (patient_name,))
    booking = cursor.fetchone()

    if not booking:
        conn.close()
        return f"No active room booking found for {patient_name}."

    cursor.execute("""
        UPDATE room_bookings
        SET booking_status='Cancelled'
        WHERE booking_id=?
    """, (booking[0],))

    cursor.execute("""
        UPDATE rooms
        SET status='Available'
        WHERE room_id=?
    """, (booking[1],))

    conn.commit()
    conn.close()

    return f"Room booking cancelled for {patient_name}."


# ---------------- ADMISSION ----------------

def admit_patient(patient_name, room_type, specialization, insurance_provider):
    conn = get_connection()
    cursor = conn.cursor()

    if not patient_name:
        conn.close()
        return "Patient name is missing."

    # Auto-create patient if patient is not already registered
    patient_id = get_or_create_patient_id(patient_name)

    if not insurance_provider:
        insurance_provider = "LIC"

    cursor.execute("""
        SELECT insurance_id
        FROM insurance_providers
        WHERE LOWER(provider_name)=LOWER(?)
        AND status='Active'
    """, (insurance_provider,))
    insurance = cursor.fetchone()

    if not insurance:
        conn.close()
        return f"{insurance_provider} insurance is not accepted."

    cursor.execute("""
        SELECT doctor_id, doctor_name
        FROM doctors
        WHERE LOWER(specialization)=LOWER(?)
        AND availability_status='Available'
        LIMIT 1
    """, (specialization,))
    doctor = cursor.fetchone()

    if not doctor:
        conn.close()
        return f"No available {specialization} doctors."

    cursor.execute("""
        SELECT rb.booking_id, rb.room_id, r.room_number, r.room_type
        FROM room_bookings rb
        JOIN rooms r ON rb.room_id = r.room_id
        WHERE rb.patient_id=?
        AND rb.booking_status='Booked'
        LIMIT 1
    """, (patient_id,))
    booking = cursor.fetchone()

    if booking:
        room_id = booking[1]
        room_number = booking[2]
        room_type_used = booking[3]

        cursor.execute("""
            UPDATE room_bookings
            SET booking_status='Admitted'
            WHERE booking_id=?
        """, (booking[0],))

    else:
        cursor.execute("""
            SELECT room_id, room_number, room_type
            FROM rooms
            WHERE LOWER(room_type)=LOWER(?)
            AND status='Available'
            LIMIT 1
        """, (room_type,))
        room = cursor.fetchone()

        if not room:
            conn.close()
            return f"No available {room_type} rooms."

        room_id = room[0]
        room_number = room[1]
        room_type_used = room[2]

    cursor.execute("""
        INSERT INTO admissions
        (patient_id, room_id, doctor_id, insurance_id, admission_date, status)
        VALUES (?, ?, ?, ?, ?, 'Admitted')
    """, (patient_id, room_id, doctor[0], insurance[0], str(date.today())))

    cursor.execute(
        "UPDATE rooms SET status='Occupied' WHERE room_id=?",
        (room_id,)
    )

    cursor.execute(
        "UPDATE doctors SET availability_status='Busy' WHERE doctor_id=?",
        (doctor[0],)
    )

    conn.commit()
    conn.close()

    return (
        f"{patient_name} registered and admitted successfully.\n"
        f"Room: {room_number} ({room_type_used})\n"
        f"Doctor: {doctor[1]}\n"
        f"Insurance: {insurance_provider}"
    )

def discharge_patient(patient_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.admission_id, a.room_id, a.doctor_id
        FROM admissions a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE LOWER(p.patient_name)=LOWER(?)
        AND a.status='Admitted'
        LIMIT 1
    """, (patient_name,))
    admission = cursor.fetchone()

    if not admission:
        conn.close()
        return f"No active admission found for {patient_name}."

    cursor.execute("""
        UPDATE admissions
        SET status='Discharged', discharge_date=?
        WHERE admission_id=?
    """, (str(date.today()), admission[0]))

    cursor.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (admission[1],))
    cursor.execute("UPDATE doctors SET availability_status='Available' WHERE doctor_id=?", (admission[2],))

    conn.commit()
    conn.close()

    return f"{patient_name} discharged successfully. Room and doctor are now available."


def view_admissions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.admission_id, p.patient_name, r.room_number, r.room_type,
               d.doctor_name, d.specialization, i.provider_name,
               a.admission_date, a.discharge_date, a.status
        FROM admissions a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN rooms r ON a.room_id = r.room_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN insurance_providers i ON a.insurance_id = i.insurance_id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- APPOINTMENTS ----------------

def book_appointment(patient_name, specialization, appointment_date, appointment_time):
    conn = get_connection()
    cursor = conn.cursor()

    patient_id = get_patient_id(patient_name)
    if not patient_id:
        return "Patient not found. Please register patient first."

    cursor.execute("""
        SELECT doctor_id, doctor_name
        FROM doctors
        WHERE LOWER(specialization)=LOWER(?)
        AND availability_status='Available'
        LIMIT 1
    """, (specialization,))
    doctor = cursor.fetchone()

    if not doctor:
        conn.close()
        return f"No available {specialization} doctor for appointment."

    cursor.execute("""
        INSERT INTO appointments
        (patient_id, doctor_id, appointment_date, appointment_time, status)
        VALUES (?, ?, ?, ?, 'Booked')
    """, (patient_id, doctor[0], appointment_date, appointment_time))

    conn.commit()
    conn.close()

    return f"Appointment booked for {patient_name} with {doctor[1]} on {appointment_date} at {appointment_time}."


def view_appointments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ap.appointment_id, p.patient_name, d.doctor_name,
               d.specialization, ap.appointment_date, ap.appointment_time, ap.status
        FROM appointments ap
        JOIN patients p ON ap.patient_id = p.patient_id
        JOIN doctors d ON ap.doctor_id = d.doctor_id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- BILLING ----------------

def generate_bill(patient_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.admission_id, r.price_per_day, d.consultation_fee,
               i.coverage_percent, p.patient_name
        FROM admissions a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN rooms r ON a.room_id = r.room_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN insurance_providers i ON a.insurance_id = i.insurance_id
        WHERE LOWER(p.patient_name)=LOWER(?)
        ORDER BY a.admission_id DESC
        LIMIT 1
    """, (patient_name,))
    data = cursor.fetchone()

    if not data:
        conn.close()
        return f"No admission found for {patient_name}."

    admission_id = data[0]
    room_charge = data[1]
    doctor_fee = data[2]
    coverage_percent = data[3]

    total_amount = room_charge + doctor_fee
    insurance_coverage = total_amount * coverage_percent / 100
    payable_amount = total_amount - insurance_coverage

    cursor.execute("""
        INSERT INTO billing
        (admission_id, total_amount, insurance_coverage, payable_amount, bill_date, status)
        VALUES (?, ?, ?, ?, ?, 'Generated')
    """, (admission_id, total_amount, insurance_coverage, payable_amount, str(date.today())))

    conn.commit()
    conn.close()

    return (
        f"Bill generated for {patient_name}:\n"
        f"Room Charge: ₹{int(room_charge)}\n"
        f"Doctor Fee: ₹{int(doctor_fee)}\n"
        f"Total Amount: ₹{int(total_amount)}\n"
        f"Insurance Coverage ({coverage_percent}%): ₹{int(insurance_coverage)}\n"
        f"Patient Payable Amount: ₹{int(payable_amount)}"
    )


def view_bills():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.bill_id, p.patient_name, b.total_amount, b.insurance_coverage,
               b.payable_amount, b.bill_date, b.status
        FROM billing b
        JOIN admissions a ON b.admission_id = a.admission_id
        JOIN patients p ON a.patient_id = p.patient_id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- CHAT HISTORY ----------------

def save_chat_history(user_query, system_response):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history (user_query, system_response, created_at)
        VALUES (?, ?, ?)
    """, (user_query, system_response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def view_chat_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_query, system_response, created_at
        FROM chat_history
        ORDER BY chat_id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------- ADMIN DASHBOARD FUNCTIONS ----------------

def get_admin_patients():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_id, patient_name, age, gender, phone, address
        FROM patients
        ORDER BY patient_id ASC
    """)

    patients = cursor.fetchall()
    conn.close()

    return patients


def get_admin_doctors():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT doctor_id, doctor_name, specialization, phone, availability_status, consultation_fee
        FROM doctors
        ORDER BY doctor_id ASC
    """)

    doctors = cursor.fetchall()
    conn.close()

    return doctors


def get_admin_rooms():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT room_id, room_number, room_type, price_per_day, status
        FROM rooms
        ORDER BY room_id ASC
    """)

    rooms = cursor.fetchall()
    conn.close()

    return rooms


def get_admin_admissions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            a.admission_id,
            p.patient_name,
            r.room_number,
            r.room_type,
            d.doctor_name,
            d.specialization,
            i.provider_name,
            a.admission_date,
            a.discharge_date,
            a.status
        FROM admissions a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN rooms r ON a.room_id = r.room_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN insurance_providers i ON a.insurance_id = i.insurance_id
        ORDER BY a.admission_id ASC
    """)

    admissions = cursor.fetchall()
    conn.close()

    return admissions


def delete_patient_by_id(patient_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT admission_id
        FROM admissions
        WHERE patient_id = ?
        AND status = 'Admitted'
    """, (patient_id,))

    active_admission = cursor.fetchone()

    if active_admission:
        conn.close()
        return "Cannot delete this patient because the patient is currently admitted. Please discharge or delete admission first."

    cursor.execute("DELETE FROM room_bookings WHERE patient_id = ?", (patient_id,))
    cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
    cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))

    conn.commit()
    conn.close()

    return "Patient deleted successfully."


def delete_admission_by_id(admission_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT room_id, doctor_id, status
        FROM admissions
        WHERE admission_id = ?
    """, (admission_id,))

    admission = cursor.fetchone()

    if not admission:
        conn.close()
        return "Admission record not found."

    room_id = admission[0]
    doctor_id = admission[1]
    status = admission[2]

    if status == "Admitted":
        cursor.execute("""
            UPDATE rooms
            SET status = 'Available'
            WHERE room_id = ?
        """, (room_id,))

        cursor.execute("""
            UPDATE doctors
            SET availability_status = 'Available'
            WHERE doctor_id = ?
        """, (doctor_id,))

    cursor.execute("DELETE FROM billing WHERE admission_id = ?", (admission_id,))
    cursor.execute("DELETE FROM admissions WHERE admission_id = ?", (admission_id,))

    conn.commit()
    conn.close()

    return "Admission deleted successfully. Room and doctor status updated."

# ---------------- ADMIT PATIENT WITH FULL DETAILS ----------------

def add_or_update_patient_details(patient_name, age, gender, phone, address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT patient_id FROM patients WHERE LOWER(patient_name)=LOWER(?)",
        (patient_name,)
    )

    patient = cursor.fetchone()

    if patient:
        patient_id = patient[0]

        cursor.execute("""
            UPDATE patients
            SET age = ?, gender = ?, phone = ?, address = ?
            WHERE patient_id = ?
        """, (age, gender, phone, address, patient_id))

    else:
        cursor.execute("""
            INSERT INTO patients (patient_name, age, gender, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_name, age, gender, phone, address))

        patient_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return patient_id


def admit_patient_with_full_details(
    patient_name,
    age,
    gender,
    phone,
    address,
    room_type,
    specialization,
    insurance_provider
):
    if not patient_name or not phone or not room_type or not specialization or not insurance_provider:
        return "Please fill all required admission details."

    patient_id = add_or_update_patient_details(
        patient_name,
        age,
        gender,
        phone,
        address
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT admission_id
        FROM admissions
        WHERE patient_id = ?
        AND status = 'Admitted'
    """, (patient_id,))

    active_admission = cursor.fetchone()

    if active_admission:
        conn.close()
        return f"{patient_name} is already admitted."

    conn.close()

    return admit_patient(
        patient_name,
        room_type,
        specialization,
        insurance_provider
    )