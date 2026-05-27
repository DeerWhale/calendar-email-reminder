"""Google Calendar authentication and API interaction."""

import logging
import os.path
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Google Calendar color ID for red events
RED_COLOR_ID = '11'


def get_calendar_service():
    """Authenticate and return the Google Calendar service."""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json not found. Please download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except HttpError as error:
        logger.error(f"Failed to build calendar service: {error}")
        return None


def get_red_events_in_next_10_minutes(service, calendar_id: str = 'primary') -> List[Dict]:
    """
    Fetch calendar events with red color that start in the next 7-12 minutes.

    Args:
        service: Google Calendar API service object
        calendar_id: Calendar ID (default is 'primary' for main calendar)

    Returns:
        List of event dictionaries containing relevant event information
    """
    try:
        now = datetime.utcnow()
        time_min = now + timedelta(minutes=7)
        time_max = now + timedelta(minutes=12)
        
        # Convert to RFC3339 format
        time_min_rfc = time_min.isoformat() + 'Z'
        time_max_rfc = time_max.isoformat() + 'Z'
        
        # Fetch events
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min_rfc,
            timeMax=time_max_rfc,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Filter for red color events
        red_events = []
        for event in events:
            color_id = event.get('colorId')
            if color_id == RED_COLOR_ID:
                red_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                })
        
        return red_events
    
    except HttpError as error:
        logger.error(f"Failed to fetch calendar events: {error}")
        return []


def format_event_time(datetime_str: str) -> str:
    """Format ISO datetime string to readable format."""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except Exception as e:
        return datetime_str
