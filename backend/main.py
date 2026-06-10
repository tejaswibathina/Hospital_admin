from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auth import verify_login, change_admin_password
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

from llm_router import classify_user_request
from mcp_client import run_mcp_tool


app = FastAPI(title="AI Hospital Management Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    message: str


class DeletePatientRequest(BaseModel):
    patient_id: int


class DeleteAdmissionRequest(BaseModel):
    admission_id: int


def patient_to_dict(row):
    return {
        "patient_id": row[0],
        "patient_name": row[1],
        "age": row[2],
        "gender": row[3],
        "phone": row[4],
        "address": row[5],
    }


def doctor_to_dict(row):
    return {
        "doctor_id": row[0],
        "doctor_name": row[1],
        "specialization": row[2],
        "phone": row[3],
        "availability_status": row[4],
        "consultation_fee": row[5],
    }


def room_to_dict(row):
    return {
        "room_id": row[0],
        "room_number": row[1],
        "room_type": row[2],
        "price_per_day": row[3],
        "status": row[4],
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
        "status": row[9],
    }


@app.get("/")
def home():
    return {
        "message": "AI Hospital Management Backend is running"
    }


@app.post("/login")
def login(data: LoginRequest):
    if verify_login(data.username, data.password):
        return {
            "success": True,
            "message": "Login successful",
            "role": "admin"
        }

    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/change-password")
def change_password(data: ChangePasswordRequest):
    success, message = change_admin_password(
        data.old_password,
        data.new_password
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message
    }


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


@app.get("/patients")
def patients():
    rows = get_admin_patients()
    return [patient_to_dict(row) for row in rows]


@app.get("/doctors")
def doctors():
    rows = get_admin_doctors()
    return [doctor_to_dict(row) for row in rows]


@app.get("/rooms")
def rooms():
    rows = get_admin_rooms()
    return [room_to_dict(row) for row in rows]


@app.get("/admissions")
def admissions():
    rows = get_admin_admissions()
    return [admission_to_dict(row) for row in rows]


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


@app.post("/delete-patient")
def delete_patient(data: DeletePatientRequest):
    result = delete_patient_by_id(data.patient_id)

    return {
        "success": True,
        "message": result
    }


@app.post("/delete-admission")
def delete_admission(data: DeleteAdmissionRequest):
    result = delete_admission_by_id(data.admission_id)

    return {
        "success": True,
        "message": result
    }


@app.post("/chatbot")
def chatbot(data: ChatRequest):
    intent_data = classify_user_request(data.message)
    result = run_mcp_tool(intent_data, data.message)

    return {
        "success": True,
        "reply": result,
        "llm_used": intent_data.get("llm_used", "System"),
        "intent_data": intent_data
    }


@app.post("/suggest-specialization")
def suggest_specialization(data: ChatRequest):
    symptoms = data.message.lower()

    if any(word in symptoms for word in ["chest pain", "heart", "breathing", "bp", "blood pressure"]):
        specialization = "Cardiologist"

    elif any(word in symptoms for word in ["ear", "nose", "throat", "cold", "cough", "sinus"]):
        specialization = "ENT"

    elif any(word in symptoms for word in ["tooth", "teeth", "gum", "dental", "mouth"]):
        specialization = "Dentist"

    elif any(word in symptoms for word in ["child", "baby", "kid", "children", "infant"]):
        specialization = "Pediatrician"

    elif any(word in symptoms for word in ["skin", "rash", "itching", "allergy", "pimples", "acne"]):
        specialization = "Dermatologist"

    else:
        specialization = "ENT"

    return {
        "specialization": specialization
    }