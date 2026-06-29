from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auth import (
    verify_login,
    change_admin_password
)

from database import (
    get_dashboard_data,
    get_admin_patients,
    get_admin_doctors,
    get_admin_rooms,
    get_admin_admissions,
    admit_patient_with_full_details,
    delete_patient_by_id,
    delete_admission_by_id,
)

from ai_receptionist import (
    get_history,
    add_message
)

from hospital_context import (
    build_hospital_context
)

from llm_router import (
    safe_chat_response
)

# ==========================================================
# FASTAPI
# ==========================================================

app = FastAPI(
    title="AI Hospital Management Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# REQUEST MODELS
# ==========================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class AdmissionRequest(BaseModel):
    patient_name: str
    age: int
    gender: str
    phone: str
    address: str
    room_type: str
    specialization: str
    insurance_provider: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class DeletePatientRequest(BaseModel):
    patient_id: int


class DeleteAdmissionRequest(BaseModel):
    admission_id: int


class SpecializationRequest(BaseModel):
    message: str

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def patient_to_dict(row):
    return {
        "patient_id": row[0],
        "patient_name": row[1],
        "age": row[2],
        "gender": row[3],
        "phone": row[4],
        "address": row[5]
    }


def doctor_to_dict(row):
    return {
        "doctor_id": row[0],
        "doctor_name": row[1],
        "specialization": row[2],
        "phone": row[3],
        "availability_status": row[4],
        "consultation_fee": row[5]
    }


def room_to_dict(row):
    return {
        "room_id": row[0],
        "room_number": row[1],
        "room_type": row[2],
        "price_per_day": row[3],
        "status": row[4]
    }


def admission_to_dict(row):
    return {
        "admission_id": row[0],
        "patient_name": row[1],
        "room_number": row[2],
        "room_type": row[3],
        "doctor_name": row[4],
        "specialization": row[5],
        "insurance_provider": row[6],
        "admission_date": row[7],
        "discharge_date": row[8],
        "status": row[9]
    }

# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def home():

    return {
        "message": "AI Hospital Management Backend Running Successfully"
    }
# ==========================================================
# AUTHENTICATION
# ==========================================================

@app.post("/login")
def login(data: LoginRequest):

    if verify_login(
        data.username,
        data.password
    ):

        return {
            "success": True,
            "role": "admin",
            "message": "Login Successful"
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid username or password."
    )


@app.post("/change-password")
def change_password(data: ChangePasswordRequest):

    success, message = change_admin_password(
        data.old_password,
        data.new_password
    )

    if not success:

        raise HTTPException(
            status_code=400,
            detail=message
        )

    return {
        "success": True,
        "message": message
    }


# ==========================================================
# DASHBOARD
# ==========================================================

@app.get("/dashboard")
def dashboard():

    data = get_dashboard_data()

    return {
        "total_patients": data.get("total_patients", 0),
        "available_rooms": data.get("available_rooms", 0),
        "booked_rooms": data.get("booked_rooms", 0),
        "occupied_rooms": data.get("occupied_rooms", 0),
        "available_doctors": data.get("available_doctors", 0),
        "active_admissions": data.get("active_admissions", 0),
    }


# ==========================================================
# PATIENTS
# ==========================================================

@app.get("/patients")
def patients():

    rows = get_admin_patients()

    return [
        patient_to_dict(row)
        for row in rows
    ]


@app.post("/delete-patient")
def delete_patient(data: DeletePatientRequest):

    result = delete_patient_by_id(
        data.patient_id
    )

    return {
        "success": True,
        "message": result
    }


# ==========================================================
# DOCTORS
# ==========================================================

@app.get("/doctors")
def doctors():

    rows = get_admin_doctors()

    return [
        doctor_to_dict(row)
        for row in rows
    ]


# ==========================================================
# ROOMS
# ==========================================================

@app.get("/rooms")
def rooms():

    rows = get_admin_rooms()

    return [
        room_to_dict(row)
        for row in rows
    ]


# ==========================================================
# ADMISSIONS
# ==========================================================

@app.get("/admissions")
def admissions():

    rows = get_admin_admissions()

    return [
        admission_to_dict(row)
        for row in rows
    ]


@app.post("/admit-patient")
def admit_patient(data: AdmissionRequest):

    result = admit_patient_with_full_details(
        data.patient_name,
        data.age,
        data.gender,
        data.phone,
        data.address,
        data.room_type,
        data.specialization,
        data.insurance_provider
    )

    return {
        "success": True,
        "message": result
    }


@app.post("/delete-admission")
def delete_admission(data: DeleteAdmissionRequest):

    result = delete_admission_by_id(
        data.admission_id
    )

    return {
        "success": True,
        "message": result
    }
# ==========================================================
# AI CHATBOT
# ==========================================================

@app.post("/chatbot")
def chatbot(data: ChatRequest):
    """
    Main AI Chatbot Endpoint.
    Handles:
    - Conversation memory
    - Hospital context
    - Tool calling
    - General chat
    """

    try:
        # ----------------------------------------
        # Load previous conversation
        # ----------------------------------------

        history = get_history(data.session_id)

        conversation_history = ""

        for item in history:
            conversation_history += (
                f"{item['role']}: {item['content']}\n"
            )

        # ----------------------------------------
        # Load hospital knowledge
        # ----------------------------------------

        hospital_context = build_hospital_context()

        # ----------------------------------------
        # Ask AI
        # ----------------------------------------

        ai_response = safe_chat_response(
            user_message=data.message,
            conversation_history=conversation_history,
            hospital_context=hospital_context
        )

        # ----------------------------------------
        # Extract reply
        # ----------------------------------------

        if isinstance(ai_response, dict):
            reply = ai_response.get(
                "reply",
                "Sorry, I couldn't generate a response."
            )
        else:
            reply = str(ai_response)

        # ----------------------------------------
        # Save conversation
        # ----------------------------------------

        add_message(
            data.session_id,
            "user",
            data.message
        )

        add_message(
            data.session_id,
            "assistant",
            reply
        )

        # ----------------------------------------
        # Return response
        # ----------------------------------------

        return {
            "success": True,
            "reply": reply
        }

    except Exception as e:

        print("CHATBOT ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# ==========================================================
# DOCTOR SPECIALIZATION SUGGESTION
# ==========================================================

@app.post("/suggest-specialization")
def suggest_specialization(data: SpecializationRequest):

    symptoms = data.message.lower()

    if any(word in symptoms for word in [
        "heart", "chest pain", "bp",
        "blood pressure", "breathing"
    ]):
        specialization = "Cardiologist"

    elif any(word in symptoms for word in [
        "ear", "nose", "throat",
        "sinus", "cold", "cough"
    ]):
        specialization = "ENT"

    elif any(word in symptoms for word in [
        "tooth", "teeth", "gum",
        "mouth", "dental"
    ]):
        specialization = "Dentist"

    elif any(word in symptoms for word in [
        "child", "baby", "kid",
        "children", "infant"
    ]):
        specialization = "Pediatrician"

    elif any(word in symptoms for word in [
        "skin", "rash", "itching",
        "allergy", "pimples", "acne"
    ]):
        specialization = "Dermatologist"

    else:
        specialization = "General Physician"

    return {
        "success": True,
        "specialization": specialization
    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "backend": "running"
    }