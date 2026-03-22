import requests
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Get your Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is not set. Make sure it's in your .env file.")

# ✅ Request model list
response = requests.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
)

# ✅ Print available models or show error
if response.status_code != 200:
    print("❌ Error:", response.status_code)
    print(response.text)
else:
    models = response.json()
    print("✅ Available models:")
    for model in models.get("data", []):
        print("🔹", model["id"])
