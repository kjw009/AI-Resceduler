import os.path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/tasks.readonly']


def authenticate() -> Credentials:
    """
    Authenticates the user and returns Google API credentials.

    Loads existing credentials from token.json if available. Refreshes them
    if expired, or runs the OAuth 2.0 flow to obtain new ones.

    Returns:
        Credentials: The user's Google API credentials.
    """
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8000)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_events(creds: Credentials, calendar_id: str = 'primary', time_min: str = None, time_max: str = None) -> list:
    """
    Retrieves events from a Google Calendar.

    Args:
        creds: Google API credentials.
        calendar_id: The calendar to fetch from. Defaults to 'primary'.
        time_min: ISO 8601 start bound. Defaults to now.
        time_max: ISO 8601 end bound. Defaults to end of current week.

    Returns:
        list: A list of raw event dicts, or an empty list on failure.
    """
    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.utcnow()

        if not time_min:
            time_min = now.isoformat() + 'Z'
        if not time_max:
            days_until_sunday = (6 - now.weekday()) % 7
            end_of_week = now + timedelta(days=days_until_sunday, hours=23, minutes=59, seconds=59)
            time_max = end_of_week.isoformat() + 'Z'

        result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = result.get('items', [])
        if not events:
            print('No upcoming events found.')
            return []
        return events

    except Exception as e:
        print(e)
        return []


def get_tasks(creds: Credentials) -> list:
    """
    Retrieves all tasks from all Google Task lists.

    Args:
        creds: Google API credentials.

    Returns:
        list: A list of raw task dicts with 'task_list_title' added, or an empty list on failure.
    """
    try:
        service = build('tasks', 'v1', credentials=creds)
        all_tasks = []

        task_lists = service.tasklists().list().execute().get('items', [])
        if not task_lists:
            print('No task lists found.')
            return []

        for task_list in task_lists:
            tasks = service.tasks().list(tasklist=task_list['id']).execute().get('items', [])
            for task in tasks:
                task['task_list_title'] = task_list['title']
                all_tasks.append(task)

        return all_tasks

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
