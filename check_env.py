import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

if key:
    print("SUCCESS: Gemini API key loaded.")
else:
    print("ERROR: GEMINI_API_KEY was not found in .env.")