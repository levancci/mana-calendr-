import datetime
import streamlit as st
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from config import GHANA_HOLIDAYS
from calendar_tools import insert_calendar_event as raw_insert_event

# ... (Helper functions get_next_weekday and calculate_exdates remain exactly the same) ...
def get_next_weekday(start_date, weekday_name):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_name = weekday_name.capitalize()
    try:
        target_day_index = days.index(weekday_name)
    except ValueError:
        map_short = {"Mo":0, "Tu":1, "We":2, "Th":3, "Fr":4, "Sa":5, "Su":6}
        target_day_index = map_short.get(weekday_name[:2], 0)

    current_day_index = start_date.weekday()
    days_ahead = target_day_index - current_day_index
    if days_ahead <= 0: 
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)

def calculate_exdates(start_datetime_obj, end_date_obj):
    exdates = []
    current = start_datetime_obj
    while current.date() <= end_date_obj:
        date_str = current.strftime("%m-%d")
        if date_str in GHANA_HOLIDAYS:
            exdates.append(current.strftime("%Y%m%dT%H%M%S"))
        current += datetime.timedelta(weeks=1)
    return exdates

def schedule_recurring_class(summary: str, day_of_week: str, start_time: str, end_time: str, description: str) -> str:
    """
    Schedules a recurring academic class for the next 3 months, skipping Ghanaian holidays.
    
    Args:
        summary (str): Title of the class (e.g., "CSM 101").
        day_of_week (str): Day it occurs (e.g., "Monday").
        start_time (str): Start time in HH:MM (24h format).
        end_time (str): End time in HH:MM (24h format).
        description (str): Extra details like lecturer or venue.
    """
    try:
        today = datetime.datetime.now()
        semester_end = today + relativedelta(months=3)
        recurrence_until = semester_end.strftime("%Y%m%dT235959Z")

        sh, sm = map(int, start_time.split(':')[:2])
        eh, em = map(int, end_time.split(':')[:2])

        first_date = get_next_weekday(today, day_of_week)
        start_dt = first_date.replace(hour=sh, minute=sm, second=0, microsecond=0)
        end_dt = first_date.replace(hour=eh, minute=em, second=0, microsecond=0)

        exception_dates = calculate_exdates(start_dt, semester_end.date())
        
        recurrence_rule = [f"RRULE:FREQ=WEEKLY;UNTIL={recurrence_until}"]
        if exception_dates:
            recurrence_rule.append("EXDATE;TZID=GMT:" + ",".join(exception_dates))

        # Insert the event
        event = raw_insert_event(
            calendar_id='primary',
            summary=summary,
            description=description,
            start={'dateTime': start_dt.isoformat(), 'timeZone': 'GMT'},
            end={'dateTime': end_dt.isoformat(), 'timeZone': 'GMT'},
            recurrence=recurrence_rule
        )
        
        # Save ID to Session State for Undo
        if "created_event_ids" not in st.session_state:
            st.session_state.created_event_ids = []
        
        st.session_state.created_event_ids.append(event['id'])

        return f"Success: Scheduled {summary} (ID: {event['id']})"
    except Exception as e:
        return f"Error scheduling {summary}: {str(e)}"

# FIX: Just export the function itself. DO NOT wrap it in FunctionTool()
schedule_tool = schedule_recurring_class