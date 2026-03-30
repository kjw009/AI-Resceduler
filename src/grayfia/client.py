# File Sharing 
import os.path

# Datetime
from datetime import datetime, timedelta

# Google Cloud Console
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/tasks.readonly']

class Grayfia:
    """
    A class to manage Google API interractions, including authentication,
    calendar event retrieval, and task list retrieval
    """

    def __init__(self):
        """Initialises Grayfia and attempts to authenticate"""
        self.creds = self._authenticate() # _authenticate is a private method

    def _authenticate(self):
        """
        Authenticates the user and obtains Google API credentials.

        This is a private method, indicated by the leading underscore.

        Returns:
            Credentials: An object containing the user's authentication credentials, or None if authentication fails.
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
        # Return       
        return creds
    
    def get_events(self, calendar_id='primary', time_min=None, time_max=None):
        """
        Retrieves events from a Google Calendar, with time_max defaulting to the end of the current week.

        Args:
            calendar_id (str, optional): The ID of the calendar to retrieve events from. Defaults to 'primary'.
            time_min (str, optional): The minimum start time for events (ISO 8601 format). Defaults to current time.
            time_max (str, optional): The maximum start time for events (ISO 8601 format). Defaults to the end of the current week.

        Returns:
            list: A list of event dictionaries, or an empty list if no events are found or an error occurs.
        """
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            now = datetime.utcnow()
            if not time_min:
                time_min = now.isoformat() + 'Z'
            if not time_max:
                days_until_sunday = (6 - now.weekday()) % 7
                end_of_week = now + timedelta(days=days_until_sunday, hours=23, minutes=59, seconds=59)
                time_max = end_of_week.isoformat() + 'Z'
            events = service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max, singleEvents=True, orderBy='startTime').execute()
            events = events.get('items', [])
            if not events:
                print('No upcoming events found.')
                return []
            return events
        except Exception as e:
            print(e)
            return []


    def get_tasks(self):
        """
        Retrieves all tasks from all task lists in Google Tasks, along with their associated task list.

        Args:
            creds (Credentials): The user's Google API credentials.

        Returns:
            list: A list of dictionaries, where each dictionary represents a task and includes the task details
                and the title of the task list it belongs to.
        """
        try:
            service = build('tasks', 'v1', credentials=self.creds)
            all_tasks = []

            # 1. Get all task lists
            task_lists_result = service.tasklists().list().execute()
            task_lists = task_lists_result.get('items', [])

            if not task_lists:
                print('No task lists found.')
                return []

            # 2. Iterate through each task list and get its tasks
            for task_list in task_lists:
                task_list_id = task_list['id']
                task_list_title = task_list['title']

                tasks_result = service.tasks().list(tasklist=task_list_id).execute()
                tasks = tasks_result.get('items', [])

                if tasks:
                    for task in tasks:
                        task['task_list_title'] = task_list_title  # Add task list title to task info
                        all_tasks.append(task)

            return all_tasks

        except Exception as e:
            print(f"An error occurred: {e}")
            return []