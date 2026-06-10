from database import (
    add_patient,
    view_patients,
    check_available_rooms,
    check_available_doctors,
    count_available_rooms,
    count_available_doctors,
    check_insurance,
    view_insurance_providers,
    book_room_for_patient,
    view_room_bookings,
    cancel_room_booking,
    admit_patient,
    discharge_patient,
    view_admissions,
    book_appointment,
    view_appointments,
    generate_bill,
    view_bills,
    get_dashboard_data,
    save_chat_history,
    view_chat_history,
)


def run_single_tool(action):
    intent = action.get("intent")

    # ---------------- PATIENT COUNT ----------------
    if intent == "count_patients":
        patients = view_patients()
        return f"Total patients: {len(patients)}"

    # ---------------- VIEW PATIENTS ----------------
    if intent == "view_patients":
        patients = view_patients()

        if not patients:
            return "No patients found."

        result = "Patient details:\n"

        for patient in patients:
            result += (
                f"- ID: {patient[0]} | Name: {patient[1]} | Age: {patient[2]} | "
                f"Gender: {patient[3]} | Phone: {patient[4]} | Address: {patient[5]}\n"
            )

        return result.strip()

    # ---------------- ADD PATIENT ----------------
    if intent == "add_patient":
        if not action.get("patient_name"):
            return "Patient name is missing."

        return add_patient(
            action.get("patient_name"),
            action.get("age", 0),
            action.get("gender", ""),
            action.get("phone", ""),
            action.get("address", "")
        )

    # ---------------- CHECK ROOMS ----------------
    if intent == "check_rooms":
        room_type = action.get("room_type")

        if room_type == "All":
            result = "Available rooms:\n"

            for category in ["General", "Deluxe", "Luxury"]:
                rooms = check_available_rooms(category)

                if rooms:
                    result += f"\n{category} Rooms:\n"

                    for room in rooms:
                        result += f"- {room[1]} | ₹{int(room[3])} per day\n"

            return result.strip()

        rooms = check_available_rooms(room_type)

        if not rooms:
            return f"No available {room_type} rooms."

        result = f"Available {room_type} rooms:\n"

        for room in rooms:
            result += f"- {room[1]} | ₹{int(room[3])} per day\n"

        return result.strip()

    # ---------------- COUNT ROOMS ----------------
    if intent == "count_rooms":
        room_type = action.get("room_type")

        if room_type == "All":
            result = "Available room count:\n"
            total = 0

            for category in ["General", "Deluxe", "Luxury"]:
                count = count_available_rooms(category)
                total += count
                result += f"- {category}: {count}\n"

            result += f"\nTotal available rooms: {total}"
            return result.strip()

        return f"Available {room_type} rooms: {count_available_rooms(room_type)}"

    # ---------------- CHECK DOCTORS ----------------
    if intent == "check_doctors":
        specialization = action.get("specialization")

        if specialization == "All":
            result = "Available doctors:\n"

            for spec in ["Dentist", "ENT", "Cardiologist", "Pediatrician", "Dermatologist"]:
                doctors = check_available_doctors(spec)

                if doctors:
                    result += f"\n{spec} Doctors:\n"

                    for doctor in doctors:
                        result += (
                            f"- {doctor[1]} | Phone: {doctor[3]} | "
                            f"Fee: ₹{int(doctor[5])}\n"
                        )

            return result.strip()

        doctors = check_available_doctors(specialization)

        if not doctors:
            return f"No available {specialization} doctors."

        result = f"Available {specialization} doctors:\n"

        for doctor in doctors:
            result += (
                f"- {doctor[1]} | Phone: {doctor[3]} | "
                f"Fee: ₹{int(doctor[5])}\n"
            )

        return result.strip()

    # ---------------- COUNT DOCTORS ----------------
    if intent == "count_doctors":
        specialization = action.get("specialization")

        if specialization == "All":
            result = "Available doctor count:\n"
            total = 0

            for spec in ["Dentist", "ENT", "Cardiologist", "Pediatrician", "Dermatologist"]:
                count = count_available_doctors(spec)
                total += count
                result += f"- {spec}: {count}\n"

            result += f"\nTotal available doctors: {total}"
            return result.strip()

        return f"Available {specialization} doctors: {count_available_doctors(specialization)}"

    # ---------------- INSURANCE ----------------
    if intent == "validate_insurance":
        provider = action.get("provider_name")

        if provider == "All":
            rows = view_insurance_providers()

            if not rows:
                return "No active insurance providers found."

            result = "Accepted insurance providers:\n"

            for row in rows:
                result += f"- {row[0]} | Coverage: {row[1]}%\n"

            return result.strip()

        insurance = check_insurance(provider)

        if insurance:
            return f"{provider} insurance is accepted with {insurance[2]}% coverage."

        return f"{provider} insurance is not accepted."

    # ---------------- BOOK ROOM ----------------
    if intent == "book_room":
        return book_room_for_patient(
            action.get("patient_name"),
            action.get("room_type")
        )

    # ---------------- VIEW ROOM BOOKINGS ----------------
    if intent == "view_room_bookings":
        bookings = view_room_bookings()

        if not bookings:
            return "No active room bookings found."

        result = "Booked rooms:\n"

        for item in bookings:
            result += (
                f"- Booking ID: {item[0]} | Patient: {item[1]} | "
                f"Room: {item[2]} ({item[3]}) | Date: {item[4]} | Status: {item[5]}\n"
            )

        return result.strip()

    # ---------------- CANCEL ROOM BOOKING ----------------
    if intent == "cancel_room_booking":
        return cancel_room_booking(
            action.get("patient_name")
        )

    # ---------------- CREATE ADMISSION ----------------
    if intent == "create_admission":
        return admit_patient(
            action.get("patient_name"),
            action.get("room_type"),
            action.get("specialization"),
            action.get("insurance_provider")
        )

    # ---------------- DISCHARGE PATIENT ----------------
    if intent == "discharge_patient":
        return discharge_patient(
            action.get("patient_name")
        )

    # ---------------- COUNT ADMITTED PATIENTS WITH DETAILS ----------------
    if intent == "count_admissions_with_details":
        admissions = view_admissions()

        active_admissions = []

        for item in admissions:
            if item[9] == "Admitted":
                active_admissions.append(item)

        if not active_admissions:
            return "Currently admitted patients: 0"

        result = f"Currently admitted patients: {len(active_admissions)}\n\n"
        result += "Admitted patient details:\n"

        for item in active_admissions:
            result += (
                f"- {item[1]} | Room: {item[2]} ({item[3]}) | "
                f"Doctor: {item[4]} | Insurance: {item[6]} | "
                f"Admitted Date: {item[7]} | Status: {item[9]}\n"
            )

        return result.strip()

    # ---------------- COUNT ADMISSIONS ONLY ----------------
    if intent == "count_admissions":
        admissions = view_admissions()

        active_count = 0

        for item in admissions:
            if item[9] == "Admitted":
                active_count += 1

        return f"Currently admitted patients: {active_count}"

    # ---------------- VIEW ADMISSIONS ----------------
    if intent == "get_admissions":
        admissions = view_admissions()

        if not admissions:
            return "No admissions found."

        result = "Admissions:\n"

        for item in admissions:
            result += (
                f"- {item[1]} | Room: {item[2]} ({item[3]}) | "
                f"Doctor: {item[4]} | Insurance: {item[6]} | "
                f"Admitted Date: {item[7]} | Discharge Date: {item[8]} | "
                f"Status: {item[9]}\n"
            )

        return result.strip()

    # ---------------- BOOK APPOINTMENT ----------------
    if intent == "book_appointment":
        return book_appointment(
            action.get("patient_name"),
            action.get("specialization"),
            action.get("appointment_date"),
            action.get("appointment_time")
        )

    # ---------------- VIEW APPOINTMENTS ----------------
    if intent == "view_appointments":
        appointments = view_appointments()

        if not appointments:
            return "No appointments found."

        result = "Appointments:\n"

        for item in appointments:
            result += (
                f"- {item[1]} with {item[2]} ({item[3]}) "
                f"on {item[4]} at {item[5]} | Status: {item[6]}\n"
            )

        return result.strip()

    # ---------------- GENERATE BILL ----------------
    if intent == "generate_bill":
        return generate_bill(
            action.get("patient_name")
        )

    # ---------------- VIEW BILLS ----------------
    if intent == "view_bills":
        bills = view_bills()

        if not bills:
            return "No bills found."

        result = "Bills:\n"

        for bill in bills:
            result += (
                f"- Bill ID: {bill[0]} | Patient: {bill[1]} | "
                f"Total: ₹{int(bill[2])} | Insurance: ₹{int(bill[3])} | "
                f"Payable: ₹{int(bill[4])} | Date: {bill[5]} | Status: {bill[6]}\n"
            )

        return result.strip()

    # ---------------- DASHBOARD ----------------
    if intent == "dashboard":
        data = get_dashboard_data()

        return (
            "Hospital Dashboard:\n"
            f"- Total Patients: {data['patients']}\n"
            f"- Available Rooms: {data['available_rooms']}\n"
            f"- Booked Rooms: {data['booked_rooms']}\n"
            f"- Occupied Rooms: {data['occupied_rooms']}\n"
            f"- Available Doctors: {data['available_doctors']}\n"
            f"- Active Admissions: {data['active_admissions']}"
        )

    # ---------------- CHAT HISTORY ----------------
    if intent == "chat_history":
        chats = view_chat_history()

        if not chats:
            return "No chat history found."

        result = "Recent chat history:\n"

        for chat in chats:
            result += (
                f"\nUser: {chat[0]}\n"
                f"Answer: {chat[1]}\n"
                f"Time: {chat[2]}\n"
            )

        return result.strip()

    # ---------------- UNKNOWN ----------------
    return (
        "Sorry, I could not understand the request.\n"
        "You can ask about patients, rooms, doctors, insurance, admissions, appointments, billing, dashboard, or chat history."
    )


def run_mcp_tool(intent_data, user_query=None):
    actions = intent_data.get("actions", [])

    if not actions:
        return "Sorry, I could not understand the request."

    results = []

    for action in actions:
        result = run_single_tool(action)
        results.append(result.strip())

    final_result = "\n\n---\n\n".join(results).strip()

    if user_query:
        save_chat_history(user_query, final_result)

    return final_result