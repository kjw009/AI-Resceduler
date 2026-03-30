from typing import Optional


def normalize_event(event: dict) -> dict:
    """
    Normalizes a raw Google Calendar event into a unified schema.

    Args:
        event (dict): A raw event dict from the Google Calendar API.

    Returns:
        dict: A normalized event.
    """
    start = event.get('start', {})
    end = event.get('end', {})

    return {
        'id': event.get('id'),
        'title': event.get('summary', 'Untitled Event'),
        'start': start.get('dateTime') or start.get('date'),
        'end': end.get('dateTime') or end.get('date'),
        'type': 'event',
        'source': 'google_calendar',
        'priority': None,
        'status': event.get('status', 'confirmed'),
        'description': event.get('description'),
    }


def normalize_task(task: dict) -> dict:
    """
    Normalizes a raw Google Tasks entry into a unified schema.

    Args:
        task (dict): A raw task dict from the Google Tasks API.

    Returns:
        dict: A normalized task.
    """
    raw_status = task.get('status', 'needsAction')
    status = 'completed' if raw_status == 'completed' else 'pending'

    return {
        'id': task.get('id'),
        'title': task.get('title', 'Untitled Task'),
        'start': None,
        'end': task.get('due'),
        'type': 'task',
        'source': 'google_tasks',
        'priority': None,
        'status': status,
        'description': task.get('notes'),
        'task_list': task.get('task_list_title'),
    }


def normalize_all(events: list, tasks: list) -> list:
    """
    Normalizes and combines events and tasks into a single sorted list.

    Args:
        events (list): Raw events from Google Calendar API.
        tasks (list): Raw tasks from Google Tasks API.

    Returns:
        list: Combined and normalized list, tasks with due dates sorted first.
    """
    normalized = []

    for event in events:
        normalized.append(normalize_event(event))

    for task in tasks:
        normalized.append(normalize_task(task))

    # Sort: items with a start/end date first, then undated tasks
    normalized.sort(key=lambda x: (x['start'] or x['end'] or '', x['type']))

    return normalized
