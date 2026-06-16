import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()


# ---------------- CONFIG ----------------

USE_PRIMARY_API = os.getenv("USE_PRIMARY_API", "true").lower() == "true"
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_URL = os.getenv("OLLAMA_URL")


# ---------------- BASIC HELPERS ----------------

def has_word(query, word):
    return re.search(rf"\b{re.escape(word)}\b", query, re.IGNORECASE) is not None


def has_any_word(query, words):
    return any(has_word(query, word) for word in words)


def extract_json_from_text(text):
    try:
        return json.loads(text)
    except Exception:
        pass

    try:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:
            json_text = text[start:end]
            return json.loads(json_text)

    except Exception:
        pass

    return None


def is_valid_intent_data(data):
    if not isinstance(data, dict):
        return False

    if "actions" not in data:
        return False

    if not isinstance(data["actions"], list):
        return False

    if len(data["actions"]) == 0:
        return False

    for action in data["actions"]:
        if not isinstance(action, dict):
            return False

        if "intent" not in action:
            return False

    return True


# ---------------- PROMPT FOR API AND OLLAMA ----------------

def build_llm_prompt(user_query):
    return f"""
You are an intent parser for an AI Hospital Management System.

Your job is to convert the user's question into JSON only.

Do not explain.
Do not write markdown.
Return only valid JSON.

Supported intents:

1. count_patients
2. view_patients
3. add_patient
4. count_admissions_with_details
5. get_admissions
6. book_room
7. view_room_bookings
8. cancel_room_booking
9. create_admission
10. discharge_patient
11. book_appointment
12. view_appointments
13. generate_bill
14. view_bills
15. dashboard
16. chat_history
17. count_rooms
18. check_rooms
19. count_doctors
20. check_doctors
21. validate_insurance
22. unknown

Allowed room_type values:
General, Deluxe, Luxury, All

Allowed specialization values:
Dentist, ENT, Cardiologist, Pediatrician, Dermatologist, All

Allowed insurance provider values:
LIC, AIG, Indian, SBI, All

Important rules:
- For actual admission, use intent create_admission only if the user clearly says admit patient.
- For "how many patients admitted", use count_admissions_with_details.
- For "total patients", use count_patients.
- For "show patients", use view_patients.
- For "show admitted patients", use get_admissions.
- If patient name is missing, keep patient_name as null.
- If room type is missing for admission, use General.
- If specialization is missing for admission, use ENT.
- If insurance is missing for admission, use LIC.
- For doctor count, use count_doctors.
- For room count, use count_rooms.
- If question asks only doctors, do not include rooms or insurance.
- If question asks only patients, do not include doctors.
- If question asks multiple things, return multiple actions.

Return format:
{{
  "actions": [
    {{
      "intent": "intent_name"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

Examples:

User: total patients
Output:
{{
  "actions": [
    {{
      "intent": "count_patients"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

User: show patients
Output:
{{
  "actions": [
    {{
      "intent": "view_patients"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

User: how many patients admitted
Output:
{{
  "actions": [
    {{
      "intent": "count_admissions_with_details"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

User: admit Sai in general with dentist
Output:
{{
  "actions": [
    {{
      "intent": "create_admission",
      "patient_name": "Sai",
      "room_type": "General",
      "specialization": "Dentist",
      "insurance_provider": "LIC"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

User: how many doctors available
Output:
{{
  "actions": [
    {{
      "intent": "count_doctors",
      "specialization": "All"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

User: show available deluxe rooms
Output:
{{
  "actions": [
    {{
      "intent": "check_rooms",
      "room_type": "Deluxe"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

User: show rooms and doctors
Output:
{{
  "actions": [
    {{
      "intent": "check_rooms",
      "room_type": "All"
    }},
    {{
      "intent": "check_doctors",
      "specialization": "All"
    }}
  ],
  "llm_used": "Primary API LLM"
}}

Now parse this user query:
{user_query}
"""


# ---------------- PRIMARY API LLM: GEMINI ----------------

def classify_with_primary_api(user_query):
    if not USE_PRIMARY_API:
        raise Exception("Primary API disabled.")

    if not GEMINI_API_KEY:
        raise Exception("Gemini API key missing.")

    prompt = build_llm_prompt(user_query)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 800
        }
    }

    response = requests.post(url, json=payload, timeout=20)

    if response.status_code != 200:
        raise Exception(f"Primary API failed: {response.text}")

    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]

    parsed = extract_json_from_text(text)

    if not is_valid_intent_data(parsed):
        raise Exception("Primary API returned invalid JSON.")

    parsed["llm_used"] = "Primary API LLM"

    return parsed


# ---------------- OLLAMA LOCAL LLM FALLBACK ----------------

def classify_with_ollama(user_query):
    if not USE_OLLAMA:
        raise Exception("Ollama disabled.")

    prompt = build_llm_prompt(user_query)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Ollama failed: {response.text}")

    data = response.json()

    text = data.get("response", "")

    parsed = extract_json_from_text(text)

    if not is_valid_intent_data(parsed):
        raise Exception("Ollama returned invalid JSON.")

    parsed["llm_used"] = "Ollama Local LLM"

    return parsed


# ---------------- RULE-BASED FALLBACK ----------------

def extract_patient_name(user_query):
    query = user_query.strip()

    patterns = [
        r"admit\s+([a-zA-Z ]+?)\s+(?:in|with|for|$)",
        r"discharge\s+([a-zA-Z ]+)",
        r"generate bill for\s+([a-zA-Z ]+)",
        r"bill for\s+([a-zA-Z ]+)",
        r"book\s+.*?\s+room for\s+([a-zA-Z ]+)",
        r"reserve\s+.*?\s+room for\s+([a-zA-Z ]+)",
        r"appointment for\s+([a-zA-Z ]+?)\s+(?:with|on|at|$)",
        r"book appointment for\s+([a-zA-Z ]+?)\s+(?:with|on|at|$)",
        r"add patient\s+([a-zA-Z ]+?)\s+(?:age|phone|address|$)",
        r"register patient\s+([a-zA-Z ]+?)\s+(?:age|phone|address|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

    return None


def classify_with_rule_based_parser(user_query):
    query = user_query.lower().strip()
    actions = []

    room_types = {
        "general": "General",
        "deluxe": "Deluxe",
        "duluxe": "Deluxe",
        "luxury": "Luxury"
    }

    specializations = {
        "dentist": "Dentist",
        "dental": "Dentist",
        "ent": "ENT",
        "cardiologist": "Cardiologist",
        "cardialogist": "Cardiologist",
        "heart": "Cardiologist",
        "pediatrician": "Pediatrician",
        "child": "Pediatrician",
        "children": "Pediatrician",
        "dermatologist": "Dermatologist",
        "dermotologist": "Dermatologist",
        "skin": "Dermatologist"
    }

    providers = {
        "lic": "LIC",
        "aig": "AIG",
        "indian": "Indian",
        "sbi": "SBI"
    }

    patient_name = extract_patient_name(user_query)

    found_room_type = None
    for key, value in room_types.items():
        if has_word(query, key):
            found_room_type = value
            break

    found_specialization = None
    for key, value in specializations.items():
        if has_word(query, key):
            found_specialization = value
            break

    found_provider = None
    for key, value in providers.items():
        if has_word(query, key):
            found_provider = value
            break

    # Patient registration
    if "add patient" in query or "register patient" in query:
        age_match = re.search(r"age\s+(\d+)", query)
        phone_match = re.search(r"phone\s+(\d+)", query)

        gender = "Not specified"
        if has_word(query, "female"):
            gender = "Female"
        elif has_word(query, "male"):
            gender = "Male"

        address = ""
        if "address" in query:
            address = user_query.split("address")[-1].strip()

        actions.append({
            "intent": "add_patient",
            "patient_name": patient_name,
            "age": int(age_match.group(1)) if age_match else 0,
            "gender": gender,
            "phone": phone_match.group(1) if phone_match else "",
            "address": address
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Total patients
    if (
        "total patients" in query
        or ("how many patients" in query and "admitted" not in query)
        or ("count patients" in query and "admitted" not in query)
        or ("number of patients" in query and "admitted" not in query)
    ):
        actions.append({
            "intent": "count_patients"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # View patients
    if (
        "show patients" in query
        or "view patients" in query
        or "list patients" in query
        or "patient details" in query
        or "all patients" in query
    ):
        actions.append({
            "intent": "view_patients"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Count admitted patients with details
    if (
        ("how many" in query or "count" in query or "number of" in query or "total" in query)
        and (
            "patients admitted" in query
            or "patient admitted" in query
            or "admitted patients" in query
            or "admissions" in query
            or "admitted" in query
        )
    ):
        actions.append({
            "intent": "count_admissions_with_details"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # View admissions
    if (
        "show admitted" in query
        or "view admitted" in query
        or "show admitted patients" in query
        or "view admitted patients" in query
        or "show admissions" in query
        or "view admissions" in query
        or "list admissions" in query
        or "admitted patient details" in query
        or "admission details" in query
    ):
        actions.append({
            "intent": "get_admissions"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Room booking
    if (
        ("book" in query or "reserve" in query)
        and ("room" in query or "bed" in query)
    ):
        actions.append({
            "intent": "book_room",
            "patient_name": patient_name,
            "room_type": found_room_type or "General"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # View booked rooms
    if (
        "show booked rooms" in query
        or "view booked rooms" in query
        or "room bookings" in query
        or "booked room details" in query
    ):
        actions.append({
            "intent": "view_room_bookings"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Cancel booking
    if "cancel" in query and "booking" in query:
        actions.append({
            "intent": "cancel_room_booking",
            "patient_name": patient_name
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Create admission
    if query.startswith("admit "):
        actions.append({
            "intent": "create_admission",
            "patient_name": patient_name,
            "room_type": found_room_type or "General",
            "specialization": found_specialization or "ENT",
            "insurance_provider": found_provider or "LIC"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Discharge patient
    if query.startswith("discharge "):
        actions.append({
            "intent": "discharge_patient",
            "patient_name": patient_name
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Appointment booking
    if "appointment" in query and ("book" in query or "schedule" in query):
        date_match = re.search(r"on\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", query)
        time_match = re.search(r"at\s+([0-9]{1,2}(:[0-9]{2})?\s?(am|pm)?)", query)

        actions.append({
            "intent": "book_appointment",
            "patient_name": patient_name,
            "specialization": found_specialization or "ENT",
            "appointment_date": date_match.group(1) if date_match else "2026-06-03",
            "appointment_time": time_match.group(1).upper() if time_match else "10 AM"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # View appointments
    if (
        "show appointments" in query
        or "view appointments" in query
        or "list appointments" in query
        or "appointment details" in query
    ):
        actions.append({
            "intent": "view_appointments"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Billing
    if "generate bill" in query or "bill for" in query:
        actions.append({
            "intent": "generate_bill",
            "patient_name": patient_name
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    if (
        "show bills" in query
        or "view bills" in query
        or "list bills" in query
        or "billing details" in query
    ):
        actions.append({
            "intent": "view_bills"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Dashboard
    if (
        "dashboard" in query
        or "summary" in query
        or "hospital status" in query
        or "hospital overview" in query
    ):
        actions.append({
            "intent": "dashboard"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Chat history
    if (
        "chat history" in query
        or "previous chats" in query
        or "recent chats" in query
        or "conversation history" in query
    ):
        actions.append({
            "intent": "chat_history"
        })

        return {
            "actions": actions,
            "llm_used": "Rule-Based Parser"
        }

    # Room check
    if has_any_word(query, ["room", "rooms", "bed", "beds"]):
        if "how many" in query or "count" in query or "number of" in query or "total" in query:
            actions.append({
                "intent": "count_rooms",
                "room_type": found_room_type or "All"
            })
        else:
            actions.append({
                "intent": "check_rooms",
                "room_type": found_room_type or "All"
            })

    # Doctor check
    if (
        has_any_word(query, ["doctor", "doctors", "physician", "physicians"])
        or found_specialization
    ):
        if "how many" in query or "count" in query or "number of" in query or "total" in query:
            actions.append({
                "intent": "count_doctors",
                "specialization": found_specialization or "All"
            })
        else:
            actions.append({
                "intent": "check_doctors",
                "specialization": found_specialization or "All"
            })

    # Insurance check
    if (
        has_any_word(query, ["insurance", "policy", "bank", "coverage"])
        or found_provider
    ):
        actions.append({
            "intent": "validate_insurance",
            "provider_name": found_provider or "All"
        })

    # Remove duplicates
    unique_actions = []
    seen = set()

    for action in actions:
        key = str(action)
        if key not in seen:
            unique_actions.append(action)
            seen.add(key)

    if not unique_actions:
        unique_actions.append({
            "intent": "unknown"
        })

    return {
        "actions": unique_actions,
        "llm_used": "Rule-Based Parser"
    }


# ---------------- FINAL ROUTER WITH FALLBACK CHAIN ----------------

def classify_user_request(user_query):
    errors = []

    try:
        result = classify_with_primary_api(user_query)
        return result
    except Exception as e:
        errors.append(f"Primary API failed: {str(e)}")

    try:
        result = classify_with_ollama(user_query)
        return result
    except Exception as e:
        errors.append(f"Ollama failed: {str(e)}")

    result = classify_with_rule_based_parser(user_query)
    result["fallback_errors"] = errors

    return result

import requests
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def chat_with_ai(
    user_message,
    conversation_history,
    hospital_context
):

    prompt = f"""
You are Sarah, a professional hospital receptionist.

Rules:

- You are the virtual receptionist of MedCare Hospital.
- Welcome users warmly.
- Answer naturally.
- Use hospital data when available.
- If information is unavailable, say so politely.
- Remember previous conversation context.
- Ask follow-up questions.
- Help users with doctors, rooms, admissions,
  insurance, billing and appointments.

Hospital Information:
{hospital_context}

Conversation History:
{conversation_history}

Patient:
{user_message}

Receptionist:
"""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        return "Sorry, I'm unable to assist right now."

    data = response.json()

    return (
        data["candidates"][0]
        ["content"]["parts"][0]["text"]
    )