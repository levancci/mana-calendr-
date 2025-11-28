import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from google.adk.tools import tool
from config import GHANA_HOLIDAYS
# Import your existing calendar_tools wrapper
# Assuming calendar_tools.py is in the same directory and has insert_calendar_event
# You might need to adapt insert_calendar_event slightly to not rely on global 'service' 
# if you want to be purely stateless, but for now we wrap it.
from calendar_tools import insert_calendar_event as raw_insert_event

def get_next_weekday(start_date, weekday_name):
    """Finds the date of the next specific weekday."""
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
    """Generates EXDATE strings for holidays."""
    exdates = []
    current = start_datetime_obj
    while current.date() <= end_date_obj:
        date_str = current.strftime("%m-%d")
        if date_str in GHANA_HOLIDAYS:
            exdates.append(current.strftime("%Y%m%dT%H%M%S"))
        current += datetime.timedelta(weeks=1)
    return exdates

@tool
def schedule_recurring_class(summary: str, day_of_week: str, start_time: str, end_time: str, description: str) -> str:
    """
    Schedules a recurring class for the next 3 months, automatically skipping Ghanaian holidays.
    
    Args:
        summary: Title of the class (e.g., "CSM 101").
        day_of_week: Day it occurs (e.g., "Monday").
        start_time: Start time in HH:MM (24h).
        end_time: End time in HH:MM (24h).
        description: Extra details.
    """
    try:
        today = datetime.datetime.now()
        semester_end = today + relativedelta(months=3)
        recurrence_until = semester_end.strftime("%Y%m%dT235959Z")

        # Parse times
        sh, sm = map(int, start_time.split(':')[:2])
        eh, em = map(int, end_time.split(':')[:2])

        # Calculate actual start date
        first_date = get_next_weekday(today, day_of_week)
        start_dt = first_date.replace(hour=sh, minute=sm, second=0, microsecond=0)
        end_dt = first_date.replace(hour=eh, minute=em, second=0, microsecond=0)

        # Calculate exceptions
        exception_dates = calculate_exdates(start_dt, semester_end.date())
        
        recurrence_rule = [f"RRULE:FREQ=WEEKLY;UNTIL={recurrence_until}"]
        if exception_dates:
            recurrence_rule.append("EXDATE;TZID=GMT:" + ",".join(exception_dates))

        # Call the underlying Google Calendar API
        raw_insert_event(
            calendar_id='primary',
            summary=summary,
            description=description,
            start={'dateTime': start_dt.isoformat(), 'timeZone': 'GMT'},
            end={'dateTime': end_dt.isoformat(), 'timeZone': 'GMT'},
            recurrence=recurrence_rule
        )
        return f"Success: Scheduled {summary} on {day_of_week}s at {start_time}."
    except Exception as e:
        return f"Error scheduling {summary}: {str(e)}"