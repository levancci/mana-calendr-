import json
from Google_apis import create_service

# Configuration
CLIENT_SECRET_FILE = 'credentials.json' # Make sure you downloaded this from Google Cloud
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

def construct_google_calendar_client(client_secret):
    return create_service(client_secret, API_NAME, API_VERSION, SCOPES)

# Initialize service globally for tools to use
service = construct_google_calendar_client(CLIENT_SECRET_FILE)

def create_calendar_list(calendar_name):
    calendar_list = {
        'summary': calendar_name
    }
    created_calendar = service.calendars().insert(body=calendar_list).execute()
    return created_calendar

def list_calendar_list(max_capacity=200):
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)
        
    all_calendars = []
    all_calendars_cleaned = []
    next_page_token = None
    capacity_tracker = 0

    while capacity_tracker < max_capacity:
        page_results = service.calendarList().list(
            maxResults=min(200, max_capacity - capacity_tracker),
            pageToken=next_page_token
        ).execute()

        calendars = page_results.get('items', [])
        all_calendars.extend(calendars)
        capacity_tracker += len(calendars)
        next_page_token = page_results.get('nextPageToken')
        
        if not next_page_token:
            break

    for calendar in all_calendars:
        all_calendars_cleaned.append({
            'id': calendar['id'],
            'summary': calendar.get('summary', ''),
            'description': calendar.get('description', '')
        })

    return all_calendars_cleaned

def list_calendar_events(calendar_id, max_capacity=20):
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    all_events = []
    next_page_token = None
    capacity_tracker = 0

    while capacity_tracker < max_capacity:
        page_results = service.events().list(
            calendarId=calendar_id,
            maxResults=min(250, max_capacity - capacity_tracker),
            pageToken=next_page_token
        ).execute()

        events = page_results.get('items', [])
        all_events.extend(events)
        capacity_tracker += len(events)
        next_page_token = page_results.get('nextPageToken')

        if not next_page_token:
            break

    return all_events

def insert_calendar_event(calendar_id, **kwargs):
    # Convert kwargs to correct JSON format
    # Example kwargs: summary="Meeting", start={'dateTime':...}, end={'dateTime':...}
    request_body = kwargs
    
    event = service.events().insert(
        calendarId=calendar_id,
        body=request_body
    ).execute()

    return event