from src.grayfia.client import authenticate, get_events, get_tasks
from src.grayfia.normalizer import normalize_all

if __name__ == "__main__":
    creds = authenticate()

    if creds:
        events = get_events(creds)
        tasks = get_tasks(creds)

        schedule = normalize_all(events, tasks)

        for item in schedule:
            print(f"[{item['type'].upper()}] {item['title']}")
            print(f"  Start: {item['start']}  End: {item['end']}")
            print(f"  Status: {item['status']}  Source: {item['source']}")
            print()
    else:
        print("Authentication Failed")