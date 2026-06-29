import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")

url = f"https://api.groq.com/openai/v1/chat/completions"

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "user",
            "content": "hello"
        }
    ]
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.text)