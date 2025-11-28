import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

# Configuration Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
MODEL_NAME = "gemini-1.5-flash-preview-0514" 

# Ghanaian Holidays (MM-DD) for 2025-2026 academic year
GHANA_HOLIDAYS = [
    "12-05", # Farmer's Day
    "12-25", # Christmas Day
    "12-26", # Boxing Day
    "01-01", # New Year's Day
    "01-07", # Constitution Day
    "03-06", # Independence Day
]