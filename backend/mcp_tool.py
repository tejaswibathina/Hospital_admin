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
    count_total_rooms,
    count_total_doctors,
)

ROOM_TYPES = ["General", "Deluxe", "Luxury"]

SPECIALIZATIONS = [
    "Dentist",
    "ENT",
    "Cardiologist",
    "Pediatrician",
    "Dermatologist",
]

def format_patients(rows):
    if not rows:
        return "No patients found."

    lines = ["Patient Details:\n"]

    for row in rows:
        lines.append(
            f"- ID:{row[0]} | Name:{row[1]} | Age:{row[2]} | "
            f"Gender:{row[3]} | Phone:{row[4]} | Address:{row[5]}"
        )

    return "\n".join(lines)


def format_rooms(room_type, rooms):
    if not rooms:
        return f"No available {room_type} rooms."

    lines = [f"Available {room_type} Rooms:\n"]

    for room in rooms:
        lines.append(
            f"- {room[1]} | ₹{int(room[3])}/day"
        )

    return "\n".join(lines)


def format_doctors(spec, doctors):
    if not doctors:
        return f"No available {spec} doctors."

    lines = [f"{spec} Doctors:\n"]

    for doctor in doctors:
        lines.append(
            f"- {doctor[1]} | Phone:{doctor[3]} | Fee:₹{int(doctor[5])}"
        )

    return "\n".join(lines)


def format_bills(rows):
    if not rows:
        return "No bills found."

    lines = ["Bills:\n"]

    for bill in rows:
        lines.append(
            f"- Bill ID:{bill[0]} | Patient:{bill[1]} | "
            f"Total:₹{int(bill[2])} | Insurance:₹{int(bill[3])} | "
            f"Payable:₹{int(bill[4])} | Status:{bill[6]}"
        )

    return "\n".join(lines)


def format_appointments(rows):
    if not rows:
        return "No appointments found."

    lines = ["Appointments:\n"]

    for item in rows:
        lines.append(
            f"- {item[1]} with {item[2]} "
            f"({item[3]}) on {item[4]} at {item[5]} "
            f"| {item[6]}"
        )

    return "\n".join(lines)


def format_chat_history(rows):
    if not rows:
        return "No chat history found."

    lines = ["Recent Chats:\n"]

    for chat in rows:
        lines.append(
            f"User : {chat[0]}\n"
            f"Bot  : {chat[1]}\n"
            f"Time : {chat[2]}\n"
        )

    return "\n".join(lines)

def handle_patients(action):
    intent = action["intent"]

    if intent == "count_patients":
        return f"Total patients: {len(view_patients())}"

    if intent == "view_patients":
        return format_patients(view_patients())

    if intent == "add_patient":

        patient_name = action.get("patient_name")

        if not patient_name:
            return "Please provide the patient name."

        return add_patient(
            patient_name,
            action.get("age", 0),
            action.get("gender", ""),
            action.get("phone", ""),
            action.get("address", "")
        )


def handle_rooms(action):
    intent = action["intent"]

    if intent == "check_rooms":

        room_type = action.get("room_type", "General")

        if room_type == "All":

            response = []

            for room in ROOM_TYPES:
                response.append(
                    format_rooms(room, check_available_rooms(room))
                )

            return "\n\n".join(response)

        return format_rooms(
            room_type,
            check_available_rooms(room_type)
        )

    if intent == "count_rooms":

        room_type = action.get("room_type", "All")

        total = count_total_rooms(room_type)

        if room_type == "All":

            return f"Total rooms: {total}"

    return f"Total {room_type} rooms: {total}"

    if intent == "book_room":

        return book_room_for_patient(
            action.get("patient_name"),
            action.get("room_type")
        )

    if intent == "view_room_bookings":

        rows = view_room_bookings()

        if not rows:
            return "No room bookings found."

        lines = ["Room Bookings:\n"]

        for row in rows:
            lines.append(
                f"- {row[1]} | Room:{row[2]} ({row[3]}) | {row[5]}"
            )

        return "\n".join(lines)

    if intent == "cancel_room_booking":

        return cancel_room_booking(
            action.get("patient_name")
        )


def handle_doctors(action):

    intent = action["intent"]

    specialization = action.get(
        "specialization",
        "ENT"
    )

    if intent == "check_doctors":

        if specialization == "All":
            response = []

            for spec in SPECIALIZATIONS:
                response.append(
                    format_doctors(
                        spec,
                        check_available_doctors(spec)
                   )
                )

            return "\n\n".join(response)

        return format_doctors(
            specialization,
            check_available_doctors(specialization)
        )

    if intent == "count_available_doctors":

        specialization = action.get("specialization", "All")

        total = count_available_doctors(specialization)

        if specialization == "All":
            return f"Available doctors: {total}"

        return f"Available {specialization} doctors: {total}"

    if intent == "count_doctors":

        specialization = action.get("specialization", "All")

        total = count_total_doctors(specialization)

        if specialization == "All":
            return f"Total doctors: {total}"

        return f"Total {specialization} doctors: {total}"

def handle_insurance(action):
    provider = action.get("provider_name", "All")

    if provider == "All":
        rows = view_insurance_providers()

        if not rows:
            return "No insurance providers found."

        lines = ["Accepted Insurance Providers:\n"]

        for row in rows:
            lines.append(
                f"- {row[0]} ({row[1]}% coverage)"
            )

        return "\n".join(lines)

    insurance = check_insurance(provider)

    if insurance:
        return (
            f"{provider} insurance is accepted "
            f"with {insurance[2]}% coverage."
        )

    return f"{provider} insurance is not accepted."


def handle_admissions(action):
    intent = action["intent"]

    if intent == "create_admission":
        return admit_patient(
            action.get("patient_name"),
            action.get("room_type"),
            action.get("specialization"),
            action.get("insurance_provider"),
        )

    if intent == "discharge_patient":
        return discharge_patient(
            action.get("patient_name")
        )

    admissions = view_admissions()

    active = [
        row for row in admissions
        if row[9] == "Admitted"
    ]

    if intent == "count_admissions":
        return f"Currently admitted patients: {len(active)}"

    if intent == "count_admissions_with_details":

        if not active:
            return "Currently admitted patients: 0"

        lines = [
            f"Currently admitted patients: {len(active)}",
            "",
            "Patient Details:"
        ]

        for row in active:
            lines.append(
                f"- {row[1]} | Room:{row[2]} ({row[3]}) | "
                f"Doctor:{row[4]} | Insurance:{row[6]}"
            )

        return "\n".join(lines)

    if intent == "get_admissions":

        if not admissions:
            return "No admissions found."

        lines = ["Admissions:\n"]

        for row in admissions:
            lines.append(
                f"- {row[1]} | "
                f"Room:{row[2]} ({row[3]}) | "
                f"Doctor:{row[4]} | "
                f"Status:{row[9]}"
            )

        return "\n".join(lines)


def handle_appointments(action):
    intent = action["intent"]

    if intent == "book_appointment":
        return book_appointment(
            action.get("patient_name"),
            action.get("specialization"),
            action.get("appointment_date"),
            action.get("appointment_time"),
        )

    return format_appointments(
        view_appointments()
    )


def handle_bills(action):
    intent = action["intent"]

    if intent == "generate_bill":
        return generate_bill(
            action.get("patient_name")
        )

    return format_bills(
        view_bills()
    )


def handle_dashboard():

    data = get_dashboard_data()

    return (
        "Hospital Dashboard\n\n"
        f"Patients : {data['patients']}\n"
        f"Available Rooms : {data['available_rooms']}\n"
        f"Booked Rooms : {data['booked_rooms']}\n"
        f"Occupied Rooms : {data['occupied_rooms']}\n"
        f"Available Doctors : {data['available_doctors']}\n"
        f"Active Admissions : {data['active_admissions']}"
    )


def handle_chat_history():
    return format_chat_history(
        view_chat_history()
    )

# ---------------- INTENT DISPATCHER ----------------

INTENT_HANDLERS = {
    # Patients
    "count_patients": handle_patients,
    "view_patients": handle_patients,
    "add_patient": handle_patients,

    # Rooms
    "check_rooms": handle_rooms,
    "count_rooms": handle_rooms,
    "book_room": handle_rooms,
    "view_room_bookings": handle_rooms,
    "cancel_room_booking": handle_rooms,

    # Doctors
    "check_doctors": handle_doctors,
    "count_doctors": handle_doctors,
    "count_available_doctors": handle_doctors,

    # Insurance
    "validate_insurance": handle_insurance,

    # Admissions
    "create_admission": handle_admissions,
    "discharge_patient": handle_admissions,
    "count_admissions": handle_admissions,
    "count_admissions_with_details": handle_admissions,
    "get_admissions": handle_admissions,

    # Appointments
    "book_appointment": handle_appointments,
    "view_appointments": handle_appointments,

    # Bills
    "generate_bill": handle_bills,
    "view_bills": handle_bills,

    # Dashboard
    "dashboard": lambda action: handle_dashboard(),

    # Chat History
    "chat_history": lambda action: handle_chat_history(),
}


# ---------------- SINGLE TOOL EXECUTION ----------------

def run_single_tool(action):
    intent = action.get("intent")

    if not intent:
        return "Intent is missing."

    handler = INTENT_HANDLERS.get(intent)

    if handler is None:
        return (
            "Sorry, I couldn't understand your request.\n"
            "Try asking about patients, rooms, doctors, "
            "insurance, appointments, admissions or billing."
        )

    try:
        return handler(action)

    except Exception as e:
        return f"Error while executing '{intent}': {str(e)}"


# ---------------- MULTI TOOL EXECUTION ----------------

def run_mcp_tool(intent_data, user_query=None):

    actions = intent_data.get("actions", [])

    if not actions:
        return "Sorry, I couldn't understand your request."

    responses = []

    for action in actions:

        response = run_single_tool(action)

        responses.append(response)

    final_response = "\n\n".join(responses)

    if user_query:
        save_chat_history(
            user_query,
            final_response
        )

    return final_response  