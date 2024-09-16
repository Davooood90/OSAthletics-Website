import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# API Scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Set up the Google Calendar API client


def build_cal_service():
    creds = Credentials.from_authorized_user_file('./token.json', SCOPES)
    return build('calendar', 'v3', credentials=creds)

# Format the Event


def build_event(title, desc, start_time, end_time):
    # Define the event details
    event = {
        'summary': title,
        'description': desc,
        'start': {
            'dateTime': start_time + ":00",
            'timeZone': 'America/Edmonton',
        },
        'end': {
            'dateTime': end_time + ":00",
            'timeZone': 'America/Edmonton',
        },
    }
    return event

# Create the Event
def create_event(service, event):
    # Call the Calendar API to create the event
    service.events().insert(calendarId='primary', body=event).execute()

# Get Events
def get_events(service, end):
    # Get Range
    start_time = datetime.datetime.utcnow()
    end_time = end
    # List of Events
    events_result = service.events().list(calendarId='primary', timeMin=start_time.isoformat(
    ) + 'Z', timeMax=end_time.isoformat() + 'Z', singleEvents=True, orderBy='startTime').execute()
    return events_result.get('items', [])

# Update Event
def update_event(service, eventId, info):
    # Get Event
    event = service.events().get(calendarId='primary', eventId=eventId).execute()

    # Change Info
    event['summary'] = info[0]
    event['description'] = info[1]
    event['start'] = {'dateTime': info[2] +
                      ":00", 'timeZone': 'America/Edmonton'}
    event['end'] = {'dateTime': info[3] +
                    ":00", 'timeZone': 'America/Edmonton'}

    # Update Event
    service.events().update(calendarId='primary', eventId=eventId, body=event).execute()

# Delete Event
def delete_event(service, eventId):
    service.events().delete(calendarId='primary', eventId=eventId).execute()
