from typing import List
from pydantic import BaseModel, Field

class CalendarEvent(BaseModel):
    summary: str = Field(description="Title of the event (e.g., 'CSM 258')")
    day_of_week: str = Field(description="Day of the week (Monday, Tuesday, Wednesday, Thursday, Friday)")
    start_time: str = Field(description="Start time in HH:MM format (24-hour), e.g., '14:00'")
    end_time: str = Field(description="End time in HH:MM format (24-hour), e.g., '16:00'")
    description: str = Field(description="Lecturer, location, or group info")
    
class SchedulePlan(BaseModel):
    events: List[CalendarEvent] = Field(description="List of events to be scheduled")