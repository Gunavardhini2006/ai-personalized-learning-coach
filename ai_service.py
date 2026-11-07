
import os
import time
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Get API key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key not found in .env file")

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


def generate_ai_response(prompt):

    max_attempts = 3

    for attempt in range(max_attempts):

        try:
            print(f"Connecting to Gemini... Attempt {attempt + 1}")

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response")

            return response.text

        except Exception as e:

            error_message = str(e).lower()

            temporary_errors = [
                "503",
                "unavailable",
                "429",
                "500",
                "502",
                "504",
                "temporarily"
            ]

            is_temporary = any(
                error in error_message
                for error in temporary_errors
            )

            if is_temporary and attempt < max_attempts - 1:

                wait_time = 2 ** (attempt + 1)

                print(f"Temporary API error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

            else:
                print("Gemini API Error:", e)
                return None

    return None
