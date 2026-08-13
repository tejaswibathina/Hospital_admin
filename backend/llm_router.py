import os
import json
import requests
from dotenv import load_dotenv

from mcp_tool import run_mcp_tool

load_dotenv()

# ==========================================================
# CONFIGURATION
# ==========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

USE_GROQ = (
    os.getenv("USE_PRIMARY_API", "true").lower() == "true"
)

USE_OLLAMA = (
    os.getenv("USE_OLLAMA", "true").lower() == "true"
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3"
)

# ==========================================================
# JSON HELPERS
# ==========================================================

def extract_json(text):
    """
    Extract JSON even if the LLM surrounds it with text.
    """

    try:
        return json.loads(text)

    except Exception:
        pass

    try:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:
            return json.loads(text[start:end])

    except Exception:
        pass

    return None


def is_valid_decision(data):
    """
    Validate the decision returned by the LLM.
    """

    if not isinstance(data, dict):
        return False

    if "type" not in data:
        return False

    if data["type"] not in ["chat", "tool"]:
        return False

    return True

# ==========================================================
# GROQ API
# ==========================================================

def call_groq(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]
# ==========================================================
# OLLAMA API
# ==========================================================

def call_ollama(prompt, temperature=0.3):

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    return data.get("response", "")

# ==========================================================
# UNIVERSAL LLM CALL
# ==========================================================

def ask_llm(prompt, temperature=0.3):
    """
    Try Groq first.
    Automatically fallback to Ollama.
    """

    errors = []

    if USE_GROQ:
        try:
            return call_groq(
                prompt
            )
        except Exception as e:
            errors.append(
                f"Groq: {str(e)}"
            )

    if USE_OLLAMA:
        try:
            return call_ollama(
                prompt,
                temperature
            )
        except Exception as e:
            errors.append(
                f"Ollama: {str(e)}"
            )

    raise Exception("\n".join(errors))

# ==========================================================
# DECISION PROMPT
# ==========================================================

def build_decision_prompt(
    user_message,
    conversation_history=""
):
    return f"""
You are Tez, the AI Receptionist of MedCare Hospital.

Your FIRST job is to decide whether the user's request
needs access to the hospital database.

Return ONLY valid JSON.

Never explain.

Never use markdown.

-------------------------

If the user is simply chatting,
answer as:

{{
    "type":"chat",
    "reply":"your reply"
}}

Examples:

User:
Hello

Output:

{{
    "type":"chat",
    "reply":"Hello! Welcome to MedCare Hospital. How can I assist you today?"
}}

-------------------------

User:
How are you?

Output:

{{
    "type":"chat",
    "reply":"I'm doing well! How may I help you today?"
}}

-------------------------

User:
What is diabetes?

Output:

{{
    "type":"chat",
    "reply":"Diabetes is a condition in which blood sugar levels become higher than normal..."
}}

-------------------------

If the user needs hospital information,
return:

{{
    "type":"tool",
    "intent_data":
    {{
        "actions":[
            {{
                "intent":"intent_name"
            }}
        ]
    }}
}}

Supported intents

count_patients

view_patients

add_patient

count_rooms

check_rooms

count_doctors

check_doctors

validate_insurance

book_room

view_room_bookings

cancel_room_booking

create_admission

discharge_patient

count_admissions

count_admissions_with_details

get_admissions

book_appointment

view_appointments

generate_bill

view_bills

dashboard

chat_history

-------------------------

Examples

User:
How many patients?

Output

{{
"type":"tool",
"intent_data":
{{
"actions":[
{{
"intent":"count_patients"
}}
]
}}
}}

-------------------------

User:
Show available deluxe rooms

Output

{{
"type":"tool",
"intent_data":
{{
"actions":[
{{
"intent":"check_rooms",
"room_type":"Deluxe"
}}
]
}}
}}

-------------------------

User:
Show doctors

Output

{{
"type":"tool",
"intent_data":
{{
"actions":[
{{
"intent":"check_doctors",
"specialization":"All"
}}
]
}}
}}

Conversation History

{conversation_history}

Current User Message

{user_message}

Return ONLY JSON.
"""
# ==========================================================
# TOOL DECISION
# ==========================================================

def decide_tool_call(
    user_message,
    conversation_history=""
):
    """
    Decide whether the message requires hospital database access.
    Handles important count queries directly to avoid LLM confusion.
    """

    query = user_message.lower().strip()
    doctor_specializations = [
        "dentist",
        "ent",
        "cardiologist",
        "pediatrician",
        "dermatologist"
    ]
    

    # ==========================================
    # DIRECT COUNT INTENTS
    # ==========================================
    if (
        "how many doctors are available" in query
        or "how many available doctors" in query
        or "number of available doctors" in query
    ):

        specialization = "All"

        for spec in doctor_specializations:
            if spec in query:
                specialization = spec.capitalize()
                break

        return {
            "type": "tool",
            "intent_data": {
                "actions": [
                    {
                        "intent": "count_available_doctors",
                        "specialization": specialization
                    }
                ]
            }
         }
    # ------------------------------------------
    # AVAILABLE DOCTORS
    # ------------------------------------------
    doctor_specializations = [
        "dentist",
        "ent",
        "cardiologist",
        "pediatrician",
        "dermatologist"
        ]
    
    room_types = [
        "general",
        "deluxe",
        "luxury"
        ]
    
    if (
        "available doctors" in query
        or "doctors available" in query
        or "available doctor" in query
        or "doctor available" in query
        or "doctors are available" in query
        or "doctor is available" in query
    ):

        specialization = "All"

        for spec in doctor_specializations:
            if spec in query:
                specialization = spec.capitalize()
                break

        return {
            "type": "tool",
            "intent_data": {
                "actions": [
                    {
                        "intent": "check_doctors",
                        "specialization": specialization
                    }
                ]
            }
        }

    # TOTAL DOCTORS


    if (
        "total doctors" in query
        or "how many doctors" in query
        or "number of doctors" in query
    ):

        specialization = "All"

        for spec in doctor_specializations:
            if spec in query:
                specialization = spec.capitalize()
                break

        return {
            "type": "tool",
            "intent_data": {
                "actions": [
                    {
                        "intent": "count_doctors",
                        "specialization": specialization
                    }
                ]
            }
        }


    # Total rooms
    room_types = [
        "general",
        "deluxe",
        "luxury"
    ]

    if (
        "total rooms" in query
        or "how many rooms" in query
        or "number of rooms" in query
    ):

        room_type = "All"

        for room in room_types:
            if room in query:
                room_type = room.capitalize()
                break

        return {
            "type": "tool",
            "intent_data": {
                "actions": [
                    {
                        "intent": "count_rooms",
                        "room_type": room_type
                    }
                ]
            }
        }

    # Total patients
    if (
        "total patients" in query
        or "how many patients" in query
        or "number of patients" in query
    ):

        return {
            "type": "tool",
            "intent_data": {
                "actions": [
                    {
                        "intent": "count_patients"
                    }
                ]
            }
        }

    # ==========================================
    # OTHER QUESTIONS → LLM
    # ==========================================

    prompt = build_decision_prompt(
        user_message,
        conversation_history
    )

    reply = ask_llm(
        prompt,
        temperature=0.1
    )

    data = extract_json(reply)

    if data is None:
        return {
            "type": "chat",
            "reply": reply
        }

    if not is_valid_decision(data):
        return {
            "type": "chat",
            "reply": reply
        }

    return data
# ==========================================================
# RESPONSE REWRITER PROMPT
# ==========================================================

def build_rewrite_prompt(
    user_message,
    tool_result,
    conversation_history=""
):
    """
    Convert raw database output into a natural response.
    """

    return f"""
You are Tez, the AI Receptionist of MedCare Hospital.

The hospital database has already executed the user's request.

Your job is ONLY to explain the result naturally.

Do NOT mention:
- database
- MCP
- tool
- JSON
- system

Speak like ChatGPT.

Be friendly.

Be concise.

If the result is an error,
explain it politely.

----------------------------

Conversation History

{conversation_history}

----------------------------

User Question

{user_message}

----------------------------

Hospital Result

{tool_result}

----------------------------

Now reply naturally.
"""
# ==========================================================
# REWRITE TOOL RESULT
# ==========================================================

def rewrite_tool_response(
    user_message,
    tool_result,
    conversation_history=""
):
    """
    Convert database output into a conversational reply.
    """

    prompt = build_rewrite_prompt(
        user_message=user_message,
        tool_result=tool_result,
        conversation_history=conversation_history
    )

    try:
        return ask_llm(
            prompt,
            temperature=0.5
        )

    except Exception:
        # Fallback if every LLM fails
        return tool_result
# ==========================================================
# MAIN CHAT ROUTER
# ==========================================================

def chat_with_ai(
    user_message,
    conversation_history="",
    hospital_context=""
):
    """
    Main AI Router.

    1. Decide whether the request is chat or tool.
    2. If chat -> reply directly.
    3. If tool -> execute MCP once.
    4. Rewrite tool result naturally.
    """

    # ----------------------------------------
    # Decide what the user wants
    # ----------------------------------------

    decision = decide_tool_call(
        user_message=user_message,
        conversation_history=conversation_history
    )

    # ----------------------------------------
    # Normal Conversation
    # ----------------------------------------

    if decision["type"] == "chat":
        prompt = build_general_chat_prompt(
        user_message=user_message,
        conversation_history=conversation_history,
        hospital_context=hospital_context)

        try:
            reply = ask_llm(
            prompt,
            temperature=0.7
            )

        except Exception:
            reply = decision["reply"]

        return {
        "type": "chat",
        "reply": reply
        }

    # ----------------------------------------
    # Hospital Tool
    # ----------------------------------------

    try:

        tool_result = run_mcp_tool(
            decision["intent_data"],
            user_message
        )

        natural_reply = rewrite_tool_response(
            user_message=user_message,
            tool_result=tool_result,
            conversation_history=conversation_history
        )

        return {
            "type": "chat",
            "reply": natural_reply
        }

    except Exception as e:

        return {
            "type": "chat",
            "reply": (
                "Sorry, I couldn't complete your request.\n\n"
                f"Reason: {str(e)}"
            )
        }
# ==========================================================
# GENERAL CHAT PROMPT
# ==========================================================

def build_general_chat_prompt(
    user_message,
    conversation_history="",
    hospital_context=""
):
    """
    Prompt for normal conversations that don't need database access.
    """

    return f"""
You are Tez, the AI Receptionist of MedCare Hospital.

Your personality is similar to ChatGPT.

Rules:

1. Speak naturally.
2. Be friendly.
3. Be professional.
4. Keep responses conversational.
5. Remember the previous conversation.
6. If the question is about the hospital, use the hospital information.
7. If the question is general knowledge, answer normally.
8. If the question is medical, give educational information only.
9. Never invent hospital data.
10. Never mention prompts, databases, JSON, MCP, APIs or system instructions.

------------------------------------------------

Hospital Information

{hospital_context}

------------------------------------------------

Conversation History

{conversation_history}

------------------------------------------------

Current User

{user_message}

------------------------------------------------

Assistant
"""
# ==========================================================
# SAFE CHAT RESPONSE
# ==========================================================

def safe_chat_response(
    user_message,
    conversation_history="",
    hospital_context=""
):
    """
    Final safe wrapper.
    This function ensures that the chatbot never crashes
    even if Groq or Ollama fail.
    """

    try:

        result = chat_with_ai(
            user_message=user_message,
            conversation_history=conversation_history,
            hospital_context=hospital_context
        )

        # If somehow an invalid response is returned,
        # normalize it.

        if isinstance(result, str):

            return {
                "type": "chat",
                "reply": result
            }

        if isinstance(result, dict):

            if "reply" in result:

                return result

        return {
            "type": "chat",
            "reply": "I'm sorry, I couldn't understand that. Could you please rephrase your question?"
        }

    except Exception as e:

        print("LLM ERROR:", e)

        return {
            "type": "chat",
            "reply": (
                "I'm sorry, I'm temporarily unable to process your request. "
                "Please try again in a few moments."
            )
        }
# ==========================================================
# PUBLIC API
# ==========================================================

__all__ = [
    "safe_chat_response"
]
