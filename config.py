import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Ensure you have Google Cloud authentication set up (gcloud auth application-default login)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
MODEL_NAME = "gemini-2.5-flash"

# Ghanaian Holidays (MM-DD)
GHANA_HOLIDAYS = [
    "12-05", # Farmer's Day
    "12-25", # Christmas Day
    "12-26", # Boxing Day
    "01-01", # New Year's Day
    "01-07", # Constitution Day
    "03-06", # Independence Day
]