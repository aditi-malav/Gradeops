import os

from dotenv import load_dotenv
import google.generativeai as genai

# Load variables from .env
load_dotenv()

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_gemini_model():
    """
    Return a configured Gemini model instance.
    """
    return genai.GenerativeModel("gemini-2.5-flash")