from google.adk.agents import Agent
from google.adk.models import Gemini
from config import MODEL_NAME
from tools import schedule_recurring_class

# Initialize the Model
# ADK's VertexAIModel handles the connection to Gemini
model = Gemini(model=MODEL_NAME)

# Define the Agent
# We use a simple Agent (which is an LlmAgent) as it perfectly fits the "Vision -> Tool" flow.
timetable_agent = Agent(
    name="GhanaTimetableScheduler",
    model=model,
    tools=[schedule_recurring_class], # The agent can call this tool directly
    instruction="""
    You are an expert academic scheduler assistant.
    
    YOUR GOAL:
    Take an image of a timetable and schedule all the classes found within it into the user's calendar.

    STEPS:
    1.  **Analyze the Image:** Look at the provided timetable image. Identify every class slot.
    2.  **Extract Details:** For each class, identify:
        * Course Code/Name (Summary)
        * Day of the Week (Monday - Friday)
        * Start and End Times. IMPORTANT: Use the slot headers to determine times. 
            * Slot 1 starts at 08:00.
            * Slot 7 starts at 15:00 (3 PM). 
            * Generally slots are 1 hour.
        * Lecturer/Venue (Description)
    3.  **Execute Tools:** For EACH class you identify, call the `schedule_recurring_class` tool. 
    
    CRITICAL NOTES:
    * Do not ask the user for confirmation for every single event. Plan the schedule and execute the tool calls.
    * If the image is blurry or ambiguous, ask the user for clarification.
    * Assume the current year for scheduling context.
    """
)