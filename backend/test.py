import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "hello"
                }
            ]
        }
    ]
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.text)